---
description: The X.509 extension classes, how to read and build each one, and what happens to one the library does not know.
---

# Extensions

An extension is an OID, a critical flag and a value. The library parses twenty-odd of them into their own
classes, and the critical flag is the first argument of every `create()`.

```php
$extensions = $certificate->tbsCertificate()->extensions();
```

## Reading

`Extensions` has a `has*()` and a getter for the extensions RFC 5280 defines:

```php
$extensions->hasBasicConstraints();
$extensions->basicConstraints();          // LogicException if absent — ask first

$extensions->hasKeyUsage();
$extensions->hasExtendedKeyUsage();
$extensions->hasSubjectAlternativeName();
$extensions->hasIssuerAlternativeName();
$extensions->hasSubjectKeyIdentifier();
$extensions->hasAuthorityKeyIdentifier();
$extensions->hasNameConstraints();
$extensions->hasCertificatePolicies();
$extensions->hasPolicyMappings();
$extensions->hasPolicyConstraints();
$extensions->hasInhibitAnyPolicy();
$extensions->hasCRLDistributionPoints();
```

By OID, for anything:

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\Extension;

$extensions->has(Extension::OID_SUBJECT_INFORMATION_ACCESS);
$extension = $extensions->get(Extension::OID_SUBJECT_INFORMATION_ACCESS);
```

Or walk them all:

```php
foreach ($extensions as $extension) {
    $extension->oid();
    $extension->isCritical();
    $extension->extensionName();   // a readable name, or the OID
}
```

`Extension::OID_*` names every extension of RFC 5280 and X.509, the obsolete ones included, prefixed
`OID_OBSOLETE_`.

## Building

```php
$tbsCertificate = $tbsCertificate->withAdditionalExtensions(
    BasicConstraintsExtension::create(true, false)
);
```

### Basic constraints

Is this a CA, and how many intermediates may follow it?

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\BasicConstraintsExtension;

BasicConstraintsExtension::create(true, false);       // critical, not a CA
BasicConstraintsExtension::create(true, true);        // a CA, no path length limit
BasicConstraintsExtension::create(true, true, 0);     // a CA that may issue only end entities

$extension->isCA();
$extension->hasPathLen();
$extension->pathLen();
```

Mark it critical. Path validation refuses a v3 intermediate without it, and refuses one whose `cA` is
false.

### Key usage

A bit field. Combine the constants with `|`:

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\KeyUsageExtension;

KeyUsageExtension::create(
    true,
    KeyUsageExtension::DIGITAL_SIGNATURE | KeyUsageExtension::KEY_ENCIPHERMENT
);

$extension->isDigitalSignature();
$extension->isNonRepudiation();
$extension->isKeyEncipherment();
$extension->isDataEncipherment();
$extension->isKeyAgreement();
$extension->isKeyCertSign();
$extension->isCRLSign();
$extension->isEncipherOnly();
$extension->isDecipherOnly();
```

`KEY_CERT_SIGN` is the one path validation looks at: an intermediate that has a `keyUsage` without it is
refused.

### Extended key usage

What the key may be used for, as OIDs:

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\ExtendedKeyUsageExtension;

ExtendedKeyUsageExtension::create(
    false,
    ExtendedKeyUsageExtension::OID_SERVER_AUTH,
    ExtendedKeyUsageExtension::OID_CLIENT_AUTH
);

$extension->has(ExtendedKeyUsageExtension::OID_SERVER_AUTH);
$extension->purposes();
count($extension);
```

The constants cover TLS server and client authentication, code signing, email protection, time stamping,
OCSP signing, the IPsec and EAP purposes, SSH client and server, and the CMC roles.

!!! note "Path validation does not check extended key usage"

    RFC 5280's algorithm says nothing about it. Checking that a certificate is allowed to be a TLS server
    is a step of your own, after validation.

### Alternative names

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\IssuerAlternativeNameExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectAlternativeNameExtension;
use SpomkyLabs\Pki\X509\GeneralName\DNSName;
use SpomkyLabs\Pki\X509\GeneralName\GeneralNames;

SubjectAlternativeNameExtension::create(false, GeneralNames::create(
    DNSName::create('example.com'),
    DNSName::create('www.example.com')
));

$extension->names();    // GeneralNames
```

See [General names](../names/general-names.md). Mark `subjectAltName` critical when the subject DN is
empty, as RFC 5280 requires — the validator handles a critical `subjectAltName` correctly either way.

### Key identifiers

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\AuthorityKeyIdentifierExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectKeyIdentifierExtension;

SubjectKeyIdentifierExtension::create(false, $publicKeyInfo->keyIdentifier());

AuthorityKeyIdentifierExtension::create(false, $caPublicKeyInfo->keyIdentifier());
AuthorityKeyIdentifierExtension::create(false, $keyId, $authorityCertIssuer, $authorityCertSerialNumber);
```

`TBSCertificate::withIssuerCertificate()` adds the authority key identifier for you, and
`fromCSR()` adds the subject key identifier. These are what
[path building](../certification-paths/building-a-path.md) follows, so a CA that omits them makes its
certificates harder to chain.

