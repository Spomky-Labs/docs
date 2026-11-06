---
description: Finding a path from a trust anchor to a target, how an issuer is matched, and the bounds on the search.
---

# Building a path

Path building answers: *given this certificate, and these certificates I trust, is there a chain between
them?*

## The usual call

```php
use SpomkyLabs\Pki\X509\Certificate\CertificateBundle;
use SpomkyLabs\Pki\X509\CertificationPath\CertificationPath;

$path = CertificationPath::toTarget($target, $trustAnchors, $intermediates);
```

- `$trustAnchors` is a bundle **you** assembled. The path will be headed by one of its certificates.
- `$intermediates` is the pool to bridge the gap, typically what the peer sent. It is untrusted: a
  certificate from it can appear in the middle of a path, never at its head.

## The builder directly

`toTarget()` is a shortcut for the shortest path. When more than one path exists, you may want them all:

```php
use SpomkyLabs\Pki\X509\CertificationPath\PathBuilding\CertificationPathBuilder;

$builder = CertificationPathBuilder::create($trustAnchors);

$paths = $builder->allPathsToTarget($target, $intermediates);   // CertificationPath[]
$path = $builder->shortestPathToTarget($target, $intermediates);
```

!!! note "The shortest path is not necessarily the valid one"

    A short path may fail validation — an expired intermediate, a name constraint, a policy — where a
    longer one would succeed. `shortestPathToTarget()` commits to one. When more than one path is
    possible, take `allPathsToTarget()` and validate them in turn:

    ```php
    foreach ($builder->allPathsToTarget($target, $intermediates) as $path) {
        try {
            return $path->validate($config);
        } catch (PathValidationException) {
            continue;
        }
    }
    throw new RuntimeException('No path validates.');
    ```

Among paths of equal length the order is deterministic, so `shortestPathToTarget()` returns the same path
for the same input.

## How an issuer is found

For each certificate, the builder looks for candidates that could have issued it:

1. **By authority key identifier.** If the certificate has an `authorityKeyIdentifier` with a key
   identifier, candidates come from `allBySubjectKeyIdentifier()` on the bundle. That lookup puts the
   certificates whose identifier is *computed from their key* ahead of those that merely *declare* the
   value in an extension — a declared identifier is arbitrary data that nothing checks against the key.
2. **By name, as a fallback.** When that yields nothing, every certificate in the bundle is a candidate.
   RFC 5280 requires the authority key identifier on a CA-issued certificate, but plenty of real
   certificates omit it, and the issuer name identifies the issuer on its own. RFC 4158 section 3.5.12
   expects a builder to match on the name. Without this fallback such a certificate could never be
   chained, which would push integrators towards the unsafe constructor.
3. **Then by name, always.** Every candidate must have a subject DN equal to the target's issuer DN, with
   [the X.501 comparison rules](../names/comparing-names.md) — not a string comparison.

Building matches names and follows identifiers. **It does not verify signatures**: that is validation's
job, and a built path is a hypothesis until you validate it.

## The bounds on the search

The search runs over certificates a peer chose, so it is bounded three ways:

| Bound | Value | Why |
|---|---|---|
| Path length while resolving | 10 certificates | bounds the depth, on top of loop detection |
| Paths produced in one step | 100 | a bundle of mutually compatible certificates yields an exponential number of paths even with no loop |
| Certificates examined | 1000 | work has to be counted where it is done: a subtree that returns no path has still explored itself, and a bundle chaining to no anchor is exactly that shape |

Exceeding one raises `PathBuildingException`. A self-issued certificate is not followed as an
intermediate, and a certificate already on the path being resolved is not revisited.

These bounds are not configurable. They are a cap on attacker-controlled work, not a tuning parameter.

## When nothing is found

```php
use SpomkyLabs\Pki\X509\CertificationPath\Exception\PathBuildingException;

try {
    $path = CertificationPath::toTarget($target, $trustAnchors, $intermediates);
} catch (PathBuildingException $e) {
    // no path, or the search hit a bound
}
```

`PathBuildingException` also wraps a name that cannot be prepared for comparison: matching an issuer name
is a name comparison, and a string the X.520 preparation steps refuse stops the resolution rather than
being reported as "not equal". It is reported as a building failure like any other, with the original as
its previous.

Common causes of no path at all:

- the peer sent a leaf without its intermediates, and your pool has none;
- your trust store does not hold the root the chain leads to;
- an intermediate's subject DN does not match what the leaf names as its issuer.

## Holding a path you already have

When you already know the sequence — from a configuration file, from a chain a peer sent — you do not
need the builder:

```php
use SpomkyLabs\Pki\X509\CertificationPath\CertificationPath;

$path = CertificationPath::create($root, $intermediate, $leaf);       // anchor first
$path = CertificationPath::fromCertificateChain($chainFromPeer);      // reverses it for you
```

!!! danger "Both of these need an explicit trust anchor to validate"

    Neither knows where its first certificate came from. `fromCertificateChain()` **throws** without
    `withTrustAnchor()`, because a peer decided what its first certificate is. `create()` raises a
    deprecation notice and falls back to its first certificate, and that fallback will be removed. See
    [Validating a path](validating-a-path.md#the-trust-anchor-is-an-input).
