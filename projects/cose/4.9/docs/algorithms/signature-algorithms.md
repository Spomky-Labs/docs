---
description: 'ECDSA, EdDSA, RSA and the fully-specified identifiers of RFC 9864.'
---

# Signature algorithms

**ECDSA** (`Cose\Algorithm\Signature\ECDSA`)

| Algorithm | Identifier | Description | Reference |
|-----------|------------|-------------|-----------|
| ES256 | -7 | ECDSA with SHA-256 | [RFC 9053 §2.1](https://www.rfc-editor.org/rfc/rfc9053#section-2.1) |
| ES384 | -35 | ECDSA with SHA-384 | [RFC 9053 §2.1](https://www.rfc-editor.org/rfc/rfc9053#section-2.1) |
| ES512 | -36 | ECDSA with SHA-512 | [RFC 9053 §2.1](https://www.rfc-editor.org/rfc/rfc9053#section-2.1) |
| ES256K | -47 | ECDSA with the secp256k1 curve and SHA-256 | [RFC 8812 §3.2](https://www.rfc-editor.org/rfc/rfc8812#section-3.2) |

**EdDSA** (`Cose\Algorithm\Signature\EdDSA`): Ed25519 keys only, whatever the class; every one of them needs
`ext-sodium` (`EdDSA::isSupported()`)

| Algorithm | Identifier | Description | Reference |
|-----------|------------|-------------|-----------|
| EdDSA | -8 | Edwards-curve Digital Signature Algorithm | [RFC 9053 §2.2](https://www.rfc-editor.org/rfc/rfc9053#section-2.2) |
| Ed25519 | -8 | The same algorithm under its own class name; identical signatures, identical identifier | [RFC 9053 §2.2](https://www.rfc-editor.org/rfc/rfc9053#section-2.2) |
| Ed256 | -260 | Ed25519 over a SHA-256 digest, **non-standard**, see below | none |
| Ed512 | -261 | Ed25519 over a SHA-512 digest, **non-standard**, see below | none |

**RSA** (`Cose\Algorithm\Signature\RSA`)

| Algorithm | Identifier | Description | Reference |
|-----------|------------|-------------|-----------|
| RS256 | -257 | RSASSA-PKCS1-v1_5 with SHA-256 | [RFC 8812 §2](https://www.rfc-editor.org/rfc/rfc8812#section-2) |
| RS384 | -258 | RSASSA-PKCS1-v1_5 with SHA-384 | [RFC 8812 §2](https://www.rfc-editor.org/rfc/rfc8812#section-2) |
| RS512 | -259 | RSASSA-PKCS1-v1_5 with SHA-512 | [RFC 8812 §2](https://www.rfc-editor.org/rfc/rfc8812#section-2) |
| PS256 | -37 | RSASSA-PSS with SHA-256 | [RFC 8230 §2](https://www.rfc-editor.org/rfc/rfc8230#section-2) |
| PS384 | -38 | RSASSA-PSS with SHA-384 | [RFC 8230 §2](https://www.rfc-editor.org/rfc/rfc8230#section-2) |
| PS512 | -39 | RSASSA-PSS with SHA-512 | [RFC 8230 §2](https://www.rfc-editor.org/rfc/rfc8230#section-2) |
| RS1 | -65535 | RSASSA-PKCS1-v1_5 with SHA-1, **not secure**, kept only for legacy authenticators, see below | [RFC 8812 §2](https://www.rfc-editor.org/rfc/rfc8812#section-2) |

Every RSA algorithm validates the key it is given (modulus and exponent bounds, public parameter constraints); see
[Validating RSA keys](../keys/validating-rsa-keys.md); the side-channel considerations of signing with RSASSA-PSS are in
[Installation](../introduction/installation.md#performance).

What `verify()` returns and when `sign()` throws is the
[The verification contract](../signing/the-verification-contract.md).

## Fully-specified algorithms

[RFC 9864](https://www.rfc-editor.org/rfc/rfc9864.html) registers identifiers that determine the curve and the hash on
their own, instead of leaving them to the other parameters of the key. WebAuthn Level 3 has adopted them, so a relying
party may receive a credential whose `alg` carries one of these values. They live in the
`Cose\Algorithm\Signature\FullySpecified` namespace.

| Algorithm | Identifier | Description | Reference |
|-----------|------------|-------------|-----------|
| ESP256 | -9 | ECDSA with the P-256 curve and SHA-256 | [RFC 9864 §2.1](https://www.rfc-editor.org/rfc/rfc9864#section-2.1) |
| ESP384 | -51 | ECDSA with the P-384 curve and SHA-384 | [RFC 9864 §2.1](https://www.rfc-editor.org/rfc/rfc9864#section-2.1) |
| ESP512 | -52 | ECDSA with the P-521 curve and SHA-512 | [RFC 9864 §2.1](https://www.rfc-editor.org/rfc/rfc9864#section-2.1) |
| ESB256 | -265 | ECDSA with the brainpoolP256r1 curve and SHA-256; requires an OpenSSL build with Brainpool | [RFC 9864 §2.1](https://www.rfc-editor.org/rfc/rfc9864#section-2.1) |
| ESB320 | -266 | ECDSA with the brainpoolP320r1 curve and SHA-384; requires an OpenSSL build with Brainpool | [RFC 9864 §2.1](https://www.rfc-editor.org/rfc/rfc9864#section-2.1) |
| ESB384 | -267 | ECDSA with the brainpoolP384r1 curve and SHA-384; requires an OpenSSL build with Brainpool | [RFC 9864 §2.1](https://www.rfc-editor.org/rfc/rfc9864#section-2.1) |
| ESB512 | -268 | ECDSA with the brainpoolP512r1 curve and SHA-512; requires an OpenSSL build with Brainpool | [RFC 9864 §2.1](https://www.rfc-editor.org/rfc/rfc9864#section-2.1) |
| Ed25519 | -19 | EdDSA with the Ed25519 parameter set | [RFC 9864 §2.2](https://www.rfc-editor.org/rfc/rfc9864#section-2.2) |
| Ed448 | -53 | EdDSA with the Ed448 parameter set; requires PHP 8.4 or later | [RFC 9864 §2.2](https://www.rfc-editor.org/rfc/rfc9864#section-2.2) |

```php
use Cose\Algorithm\Manager;
use Cose\Algorithm\Signature\FullySpecified\ESP256;
use Cose\Algorithm\Signature\FullySpecified\Ed25519;

$manager = Manager::create()
    ->add(ESP256::create())
    ->add(Ed25519::create());
```

`Cose\Algorithm\Signature\FullySpecified\Ed25519` (-19) and `Cose\Algorithm\Signature\EdDSA\Ed25519` (-8)
compute the same signatures; only the algorithm identifier differs.

Ed448 goes through OpenSSL, which PHP only wires up for Edwards curves as of PHP 8.4, and the Brainpool curves are
compiled out of some OpenSSL builds and of every FIPS provider. `Ed448::isSupported()` and `ESB256::isSupported()`
(each `ESB*` class) say; `create()` throws a `RuntimeException` naming what is missing. See
[Optional extensions](../introduction/pre-requisite.md#optional-extensions) for the conditional registration.

[`examples/10-fully-specified-algorithms.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/10-fully-specified-algorithms.php) runs the fully-specified
identifiers next to the polymorphic ones.

## The polymorphic identifiers are deprecated at IANA, and still required

RFC 9864 marks ES256 (-7), EdDSA (-8), ES384 (-35) and ES512 (-36) as *Deprecated* in the IANA COSE Algorithms
registry, in favour of the fully-specified identifiers above. That is a registry status, not an operational one:
WebAuthn and CTAP authenticators emit -7 and -8, an authenticator's algorithm is fixed at manufacture, and they will
keep emitting them for years. This library keeps the four identifiers as first-class algorithms: no deprecation
notice, no runtime warning, and no change to how `EdDSA` (-8) resolves its curve. A relying party registers both
forms and lets the credential decide:

```php
use Cose\Algorithm\Manager;
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Algorithm\Signature\EdDSA\EdDSA;
use Cose\Algorithm\Signature\FullySpecified\Ed25519;
use Cose\Algorithm\Signature\FullySpecified\ESP256;

$manager = Manager::create()->add(
    ES256::create(),    // -7, what today's authenticators emit
    ESP256::create(),   // -9, its fully-specified form
    new EdDSA(),        // -8
    Ed25519::create(),  // -19
);
```
