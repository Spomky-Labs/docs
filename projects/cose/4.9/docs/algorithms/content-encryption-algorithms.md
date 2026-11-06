---
description: 'The AEAD algorithms of RFC 9053 §4: AES-GCM, AES-CCM and ChaCha20/Poly1305.'
---

# Content encryption algorithms

The AEAD algorithms of [RFC 9053 §4](https://datatracker.ietf.org/doc/html/rfc9053#section-4), in
`Cose\Algorithm\ContentEncryption`. Each implements `ContentEncryption` (`encrypt()`, `decrypt()`, `keyLength()`,
`nonceLength()` and `tagLength()`) and is used through the `Enc_structure` classes, see [Encryption](../encryption/README.md).

| Algorithm | Identifier | Class | Key | Nonce | Tag | Reference |
|-----------|------------|-------|-----|-------|-----|-----------|
| A128GCM | 1 | `A128GCM` | 128 bits | 12 bytes | 128 bits | [RFC 9053 §4.1](https://www.rfc-editor.org/rfc/rfc9053#section-4.1) |
| A192GCM | 2 | `A192GCM` | 192 bits | 12 bytes | 128 bits | [RFC 9053 §4.1](https://www.rfc-editor.org/rfc/rfc9053#section-4.1) |
| A256GCM | 3 | `A256GCM` | 256 bits | 12 bytes | 128 bits | [RFC 9053 §4.1](https://www.rfc-editor.org/rfc/rfc9053#section-4.1) |
| AES-CCM-16-64-128 | 10 | `A128CCM_16_64` | 128 bits | 13 bytes | 64 bits | [RFC 9053 §4.2](https://www.rfc-editor.org/rfc/rfc9053#section-4.2) |
| AES-CCM-16-64-256 | 11 | `A256CCM_16_64` | 256 bits | 13 bytes | 64 bits | [RFC 9053 §4.2](https://www.rfc-editor.org/rfc/rfc9053#section-4.2) |
| AES-CCM-64-64-128 | 12 | `A128CCM_64_64` | 128 bits | 7 bytes | 64 bits | [RFC 9053 §4.2](https://www.rfc-editor.org/rfc/rfc9053#section-4.2) |
| AES-CCM-64-64-256 | 13 | `A256CCM_64_64` | 256 bits | 7 bytes | 64 bits | [RFC 9053 §4.2](https://www.rfc-editor.org/rfc/rfc9053#section-4.2) |
| ChaCha20/Poly1305 | 24 | `ChaCha20Poly1305` | 256 bits | 12 bytes | 128 bits | [RFC 9053 §4.3](https://www.rfc-editor.org/rfc/rfc9053#section-4.3) |
| AES-CCM-16-128-128 | 30 | `A128CCM_16_128` | 128 bits | 13 bytes | 128 bits | [RFC 9053 §4.2](https://www.rfc-editor.org/rfc/rfc9053#section-4.2) |
| AES-CCM-16-128-256 | 31 | `A256CCM_16_128` | 256 bits | 13 bytes | 128 bits | [RFC 9053 §4.2](https://www.rfc-editor.org/rfc/rfc9053#section-4.2) |
| AES-CCM-64-128-128 | 32 | `A128CCM_64_128` | 128 bits | 7 bytes | 128 bits | [RFC 9053 §4.2](https://www.rfc-editor.org/rfc/rfc9053#section-4.2) |
| AES-CCM-64-128-256 | 33 | `A256CCM_64_128` | 256 bits | 7 bytes | 128 bits | [RFC 9053 §4.2](https://www.rfc-editor.org/rfc/rfc9053#section-4.2) |

The *Algorithm* column is the IANA name. The AES-CCM class names follow the JOSE convention of the
[web-token](https://github.com/web-token/jwt-framework) libraries: `A<key>CCM_<L>_<tag>`, where L is the size of the
length field in bits, which fixes the nonce length at 15 − L/8 bytes; the IANA name orders the same three numbers as
AES-CCM-L-tag-key.

What every algorithm checks, per RFC 9053 §4.1 to §4.3, before any primitive runs:

- the key is a `SymmetricKey` whose `k` is exactly `keyLength()` bytes long; a key of another length is rejected
  with an `InvalidArgumentException`;
- the nonce is exactly `nonceLength()` bytes long. This matters most for AES-CCM: OpenSSL accepts any nonce between
  7 and 13 bytes and derives L from it, so a 12-byte nonce handed to AES-CCM-16-64-128 would be encrypted with a
  different L and no conforming recipient could open the result. It is refused before OpenSSL sees it;
- the `alg` and `key_ops` restrictions of the key, see below.

The ciphertext is laid out as COSE carries it: the encrypted content followed by the `tagLength()` bytes of the
authentication tag. `decrypt()` hands the tag to the primitive, which verifies it in constant time; the library never
compares a tag itself.

**Key restrictions are enforced by default for these algorithms**, unlike the signature and MAC algorithms for which
enforcement is [opt-in](../keys/key-restrictions.md) so that existing keys keep working. RFC 9053 §4
makes the checks a MUST ("If the 'alg' field is present, it MUST match the … algorithm being used", "If the
'key_ops' field is present, it MUST include 'encrypt' or 'wrap key' when encrypting" and "'decrypt' or 'unwrap key'
when decrypting") and these algorithms have no caller to keep compatible. `withKeyRestrictionsEnforced(false)` turns
it off, on one algorithm or through `Manager::withKeyRestrictionsEnforced(false)`. `Key::assertUsableWithAny()` is
the form of the check that accepts either name of an operation.

**Platform support.** AES-GCM is in every OpenSSL build PHP links against. AES-CCM is not: `AesCcm::isSupported()`
(on any of the eight classes) says whether the build implements it. ChaCha20/Poly1305 goes through the sodium
extension when it is loaded and through OpenSSL's `chacha20-poly1305` otherwise; `ChaCha20Poly1305::isSupported()`
answers for both. An algorithm used on a platform that lacks it throws a `RuntimeException` naming the cipher.

```php
use Cose\Algorithm\ContentEncryption\A128CCM_16_64;
use Cose\Algorithm\ContentEncryption\A256GCM;
use Cose\Algorithm\ContentEncryption\ChaCha20Poly1305;
use Cose\Algorithm\Manager;

$manager = Manager::create()->add(A256GCM::create());
if (A128CCM_16_64::isSupported()) {
    $manager->add(A128CCM_16_64::create());
}
if (ChaCha20Poly1305::isSupported()) {
    $manager->add(ChaCha20Poly1305::create());
}
```

!!! warning

    A nonce reused under the same key breaks every one of these algorithms: AES-GCM and ChaCha20/Poly1305 give up
    their authentication key, AES-CCM the XOR of the plaintexts. Use `random_bytes()` per message, or a strictly
    increasing counter sent as the `Partial IV`; see [The nonce](../encryption/the-nonce.md).
