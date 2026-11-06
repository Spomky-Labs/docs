---
description: Who actually signs and verifies in PKI Framework, what the runtime limits, and how to replace the engine.
---

# The crypto engine

Every structure in the library is data. The arithmetic — signing, verifying, encrypting — happens in a
`Crypto` engine, and the one shipped wraps `ext-openssl`.

```php
use SpomkyLabs\Pki\CryptoBridge\Crypto;

$crypto = Crypto::getDefault();
```

`getDefault()` returns an `OpenSSLCrypto` when `OPENSSL_VERSION_NUMBER` is defined, and throws
`RuntimeException` otherwise. Nothing is cached: it is a new instance each call, and the engine holds no
state worth keeping.

Every method that needs an engine takes one as an optional last argument and falls back to the default:

```php
$certificate = $tbsCertificate->sign($algorithm, $privateKeyInfo);           // the default engine
$certificate = $tbsCertificate->sign($algorithm, $privateKeyInfo, $crypto);  // yours

$path->validate($config);           // the default engine
$path->validate($config, $crypto);  // yours
```

## What it does

```php
$signature = $crypto->sign($data, $privateKeyInfo, $signatureAlgorithm);
$valid = $crypto->verify($data, $signature, $publicKeyInfo, $signatureAlgorithm);

$ciphertext = $crypto->encrypt($plaintext, $key, $cipherAlgorithm);
$plaintext = $crypto->decrypt($ciphertext, $key, $cipherAlgorithm);
```

`encrypt()` and `decrypt()` are there for the PKCS structures that need a block cipher. **Padding is
yours**: the engine encrypts with zero padding and raw data, and the initialisation vector comes from the
algorithm identifier, which is why there is no separate IV argument. They are not a general-purpose
encryption API — reach for `sodium` for that.

## The algorithm and the key must agree

Before anything else, `sign()` and `verify()` check that the signature algorithm accepts the key type. An
ECDSA algorithm with an RSA key raises `UnexpectedValueException` naming both, rather than failing
somewhere inside OpenSSL with a message about a PEM header.

A cipher whose key is the wrong length is refused the same way, with the expected size in the message.

## What this runtime can do

RSA and ECDSA with SHA-1 through SHA-512 work wherever `ext-openssl` does. **EdDSA is the one that
depends on the runtime.**

- PHP 8.5 verifies Ed25519 and Ed448 through `openssl_verify()`.
- Older runtimes have no EdDSA in the OpenSSL extension at all. Ed25519 then goes through `ext-sodium`,
  bundled since PHP 7.2. **There is no equivalent for Ed448.**
- Signing needs OpenSSL either way: `ext-sodium` could sign Ed25519, but it cannot produce an Ed448
  signature, and the engine does not grow a second signing path for the half case. Signing with an EdDSA
  algorithm the OpenSSL extension does not support raises `UnexpectedValueException`.

The engine works out what OpenSSL can do by verifying RFC 8032's known-good test vector for each curve,
once per process and once per curve — an extension without EdDSA reports the vector as invalid rather
than raising, which is exactly the failure this guards against. Ask before you configure:

```php
use SpomkyLabs\Pki\CryptoBridge\Crypto\OpenSSLCrypto;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Asymmetric\Ed25519AlgorithmIdentifier;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Asymmetric\Ed448AlgorithmIdentifier;

$crypto = new OpenSSLCrypto();

$crypto->supportsSignatureAlgorithm(Ed25519AlgorithmIdentifier::create());   // OpenSSL or sodium
$crypto->supportsSignatureAlgorithm(Ed448AlgorithmIdentifier::create());     // OpenSSL only
```

!!! warning "Verification fails closed, which looks like a bad chain"

    Ed25519 and Ed448 are in the default set of allowed signature algorithms, so a chain signed with one
    reaches the engine and is then refused on a runtime that cannot check it. From the outside that is
    indistinguishable from an invalid signature. If your deployment may meet EdDSA, probe for it at boot
    and either narrow the
    [allowed set](../certification-paths/configuration.md#allowed-signature-algorithms) or say plainly
    that the runtime is missing an extension.

## Errors

| Thrown | When |
|---|---|
| `RuntimeException` | no OpenSSL at all (`getDefault()`), or an OpenSSL call failed; the message carries OpenSSL's own |
| `UnexpectedValueException` | the algorithm and the key disagree, the cipher key is the wrong length, or the runtime cannot do EdDSA |

`verify()` returns `false` for a signature that simply does not match. It throws only when the question
could not be asked.

## Replacing it

`Crypto` is an abstract class with four methods. Extend it to put signing behind a hardware module, a
remote service or a key management system:

```php
use SpomkyLabs\Pki\CryptoBridge\Crypto;

final class HsmCrypto extends Crypto
{
    public function sign(string $data, PrivateKeyInfo $privkey_info, SignatureAlgorithmIdentifier $algo): Signature
    {
        // ask the module, then:
        return Signature::fromSignatureData($bytes, $algo);
    }

    // verify(), encrypt(), decrypt()
}
```

Pass it as the last argument everywhere, or make it the one your application resolves — the library never
reads a global, so there is nothing to register.

!!! note "`sign()` receives the private key as a value"

    The signature of `Crypto::sign()` takes a `PrivateKeyInfo`, so an engine that never sees key material
    needs a `PrivateKeyInfo` that stands for a key it holds elsewhere — a handle rather than a secret.
    `OpenSSLCrypto` writes it out as PEM and hands it to `openssl_sign()`; yours is free to read only the
    algorithm identifier and the key identifier, and look the real key up.
