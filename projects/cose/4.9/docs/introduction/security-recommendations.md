---
description: 'The decisions COSE leaves to you, and the defaults that warn today and will refuse tomorrow.'
---

# Security recommendations

The library computes and checks cryptography over the structures the RFCs define. Several decisions are
not cryptographic, and it does not make them for you. This page lists every one it hands back, and every
default that is looser than a new deployment would choose.

Read it before you ship. Each item links to the page that explains it in full.

## Check `alg` and `crit` yourself

!!! danger "A verification that returned `true` says nothing about which algorithm was allowed"

    The library verifies the signature the message names. Deciding that the message was allowed to name
    that algorithm is a separate step, and
    [RFC 9052 §3.1](https://datatracker.ietf.org/doc/html/rfc9052#section-3.1) requires both:

    - **`alg` (label 1)**, read from the *protected* bucket, compared with what you accept for that key. A
      verifier that hard-codes its algorithm and ignores the header still accepts a message announcing a
      different one.
    - **`crit` (label 2)**: any label listed there that your application does not process makes the
      message unusable. Reject it instead of verifying it.

See [What the application must check](../signing/what-the-application-must-check.md).

## Never sign or MAC the payload on its own

A COSE signature or MAC covers a **structure** that binds the protected header and the message type, not
the payload. `Mac::hash()` and `Signature::sign()` authenticate exactly the bytes they are handed, so
passing `getPayload()->getValue()` straight to them produces a tag bound to no header, no algorithm and no
message type — which no other implementation will accept, and which a message of another type can be
replayed into. Build the structure; see
[Cryptographic structures](../messages/cryptographic-structures.md).

## Turn on the key restrictions when the algorithm comes from the message

A key may pin itself to one algorithm (`alg`) and to a set of operations (`key_ops`). For the signature
and MAC algorithms, enforcing that is **opt-in**, so a key that used to work keeps working:

```php
$manager = Manager::create()->add(ES256::create(), RS256::create())->withKeyRestrictionsEnforced();
```

Without it, a verifier that reads `alg` from the header and resolves it with `Manager::get()` has no
reason to refuse a downgrade the key itself forbids. The content encryption and key management algorithms
enforce the restrictions from the start. See
[Key restrictions](../keys/key-restrictions.md).

## Know what the weak algorithms cost you

Three of them are kept only for deployments that already rely on them, and each asks you to say so in
code:

| Algorithm | Why it is kept | What it asks |
|---|---|---|
| `RS1` (-65535) | Legacy authenticators that still sign with SHA-1 | `RS1::create(acknowledgeInsecureAlgorithm: true)`, or an `E_USER_WARNING` |
| `Ed256` (-260) | A construction no specification defines; IANA has reassigned the identifier to WalnutDSA | `Ed256::create(acknowledgeNonStandardAlgorithm: true)` |
| `Ed512` (-261) | The same, reassigned to TurboSHAKE128; it is **not** Ed448 | `Ed512::create(acknowledgeNonStandardAlgorithm: true)` |

Prefer `Ed25519` (-8 or -19) over `Ed256` and `Ed512`, and `Ed448` (-53) where you meant Curve448. As of
the next major version, omitting the acknowledgement throws instead of warning. See
[Non-standard and insecure algorithms](../algorithms/insecure-algorithms.md).

## Decide your own RSA modulus floor

The upper bounds are not negotiable: a modulus longer than 16384 bits or an exponent longer than 256 bits
is refused, because an RSA operation costs what the key it was given costs, and a verifier takes that key
from whoever produced the message.

The **minimum** is where the default is loose. A key below `RsaKeyValidator::MINIMUM_MODULUS_LENGTH`
(2048) bits only emits an `E_USER_WARNING` and the operation goes through, so that no deployment breaks on
upgrade. If 1024-bit authenticators are not your problem, write the bound down — and writing it down is
itself the acknowledgement, because a key below a bound *you* chose is refused with an exception:

```php
$algorithm = RS256::create(RsaKeyValidator::create(minimumModulusLength: 3072));
```

As of the next major version the implicit default becomes an exception on `sign()` and `false` on
`verify()`. See [Validating RSA keys](../keys/validating-rsa-keys.md).

## A certificate in a header is untrusted input

The X.509 header parameters are read, and the certificate they carry can become a key, but **no chain is
built or validated and no network call is ever made**. `x5u`, `x5u-sender` and `payload-location` are
returned to you, never fetched. RFC 9360 is explicit that a self-signed certificate in the parameter "MUST
NOT cause the update of the set of trust anchors without some out-of-band confirmation", and that the
end-entity certificate must be integrity protected by COSE — by the parameter sitting in the protected
bucket, by an `x5t` there naming it, or by the certificate being in the `external_aad`. The accessors take
the protected value first and do not tell you which bucket answered;
`getProtectedHeaderParameter(CoseHeaders::LABEL_X5CHAIN)` does, when your policy needs to know. A
thumbprint "does not provide any trust": it selects a candidate. See
[X.509 header parameters](../header-parameters/x509.md).

## A binding checked is not an issuer trusted

For a receipt and for a timestamp token, the library checks that the object is bound to the message it
travels with, and the proof it carries against the structure it claims. Whether the authority that issued
it is one you trust is yours, and so is the freshness of what it asserts. See
[Receipts](../header-parameters/receipts.md) and
[Timestamp tokens](../header-parameters/timestamp-tokens.md).

## A CWT is a message, its claims are yours

Verifying a CWT confirms the COSE message around the claims. `iss`, `aud`, `exp`, `nbf` and anything your
protocol adds are not checked by this library. See [CBOR Web Tokens](../header-parameters/cwt.md).

## Install the CBOR package this library expects

Two rules a crafted header depends on are enforced by the decoder, not here: a label appearing twice makes
the message malformed, and nesting is bounded so that a header cannot exhaust the memory of the process.
Both come from [spomky-labs/cbor-php](https://github.com/Spomky-Labs/cbor-php) 3.4.0 or later, which is
why the package declares `conflict: <3.4.0`. Nothing in this library re-checks either rule. See
[Installation](installation.md#the-cbor-package).

## Ask before you register an algorithm the platform may not have

`create()` throws on a platform that cannot run the algorithm, rather than reporting valid signatures as
invalid. A registry assembled on an unknown host should ask each class with its static `isSupported()`
first. See [the algorithms that depend on the platform](pre-requisite.md#the-algorithms-that-depend-on-the-platform).
