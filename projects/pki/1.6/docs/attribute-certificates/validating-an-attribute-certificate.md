---
description: Validating an attribute certificate, the two certification paths it needs, and the check you must configure yourself.
---

# Validating an attribute certificate

Validating an attribute certificate means validating **two** certification paths — the holder's and the
issuer's — and then six more checks on top.

## The call

```php
use SpomkyLabs\Pki\X509\AttributeCertificate\Validation\ACValidationConfig;
use SpomkyLabs\Pki\X509\AttributeCertificate\Validation\ACValidator;
use SpomkyLabs\Pki\X509\AttributeCertificate\Validation\Exception\ACValidationException;
use SpomkyLabs\Pki\X509\CertificationPath\CertificationPath;

$holderPath = CertificationPath::toTarget($holderCertificate, $trustAnchors, $intermediates);
$issuerPath = CertificationPath::toTarget($authorityCertificate, $trustAnchors, $intermediates);

$config = ACValidationConfig::create($holderPath, $issuerPath)
    ->withTrustedAttributeAuthorities($authorityCertificate)   // see below — do not skip this
    ->withTargets(TargetName::create(DNSName::create('app.example.com')));

try {
    $validated = ACValidator::create($ac, $config)->validate();
} catch (ACValidationException $e) {
    // not authorised
}
```

`validate()` returns the attribute certificate, or throws. Pass a
[crypto engine](../keys/the-crypto-engine.md) as the third argument of `create()` to use your own.

## The check you have to configure

!!! danger "Without `withTrustedAttributeAuthorities()`, any end-entity certificate will do"

    RFC 5755 section 5 check 4 says the attribute certificate's issuer must be **directly trusted** as an
    attribute authority. The validator cannot know who you trust, so without this call it skips the
    check — and then accepts whatever end-entity certificate the issuer path happens to end in.

    Any certificate from any CA in your trust store would then be able to grant any role.

    ```php
    $config = $config->withTrustedAttributeAuthorities($authorityA, $authorityB);
    $config->trustedAttributeAuthorities();   // a CertificateBundle, or null
    ```

    The check is `CertificateBundle::contains()`, so it is an exact match on the encoding.

## What the validator checks

In order:

1. **The holder's certification path** validates, and `$ac->isHeldBy()` that path's end-entity
   certificate. A path failure is wrapped: `Failed to validate holder PKC's certification path.`
2. **The issuer's certification path** validates, and `$ac->isIssuedBy()` its end-entity certificate.
3. **The issuer profile**, RFC 5755 section 4.5: the issuer certificate is **not** a CA, and its
   `keyUsage`, if present, permits `digitalSignature` or `nonRepudiation`.
4. **The attribute authority is trusted**, if you configured the bundle.
5. **The AC's own signature**, under the same policy as the paths — see below.
6. **The validity period** contains the evaluation time.
7. **The targets** match, if the AC carries a `targetInformation` extension.
8. **Every critical extension** is one the validator processes, or one you declared.

!!! note "The AC's own signature is held to the path policy"

    The attribute authority's key is never a *working key* of either path, so its size would never have
    been measured, and the crypto engine would happily verify an MD5 signature. The signature that
    carries the authorisation is checked against the same `allowedSignatureAlgorithms()` and
    `minimumRSAKeySize()` as the paths — which is a reason to hand the config a hardened
    `PathValidationConfig`.

## Configuration

```php
$config = ACValidationConfig::create($holderPath, $issuerPath);

$config = $config->withPathValidationConfig($pathConfig);
$config = $config->withEvaluationTime(new DateTimeImmutable('2026-06-01'));
$config = $config->withTrustedAttributeAuthorities(...$certificates);
$config = $config->withTargets(...$targets);
$config = $config->withAdditionalCriticalExtensions('1.3.6.1.4.1.99999.7');

$config->holderPath();
$config->issuerPath();
$config->hasPathValidationConfig();
$config->pathValidationConfig();
$config->evaluationTime();
$config->targets();
$config->additionalCriticalExtensions();
```

