---
description: The Signature classes, the encoding each algorithm family uses, and where a signature comes from.
---

# Signatures

A signature is not just bytes: ECDSA writes a `SEQUENCE` of two integers, RSA writes an octet string, and
EdDSA writes a fixed-length string. `Signature` is the type that keeps the difference straight.

## The classes

| Class, under `CryptoTypes\Signature` | Encoding |
|---|---|
| `RSASignature` | the signature value as it is |
| `ECSignature` | a `SEQUENCE` of `r` and `s` |
| `Ed25519Signature` | 64 bytes |
| `Ed448Signature` | 114 bytes |
| `GenericSignature` | a bit string and the algorithm that made it |

## Where one comes from

Reading a structure:

```php
$signature = $certificate->signatureValue();
$signature = $csr->signature();
$signature = $attributeCertificate->signatureValue();
```

Signing:

```php
use SpomkyLabs\Pki\CryptoBridge\Crypto;

$signature = Crypto::getDefault()->sign($data, $privateKeyInfo, $algorithm);
```

You rarely call that directly — `TBSCertificate::sign()` and its siblings do it for you and hand back the
signed structure. See [Issuing a certificate](../certificates/issuing-a-certificate.md).

From raw bytes, when the algorithm says how to read them:

```php
use SpomkyLabs\Pki\CryptoTypes\Signature\Signature;

$signature = Signature::fromSignatureData($bytes, $algorithm);
```

That is the factory the engine uses: it dispatches on the algorithm and builds the right class, so an
ECDSA signature is parsed into `r` and `s` rather than kept as an opaque blob.

## Reading one

```php
$signature->bitString()->string();   // the bytes, whatever the class
```

`ECSignature` exposes the two halves, which is what you need when bridging to a library that wants them
separately:

```php
use SpomkyLabs\Pki\CryptoTypes\Signature\ECSignature;

/** @var ECSignature $signature */
$signature->r();         // decimal string
$signature->s();
$signature->toDER();     // the SEQUENCE
```

`ECSignature::create($r, $s)` builds one from the two integers, and `fromDER()` reads the `SEQUENCE`
back.

!!! note "`r` and `s` are decimal strings, not integers"

    They are coordinates on a curve: on P-521 they do not fit in a PHP integer. Pass them to
    [brick/math](https://github.com/brick/math) if you need arithmetic, and to
    `EC\ECConversion::numberToOctets()` if you need the fixed-length octet form that JWS and COSE use.

## Verifying

Verification takes the data, the signature, the public key and the algorithm:

```php
use SpomkyLabs\Pki\CryptoBridge\Crypto;

$valid = Crypto::getDefault()->verify($data, $signature, $publicKeyInfo, $algorithm);
```

Again, the structures do it for you:

```php
$certificate->verify($issuerPublicKeyInfo);
$csr->verify();                                  // self-signed by definition
$attributeCertificate->verify($issuerPublicKeyInfo);
```

Each one re-encodes the signed part, hands it to the engine with the algorithm the structure names, and
returns a boolean.

!!! warning "A true from `verify()` is one fact, not trust"

    It says the signature was made by the key you passed. It does not say the key belongs to anyone, that
    the certificate is in date, or that its issuer was allowed to sign it. Those are
    [path validation](../certification-paths/validating-a-path.md).

## Mismatched algorithm and key

The engine checks that the signature algorithm and the key agree before it does anything: an ECDSA
algorithm with an RSA key raises `UnexpectedValueException` rather than failing somewhere inside OpenSSL.

An algorithm the runtime cannot handle fails the same way, with the algorithm named in the message. See
[The crypto engine](the-crypto-engine.md).
