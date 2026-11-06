---
description: The AlgorithmIdentifier classes, the OIDs they carry, and adding one of your own.
---

# Algorithm identifiers

An `AlgorithmIdentifier` is an OID and, sometimes, parameters. It appears everywhere: beside a key to say
what kind of key it is, beside a signature to say how it was made, inside an extension to name a digest.

Every one is its own class, so a signature algorithm is a type rather than a string you have to
recognise.

```php
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\SHA256WithRSAEncryptionAlgorithmIdentifier;

$algorithm = SHA256WithRSAEncryptionAlgorithmIdentifier::create();

$algorithm->oid();    // "1.2.840.113549.1.1.11"
$algorithm->name();   // a human-readable name, for an error message
```

## The families

The interfaces under `AlgorithmIdentifier\Feature` are what a signature takes when any member of a
family will do.

| Interface | Means |
|---|---|
| `SignatureAlgorithmIdentifier` | may sign a certificate, a request or an attribute certificate |
| `HashAlgorithmIdentifier` | a digest |
| `CipherAlgorithmIdentifier` | a symmetric cipher |
| `BlockCipherAlgorithmIdentifier` | a block cipher, with a block size and an IV |
| `AsymmetricCryptoAlgorithmIdentifier` | names a key type |
| `PRFAlgorithmIdentifier` | a pseudo-random function |
| `EncryptionAlgorithmIdentifier` | encrypts |

`TBSCertificate::sign()` takes a `SignatureAlgorithmIdentifier`, so passing a hash is a type error rather
than a runtime surprise.

## Signature algorithms

| Class, under `AlgorithmIdentifier\Signature` | Accepted by default in path validation |
|---|---|
| `SHA1WithRSAEncryptionAlgorithmIdentifier` | yes |
| `SHA224WithRSAEncryptionAlgorithmIdentifier` | yes |
| `SHA256WithRSAEncryptionAlgorithmIdentifier` | yes |
| `SHA384WithRSAEncryptionAlgorithmIdentifier` | yes |
| `SHA512WithRSAEncryptionAlgorithmIdentifier` | yes |
| `ECDSAWithSHA1AlgorithmIdentifier` | yes |
| `ECDSAWithSHA224AlgorithmIdentifier` | yes |
| `ECDSAWithSHA256AlgorithmIdentifier` | yes |
| `ECDSAWithSHA384AlgorithmIdentifier` | yes |
| `ECDSAWithSHA512AlgorithmIdentifier` | yes |
| `MD2WithRSAEncryptionAlgorithmIdentifier` | **no** |
| `MD4WithRSAEncryptionAlgorithmIdentifier` | **no** |
| `MD5WithRSAEncryptionAlgorithmIdentifier` | **no** |

Ed25519 and Ed448 sign too, through `Asymmetric\Ed25519AlgorithmIdentifier` and
`Asymmetric\Ed448AlgorithmIdentifier`: in RFC 8410 the key type and the signature algorithm are the same
OID. Both are accepted by default, subject to [what the runtime can do](the-crypto-engine.md).

The MD2, MD4 and MD5 classes exist so that a certificate signed with one can be parsed and reported.
They are left out of the default accepted set: chosen-prefix collisions against MD5 have been practical
since 2009, which is enough to forge a certificate that verifies, and no authority in service still signs
with them.

**RSASSA-PSS is not implemented.** `Asymmetric\RSAPSSSSAEncryptionAlgorithmIdentifier` models the
identifier, and a PSS-signed certificate is refused when it is parsed. The OID is deliberately absent
from the default accepted set: allowing it would advertise a capability that does not exist. Implementing
it will mean binding the parameters as well as the OID, since `Certificate::fromASN1()` compares only the
OIDs of the outer and signed algorithm identifiers, which would otherwise leave a hash, MGF and salt
length downgrade open.

## Key algorithms

| Class, under `AlgorithmIdentifier\Asymmetric` | Key type |
|---|---|
| `RSAEncryptionAlgorithmIdentifier` | RSA |
| `RSAPSSSSAEncryptionAlgorithmIdentifier` | RSASSA-PSS |
| `ECPublicKeyAlgorithmIdentifier` | elliptic curve; carries the named curve |
| `Ed25519AlgorithmIdentifier`, `Ed448AlgorithmIdentifier` | EdDSA signing keys |
| `X25519AlgorithmIdentifier`, `X448AlgorithmIdentifier` | key agreement keys |

`ECPublicKeyAlgorithmIdentifier` is the one that carries a parameter — the curve — as an OID:

```php
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Asymmetric\ECPublicKeyAlgorithmIdentifier;

$algorithm = ECPublicKeyAlgorithmIdentifier::create(ECPublicKeyAlgorithmIdentifier::CURVE_PRIME256V1);
$algorithm->namedCurve();
```

The `CURVE_*` constants cover the prime curves of X9.62 and the SEC 2 curves, `CURVE_PRIME256V1`
(P-256), `CURVE_SECP384R1` (P-384) and `CURVE_SECP521R1` (P-521) among them.

## Hashes and ciphers

Under `AlgorithmIdentifier\Hash`: `MD5`, `SHA1`, `SHA224`, `SHA256`, `SHA384`, `SHA512`, and the
RFC 4231 HMAC identifiers `HMACWithSHA1` through `HMACWithSHA512`.

Under `AlgorithmIdentifier\Cipher`: `DESCBC`, `DESEDE3CBC`, `RC2CBC`, `AES128CBC`, `AES192CBC`,
`AES256CBC`. A block cipher identifier carries its initialisation vector, which is why
`Crypto::encrypt()` takes no separate IV.

## Reading one you were handed

`AlgorithmIdentifier::fromASN1()` dispatches on the OID and returns the right class:

```php
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\AlgorithmIdentifier;

$algorithm = AlgorithmIdentifier::fromASN1($sequence);
```

An OID the library does not know comes back as a `GenericAlgorithmIdentifier`, which keeps the OID and
the parameters as they were. Nothing is lost and nothing throws: you can inspect and re-encode an
identifier the library has no class for.

## Adding your own

Implement `AlgorithmIdentifierProvider` — `supportsOID(string $oid): bool` and
`getClassByOID(string $oid): string` — and hand it to the factory:

```php
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\AlgorithmIdentifierFactory;

$factory = AlgorithmIdentifierFactory::create($myProvider);

$factory->getClass('1.3.6.1.4.1.99999.1');   // your class name, or null
$algorithm = $factory->parse($sequence);     // your class, or one of the library's
```

Your class extends `SpecificAlgorithmIdentifier` and implements the `Feature` interface of its family —
`SignatureAlgorithmIdentifier` for a signature algorithm, which is what makes it acceptable to `sign()`.

!!! note "A provider adds, it does not override"

    The built-in map is consulted first, so a provider cannot replace an identifier the library already
    ships. `AlgorithmIdentifier::fromASN1()` uses a factory with no providers at all, so an OID only your
    provider knows comes back from it as a `GenericAlgorithmIdentifier`. Call your own factory's
    `parse()` where you want your classes.

Signing with it is a separate matter: the [crypto engine](the-crypto-engine.md) has to know how, and the
one shipped speaks the algorithms OpenSSL does.
