---
description: 'How a recipient gets the content encryption key: direct, HKDF, AES Key Wrap and ECDH.'
---

# Key management

The content key distribution methods of [RFC 9053 §5 and §6](https://datatracker.ietf.org/doc/html/rfc9053#section-5),
in `Cose\Algorithm\KeyManagement`: what fills a `COSE_recipient` on the sending side and reads one on the receiving
side, to hand the layer below (the AEAD of a `COSE_Encrypt`, the MAC of a `COSE_Mac`, or the recipient above when
recipients are nested) its key. [RFC 9052 §8.5](https://datatracker.ietf.org/doc/html/rfc9052#section-8.5) sorts
them into classes, and each class is an interface here, all extending `KeyManagement`: `DirectEncryption`
(`direct`, `direct+HKDF-*`), `KeyWrap` (`A128KW`, `A192KW`, `A256KW`) and `KeyAgreement` (the twelve `ECDH-*`).
The eighteen identifiers, with their classes, are listed in
[Key management algorithms](../algorithms/key-management-algorithms.md); RSAES-OAEP (-40, -41, -42) and COSE-HPKE are
not implemented.

`EncryptStructure::encryptFor()` runs the sending side for a whole message, see
[COSE_Encrypt](../encryption/cose-encrypt.md); the receiving side is one
call per recipient, the application picking the recipient that is its own.

- [The two sides of an algorithm](the-two-sides-of-an-algorithm.md) — what the sender computes and what
  the recipient computes
- [What each family enforces](what-each-family-enforces.md) — the rules of RFC 9052 §8.5 and RFC 9053 §6
- [The KDF context](the-kdf-context.md) — the `COSE_KDF_Context` and the parameters that fill it
- [Key restrictions](key-restrictions.md) — the `alg` and `key_ops` checks of a recipient key
