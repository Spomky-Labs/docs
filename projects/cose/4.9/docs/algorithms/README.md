---
description: 'Every algorithm identifier the library ships, with its RFC reference.'
---

# Algorithms

Every table carries a *Reference* column naming the section of the RFC that defines the identifier; every value was
checked against the IANA [COSE Algorithms](https://www.iana.org/assignments/cose/cose.xhtml#algorithms) registry,
and `tests/RfcReferencesTest.php` keeps the tables in step with the classes. The key types and curves the
algorithms take are in [Keys](../keys/README.md#key-types). Every class has a static `create()` and `identifier()`, and
registers in a [`Manager`](registering-algorithms.md).

- [Signature algorithms](signature-algorithms.md) — ECDSA, EdDSA, RSA and the fully-specified identifiers
- [ML-DSA](ml-dsa.md) — the post-quantum signatures of RFC 9964
- [Non-standard and insecure algorithms](insecure-algorithms.md) — what is weak, still required, and what
  it asks of you
- [MAC algorithms](mac-algorithms.md) — HMAC and AES-CBC-MAC
- [Content encryption algorithms](content-encryption-algorithms.md) — AES-GCM, AES-CCM and
  ChaCha20/Poly1305
- [Key management algorithms](key-management-algorithms.md) — `direct`, HKDF, AES Key Wrap and ECDH
- [Hash algorithms](hash-algorithms.md) — the RFC 9054 registry and the SHAKE sponges
- [Registering algorithms](registering-algorithms.md) — building the `Manager` an application accepts
