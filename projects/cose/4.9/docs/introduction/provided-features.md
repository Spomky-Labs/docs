---
description: 'The specifications COSE implements, and what it deliberately leaves to the calling application.'
---

# Provided features

The library implements COSE (CBOR Object Signing and Encryption) as defined in
[RFC 9052](https://datatracker.ietf.org/doc/html/rfc9052) and
[RFC 9053](https://datatracker.ietf.org/doc/html/rfc9053): the COSE key types, the signature, MAC, content
encryption and key management algorithms, the cryptographic structures a signature, a MAC or an encryption
is computed over, and the header rules that decide what a message says.

The six COSE message types themselves come from
[spomky-labs/cbor-php](https://github.com/Spomky-Labs/cbor-php) 3.4.0 or later, as `CBOR\Tag\CoseSign1Tag`
and its siblings; this library owns what RFC 9052 reads into them.

## What it implements

| Specification | What the library does with it |
|---|---|
| [RFC 9052](https://datatracker.ietf.org/doc/html/rfc9052) | Structures and process: the `Sig_structure`, `MAC_structure` and `Enc_structure`, the header rules, `external_aad`, detached content |
| [RFC 9053](https://datatracker.ietf.org/doc/html/rfc9053) | Initial algorithms: signatures, HMAC, AES-CBC-MAC, the AEAD content encryption algorithms, the key management algorithms (`direct`, HKDF, AES Key Wrap, ECDH) and the key types |
| [RFC 8230](https://datatracker.ietf.org/doc/html/rfc8230) | RSASSA-PSS (`PS256`, `PS384`, `PS512`) and the RSA key type |
| [RFC 8812](https://datatracker.ietf.org/doc/html/rfc8812) | RSASSA-PKCS1-v1_5 (`RS256`, `RS384`, `RS512`, `RS1`) and ECDSA with secp256k1 (`ES256K`) |
| [RFC 9864](https://www.rfc-editor.org/rfc/rfc9864.html) | Fully-specified algorithm identifiers |
| [RFC 9596](https://www.rfc-editor.org/rfc/rfc9596.html) | The `typ` (type) header parameter |
| [RFC 9597](https://www.rfc-editor.org/rfc/rfc9597.html) | CWT Claims in COSE headers |
| [RFC 9054](https://www.rfc-editor.org/rfc/rfc9054.html) | The hash algorithms, as a registry of their own |
| [RFC 9679](https://www.rfc-editor.org/rfc/rfc9679.html) | The COSE Key Thumbprint |
| [RFC 9360](https://www.rfc-editor.org/rfc/rfc9360.html) | The header parameters carrying and referencing X.509 certificates |
| [RFC 9995](https://www.rfc-editor.org/rfc/rfc9995.html) | The hash envelope |
| [RFC 9338](https://www.rfc-editor.org/rfc/rfc9338.html) | Countersignatures, version 2, labels 11 and 12 |
| [RFC 9964](https://www.rfc-editor.org/rfc/rfc9964.html) | ML-DSA for JOSE and COSE: ML-DSA-44/65/87 and the AKP key type |
| [RFC 9942](https://www.rfc-editor.org/rfc/rfc9942.html) | Receipts: the `receipts`, `vds` and `vdp` header parameters and the `RFC9162_SHA256` verifiable data structure |
| [RFC 9921](https://www.rfc-editor.org/rfc/rfc9921.html) | RFC 3161 timestamp tokens, carried and bound to the message, not validated |

## Where to start

- **Producing or checking a signed message** —
  [Signing and verifying](../signing/README.md), then
  [What the application must check](../signing/what-the-application-must-check.md) before you rely on a
  verification that returned `true`.
- **Reading a message someone handed you** —
  [Messages, structures and headers](../messages/README.md), and
  [Reading headers](../messages/reading-headers.md) for the rules RFC 9052 puts on a header map.
- **Encrypting** — [Encryption](../encryption/README.md) for the message, and
  [Key management](../key-management/README.md) for how a recipient gets the content encryption key.
- **Handling keys** — [Keys](../keys/README.md), and
  [Key restrictions](../keys/key-restrictions.md) for the `alg` and `key_ops` rules the library enforces.
- **Choosing an identifier** — [Algorithms](../algorithms/README.md) lists every one the library ships
  with its RFC reference.
- **Verifying a CBOR Web Token** — [CBOR Web Tokens](../header-parameters/cwt.md).

## What it leaves to the application

The library computes and checks cryptography over the structures the RFCs define. Several decisions are
not cryptographic, and it does not make them for you:

- **Which algorithm is acceptable** for a given message. A verification confirms the signature made by
  the algorithm the message names; deciding that the algorithm was allowed to sign it is a separate step.
  See [What the application must check](../signing/what-the-application-must-check.md).
- **Whether a certificate is trusted.** The X.509 header parameters are read and the certificate they
  carry can be turned into a key, but no chain is built or validated and no network call is made. See
  [X.509 header parameters](../header-parameters/x509.md).
- **Whether a claim is acceptable.** A CWT is verified as a COSE message; the claims inside it are yours
  to check. See [CBOR Web Tokens](../header-parameters/cwt.md).
- **Whether a timestamp token or a receipt comes from an authority you trust.** The binding between the
  token and the message is checked; the trust in the issuer is not. See
  [Timestamp tokens](../header-parameters/timestamp-tokens.md) and
  [Receipts](../header-parameters/receipts.md).

Each of those pages ends with a section saying where the library stops.

## References

- [RFC 9052 — CBOR Object Signing and Encryption (COSE): Structures and Process](https://datatracker.ietf.org/doc/html/rfc9052)
- [RFC 9053 — CBOR Object Signing and Encryption (COSE): Initial Algorithms](https://datatracker.ietf.org/doc/html/rfc9053)
- [RFC 8230 — Using RSA Algorithms with COSE Messages](https://datatracker.ietf.org/doc/html/rfc8230)
- [RFC 8812 — COSE and JOSE Registrations for WebAuthn Algorithms](https://datatracker.ietf.org/doc/html/rfc8812)
- [RFC 9864 — Fully-Specified Algorithms for JOSE and COSE](https://www.rfc-editor.org/rfc/rfc9864.html)
- [RFC 9596 — COSE "typ" (type) Header Parameter](https://www.rfc-editor.org/rfc/rfc9596.html)
- [RFC 9597 — CBOR Web Token (CWT) Claims in COSE Headers](https://www.rfc-editor.org/rfc/rfc9597.html)
- [RFC 9054 — COSE: Hash Algorithms](https://www.rfc-editor.org/rfc/rfc9054.html)
- [RFC 9679 — COSE Key Thumbprint](https://www.rfc-editor.org/rfc/rfc9679.html)
- [RFC 9360 — COSE: Header Parameters for Carrying and Referencing X.509 Certificates](https://www.rfc-editor.org/rfc/rfc9360.html)
- [RFC 9995 — COSE Hash Envelope](https://www.rfc-editor.org/rfc/rfc9995.html)
- [RFC 9338 — COSE: Countersignatures](https://www.rfc-editor.org/rfc/rfc9338.html)
- [RFC 9964 — ML-DSA for JOSE and COSE](https://www.rfc-editor.org/rfc/rfc9964.html)
- [RFC 9881 — Algorithm Identifiers for ML-DSA](https://www.rfc-editor.org/rfc/rfc9881.html)
- [FIPS 204 — Module-Lattice-Based Digital Signature Standard](https://doi.org/10.6028/NIST.FIPS.204)
- [RFC 9942 — COSE Receipts](https://www.rfc-editor.org/rfc/rfc9942.html)
- [RFC 9162 — Certificate Transparency Version 2.0](https://www.rfc-editor.org/rfc/rfc9162.html)
- [RFC 9921 — COSE Header Parameter for Timestamp Tokens as Defined in RFC 3161](https://www.rfc-editor.org/rfc/rfc9921.html)
- [RFC 3161 — Internet X.509 PKI Time-Stamp Protocol (TSP)](https://www.rfc-editor.org/rfc/rfc3161.html)
- [RFC 8392 — CBOR Web Token (CWT)](https://datatracker.ietf.org/doc/html/rfc8392)
- [RFC 3394 — Advanced Encryption Standard (AES) Key Wrap Algorithm](https://www.rfc-editor.org/rfc/rfc3394.html)
- [RFC 5869 — HMAC-based Extract-and-Expand Key Derivation Function (HKDF)](https://www.rfc-editor.org/rfc/rfc5869.html)
- [RFC 7748 — Elliptic Curves for Security](https://www.rfc-editor.org/rfc/rfc7748.html)
- [IANA COSE registry](https://www.iana.org/assignments/cose/cose.xhtml): the algorithm, key type and
  curve registries every identifier of this library is checked against
