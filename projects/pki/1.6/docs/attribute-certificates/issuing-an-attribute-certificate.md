---
description: Building and signing an attribute certificate as an attribute authority.
---

# Issuing an attribute certificate

You are an attribute authority: a holder already has a public key certificate, and you want to say
something about them.

## The whole thing

```php
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\SHA256WithRSAEncryptionAlgorithmIdentifier;
use SpomkyLabs\Pki\X509\AttributeCertificate\AttCertIssuer;
use SpomkyLabs\Pki\X509\AttributeCertificate\AttCertValidityPeriod;
use SpomkyLabs\Pki\X509\AttributeCertificate\Attribute\RoleAttributeValue;
use SpomkyLabs\Pki\X509\AttributeCertificate\AttributeCertificateInfo;
use SpomkyLabs\Pki\X509\AttributeCertificate\Attributes;
use SpomkyLabs\Pki\X509\AttributeCertificate\Holder;
use SpomkyLabs\Pki\X509\AttributeCertificate\IssuerSerial;
use SpomkyLabs\Pki\X509\GeneralName\UniformResourceIdentifier;

$acinfo = AttributeCertificateInfo::create(
    Holder::create(IssuerSerial::fromPKC($holderCertificate)),
    AttCertIssuer::fromPKC($authorityCertificate),
    AttCertValidityPeriod::fromStrings('now', 'now + 8 hours'),
    Attributes::fromAttributeValues(
        RoleAttributeValue::create(UniformResourceIdentifier::create('urn:roles:administrator'))
    )
);

$ac = $acinfo->sign(
    SHA256WithRSAEncryptionAlgorithmIdentifier::create(),
    $authorityPrivateKeyInfo
);

file_put_contents('role.ac', $ac->toPEM()->string());
```

Four arguments to `create()`: **holder, issuer, validity, attributes**.

## The holder

`IssuerSerial::fromPKC()` is the one to use: it ties the attribute certificate to one specific public key
certificate, by its issuer and serial number.

```php
Holder::create(IssuerSerial::fromPKC($holderCertificate));
```

The alternatives exist because the ASN.1 offers them, and are looser:

```php
use SpomkyLabs\Pki\X509\GeneralName\DirectoryName;
use SpomkyLabs\Pki\X509\GeneralName\GeneralNames;

Holder::create(null, GeneralNames::create(DirectoryName::create($name)));   // by name
```

!!! warning "Naming a holder by name binds to whoever holds that name"

    A `baseCertificateID` names one certificate. An `entityName` names a subject, and any certificate
    with that subject — from any CA your relying parties trust — satisfies it. Prefer
    `IssuerSerial::fromPKC()`.

## Validity

```php
AttCertValidityPeriod::fromStrings('now', 'now + 8 hours');
AttCertValidityPeriod::create($notBefore, $notAfter);   // two DateTimeImmutable
```

Unlike a certificate's `Validity`, both fields are `GeneralizedTime`, so there is no 2050 question.

Keep it short. An attribute certificate carries authorisation, there is nothing to revoke it with, and a
validity period is the only expiry it has.

## The attributes

```php
use SpomkyLabs\Pki\X509\AttributeCertificate\Attribute\GroupAttributeValue;
use SpomkyLabs\Pki\X509\AttributeCertificate\Attribute\IetfAttrValue;

Attributes::fromAttributeValues(
    RoleAttributeValue::create(UniformResourceIdentifier::create('urn:roles:administrator')),
    GroupAttributeValue::create(IetfAttrValue::fromString('engineering'))
);
```

`RoleAttributeValue::create()` takes an optional second argument, the `GeneralNames` of the authority
that defines the role — useful when the role namespace is not yours.

## The serial number

```php
$acinfo = $acinfo->withRandomSerialNumber();      // 20 octets
$acinfo = $acinfo->withSerialNumber('12345');
```

As with certificates, `sign()` draws a 20-octet random serial number when none is set, and a size below
`MIN_RANDOM_SERIAL_SIZE` — nine octets — raises a deprecation notice. See
[Issuing a certificate](../certificates/issuing-a-certificate.md#the-serial-number).

## Narrowing what you grant

### Targets

`targetInformation` says which servers or services the attribute certificate is meant for. Validation
checks it against the targets the verifier configured, so an AC captured from one service is not usable
at another:

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\Target\TargetName;
use SpomkyLabs\Pki\X509\Certificate\Extension\Target\Targets;
use SpomkyLabs\Pki\X509\Certificate\Extension\TargetInformationExtension;
use SpomkyLabs\Pki\X509\GeneralName\DNSName;

$acinfo = $acinfo->withAdditionalExtensions(
    TargetInformationExtension::create(true, Targets::create(
        TargetName::create(DNSName::create('app.example.com'))
    ))
);
```

Mark it critical: a verifier that cannot process it must then refuse the AC rather than honour it
everywhere.

### Not revocable

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\NoRevocationAvailableExtension;

$acinfo = $acinfo->withAdditionalExtensions(NoRevocationAvailableExtension::create(false));
```

An honest statement rather than a restriction: it tells a verifier not to look for a revocation list that
does not exist.

### Extensions in general

```php
$acinfo = $acinfo->withExtensions($extensions);          // replaces the set
$acinfo = $acinfo->withAdditionalExtensions(...$exts);   // adds to it
```

!!! danger "Do not sign a critical extension a verifier cannot process"

    The validator refuses an attribute certificate carrying a critical extension it does not handle, and
    it handles exactly `targetInformation` and `noRevAvail`. A critical extension of your own makes the
    AC unusable unless every verifier declares it with
    `ACValidationConfig::withAdditionalCriticalExtensions()` **and** implements the check.

## The signing certificate

Your attribute authority certificate has to pass the issuer profile of RFC 5755 section 4.5, or no
conforming verifier will accept what you sign:

- **not** a CA — `basicConstraints` with `cA:TRUE` is refused;
- `keyUsage`, if present, permits `digitalSignature` or `nonRepudiation`.

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\BasicConstraintsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\KeyUsageExtension;

// when issuing the attribute authority's own certificate
BasicConstraintsExtension::create(true, false);
KeyUsageExtension::create(true, KeyUsageExtension::DIGITAL_SIGNATURE);
```

## Checking what you made

```php
$ac->verify($authorityPrivateKeyInfo->publicKeyInfo());   // true
$ac->isHeldBy($holderCertificate);                        // true
$ac->isIssuedBy($authorityCertificate);                   // true
```

Then validate it the way a verifier would:
[Validating an attribute certificate](validating-an-attribute-certificate.md).
