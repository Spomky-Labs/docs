---
description: Every setting of PathValidationConfig, its default, and whether a new deployment should change it.
---

# Configuration

`PathValidationConfig` is immutable: every `with*()` returns a copy.

```php
use SpomkyLabs\Pki\X509\CertificationPath\PathValidation\PathValidationConfig;

$config = PathValidationConfig::defaultConfig();                        // now, maximum length 3
$config = PathValidationConfig::create(new DateTimeImmutable(), 5);     // reference time, maximum length
```

## What a hardened configuration looks like

```php
$config = PathValidationConfig::defaultConfig()
    ->withAllowedSignatureAlgorithms(...PathValidationConfig::HARDENED_ALLOWED_SIGNATURE_ALGORITHMS)
    ->withMinimumRSAKeySize(PathValidationConfig::HARDENED_MINIMUM_RSA_KEY_SIZE)
    ->withTrustAnchor($root);
```

Two settings, and they are the two whose defaults are looser than a new deployment would choose.

## The trust anchor

```php
$config = $config->withTrustAnchor($root);

$config->hasTrustAnchor();
$config->trustAnchor();
```

The single most important setting. See
[Validating a path](validating-a-path.md#the-trust-anchor-is-an-input).

## Allowed signature algorithms

```php
$config = $config->withAllowedSignatureAlgorithms(...$oids);
$config->allowedSignatureAlgorithms();
```

Replaces the set entirely — it is not additive.

| Constant | Contains |
|---|---|
| `DEFAULT_ALLOWED_SIGNATURE_ALGORITHMS` | SHA-1 through SHA-512 with RSA, ECDSA with the same hashes, Ed25519, Ed448 |
| `HARDENED_ALLOWED_SIGNATURE_ALGORITHMS` | the same **without SHA-1** |

MD2, MD4 and MD5 are in neither: chosen-prefix collisions against MD5 have been practical since 2009,
which is enough to forge a certificate that verifies, and no authority in service still signs with them.
Refusing them costs nothing, and an opt-in would protect only those who already knew to ask.

**SHA-1 is in the default**, despite chosen-prefix collisions against it being practical since 2020.
Legacy enterprise and device PKIs continue to rely on it, and cutting them off silently in a patch
release is not this library's call. If yours is not one of them, harden it. `HARDENED_…` is the set the
default will narrow to in a future major release.

RSASSA-PSS is in neither, because it is not implemented: a PSS-signed certificate is refused when it is
parsed, so allowing the OID would advertise a capability that does not exist.

An algorithm not in the set is refused **before the signature is checked** — a signature is only as good
as its digest, and without the check the validator would accept MD5 with no way for the application to
say no.

!!! note "Ed25519 and Ed448 are allowed by default but may not be checkable"

    Whether they can be verified depends on the runtime. Probe with
    `OpenSSLCrypto::supportsSignatureAlgorithm()` and narrow the set rather than letting a chain fail
    closed; see [The crypto engine](../keys/the-crypto-engine.md).

## The RSA floor

```php
$config = $config->withMinimumRSAKeySize(2048);
$config->minimumRSAKeySize();
```

| Constant | Bits |
|---|---|
| `DEFAULT_MINIMUM_RSA_KEY_SIZE` | 1024 |
| `HARDENED_MINIMUM_RSA_KEY_SIZE` | 2048 |

RSA-512 has been factorable for decades and RSA-768 was factored in 2009, so a signature made with such a
key proves nothing and the default refuses them. It stops at 1024 rather than at the 2048 bits the
CA/Browser Forum has required since 2014, for the same reason SHA-1 stays in the default set.

Zero disables the check; a negative value raises `InvalidArgumentException`.

Only RSA is covered: an EC key's strength is fixed by its named curve, and the curves this library knows
are all above the line.

## Reference time

```php
$config = $config->withDateTime(new DateTimeImmutable('2026-01-01'));
$config->dateTime();
```

Every validity period in the path is checked against this one instant. Setting it to the past is how you
validate a signature that was made when the certificate was still valid; setting it from a request
parameter is how you let a peer validate an expired chain.

## Maximum path length

```php
$config = $config->withMaxLength(5);
$config->maxLength();
```

The default is 3. It bounds the path independently of any `pathLenConstraint`, and the lower of the two
wins.

## Policies

```php
$config = $config->withPolicySet('1.3.6.1.4.1.99999.1.1', '1.3.6.1.4.1.99999.1.2');
$config = $config->withExplicitPolicy(true);
$config = $config->withPolicyMappingInhibit(true);
$config = $config->withAnyPolicyInhibit(true);

$config->policySet();
$config->explicitPolicy();
$config->policyMappingInhibit();
$config->anyPolicyInhibit();
```

| Setting | Default | Means |
|---|---|---|
| `withPolicySet()` | `[PolicyInformation::OID_ANY_POLICY]` | the initial policy set: which policies you accept |
| `withExplicitPolicy()` | `false` | the path must be valid for at least one policy of that set |
| `withPolicyMappingInhibit()` | `false` | refuse policy mapping along the path |
| `withAnyPolicyInhibit()` | `false` | refuse `anyPolicy` |

Most deployments leave all four alone: policy processing matters inside a PKI that defines policies and
cross-certifies, and a web PKI client has no use for it. If you set `withPolicySet()` to a specific OID,
set `withExplicitPolicy(true)` as well — otherwise a path valid for no policy at all still passes.

A failure here reads `No valid policies.`

## Critical extensions you handle yourself

```php
$config = $config->withAdditionalCriticalExtensions('1.3.6.1.4.1.99999.7');
$config->additionalCriticalExtensions();
```

Validation refuses any certificate carrying a critical extension it cannot process. Declaring an OID here
stops that rejection.

!!! warning "Naming an extension here means you check it"

    The validator stops objecting; it does not start handling. An OID listed here with no code behind it
    is a critical extension nobody enforces, which is exactly what the critical flag exists to prevent.

## Version 1 and version 2 intermediates

```php
$config = $config->withLegacyV1IntermediatesTrusted(true);
$config->legacyV1IntermediatesTrusted();
```

Default `false`, and leave it there.

!!! danger "What this flag actually allows"

    A v1 or v2 certificate carries no extensions, hence neither `basicConstraints` nor `keyUsage`, so
    nothing in it states that it may sign certificates. RFC 5280 section 6.1.4 (k) requires the
    application to confirm that out of band or reject it.

    Turning this on means **any end-entity certificate a trusted CA ever issued in version 1 becomes
    usable as an intermediate CA for any identity**. Set it only for certificates vouched for by other
    means, never to make a chain you do not understand go through.

## Everything at a glance

| Setting | Default | Change it? |
|---|---|---|
| `withTrustAnchor()` | none | **yes**, unless the path came from `toTarget()` |
| `withAllowedSignatureAlgorithms()` | includes SHA-1 | **yes**, if you can refuse SHA-1 |
| `withMinimumRSAKeySize()` | 1024 | **yes**, if you can require 2048 |
| `withDateTime()` | now | only to validate at another instant |
| `withMaxLength()` | 3 | if your PKI is deeper |
| `withPolicySet()` and the policy flags | `anyPolicy`, all off | only in a PKI that defines policies |
| `withAdditionalCriticalExtensions()` | empty | only for extensions you really process |
| `withLegacyV1IntermediatesTrusted()` | `false` | almost never |
