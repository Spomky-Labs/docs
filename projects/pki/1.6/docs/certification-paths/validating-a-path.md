---
description: Running the RFC 5280 validation algorithm, what it checks, what it returns, and why the trust anchor is an input.
---

# Validating a path

```php
use SpomkyLabs\Pki\X509\CertificationPath\Exception\PathValidationException;
use SpomkyLabs\Pki\X509\CertificationPath\PathValidation\PathValidationConfig;

try {
    $result = $path->validate(PathValidationConfig::defaultConfig());
} catch (PathValidationException $e) {
    // the path does not validate; $e->getMessage() says why
}
```

Validation either returns a `PathValidationResult` or throws. There is no boolean and no partial success.

## The trust anchor is an input

This is the one thing to get right. **The trust anchor is something your application names, never
something read out of the material a peer sent.**

```php
// Right: the path is headed by a certificate from your own trust list.
$path = CertificationPath::toTarget($leafFromPeer, $trustAnchors, $intermediatesFromPeer);
$result = $path->validate(PathValidationConfig::defaultConfig());

// Right: you hold the path, so you name the anchor.
$config = PathValidationConfig::defaultConfig()->withTrustAnchor($root);
$result = $path->validate($config);
```

Left to itself, validation falls back to the first certificate of the path and then confirms only that
the chain is internally consistent — which any attacker can arrange with a root of their own.

The library makes that hard to do by accident:

| Path from | Without `withTrustAnchor()` |
|---|---|
| `toTarget()`, `fromTrustAnchorToTarget()` | fine: already headed by a certificate from the trust list you gave |
| `fromCertificateChain()` | **throws.** A peer decided what the first certificate is |
| `create()` | **deprecation notice**, then falls back to the first certificate. The fallback will be removed in the next major release |

Nothing in a `PathValidationResult` distinguishes a chain anchored in your trust store from one anchored
in an attacker's, which is why the warning is at the call rather than in the result. Use the deprecation
notice to find your `create()` call sites.

## What validation checks

The algorithm is RFC 5280 section 6.1, walked from the anchor to the target.

**Per certificate**

- the signature algorithm is in the allowed set — an algorithm not named is refused before the signature
  is even checked, because a signature is only as good as its digest;
- the issuer's RSA modulus is at or above the minimum key size;
- the signature verifies against the working public key;
- the validity period contains the reference time;
- the issuer DN equals the previous certificate's subject DN, under
  [the X.501 rules](../names/comparing-names.md);
- no name of the certificate falls outside the permitted subtrees or inside the excluded subtrees of the
  name constraints in force;
- every **critical** extension is one the validator recognises, or one you declared with
  `withAdditionalCriticalExtensions()`.

**Per intermediate, additionally**

- it is a v3 certificate carrying `basicConstraints` with `cA:TRUE` — a v1 or v2 certificate is refused
  unless you set `withLegacyV1IntermediatesTrusted(true)`;
- its `keyUsage`, if it has one, includes `keyCertSign`;
- the remaining path length has not run out, counting both the configured maximum and every
  `pathLenConstraint` met along the way.

**Across the path**

- the policy tree: certificate policies, policy mappings, `requireExplicitPolicy`, `inhibitPolicyMapping`
  and `inhibitAnyPolicy`, intersected with the initial policy set.

## The result

```php
$result = $path->validate($config);

$result->certificate();         // the end-entity certificate
$result->getPublicKeyInfo();    // its public key, as validation worked it out
$result->getPublicKeyAlgo();
$result->getPublicKeyParameters();
$result->policies();            // the policies valid for this path
$result->getPolicyTree();       // the tree, or null
```

`getPublicKeyInfo()` is the useful one: the key you may now rely on, carried forward through the path
including any inherited parameters.

## Using your own crypto engine

```php
$result = $path->validate($config, $crypto);
```

See [The crypto engine](../keys/the-crypto-engine.md).

## What the exception tells you

Everything raises `PathValidationException`, with a message naming the check that failed:

| Message | Means |
|---|---|
| `Signature algorithm … is not allowed.` | not in the configured set — SHA-1 if you hardened, MD5 always |
| `RSA key size … is below the minimum of … bits.` | the issuer's modulus is too small |
| `Certificate signature doesn't match.` | the signature is wrong |
| `Failed to verify signature: …` | the engine could not ask — often EdDSA on a runtime without it |
| `Certificate has expired.` / `… has not started.` | the reference time is outside a validity period |
| `Certification issuer mismatch.` | a subject DN and the next issuer DN do not match |
| `Certificate is not a CA certificate.` / `v3 certificate must have basicConstraints extension.` | an intermediate that is not one |
| `keyCertSign usage not set.` | an intermediate whose `keyUsage` forbids signing certificates |
| `Certification path length exceeded.` | the configured maximum, or a `pathLenConstraint` |
| `Name '…' is not within the permitted subtrees.` / `… is within an excluded subtree.` | name constraints |
| `No valid policies.` | the policy tree is empty and an explicit policy was required |
| `Certificate contains an unhandled critical extension: ….` | a critical extension nobody processes |
| `A name of the certification path cannot be prepared for comparison: …` | see below |

!!! note "A name that cannot be compared fails validation"

    A name comparison here is a security decision, so a string the X.520 preparation steps refuse fails
    the validation rather than being reported as "not equal" — which would let a name escape an excluded
    subtree. It is reported as a `PathValidationException` with the original as its previous, instead of
    escaping as the `StringPreparationException` raised deep inside the comparison.

## Trying several paths

When more than one path exists, a failure on one says nothing about the others:

```php
use SpomkyLabs\Pki\X509\CertificationPath\PathBuilding\CertificationPathBuilder;

$builder = CertificationPathBuilder::create($trustAnchors);

foreach ($builder->allPathsToTarget($target, $intermediates) as $candidate) {
    try {
        $result = $candidate->validate($config);
        break;
    } catch (PathValidationException) {
        continue;
    }
}
```

## Then what

A successful validation is a strong statement with sharp edges. It does not mean the certificate is
unrevoked, that it is the right certificate for the host you dialled, or that its extended key usage
allows what you are about to do.

**[What validation does not do](what-validation-does-not-do.md) is the other half of this page.**
