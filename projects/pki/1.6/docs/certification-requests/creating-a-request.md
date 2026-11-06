---
description: Building and signing a PKCS #10 certification request, with the extensions you would like the issuer to honour.
---

# Creating a request

This is the subject's side: you hold a key, you want a certificate for it.

## The whole thing

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\SHA256WithRSAEncryptionAlgorithmIdentifier;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;
use SpomkyLabs\Pki\X501\ASN1\Name;
use SpomkyLabs\Pki\X509\CertificationRequest\CertificationRequestInfo;

$privateKeyInfo = PrivateKeyInfo::fromPEM(PEM::fromFile('key.pem'));

$cri = CertificationRequestInfo::create(
    Name::fromString('cn=example.com, o=ACME Ltd, c=FR'),
    $privateKeyInfo->publicKeyInfo()
);

$csr = $cri->sign(SHA256WithRSAEncryptionAlgorithmIdentifier::create(), $privateKeyInfo);

file_put_contents('request.csr', $csr->toPEM()->string());
```

The key you sign with must be the one whose public half you put in: that is the proof of possession the
request exists to carry. The algorithm has to match the key —
`ECDSAWithSHA256AlgorithmIdentifier` for an EC key, `Ed25519AlgorithmIdentifier` for an Ed25519 key — and
a mismatch raises `UnexpectedValueException`.

`sign()` takes a [crypto engine](../keys/the-crypto-engine.md) as an optional third argument.

## Requesting extensions

What you want in the certificate goes in the extension request attribute:

```php
use SpomkyLabs\Pki\X509\Certificate\Extensions;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectAlternativeNameExtension;
use SpomkyLabs\Pki\X509\GeneralName\DNSName;
use SpomkyLabs\Pki\X509\GeneralName\GeneralNames;

$cri = $cri->withExtensionRequest(Extensions::create(
    SubjectAlternativeNameExtension::create(false, GeneralNames::create(
        DNSName::create('example.com'),
        DNSName::create('www.example.com')
    ))
));

$csr = $cri->sign(SHA256WithRSAEncryptionAlgorithmIdentifier::create(), $privateKeyInfo);
```

`withExtensionRequest()` creates the attribute set if there is none and replaces any extension request
already there, so calling it twice does not leave two.

!!! note "Requesting is asking, not getting"

    A conforming issuer decides what to honour. This library's `fromCSR()` copies only the extensions the
    issuer names, and never the ones that decide what a certificate may do — `basicConstraints`,
    `keyUsage`, `extKeyUsage`, `nameConstraints` and the policy extensions among them. Asking for
    `cA:TRUE` gets you nothing. See [Issuing from a request](issuing-from-a-request.md).

    Do not mark a requested extension critical unless you know the issuer parses it: an issuer that
    copies a critical extension it does not recognise produces a certificate no validator will accept, so
    a careful one drops it instead.

## Other attributes

For an attribute that is not an extension request:

```php
use SpomkyLabs\Pki\X501\ASN1\Attribute;
use SpomkyLabs\Pki\X509\CertificationRequest\Attributes;

$cri = $cri->withAttributes(Attributes::create(
    Attribute::fromAttributeValues($myValue)
));
```

`withAttributes()` replaces the whole set, extension request included, so set the attributes first and
call `withExtensionRequest()` after — not the other way round.

## Changing the subject

```php
$cri = $cri->withSubject(Name::fromString('cn=other.example.com'));
```

Immutable, like the rest: `with*()` returns a copy. Change it before you sign; a signed request is
closed.

## Checking what you made

```php
$csr->verify();                                             // true
$csr->certificationRequestInfo()->subject()->toString();
echo $csr->toPEM()->string();
```

And against OpenSSL, worth doing once:

```bash
openssl req -in request.csr -noout -text -verify
```

## Generating the key first

The library does not generate keys. For a request you will need one:

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out key.pem
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out key.pem
openssl genpkey -algorithm ED25519 -out key.pem
```

All three write a `PRIVATE KEY` block, which `PrivateKeyInfo::fromPEM()` reads directly. See
[Private keys](../keys/private-keys.md).
