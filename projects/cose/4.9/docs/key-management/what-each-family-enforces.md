---
description: 'The rules of RFC 9052 §8.5 and RFC 9053 §6 that each key management family applies.'
---

# What each family enforces

**Direct encryption** (`DirectEncryption`: `direct`, `direct+HKDF-*`) and **direct key agreement**
(`ECDH-*+HKDF-*`) decide the key of the layer below instead of transporting one: `isDirect()` is true, `protectKey()`
takes no key and derives it. [RFC 9052 §8.5.1](https://datatracker.ietf.org/doc/html/rfc9052#section-8.5.1) and
[§8.5.4](https://datatracker.ietf.org/doc/html/rfc9052#section-8.5.4) follow from that, and are enforced on both
sides: such a recipient "MUST be the only mode used on the message" (a sibling recipient is refused), its
`ciphertext` "MUST be a zero-length byte string", its `recipients` "MUST be absent". `direct` adds that the protected
bucket "MUST be zero length" (RFC 9053 §6.1.1) and uses the key as it is; the four `direct+HKDF-*` run it through the
HKDF of §5.1: HMAC with the extract step for SHA-256 and SHA-512, AES-CBC-MAC without it for AES-128 and AES-256,
where the shared secret is the PRK, has to be exactly 16 or 32 bytes, and the `salt`, if carried, is not used
(§5.1). "Either the 'salt' parameter for HKDF or the 'PartyU nonce' parameter MUST be present" (§6.1.2): the sending
side refuses to derive without one; the receiving side derives with what the message carries, the interoperability
fixtures omitting both.

**Key wrap** (`KeyWrap`: `A128KW`, `A192KW`, `A256KW`) is the AES Key Wrap of RFC 3394, through
[spomky-labs/aes-key-wrap](https://github.com/Spomky-Labs/aes-key-wrap), with `wrap()` and `unwrap()` exposed on their
own. "The protected header bucket MUST be empty" (§6.2.1), in either of the two empty forms of RFC 9052 §3. The KEK
is a symmetric key of exactly the size the identifier names; the key to wrap is a multiple of 64 bits, at least 128.
A wrapped key that fails the integrity check of RFC 3394 §2.2.3 is reported with one message
(`AesKeyWrap::UNWRAP_FAILED`), whether the KEK is wrong or the value was tampered with.

**Key agreement** (`KeyAgreement`: the twelve `ECDH-*`) runs an elliptic curve Diffie-Hellman agreement, the HKDF
over its shared secret with the `COSE_KDF_Context`, and either hands the derived key to the layer below (§6.3.1) or
wraps the layer's key with it (§6.4.1, where the context binds to the key wrap algorithm and its key size).
`agree()` exposes the agreement-and-KDF step on its own. Before anything is multiplied:

- the two keys are of the same type and on the same curve (§6.3.1: "Implementations MUST verify that the key type
  and curve are correct"); an EC2 ephemeral key for an OKP recipient is refused, and so is a key on another curve;
- the curve is one ECDH is defined for: P-256, P-384, P-521, X25519, X448, and the four Brainpool curves where the
  OpenSSL build provides them (`EllipticCurveDiffieHellman::isCurveSupported()`); secp256k1, registered for ES256K
  and nothing else, and the Edwards curves, which sign, are refused;
- **an EC2 point is checked to be on the curve** (§6.3.1.1) by `Ec2Key::assertOnCurve()`, by the library itself and
  before OpenSSL sees the point: an off-curve point fed to a scalar multiplication is the invalid-curve attack, which
  leaks the private key a few bits per message. The constructor of `Ec2Key` does not run the check, so that keys
  built from arbitrary bytes keep loading; `isOnCurve()` answers without throwing;
- **an all-zero OKP secret is refused** (RFC 7748 §6.1): "for the 'OKP' format, there is no simple way to perform
  point validation", and the all-zero output is what a low-order point produces.

*Ephemeral-Static* (`ECDH-ES`): "the sender MUST generate a new ephemeral key for every key agreement operation"
(§6.3.1). `protectKey()` generates it on the recipient's curve and hands back its public half, `kty`, `crv`, `x`,
`y` and nothing else, as the `ephemeral key` (-1) header parameter; `recoverKey()` reads it with
`CoseHeaders::getEphemeralKey()`, which refuses a key carrying a private part.

*Static-Static* (`ECDH-SS`): the sender's static key is the application's to supply on both sides,
`RecipientLayer::withSenderKey()`: its private key when sending, the sender's public key when receiving, resolved
from whatever identifies it in the headers: `static key id` (-3, `getStaticKeyId()`), or the `x5t-sender`,
`x5u-sender` and `x5chain-sender` parameters of RFC 9360 §3 (`getX5TSender()`, `getX5USender()`,
`getX5ChainSender()`, see [X.509 header parameters](../header-parameters/x509.md)), after the validation the application owns. A
`static key` (-2, `getStaticKey()`) carried in the message is used when no key was supplied, with the caveat that a
header authenticates nothing on its own. "The sender MUST either generate a new random value or create a unique value
for use as a KDF input": the sending side refuses to run without a `salt` (-20) or a `PartyU nonce` (-22) header
parameter.

```php
use CBOR\ByteStringObject;
use CBOR\MapItem;
use CBOR\MapObject;
use CBOR\NegativeIntegerObject;
use Cose\Algorithm\KeyManagement\ECDH_SS_HKDF256;
use Cose\Algorithm\KeyManagement\RecipientLayer;
use Cose\Encryption\Recipient;
use Cose\Structure\CoseHeaders;

// Sending: Alice's static private key, Bob's public key, and a nonce that is unique for the pair of keys
$recipient = Recipient::create(ECDH_SS_HKDF256::create(), $bobPublicKey, null, MapObject::create([
    MapItem::create(NegativeIntegerObject::create(CoseHeaders::LABEL_STATIC_KEY_ID), ByteStringObject::create('alice')),
    MapItem::create(NegativeIntegerObject::create(CoseHeaders::LABEL_PARTY_U_NONCE), ByteStringObject::create(random_bytes(32))),
]))->withSenderKey($alicePrivateKey);

// Receiving: Bob resolves "alice" out of the keys he trusts, and hands Alice's public key to the layer
$layer = RecipientLayer::fromRecipient($coseRecipient, $algorithm)->withSenderKey($alicePublicKey);
$cek = ECDH_SS_HKDF256::create()->recoverKey($layer, $bobPrivateKey);
```
