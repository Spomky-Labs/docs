---
description: Building a TBSCertificate, setting the extensions an issuer owns, and signing it.
---

# Issuing a certificate

`TBSCertificate` is the mutable-by-copy builder, `sign()` turns it into a `Certificate`.

## The shortest complete example

A self-signed certificate, which is a certificate whose issuer is its own subject:

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\SHA256WithRSAEncryptionAlgorithmIdentifier;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;
use SpomkyLabs\Pki\X501\ASN1\Name;
use SpomkyLabs\Pki\X509\Certificate\TBSCertificate;
use SpomkyLabs\Pki\X509\Certificate\Validity;

$privateKeyInfo = PrivateKeyInfo::fromPEM(PEM::fromFile('key.pem'));
$name = Name::fromString('cn=example.com, o=ACME Ltd, c=FR');

$tbsCertificate = TBSCertificate::create(
    $name,                              // subject
    $privateKeyInfo->publicKeyInfo(),   // the subject's public key
    $name,                              // issuer
    Validity::fromStrings('now', 'now + 1 year')
);

$certificate = $tbsCertificate->sign(
    SHA256WithRSAEncryptionAlgorithmIdentifier::create(),
    $privateKeyInfo
);

file_put_contents('cert.pem', $certificate->toPEM()->string());
```

Note the argument order of `create()`: **subject, key, issuer, validity**. The subject comes first.

## Validity

```php
use SpomkyLabs\Pki\X509\Certificate\Time;
use SpomkyLabs\Pki\X509\Certificate\Validity;

Validity::fromStrings('now', 'now + 90 days');
Validity::fromStrings('2026-01-01 00:00:00', '2027-01-01 00:00:00', 'UTC');

Validity::create(
    Time::create(new DateTimeImmutable('2026-01-01', new DateTimeZone('UTC'))),
    Time::create(new DateTimeImmutable('2027-01-01', new DateTimeZone('UTC')))
);
```

The strings go through `DateTimeImmutable`, so anything it understands works. `Time` picks `UTCTime`
before 2050 and `GeneralizedTime` after, as RFC 5280 asks.

## The serial number

```php
$tbsCertificate = $tbsCertificate->withRandomSerialNumber();      // 20 octets
$tbsCertificate = $tbsCertificate->withRandomSerialNumber(16);
$tbsCertificate = $tbsCertificate->withSerialNumber('12345');     // if you keep a register
```

**Leaving it unset is safe**: `sign()` draws a 20-octet random serial number — `DEFAULT_RANDOM_SERIAL_SIZE`,
the RFC 5280 maximum — rather than writing a zero.

!!! warning "A constant serial number breaks two things at once"

    It removes the unpredictability that protects issuance against collision attacks, and it breaks CRL
    revocation, which identifies a certificate by the (issuer, serial number) pair. If you draw your own,
    use at least `TBSCertificate::MIN_RANDOM_SERIAL_SIZE` — nine octets. That is the 64 bits of CSPRNG
    output the CA/Browser Forum Baseline Requirements ask for, plus the octet the sign bit costs. A
    smaller size still works and raises a deprecation notice saying how many bits it actually carries.

## The version

You do not set it. `sign()` works out the minimum the structure needs: version 3 when there are
extensions, version 2 when there is a unique identifier, version 1 otherwise. `withVersion()` exists if
you need to force one.

## Signing as a CA

`withIssuerCertificate()` fills in what the issuer's certificate implies — the issuer DN from the CA's
subject, and an `authorityKeyIdentifier` pointing at the CA's key:

```php
$tbsCertificate = TBSCertificate::create(
    $subjectName,
    $subjectPublicKeyInfo,
    Name::create(),                       // replaced below
    Validity::fromStrings('now', 'now + 90 days')
);

$tbsCertificate = $tbsCertificate
    ->withIssuerCertificate($caCertificate)
    ->withRandomSerialNumber();

$certificate = $tbsCertificate->sign(
    SHA256WithRSAEncryptionAlgorithmIdentifier::create(),
    $caPrivateKeyInfo                     // the CA's key, not the subject's
);
```

## Extensions

Two methods, and the difference matters:

```php
$tbsCertificate = $tbsCertificate->withExtensions($extensions);          // replaces the whole set
$tbsCertificate = $tbsCertificate->withAdditionalExtensions(...$exts);   // adds to it
```

`withExtensions()` after `withIssuerCertificate()` throws away the `authorityKeyIdentifier` that call
added. Use `withAdditionalExtensions()`, or set the extensions first.

A typical TLS server certificate:

```php
use SpomkyLabs\Pki\X509\Certificate\Extension\BasicConstraintsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\ExtendedKeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\KeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectAlternativeNameExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectKeyIdentifierExtension;
use SpomkyLabs\Pki\X509\GeneralName\DNSName;
use SpomkyLabs\Pki\X509\GeneralName\GeneralNames;

$tbsCertificate = $tbsCertificate->withAdditionalExtensions(
    BasicConstraintsExtension::create(true, false),
    KeyUsageExtension::create(true, KeyUsageExtension::DIGITAL_SIGNATURE | KeyUsageExtension::KEY_ENCIPHERMENT),
    ExtendedKeyUsageExtension::create(false, ExtendedKeyUsageExtension::OID_SERVER_AUTH),
    SubjectAlternativeNameExtension::create(false, GeneralNames::create(
        DNSName::create('example.com'),
        DNSName::create('www.example.com')
    )),
    SubjectKeyIdentifierExtension::create(false, $subjectPublicKeyInfo->keyIdentifier())
);
```

A CA certificate instead:

```php
$tbsCertificate = $tbsCertificate->withAdditionalExtensions(
    BasicConstraintsExtension::create(true, true, 0),   // critical, cA, pathLenConstraint
    KeyUsageExtension::create(true, KeyUsageExtension::KEY_CERT_SIGN | KeyUsageExtension::CRL_SIGN)
);
```

The first argument of every extension is `$critical`. See [Extensions](extensions.md) for the whole set.

!!! warning "A CA certificate without `basicConstraints` is not a CA"

    Path validation refuses an intermediate that does not assert `cA:TRUE`, and refuses one whose
    `keyUsage` omits `keyCertSign` when it has a `keyUsage` at all. Setting both is not a formality.

## Signing

```php
$certificate = $tbsCertificate->sign($algorithm, $privateKeyInfo);
$certificate = $tbsCertificate->sign($algorithm, $privateKeyInfo, $crypto);
```

The algorithm has to match the key: `SHA256WithRSAEncryptionAlgorithmIdentifier` for an RSA key,
`ECDSAWithSHA256AlgorithmIdentifier` for an EC key, `Ed25519AlgorithmIdentifier` for an Ed25519 key.
A mismatch raises `UnexpectedValueException` naming both.

Signing sets the `signature` field inside the signed part and repeats the algorithm outside, so the two
agree — which is what `Certificate::fromASN1()` checks when the certificate is read back.

`sign()` returns a new `Certificate` and leaves the `TBSCertificate` untouched; nothing in the library
mutates.

## Checking what you made

```php
$certificate->verify($privateKeyInfo->publicKeyInfo());       // the signature is good
$certificate->tbsCertificate()->version();                    // 2, i.e. v3
echo $certificate->toPEM()->string();
```

And against OpenSSL, which is worth doing once for any new issuance path:

```bash
openssl x509 -in cert.pem -noout -text
```

## From a certification request

When the subject sent a CSR, start from it — but treat it as untrusted input. See
[Issuing from a request](../certification-requests/issuing-from-a-request.md), which is the page to read
before you wire an issuance endpoint to anything.
