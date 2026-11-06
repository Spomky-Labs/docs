---
description: 'The COSE_KDF_Context of RFC 9053 §5.2 and the header parameters that fill it.'
---

# The KDF context

`KdfContext` builds the `COSE_KDF_Context` of [RFC 9053 §5.2](https://datatracker.ietf.org/doc/html/rfc9053#section-5.2)
exactly as the CDDL says: `[ AlgorithmID, PartyUInfo, PartyVInfo, SuppPubInfo, ? SuppPrivInfo ]`, the two `PartyInfo`
always three items long with `nil` where nothing is known, `keyDataLength` in bits, the protected bucket of the
recipient embedded as carried (or `h''` when empty, in either form), `other` and `SuppPrivInfo` present only when the
application defines them. `RecipientLayer::kdfContext()` builds it for a layer: the `PartyU *` and `PartyV *`
parameters (-21 to -26, `getPartyUIdentity()` and siblings, see
[Common header parameters](../messages/common-header-parameters.md)) come from the headers, and the application
completes them with what its protocol implies (identities are "often known as part of the protocol and can thus be
inferred rather than made explicit") through `withPartyU()`, `withPartyV()`, `withSuppPubInfoOther()` and
`withSuppPrivInfo()`, on the layer or on a `Recipient`. Where the headers carry a value, it wins element by element.

`Hkdf` is the HKDF of §5.1 as one construction with the PRF as a parameter (`Hkdf::hmac('sha256')`,
`Hkdf::hmac('sha512')`, `Hkdf::aesCbcMac(128)`, `Hkdf::aesCbcMac(256)`), checked against the vectors of RFC 5869
and against `hash_hkdf()`. "The AES HKDF version cannot be used with ECDH" (§5.1), and no such identifier exists.
