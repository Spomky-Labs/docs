---
description: 'COSE_Encrypt0 and COSE_Encrypt, and the nonce the AEAD algorithms take.'
---

# Encryption

The content encryption algorithms of [RFC 9053 §4](https://datatracker.ietf.org/doc/html/rfc9053#section-4) live in
`Cose\Algorithm\ContentEncryption`: `A128GCM`, `A192GCM`, `A256GCM`, the eight AES-CCM variants and
`ChaCha20Poly1305`, see [Content encryption algorithms](../algorithms/content-encryption-algorithms.md). Every one of
them encrypts with a symmetric key, a nonce whose length the algorithm fixes, and the `Enc_structure` of
[RFC 9052 §5.3](https://datatracker.ietf.org/doc/html/rfc9052#section-5.3) as additional authenticated data, never
the protected header on its own. `Encrypt0Structure` and `EncryptStructure` build that structure and hand it to the
algorithm through `encrypt()` and `decrypt()`. How the content key reaches the recipients of a `COSE_Encrypt` is the
subject of [Key management](../key-management/README.md).

- [COSE_Encrypt0](cose-encrypt0.md) — a single recipient that already holds the content encryption key
- [COSE_Encrypt](cose-encrypt.md) — several recipients, each given the key by its own algorithm
- [The nonce: IV and Partial IV](the-nonce.md) — where the nonce comes from
