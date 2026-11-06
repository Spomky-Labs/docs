---
description: Every field of an X.509 certificate and what the library gives you for it.
---

# Reading a certificate

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\X509\Certificate\Certificate;

$certificate = Certificate::fromPEM(PEM::fromFile('server.crt'));
$tbs = $certificate->tbsCertificate();
```

Everything below is on `$tbs`, except the three fields of the outer structure.

## The outer structure

```php
$certificate->signatureAlgorithm();   // a SignatureAlgorithmIdentifier
$certificate->signatureValue();       // a Signature
$certificate->tbsCertificate();       // the signed part
```

The signature algorithm appears twice in a certificate — once outside, once inside the signed part — and
they have to agree. `fromASN1()` checks that the OIDs match and refuses the certificate otherwise, which
closes the oldest trick in the format.

!!! note "Only the OIDs are compared"

    For RSASSA-PSS the parameters matter as much as the OID — a hash, MGF and salt length downgrade would
    slip through an OID-only comparison — which is one reason PSS is not implemented and a PSS-signed
    certificate is refused outright.

## Version, serial number

```php
$tbs->version();          // 0, 1 or 2 for v1, v2, v3
$tbs->hasVersion();
$tbs->serialNumber();     // a decimal string
$tbs->hasSerialNumber();
```

The constants are `TBSCertificate::VERSION_1`, `VERSION_2` and `VERSION_3`, whose values are 0, 1 and 2:
the field is zero-based, as the ASN.1 says. Almost everything you will meet is a v3 certificate.

The serial number is a **decimal string**, not an integer. A 20-octet serial number does not fit in a PHP
integer, and comparing serial numbers as integers is how revocation lookups break.

## Names

```php
$tbs->subject();   // a Name
$tbs->issuer();    // a Name

$tbs->subject()->toString();
$tbs->subject()->firstValueOf('cn')->stringValue();
```

See [Distinguished names](../names/distinguished-names.md). For a TLS certificate the hostname is in
[`subjectAltName`](../names/general-names.md), not in the common name.

## Validity

```php
$validity = $tbs->validity();

$notBefore = $validity->notBefore()->dateTime();   // DateTimeImmutable
$notAfter = $validity->notAfter()->dateTime();

$now = new DateTimeImmutable();
$inDate = $now >= $notBefore && $now <= $notAfter;
```

`Time` wraps a `DateTimeImmutable` and remembers which ASN.1 type it was read from — `UTCTime` before
2050, `GeneralizedTime` after — so a round trip gives back the same bytes.

!!! warning "Checking the dates yourself is not validation"

    A certificate in date may still be revoked, outside its constraints, or signed by a key you have no
    reason to trust. Path validation checks the dates of every certificate in the path against one
    reference time; see [Validating a path](../certification-paths/validating-a-path.md).

## The public key

```php
$publicKeyInfo = $tbs->subjectPublicKeyInfo();

$publicKeyInfo->algorithmIdentifier()->name();
$publicKeyInfo->keyIdentifier();        // 20 bytes, RFC 5280 method 1
$publicKeyInfo->publicKey();            // RSAPublicKey, ECPublicKey, …
```

See [Public keys](../keys/public-keys.md).

## Extensions

```php
$extensions = $tbs->extensions();

$extensions->hasBasicConstraints();
$extensions->basicConstraints()->isCA();

$extensions->hasSubjectAlternativeName();
$extensions->subjectAlternativeName()->names()->firstDNS();

count($extensions);

foreach ($extensions as $extension) {
    $extension->oid();
    $extension->isCritical();
    $extension->extensionName();
}
```

Every extension in the certificate is there, known or not. See [Extensions](extensions.md).

## Unique identifiers

Two fields from version 2, which you will almost certainly never meet:

```php
$tbs->hasIssuerUniqueID();
$tbs->issuerUniqueID()->string();
$tbs->hasSubjectUniqueID();
$tbs->subjectUniqueID()->string();
```

They exist to disambiguate a reused name. RFC 5280 says not to issue new certificates with them.

## Printing one

There is no formatter in the library — no `openssl x509 -text` equivalent — so a dump is a few lines of
your own:

```php
$tbs = $certificate->tbsCertificate();

printf(
    "subject:  %s\nissuer:   %s\nserial:   %s\nvalid:    %s → %s\nkey:      %s\nalgorithm: %s\n",
    $tbs->subject()->toString(),
    $tbs->issuer()->toString(),
    $tbs->serialNumber(),
    $tbs->validity()->notBefore()->dateTime()->format('c'),
    $tbs->validity()->notAfter()->dateTime()->format('c'),
    $tbs->subjectPublicKeyInfo()->algorithmIdentifier()->name(),
    $certificate->signatureAlgorithm()->name()
);

foreach ($tbs->extensions() as $extension) {
    printf("  %-28s %s%s\n", $extension->extensionName(), $extension->oid(), $extension->isCritical() ? ' (critical)' : '');
}
```

## What can go wrong

| Thrown | When |
|---|---|
| `UnexpectedValueException` | the PEM label is not `CERTIFICATE` |
| `DecodeException` | the DER is malformed, nested too deep, or carries a repeated optional field |
| `UnexpectedValueException` | the outer and inner signature algorithms disagree, or the signature algorithm is one the library refuses |
| `LogicException` | you asked for a field the certificate does not have — call the matching `has*()` first |

Material from a peer deserves the limits in
[Decoding untrusted input](../asn1/untrusted-input.md).
