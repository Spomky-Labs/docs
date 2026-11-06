---
description: 'CBOR Object Signing and Encryption for PHP: signing, MAC, encryption and key management, with the header rules and the structures of RFC 9052 applied for you.'
---

# COSE

COSE produces and checks COSE messages: signatures, message authentication codes, content encryption and
key management, over the CBOR message types of
[spomky-labs/cbor-php](https://github.com/Spomky-Labs/cbor-php), with the cryptographic structures and the
header rules of [RFC 9052](https://datatracker.ietf.org/doc/html/rfc9052) applied for you. It is used by
WebAuthn and FIDO2 relying parties, by verifiers of the EU Digital COVID Certificate, and wherever a CBOR
Web Token or a COSE message has to be produced or read.

```bash
composer require web-auth/cose-lib spomky-labs/cbor-php
```

```php
use CBOR\ByteStringObject;
use CBOR\ListObject;
use CBOR\MapItem;
use CBOR\MapObject;
use CBOR\NegativeIntegerObject;
use CBOR\Tag\CoseSign1Tag;
use CBOR\UnsignedIntegerObject;
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Key\Ec2Key;
use Cose\Signature\Signature1;
use Cose\Structure\HeaderMapHelper;

$algorithm = ES256::create();
$key = Ec2Key::create($yourPrivateCoseKey);

// Encode the protected bucket once, so the bytes that are signed are the bytes the message carries.
$protectedHeader = HeaderMapHelper::encodeProtected(MapObject::create([
    MapItem::create(
        UnsignedIntegerObject::create(1),                   // alg
        NegativeIntegerObject::create(ES256::identifier())  // ES256 (-7)
    ),
]));
$payload = ByteStringObject::create('Message to sign');

// The signature covers the Sig_structure, never the payload on its own.
$toBeSigned = Signature1::create($protectedHeader, $payload);
$signature = ByteStringObject::create($algorithm->sign((string) $toBeSigned, $key));

$coseSign1 = CoseSign1Tag::create(ListObject::create([
    $protectedHeader,
    MapObject::create(),
    $payload,
    $signature,
]));

$encoded = (string) $coseSign1;
```

## What it covers

| Chapter | What it covers |
|---|---|
| [Messages, structures and headers](messages/README.md) | The six COSE tags, the `Sig_structure` / `MAC_structure` / `Enc_structure` classes, reading headers the RFC 9052 way, detached content, `external_aad` |
| [Signing and verifying](signing/README.md) | `COSE_Sign1` and `COSE_Sign`, what the application must check, the verification contract, verifying with a certificate, countersignatures |
| [Message authentication codes](mac/README.md) | `COSE_Mac0` and `COSE_Mac`, and why the tag covers the `MAC_structure` |
| [Encryption](encryption/README.md) | `COSE_Encrypt0` and `COSE_Encrypt`, `encryptFor()`, the nonce |
| [Key management](key-management/README.md) | `direct`, HKDF, AES Key Wrap and ECDH recipients, and the KDF context |
| [Keys](keys/README.md) | Key types and curves, parameter forms, AKP keys, `alg` / `key_ops` restrictions, validation, thumbprints |
| [Algorithms](algorithms/README.md) | Every identifier the library ships, with its RFC reference, ML-DSA included |
| [Header parameters and profiles](header-parameters/cwt.md) | CBOR Web Tokens, the X.509 parameters, the hash envelope, receipts and timestamp tokens |

## Where to start

- **Signing or verifying a message** — [COSE_Sign1](signing/cose-sign1.md), then
  [What the application must check](signing/what-the-application-must-check.md) before you rely on a
  verification that returned `true`.
- **Reading a message someone handed you** — [Reading headers](messages/reading-headers.md).
- **Encrypting for several recipients** — [COSE_Encrypt](encryption/cose-encrypt.md) and
  [Key management](key-management/README.md).
- **Verifying a CBOR Web Token** — [CBOR Web Tokens](header-parameters/cwt.md).
- **Choosing an identifier** — [Algorithms](algorithms/README.md).

## Two things to know before you build on it

**A verification tells you the signature is good, not that the message was allowed to say what it says.**
`alg` and `crit` are checks [RFC 9052 §3.1](https://datatracker.ietf.org/doc/html/rfc9052#section-3.1)
requires of the caller, and a verifier that skips them accepts a message announcing an algorithm it never
agreed to. See [What the application must check](signing/what-the-application-must-check.md).

**A signature or a MAC never covers the payload alone.** It covers a structure that binds the protected
header and the message type, so a tag cannot be lifted from one message type into another. Handing a bare
payload to `hash()` or `sign()` produces something no other implementation accepts. See
[Cryptographic structures](messages/cryptographic-structures.md).

[Security recommendations](introduction/security-recommendations.md) collects every such decision in one
place.

## The message classes come from cbor-php

The six COSE message types are `CBOR\Tag\CoseSign1Tag` and its siblings, shipped by
[spomky-labs/cbor-php](https://github.com/Spomky-Labs/cbor-php) 3.4.0 or later; this library owns what
RFC 9052 reads into them. The `Cose\...Tag` classes it used to ship are deprecated, see
[Upgrading](migration/upgrading.md).
