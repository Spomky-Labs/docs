---
description: PKCS #10 certification requests: what they are, what they prove, and what they do not.
---

# Certification requests

A certification request — a CSR, after [RFC 2986](https://tools.ietf.org/html/rfc2986) — is a subject
saying *here is my public key, here is the name I would like, please issue me a certificate*, signed with
the matching private key.

```
CertificationRequest
├── CertificationRequestInfo    version, subject, public key, attributes
├── AlgorithmIdentifier         how it was signed
└── Signature                   over the DER of the CertificationRequestInfo
```

Same split as a certificate: `CertificationRequestInfo` is the builder, `CertificationRequest` is the
signed result.

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\X509\CertificationRequest\CertificationRequest;

$csr = CertificationRequest::fromPEM(PEM::fromFile('request.csr'));

$cri = $csr->certificationRequestInfo();
$cri->subject()->toString();
$cri->subjectPKInfo();
$csr->signatureAlgorithm()->name();
```

## What a request proves, and what it does not

A valid signature on a CSR proves **one** thing: whoever produced it holds the private key matching the
public key inside. That is a proof of possession, and it is useful.

It does not prove that the subject is entitled to the name it asked for, that the extensions it requested
are ones it should get, or that anyone should issue it anything. Every field of a request was chosen by
whoever submitted it.

!!! danger "Read this before you wire a request to an issuance path"

    [Issuing from a request](issuing-from-a-request.md) is where that matters. `TBSCertificate::fromCSR()`
    does **not** verify the signature, and the extensions a certificate may do things with are never
    copied from a request.

## Verifying a request

```php
if (! $csr->verify()) {
    throw new RuntimeException('The request is not signed by the key it carries.');
}
```

`verify()` takes no key: a request is self-signed by definition, so the key it checks against is the one
inside it. Pass a [crypto engine](../keys/the-crypto-engine.md) as the only argument to use your own.

It returns `false` rather than throwing for anything that means *the signature was not verified*: an
algorithm the runtime cannot check, a key the algorithm does not match, an engine failure. The algorithm
is named by the request, so an attacker picks it, and `if (! $csr->verify())` in your code must not become
an unhandled fatal.

!!! note "A request read from bytes is verified over those bytes"

    `fromDER()` and `fromPEM()` keep the `CertificationRequestInfo` exactly as it arrived, so the
    signature is checked over what the subject signed. A request you built in memory was never received
    as bytes, and re-encoding it is then the only option — and the correct one.

## In and out

```php
CertificationRequest::fromPEM($pem);      // label: CERTIFICATE REQUEST
CertificationRequest::fromDER($der);
CertificationRequest::fromASN1($sequence);

$csr->toPEM()->string();
$csr->toDER();
$csr->toASN1();
echo $csr;
```

## Attributes

A request carries attributes, and the one that matters is the extension request:

```php
$cri = $csr->certificationRequestInfo();

if ($cri->hasAttributes() && $cri->attributes()->hasExtensionRequest()) {
    $requested = $cri->attributes()->extensionRequest()->extensions();

    foreach ($requested as $extension) {
        $extension->oid();
        $extension->isCritical();
    }
}
```

`attributes()` throws `LogicException` when there are none, so ask `hasAttributes()` first. The
collection is a `SetOfAttributes`; see [Attributes](../names/attributes.md).

These are **requests**, not facts. Reading them tells you what the subject asked for. Deciding what to
honour is the issuer's job.

## What to read next

- [Creating a request](creating-a-request.md) — building and signing one, as the subject.
- [Issuing from a request](issuing-from-a-request.md) — turning one into a certificate, as the issuer.
