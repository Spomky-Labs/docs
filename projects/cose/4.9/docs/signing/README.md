---
description: 'COSE_Sign1 and COSE_Sign, what the application must check, and the verification contract.'
---

# Signing and verifying

The signature algorithms themselves (ECDSA, EdDSA, RSA, the fully-specified identifiers of RFC 9864, ML-DSA) are listed
in [Algorithms](../algorithms/signature-algorithms.md); the keys they take in [Keys](../keys/README.md).

- [COSE_Sign1](cose-sign1.md) — a message with a single signer, created and verified
- [What the application must check](what-the-application-must-check.md) — the two checks RFC 9052 §3.1
  leaves to the caller
- [COSE_Sign](cose-sign.md) — several signers, each covering the `Signature` structure
- [The verification contract](the-verification-contract.md) — what `verify()` returns and what it throws
- [Verifying with a certificate](verifying-with-a-certificate.md) — verifying with the key of an X.509
  certificate
- [Countersignatures](countersignatures.md) — a signature added after the message was finalized