### The path validation configuration

Pass a hardened one, since it governs the AC's own signature as well as the two paths:

```php
use SpomkyLabs\Pki\X509\CertificationPath\PathValidation\PathValidationConfig;

$pathConfig = PathValidationConfig::defaultConfig()
    ->withAllowedSignatureAlgorithms(...PathValidationConfig::HARDENED_ALLOWED_SIGNATURE_ALGORITHMS)
    ->withMinimumRSAKeySize(PathValidationConfig::HARDENED_MINIMUM_RSA_KEY_SIZE);

$config = $config->withPathValidationConfig($pathConfig);
```

The evaluation time is applied to the path configuration for you, so both paths and the AC are judged at
the same instant.

!!! note "The maximum path length is derived only when you supply no configuration"

    With no `withPathValidationConfig()`, the maximum length is taken from each path's own length. Once
    you supply a configuration, your `withMaxLength()` is respected — overriding it unconditionally made
    `maxLength()` a no-op for both paths.

### Targets

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\Target\TargetGroup;
use SpomkyLabs\Pki\X509\Certificate\Extension\Target\TargetName;
use SpomkyLabs\Pki\X509\GeneralName\DNSName;

$config = $config->withTargets(
    TargetName::create(DNSName::create('app.example.com')),
    TargetGroup::create(DNSName::create('example.com'))
);
```

An AC with a `targetInformation` extension is refused unless one of its targets is among these. An AC
without the extension is not targeted at all and passes whatever you configure — targeting constrains
only the ACs that opt into it.

### Critical extensions

The validator processes `targetInformation` and `noRevAvail`. Anything else marked critical makes
validation fail, which is RFC 5755 section 5 check 7: an attribute certificate carries authorisation, a
critical extension is how its issuer narrows that authorisation, and honouring one you cannot process
would grant the attributes unconditionally.

`withAdditionalCriticalExtensions()` stops the objection. It does not implement the check — that is
yours.

## What the exception tells you

| Message | Means |
|---|---|
| `Failed to validate holder PKC's certification path.` | the holder's path failed; `$e->getPrevious()` is the `PathValidationException` |
| `Name mismatch of AC's holder PKC.` | the path validated, but the AC is not held by that certificate |
| `Failed to validate issuer PKC's certification path.` | the issuer's path failed |
| `Name mismatch of AC's issuer PKC.` | the AC was not issued by that certificate |
| `Issuer PKC must not be a CA.` | the attribute authority's certificate asserts `cA:TRUE` |
| `Issuer PKC's Key Usage extension doesn't permit verification of digital signatures.` | neither `digitalSignature` nor `nonRepudiation` |
| `Issuer PKC is not a trusted attribute authority.` | not in the bundle you configured |
| `Signature algorithm … is not allowed.` / `RSA key size … is below the minimum …` | the AC's own signature, under the path policy |
| `Failed to verify signature.` | the AC's signature does not match |
| `Validity period has not started.` / `Attribute certificate has expired.` | the evaluation time |
| `Attribute certificate doesn't have a matching target.` | `targetInformation` does not include your targets |
| `Attribute certificate contains an unhandled critical extension: ….` | see above |

## Using the result

```php
$validated = ACValidator::create($ac, $config)->validate();

$attributes = $validated->acinfo()->attributes();

if ($attributes->hasRole()) {
    $role = $attributes->role()->roleName()->string();
}
```

The attributes are authorisation statements. **Mapping them to permissions in your application is your
decision**, as is what to do when the same holder presents two attribute certificates that disagree.

And remember what the two paths do not tell you:
[revocation is not checked](../certification-paths/what-validation-does-not-do.md), for the holder's
certificate, the issuer's, or — there being nothing to check it with — the attribute certificate itself.
