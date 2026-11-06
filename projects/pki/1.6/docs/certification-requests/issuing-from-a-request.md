---
description: 'Turning a certification request into a certificate safely: verify it yourself, and name the extensions you will honour.'
---

# Issuing from a request

This is the issuer's side, and the page with the most ways to get it wrong. **Everything a certification
request contains was chosen by whoever submitted it.**

## The whole thing, done right

```php
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\SHA256WithRSAEncryptionAlgorithmIdentifier;
use SpomkyLabs\Pki\X509\Certificate\Extension\Extension;
use SpomkyLabs\Pki\X509\Certificate\Extension\ExtendedKeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\BasicConstraintsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\KeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\TBSCertificate;
use SpomkyLabs\Pki\X509\Certificate\Validity;

// 1. The signature is yours to check. fromCSR() does not.
if (! $csr->verify()) {
    throw new RuntimeException('The request is not signed by the key it carries.');
}

// 2. Decide whether this subject may have this name. Nothing in the library can do that for you.
$subject = $myPolicy->nameFor($csr);

// 3. Copy only the extensions you are willing to honour, by OID.
$tbsCertificate = TBSCertificate::fromCSR($csr, [Extension::OID_SUBJECT_ALT_NAME]);

// 4. The issuer sets everything that decides what the certificate may do.
$tbsCertificate = $tbsCertificate
    ->withSubject($subject)
    ->withIssuerCertificate($caCertificate)
    ->withValidity(Validity::fromStrings('now', 'now + 90 days'))
    ->withRandomSerialNumber()
    ->withAdditionalExtensions(
        BasicConstraintsExtension::create(true, false),
        KeyUsageExtension::create(true, KeyUsageExtension::DIGITAL_SIGNATURE | KeyUsageExtension::KEY_ENCIPHERMENT),
        ExtendedKeyUsageExtension::create(false, ExtendedKeyUsageExtension::OID_SERVER_AUTH)
    );

// 5. Sign with the CA's key.
$certificate = $tbsCertificate->sign(
    SHA256WithRSAEncryptionAlgorithmIdentifier::create(),
    $caPrivateKeyInfo
);
```

Each numbered step is a decision the library deliberately does not make for you.

## `fromCSR()` does not verify the signature

```php
$tbsCertificate = TBSCertificate::fromCSR($csr);   // the signature was not checked
```

Call `CertificationRequest::verify()` yourself, before anything else. A request whose signature does not
verify is a request whose submitter may not hold the key at all.

## What `fromCSR()` takes, and what it refuses

It takes the **subject DN** and the **public key** from the request, sets an empty issuer and an empty
validity for you to fill, and adds a `subjectKeyIdentifier` computed from the key.

Extensions are the interesting part.

### Never copied, whatever you ask

These decide what a certificate is allowed to do, so they belong to the issuer. They are in
`TBSCertificate::FORBIDDEN_CSR_EXTENSIONS` and naming one in the allow list raises
`InvalidArgumentException`:

| Extension | Why |
|---|---|
| `basicConstraints` | `cA:TRUE` is asking to become a certificate authority |
| `keyUsage` | `keyCertSign` is the same request by another route |
| `extKeyUsage` | what the key may be used for |
| `nameConstraints` | what an intermediate may vouch for |
| `policyConstraints`, `policyMappings`, `inhibitAnyPolicy`, `certificatePolicies` | the policy processing of every validator downstream |
| `authorityKeyIdentifier` | names the issuer's key; the issuer sets it |

### Never copied if critical and unknown

An extension this library cannot parse, signed as critical, produces a certificate that is dead on
arrival: no conforming validator accepts it, this library's own included. Such an extension is dropped
even when the allow list names its OID.

### Copied only if you name it

```php
$tbsCertificate = TBSCertificate::fromCSR($csr, [Extension::OID_SUBJECT_ALT_NAME]);
$tbsCertificate = TBSCertificate::fromCSR($csr, []);   // nothing from the request
```

An allow list, by OID. Anything not named is dropped.

### Leaving the argument out is deprecated

```php
$tbsCertificate = TBSCertificate::fromCSR($csr);   // raises a deprecation notice
```

It copies every requested extension that is not forbidden and raises `E_USER_DEPRECATED` naming what it
took.

!!! danger "That default is a deny list, and it will become an empty allow list"

    The set of extensions that matter grows over time, and a deny list copies every future one by
    default. Today a request can already carry:

    - a `subjectAltName` naming an identity the subject DN says nothing about — a hostname, an email
      address, a URI your relying parties will trust;
    - an `authorityInformationAccess` choosing the OCSP responder a relying party will ask.

    In the next major release the default becomes the empty allow list. Pass `null` explicitly if you
    really want the current behaviour, which silences the notice and keeps the deny list:

    ```php
    $tbsCertificate = TBSCertificate::fromCSR($csr, null);
    ```

    Use the deprecation notice to find your call sites before the default changes.

## The subject name

`fromCSR()` copies the subject DN from the request, because that is what the structure says. **It is
still a name the requester chose.** Whether this requester may have this name is your policy, and the
library has no opinion:

```php
$tbsCertificate = $tbsCertificate->withSubject($nameYourPolicyDecided);
```

For a public CA this is domain validation. For an internal CA it is whatever ties a request to an
identity you already authenticated. Either way it happens outside this library.

## Do not forget the validity

`fromCSR()` leaves it empty, and `sign()` will not fill it in. Set it:

```php
$tbsCertificate = $tbsCertificate->withValidity(Validity::fromStrings('now', 'now + 90 days'));
```

## The serial number

`sign()` draws a 20-octet random one when you set none, so the safe thing is the default. See
[Issuing a certificate](../certificates/issuing-a-certificate.md#the-serial-number).

## A checklist

Before an issuance path goes anywhere near production:

- [ ] `$csr->verify()` is called, and its `false` is handled.
- [ ] `fromCSR()` is given an explicit allow list — `[]` if you copy nothing.
- [ ] The subject DN is the one your policy decided, not the one the request asked for.
- [ ] `withValidity()` is set.
- [ ] `basicConstraints` and `keyUsage` are set by you, critical.
- [ ] The serial number is random — the default, or at least nine octets.
- [ ] The signing key is the CA's, and the algorithm matches it.
- [ ] You have read what a request bounded by nothing can cost you:
      [Decoding untrusted input](../asn1/untrusted-input.md).
