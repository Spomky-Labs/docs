---
description: How PKI Framework models keys, the algorithms that name them, and the signatures they produce.
---

# Keys, algorithms and signatures

`SpomkyLabs\Pki\CryptoTypes` holds three things that travel together: a key, an algorithm identifier that
says what kind of key it is and what may be done with it, and a signature.

The library does not generate keys. Generate them with `ext-openssl`, `ext-sodium` or a command line, and
read the result in.

## Two levels of key

**The container.** `PrivateKeyInfo` (a PKCS #8 `OneAsymmetricKey`) and `PublicKeyInfo` (a
`SubjectPublicKeyInfo`) are the wrappers that carry an algorithm identifier beside the key material.
This is what the rest of the library takes and returns: a certificate holds a `PublicKeyInfo`, and
`sign()` takes a `PrivateKeyInfo`.

**The key itself.** `RSAPrivateKey`, `ECPublicKey`, `Ed25519PrivateKey` and their siblings are the
algorithm-specific structures inside. Go down to them when you need a modulus, a curve name or the raw
point.

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;

$privateKeyInfo = PrivateKeyInfo::fromPEM(PEM::fromFile('key.pem'));

$publicKeyInfo = $privateKeyInfo->publicKeyInfo();   // derived, or read from the container
$rsa = $privateKeyInfo->privateKey();                // RSAPrivateKey, ECPrivateKey, Ed25519PrivateKey, …
```

Going up is as short:

```php
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PublicKeyInfo;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\RSA\RSAPublicKey;

$publicKeyInfo = PublicKeyInfo::fromPublicKey(RSAPublicKey::fromPEM($pem));
```

## What is supported

| Algorithm | Private key class | Public key class |
|---|---|---|
| RSA | `RSA\RSAPrivateKey` | `RSA\RSAPublicKey` |
| RSASSA-PSS | `RSA\RSASSAPSSPrivateKey` | — |
| Elliptic curve | `EC\ECPrivateKey` | `EC\ECPublicKey` |
| Ed25519 | `RFC8410\Curve25519\Ed25519PrivateKey` | `RFC8410\Curve25519\Ed25519PublicKey` |
| Ed448 | `RFC8410\Curve448\Ed448PrivateKey` | `RFC8410\Curve448\Ed448PublicKey` |
| X25519 | `RFC8410\Curve25519\X25519PrivateKey` | `RFC8410\Curve25519\X25519PublicKey` |
| X448 | `RFC8410\Curve448\X448PrivateKey` | `RFC8410\Curve448\X448PublicKey` |

X25519 and X448 are key agreement keys, not signing keys: the library reads and writes them, and nothing
signs with them.

RSASSA-PSS keys are read, but **PSS signatures are not implemented**. A PSS-signed certificate is refused
when it is parsed, and the OID is deliberately absent from the default set of allowed signature
algorithms.

## Key identifiers

RFC 5280 gives two ways to name a key, and `PublicKeyInfo` implements both:

```php
$publicKeyInfo->keyIdentifier();     // method 1: the SHA-1 of the public key bit string, 20 bytes
$publicKeyInfo->keyIdentifier64();   // method 2: 8 bytes, the type-and-value form
```

Method 1 is what goes into a `subjectKeyIdentifier` extension and what an
`authorityKeyIdentifier` points at. `TBSCertificate::withIssuerCertificate()` and `fromCSR()` set them
for you.

## What to read next

- [Private keys](private-keys.md) — reading them, the formats, what each one gives you.
- [Public keys](public-keys.md) — the same from the other side, and getting one out of a certificate.
- [Algorithm identifiers](algorithm-identifiers.md) — the OIDs, the classes, and the factory.
- [Signatures](signatures.md) — the `Signature` types and their encodings.
- [The crypto engine](the-crypto-engine.md) — who actually signs and verifies, and what the runtime can
  do.
