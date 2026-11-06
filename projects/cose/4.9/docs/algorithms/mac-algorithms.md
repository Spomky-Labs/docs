---
description: 'HMAC and AES-CBC-MAC, and the key length each one requires.'
---

# MAC algorithms

**HMAC** (`Cose\Algorithm\Mac`)

| Algorithm | Identifier | Description | Reference |
|-----------|------------|-------------|-----------|
| HS256 | 5 | HMAC with SHA-256 (IANA name `HMAC 256/256`) | [RFC 9053 §3.1](https://www.rfc-editor.org/rfc/rfc9053#section-3.1) |
| HS384 | 6 | HMAC with SHA-384 (`HMAC 384/384`) | [RFC 9053 §3.1](https://www.rfc-editor.org/rfc/rfc9053#section-3.1) |
| HS512 | 7 | HMAC with SHA-512 (`HMAC 512/512`) | [RFC 9053 §3.1](https://www.rfc-editor.org/rfc/rfc9053#section-3.1) |
| HS256/64 | 4 | HMAC with SHA-256 truncated to 64 bits (`HMAC 256/64`), class `HS256Truncated64` | [RFC 9053 §3.1](https://www.rfc-editor.org/rfc/rfc9053#section-3.1) |

**AES-CBC-MAC** (`Cose\Algorithm\Mac\AESMAC128_64` and siblings)

| Algorithm | Identifier | Description | Reference |
|-----------|------------|-------------|-----------|
| AES-MAC 128/64 | 14 | AES-128 in CBC mode, 64-bit tag; class `AESMAC128_64` | [RFC 9053 §3.2](https://www.rfc-editor.org/rfc/rfc9053#section-3.2) |
| AES-MAC 256/64 | 15 | AES-256 in CBC mode, 64-bit tag; class `AESMAC256_64` | [RFC 9053 §3.2](https://www.rfc-editor.org/rfc/rfc9053#section-3.2) |
| AES-MAC 128/128 | 25 | AES-128 in CBC mode, 128-bit tag; class `AESMAC128_128` | [RFC 9053 §3.2](https://www.rfc-editor.org/rfc/rfc9053#section-3.2) |
| AES-MAC 256/128 | 26 | AES-256 in CBC mode, 128-bit tag; class `AESMAC256_128` | [RFC 9053 §3.2](https://www.rfc-editor.org/rfc/rfc9053#section-3.2) |

Every MAC algorithm implements `Cose\Algorithm\Mac\Mac`: `hash()` computes the tag, `verify()` compares it with
`hash_equals()`, and both take a symmetric `Key`, whose type, presence and length are checked; see
[Validating symmetric keys](../keys/validating-symmetric-keys.md). The tag is computed over the `MAC_structure`, see
[Message authentication codes](../mac/README.md).

```php
use Cose\Algorithm\Mac\AESMAC128_64;
use Cose\Key\SymmetricKey;
use Cose\Mac\Mac0Structure;

$key = SymmetricKey::create([
    SymmetricKey::TYPE => SymmetricKey::TYPE_OCT,
    SymmetricKey::DATA_K => random_bytes(16), // exactly 16 bytes for the 128-bit identifiers, 32 for the 256-bit ones
]);
$algorithm = AESMAC128_64::create();

$toBeMaced = Mac0Structure::create($protectedHeaderAsBytes, $payload);
$tag = $algorithm->hash((string) $toBeMaced, $key);                  // 8 bytes
$isValid = $algorithm->verify((string) $toBeMaced, $key, $tag);
```

!!! warning

    **AES-CBC-MAC is a MAC for structured messages, not for arbitrary bytes.**
    [RFC 9053 §3.2.1](https://www.rfc-editor.org/rfc/rfc9053#section-3.2.1) states two conditions the algorithm
    classes cannot check for you:

    - *"A single key must only be used for messages of a fixed or known length."* Otherwise, given two message and
      tag pairs, an attacker forges a third. Computing the tag over a `Mac0Structure` or `MacStructure`, as above, is
      the mitigation: the `MAC_structure` of [RFC 9052 §6.3](https://www.rfc-editor.org/rfc/rfc9052#section-6.3) is
      CBOR, and CBOR encodes the length of every field it holds. A tag computed over `$payload->getValue()` directly
      has no such protection, on top of being interoperable with nothing.
    - *"Cipher Block Chaining (CBC) encryption and CBC-MAC MUST use different keys."* A key that also encrypts
      anything in CBC mode turns the last ciphertext block into a valid tag.

    The construction is AES in CBC mode with an all-zero IV, padding method 1 of ISO/IEC 9797-1 (zero bytes up to
    the block boundary, none when the message already is a multiple of 16 bytes; the padding the
    [cose-wg/Examples](https://github.com/cose-wg/Examples/tree/master/cbc-mac-examples) vectors use), and the last
    block truncated to the tag length. It is **not** AES-CMAC ([RFC 4493](https://www.rfc-editor.org/rfc/rfc4493)).

    The 64-bit tag variants are the ones constrained devices use; all four identifiers are marked *Recommended: Yes* at
    IANA and none of them needs an acknowledgement.
