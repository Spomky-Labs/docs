---
description: Reading and writing PEM, the textual encoding of RFC 7468, a single block or a bundle.
---

# Textual encoding (PEM)

DER is bytes. PEM is those bytes in base64 between two labelled lines, which is how certificates and keys
travel through files, configuration and copy-paste. `SpomkyLabs\Pki\CryptoEncoding` reads and writes it,
after [RFC 7468](https://tools.ietf.org/html/rfc7468).

```
-----BEGIN CERTIFICATE-----
MIIDdzCCAl+gAwIBAgIEAgAAuTANBgkqhkiG9w0BAQUFADBaMQswCQYDVQQGEwJJ
…
-----END CERTIFICATE-----
```

## One block

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;

$pem = PEM::fromFile('/etc/ssl/certs/server.crt');
$pem = PEM::fromString($text);
$pem = PEM::create(PEM::TYPE_CERTIFICATE, $der);

$pem->type();     // "CERTIFICATE", the label between the dashes
$pem->data();     // the DER bytes
$pem->string();   // the whole block, with its dashes and line breaks
echo $pem;        // the same
```

`fromString()` reads the first block of the string and ignores what surrounds it, so a certificate
pasted into a mail body still parses.

### The labels

| Constant | Label |
|---|---|
| `TYPE_CERTIFICATE` | `CERTIFICATE` |
| `TYPE_CRL` | `X509 CRL` |
| `TYPE_CERTIFICATE_REQUEST` | `CERTIFICATE REQUEST` |
| `TYPE_ATTRIBUTE_CERTIFICATE` | `ATTRIBUTE CERTIFICATE` |
| `TYPE_PRIVATE_KEY` | `PRIVATE KEY` |
| `TYPE_ENCRYPTED_PRIVATE_KEY` | `ENCRYPTED PRIVATE KEY` |
| `TYPE_PUBLIC_KEY` | `PUBLIC KEY` |
| `TYPE_RSA_PRIVATE_KEY` | `RSA PRIVATE KEY` |
| `TYPE_RSA_PUBLIC_KEY` | `RSA PUBLIC KEY` |
| `TYPE_EC_PRIVATE_KEY` | `EC PRIVATE KEY` |
| `TYPE_PKCS7` | `PKCS7` |
| `TYPE_CMS` | `CMS` |

A label the list does not name is still read: `type()` gives it back as it was written.

The label says what the bytes are meant to be, and nothing checks that it is true. `Certificate::fromPEM()`
and the other `fromPEM()` methods assert the label they need and refuse a block that carries another
one, so a private key handed to a certificate parser fails there rather than decoding into something
unexpected.

## A bundle

A file holding several blocks — a chain, a trust store — is a `PEMBundle`:

```php
use SpomkyLabs\Pki\CryptoEncoding\PEMBundle;

$bundle = PEMBundle::fromFile('/etc/ssl/certs/ca-bundle.crt');

count($bundle);        // how many blocks
$bundle->first();      // the first PEM
$bundle->last();       // the last
$bundle->all();        // PEM[]

foreach ($bundle as $pem) {
    // in the order the file has them
}

echo $bundle->string();   // every block, back to back
```

Each block is read on its own, so a bundle may mix labels: a key and its certificate in one file comes
back as two `PEM` objects with different types.

Turning a bundle into certificates is one call:

```php
use SpomkyLabs\Pki\X509\Certificate\CertificateBundle;

$certificates = CertificateBundle::fromPEMBundle($bundle);
```

See [Bundles and chains](../certificates/bundles-and-chains.md).

## Writing

```php
file_put_contents('server.crt', $certificate->toPEM()->string());
```

`toPEM()` exists on `Certificate`, `CertificationRequest`, `AttributeCertificate`, `PublicKeyInfo`,
`OneAsymmetricKey` and the key classes, each with the right label.

## What is refused

`PEM::fromString()` and `PEMBundle::fromString()` throw `UnexpectedValueException` when there is no block
to read, or when the base64 is not valid.

RFC 7468 section 3 asks for the padded base64 alphabet of RFC 4648. PHP's `base64_decode()` is strict
about the alphabet but not about the padding, so a payload whose length is not a multiple of four — one
OpenSSL would refuse — is refused here too rather than decoded into fewer bytes than it looks like.

!!! note "Encrypted private keys are not decrypted"

    `PEM` reads a block labelled `ENCRYPTED PRIVATE KEY` and hands you its bytes, but those bytes are
    ciphertext and there is no class that models them: the library has no password-based key derivation,
    and `OneAsymmetricKey::fromPEM()` refuses that label. Decrypt it elsewhere —
    `openssl pkey -in key.pem -out plain.pem`, for one — and read the result.

A PEM bundle from a peer holds as many blocks as they chose to send. Count them before you walk them;
see [Decoding untrusted input](../asn1/untrusted-input.md#what-you-have-to-bound).
