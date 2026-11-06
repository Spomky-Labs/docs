---
description: How PKI Framework models an X.509 certificate, and the split between the signed part and the signature.
---

# Certificates

An X.509 certificate is a statement — *this key belongs to this subject* — and a signature over it. The
library keeps the two apart, because that is what the structure does:

```
Certificate
├── TBSCertificate      the statement: version, serial, issuer, validity, subject, key, extensions
├── AlgorithmIdentifier how it was signed
└── Signature           the signature over the DER of the TBSCertificate
```

`Certificate` is immutable and read-only. Everything you build or change happens on `TBSCertificate`,
and signing it produces a `Certificate`.

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\X509\Certificate\Certificate;

$certificate = Certificate::fromPEM(PEM::fromFile('server.crt'));

$tbs = $certificate->tbsCertificate();
$tbs->subject()->toString();
$tbs->issuer()->toString();
$tbs->serialNumber();
$tbs->validity()->notAfter()->dateTime();
$tbs->subjectPublicKeyInfo();
$tbs->extensions();
```

## The three questions

They are different questions and the library answers them separately. Confusing them is the most common
way to build something that looks safe and is not.

| Question | Call |
|---|---|
| Is this certificate well-formed? | it decoded: `fromPEM()`, `fromDER()` returned |
| Was it signed by this key? | `$certificate->verify($publicKeyInfo)` |
| Does it chain to something I trust, in date, within its constraints? | [path validation](../certification-paths/validating-a-path.md) |

`verify()` takes the issuer's `PublicKeyInfo` and returns a boolean. It says nothing about trust, dates
or constraints — only path validation does.

```php
$certificate->verify($issuerCertificate->tbsCertificate()->subjectPublicKeyInfo());
$certificate->isSelfIssued();   // the subject and the issuer are the same name
```

!!! note "Self-issued is not self-signed"

    `isSelfIssued()` compares the two names. It does not check the signature. A certificate whose
    subject and issuer match is self-signed only if it also verifies against its own key:

    ```php
    $selfSigned = $certificate->isSelfIssued()
        && $certificate->verify($certificate->tbsCertificate()->subjectPublicKeyInfo());
    ```

## Comparing two of them

```php
$a->equals($b);                     // the two encodings, octet by octet
$a->hasEqualSubjectIdentity($b);    // same subject, same key, same serial number
```

`hasEqualSubjectIdentity()` is the looser question and **not an identity check**: two certificates can
agree on all three and still be issued by different issuers with different extensions.

## In and out

```php
Certificate::fromPEM($pem);
Certificate::fromDER($der);
Certificate::fromASN1($sequence);

$certificate->toPEM()->string();
$certificate->toDER();
$certificate->toASN1();
echo $certificate;              // the PEM block
```

A certificate read with `fromDER()` or `fromPEM()` keeps the `TBSCertificate` bytes exactly as they
arrived, so `verify()` checks the signature over **what the issuer signed** rather than over what the
parser produced. Re-encoding is not relied on for the one operation where a single differing octet would
change the answer.

```php
$certificate->toDER();   // the certificate as it was read
```

## What to read next

- [Reading a certificate](reading-a-certificate.md) — every field, and what each one gives you.
- [Issuing a certificate](issuing-a-certificate.md) — building a `TBSCertificate` and signing it.
- [Extensions](extensions.md) — the twenty-odd extension classes.
- [Bundles and chains](bundles-and-chains.md) — holding several certificates: a trust store, a chain.
