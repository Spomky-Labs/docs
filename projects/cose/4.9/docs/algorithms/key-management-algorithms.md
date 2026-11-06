---
description: 'direct, HKDF, AES Key Wrap and the ECDH variants, with their identifiers.'
---

# Key management algorithms

The content key distribution methods of [RFC 9053 §5 and §6](https://datatracker.ietf.org/doc/html/rfc9053#section-5),
in `Cose\Algorithm\KeyManagement`. [RFC 9052 §8.5](https://datatracker.ietf.org/doc/html/rfc9052#section-8.5)
sorts them into classes, and each class is an interface here, all extending `KeyManagement`. How they are used, and
the rules each family enforces, are in [Key management](../key-management/README.md).

| Algorithm | Identifier | Class | Family | Reference |
|-----------|------------|-------|--------|-----------|
| direct | -6 | `Direct` | `DirectEncryption` | [RFC 9053 §6.1.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.1.1) |
| direct+HKDF-SHA-256 | -10 | `DirectHKDF_SHA256` | `DirectEncryption` | [RFC 9053 §6.1.2](https://www.rfc-editor.org/rfc/rfc9053#section-6.1.2) |
| direct+HKDF-SHA-512 | -11 | `DirectHKDF_SHA512` | `DirectEncryption` | [RFC 9053 §6.1.2](https://www.rfc-editor.org/rfc/rfc9053#section-6.1.2) |
| direct+HKDF-AES-128 | -12 | `DirectHKDF_AES128` | `DirectEncryption` | [RFC 9053 §6.1.2](https://www.rfc-editor.org/rfc/rfc9053#section-6.1.2) |
| direct+HKDF-AES-256 | -13 | `DirectHKDF_AES256` | `DirectEncryption` | [RFC 9053 §6.1.2](https://www.rfc-editor.org/rfc/rfc9053#section-6.1.2) |
| A128KW | -3 | `A128KW` | `KeyWrap` | [RFC 9053 §6.2.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.2.1) |
| A192KW | -4 | `A192KW` | `KeyWrap` | [RFC 9053 §6.2.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.2.1) |
| A256KW | -5 | `A256KW` | `KeyWrap` | [RFC 9053 §6.2.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.2.1) |
| ECDH-ES + HKDF-256 | -25 | `ECDH_ES_HKDF256` | `KeyAgreement` | [RFC 9053 §6.3.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.3.1) |
| ECDH-ES + HKDF-512 | -26 | `ECDH_ES_HKDF512` | `KeyAgreement` | [RFC 9053 §6.3.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.3.1) |
| ECDH-SS + HKDF-256 | -27 | `ECDH_SS_HKDF256` | `KeyAgreement` | [RFC 9053 §6.3.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.3.1) |
| ECDH-SS + HKDF-512 | -28 | `ECDH_SS_HKDF512` | `KeyAgreement` | [RFC 9053 §6.3.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.3.1) |
| ECDH-ES + A128KW | -29 | `ECDH_ES_A128KW` | `KeyAgreement` | [RFC 9053 §6.4.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.4.1) |
| ECDH-ES + A192KW | -30 | `ECDH_ES_A192KW` | `KeyAgreement` | [RFC 9053 §6.4.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.4.1) |
| ECDH-ES + A256KW | -31 | `ECDH_ES_A256KW` | `KeyAgreement` | [RFC 9053 §6.4.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.4.1) |
| ECDH-SS + A128KW | -32 | `ECDH_SS_A128KW` | `KeyAgreement` | [RFC 9053 §6.4.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.4.1) |
| ECDH-SS + A192KW | -33 | `ECDH_SS_A192KW` | `KeyAgreement` | [RFC 9053 §6.4.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.4.1) |
| ECDH-SS + A256KW | -34 | `ECDH_SS_A256KW` | `KeyAgreement` | [RFC 9053 §6.4.1](https://www.rfc-editor.org/rfc/rfc9053#section-6.4.1) |

The *Algorithm* column is the IANA name. The AES Key Wrap primitive is
[spomky-labs/aes-key-wrap](https://github.com/Spomky-Labs/aes-key-wrap) (RFC 3394); ECDH runs on P-256, P-384,
P-521, X25519, X448 and the Brainpool curves where OpenSSL has them. RSAES-OAEP (-40, -41, -42; RFC 8230 §3) and
COSE-HPKE are not implemented.
