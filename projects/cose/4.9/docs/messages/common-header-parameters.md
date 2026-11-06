---
description: 'Every COSE header label the library reads, with its type, its RFC and its typed accessor.'
---

# Common header parameters

| Label | Name | Type | Description |
|-------|------|------|-------------|
| 1 | alg | int | Cryptographic algorithm |
| 2 | crit | [+label] | Critical headers |
| 3 | content type | tstr / uint | Content type of payload |
| 4 | kid | bstr | Key identifier |
| 5 | IV | bstr | Initialization Vector, see [The nonce](../encryption/the-nonce.md) |
| 6 | Partial IV | bstr | Partial Initialization Vector |
| 15 | CWT Claims | map | CWT claims in the header (RFC 9597), `getCwtClaims()` |
| 16 | typ | tstr / uint | Type of the COSE object (RFC 9596), `getTyp()` |
| 11 | Countersignature version 2 | COSE_Countersignature / [+ COSE_Countersignature] | Full countersignatures, unprotected only (RFC 9338), `getCountersignatures()` |
| 12 | Countersignature0 version 2 | bstr | Abbreviated countersignature, unprotected only (RFC 9338), `getCountersignature0()` |
| 32 | x5bag | COSE_X509 | Unordered bag of X.509 certificates (RFC 9360), `getX5Bag()` |
| 33 | x5chain | COSE_X509 | Ordered chain of X.509 certificates, end-entity first (RFC 9360), `getX5Chain()` |
| 34 | x5t | COSE_CertHash | Thumbprint of the end-entity certificate (RFC 9360), `getX5T()` |
| 35 | x5u | uri | URI of an X.509 certificate, never fetched by this library (RFC 9360), `getX5U()` |
| 258 | payload-hash-alg | int | Hash algorithm of the payload of a hash envelope, protected only (RFC 9995), `getPayloadHashAlg()` |
| 259 | preimage-content-type | uint / tstr | Content type of the hashed bytes, protected only (RFC 9995), `getPreimageContentType()` |
| 260 | payload-location | tstr | Where the hashed bytes can be retrieved, never fetched by this library (RFC 9995), `getPayloadLocation()` |
| 394 | receipts | [+ bstr .cbor Receipt] | COSE receipts, each a tagged COSE_Sign1 (RFC 9942), `getReceipts()` |
| 395 | vds | int | Verifiable data structure of a receipt, protected bucket only (RFC 9942), `getVds()` |
| 396 | vdp | map | Verifiable data structure proofs of a receipt, keyed by proof type (RFC 9942), `getVdp()` |

## The key management parameters

The header *algorithm* parameters of the key management algorithms, read from a `COSE_recipient`
by the same accessors:

| Label | Name | Type | Description |
|-------|------|------|-------------|
| -1 | ephemeral key | COSE_Key | Sender's ephemeral public key, ECDH-ES (RFC 9053 §6.3.1), `getEphemeralKey()` |
| -2 | static key | COSE_Key | Sender's static public key, ECDH-SS (RFC 9053 §6.3.1), `getStaticKey()` |
| -3 | static key id | bstr | Identifier of the sender's static key, ECDH-SS (RFC 9053 §6.3.1), `getStaticKeyId()` |
| -20 | salt | bstr | Salt of the HKDF extract step (RFC 9053 §5.1), `getSalt()` |
| -21 | PartyU identity | bstr | PartyUInfo of the COSE_KDF_Context (RFC 9053 §5.2), `getPartyUIdentity()` |
| -22 | PartyU nonce | bstr / int | `getPartyUNonce()` |
| -23 | PartyU other | bstr | `getPartyUOther()` |
| -24 | PartyV identity | bstr | PartyVInfo of the COSE_KDF_Context (RFC 9053 §5.2), `getPartyVIdentity()` |
| -25 | PartyV nonce | bstr / int | `getPartyVNonce()` |
| -26 | PartyV other | bstr | `getPartyVOther()` |
| -27 | x5t-sender | COSE_CertHash | Thumbprint of the sender's key exchange certificate, ECDH-SS (RFC 9360 §3), `getX5TSender()` |
| -28 | x5u-sender | uri | URI of the sender's key exchange certificate, never fetched (RFC 9360 §3), `getX5USender()` |
| -29 | x5chain-sender | COSE_X509 | Chain of the sender's key exchange certificate, ECDH-SS (RFC 9360 §3), `getX5ChainSender()` |