### Name constraints

What names an intermediate is allowed to vouch for. This is the extension that makes a delegated CA safe:

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\NameConstraints\GeneralSubtree;
use SpomkyLabs\Pki\X509\Certificate\Extension\NameConstraints\GeneralSubtrees;
use SpomkyLabs\Pki\X509\Certificate\Extension\NameConstraintsExtension;

NameConstraintsExtension::create(
    true,
    GeneralSubtrees::create(GeneralSubtree::create(DNSName::create('example.com'))),
    GeneralSubtrees::create(GeneralSubtree::create(DNSName::create('internal.example.com')))
);

$extension->hasPermittedSubtrees();
$extension->permittedSubtrees();
$extension->hasExcludedSubtrees();
$extension->excludedSubtrees();
```

Path validation enforces these on DNS names, email addresses, URIs, IP addresses and directory names.

### Policies

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\CertificatePoliciesExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\CertificatePolicy\PolicyInformation;
use SpomkyLabs\Pki\X509\Certificate\Extension\InhibitAnyPolicyExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\PolicyConstraintsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\PolicyMappings\PolicyMapping;
use SpomkyLabs\Pki\X509\Certificate\Extension\PolicyMappingsExtension;

CertificatePoliciesExtension::create(false, PolicyInformation::create('1.3.6.1.4.1.99999.1.1'));
PolicyConstraintsExtension::create(true, 0, 0);          // requireExplicitPolicy, inhibitPolicyMapping
PolicyMappingsExtension::create(true, PolicyMapping::create($issuerPolicy, $subjectPolicy));
InhibitAnyPolicyExtension::create(true, 0);              // skipCerts
```

`PolicyInformation::OID_ANY_POLICY` is `2.5.29.32.0`, the initial policy set of a default configuration.
A `PolicyInformation` may carry qualifiers — `CPSQualifier` for a URI, `UserNoticeQualifier` for text.
See [Configuration](../certification-paths/configuration.md#policies).

### Distribution points and access descriptions

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\AccessDescription\AuthorityAccessDescription;
use SpomkyLabs\Pki\X509\Certificate\Extension\AuthorityInformationAccessExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\CRLDistributionPointsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\DistributionPoint\DistributionPoint;
use SpomkyLabs\Pki\X509\Certificate\Extension\DistributionPoint\FullName;
use SpomkyLabs\Pki\X509\GeneralName\UniformResourceIdentifier;

CRLDistributionPointsExtension::create(false, DistributionPoint::create(
    FullName::create(GeneralNames::create(UniformResourceIdentifier::create('http://crl.example.com/a.crl')))
));

AuthorityInformationAccessExtension::create(false, AuthorityAccessDescription::create(
    AuthorityAccessDescription::OID_METHOD_OSCP,
    UniformResourceIdentifier::create('http://ocsp.example.com/')
));
```

!!! warning "The library writes these and never follows them"

    It makes no network call: a CRL distribution point is not fetched and an OCSP responder is not asked.
    Reading them to drive your own revocation checking is exactly what they are for. See
    [What validation does not do](../certification-paths/what-validation-does-not-do.md).

### The rest

| Class | What it carries |
|---|---|
| `SubjectInformationAccessExtension` | where to find information about the subject |
| `SubjectDirectoryAttributesExtension` | X.501 attributes about the subject |
| `FreshestCRLExtension` | where to find the delta CRL |
| `NoRevocationAvailableExtension` | this certificate is not revocable (attribute certificates) |
| `TargetInformationExtension` | the targets an attribute certificate is meant for |
| `AAControlsExtension` | what an attribute authority may delegate |

## An extension the library does not know

It becomes an `UnknownExtension`, which keeps the OID, the critical flag and the value as they were.
Nothing is lost and nothing throws:

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\UnknownExtension;

$extension = $extensions->get('1.3.6.1.4.1.99999.7');

if ($extension instanceof UnknownExtension) {
    $der = $extension->extensionValue();       // the encoded value, as it arrived
    $element = Element::fromDER($der);         // decode it yourself
}
```

`extensionValue()` returns the raw DER of the extension's value, so what you do with it is
[the ASN.1 layer](../asn1/README.md).

You can write one too:

```php
use SpomkyLabs\Pki\ASN1\Type\Primitive\UTF8String;

UnknownExtension::create('1.3.6.1.4.1.99999.7', false, UTF8String::create('whatever your schema says'));
```

!!! danger "A critical unknown extension makes a certificate useless"

    RFC 5280 says a validator must refuse a certificate carrying a critical extension it does not
    recognise, and this library's validator does. So:

    - **do not sign one.** `TBSCertificate::fromCSR()` never copies a critical `UnknownExtension`,
      whatever the allow list says, precisely because the result would be dead on arrival;
    - **if your application processes one by its own means**, tell the validator with
      `PathValidationConfig::withAdditionalCriticalExtensions()`. Naming it there means *you* check it —
      the validator only stops objecting.
