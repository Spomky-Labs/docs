---
description: 'The COSE key types and curves, and the classes that carry them.'
---

# Keys

## Key types

The `Cose\Key` classes cover the five key types of the IANA
[COSE Key Types](https://www.iana.org/assignments/cose/cose.xhtml#key-type) registry that the
[algorithms](../algorithms/README.md) use. `Key::createFromData()` picks the class from `kty` (label 1), and the parameter
labels are the `DATA_*` constants of each class: `Ec2Key::DATA_X` is -2, `RsaKey::DATA_N` is -1, and so on.

| Key type | `kty` | Class | Parameters | Reference |
|----------|-------|-------|------------|-----------|
| OKP | 1 | `Cose\Key\OkpKey` | `crv` (-1), `x` (-2), `d` (-4) | [RFC 9053 §7.2](https://www.rfc-editor.org/rfc/rfc9053#section-7.2) |
| EC2 | 2 | `Cose\Key\Ec2Key` | `crv` (-1), `x` (-2), `y` (-3), `d` (-4) | [RFC 9053 §7.1.1](https://www.rfc-editor.org/rfc/rfc9053#section-7.1.1) |
| RSA | 3 | `Cose\Key\RsaKey` | `n` (-1), `e` (-2), `d` (-3), `p` (-4), `q` (-5), `dP` (-6), `dQ` (-7), `qInv` (-8), `other` (-9), `r_i` (-10), `d_i` (-11), `t_i` (-12) | [RFC 8230 §4](https://www.rfc-editor.org/rfc/rfc8230#section-4) |
| Symmetric | 4 | `Cose\Key\SymmetricKey` | `k` (-1) | [RFC 9053 §7.3](https://www.rfc-editor.org/rfc/rfc9053#section-7.3) |
| AKP | 7 | `Cose\Key\AkpKey` | `pub` (-1), `priv` (-2) | [RFC 9964 §3](https://www.rfc-editor.org/rfc/rfc9964#section-3) |

An AKP key is a pair of byte strings whose format the algorithm decides, so `alg` is a **required** parameter of the
type (RFC 9964 §3) rather than the optional restriction it is elsewhere; the class accepts a key without it, so that a
map read from the wire can be inspected, and every consumer of the key refuses it. For the ML-DSA algorithms, `pub`
is the encoded public key of FIPS 204 and `priv` the 32-byte seed, with the sizes checked against `alg` when the key
is built; see [ML-DSA](../algorithms/ml-dsa.md).

The curves an `OkpKey` or an `Ec2Key` may carry in `crv`, with the `CURVE_*` constant naming each value:

| Curve | `crv` | Key type | Constant | Reference |
|-------|-------|----------|----------|-----------|
| P-256 | 1 | EC2 | `Ec2Key::CURVE_P256` | [RFC 9053 §7.1](https://www.rfc-editor.org/rfc/rfc9053#section-7.1) |
| P-384 | 2 | EC2 | `Ec2Key::CURVE_P384` | [RFC 9053 §7.1](https://www.rfc-editor.org/rfc/rfc9053#section-7.1) |
| P-521 | 3 | EC2 | `Ec2Key::CURVE_P521` | [RFC 9053 §7.1](https://www.rfc-editor.org/rfc/rfc9053#section-7.1) |
| X25519 | 4 | OKP | `OkpKey::CURVE_X25519` | [RFC 9053 §7.1](https://www.rfc-editor.org/rfc/rfc9053#section-7.1) |
| X448 | 5 | OKP | `OkpKey::CURVE_X448` | [RFC 9053 §7.1](https://www.rfc-editor.org/rfc/rfc9053#section-7.1) |
| Ed25519 | 6 | OKP | `OkpKey::CURVE_ED25519` | [RFC 9053 §7.1](https://www.rfc-editor.org/rfc/rfc9053#section-7.1) |
| Ed448 | 7 | OKP | `OkpKey::CURVE_ED448` | [RFC 9053 §7.1](https://www.rfc-editor.org/rfc/rfc9053#section-7.1) |
| secp256k1 | 8 | EC2 | `Ec2Key::CURVE_P256K` | [RFC 8812 §4.2](https://www.rfc-editor.org/rfc/rfc8812#section-4.2) |
| brainpoolP256r1 | 256 | EC2 | `Ec2Key::CURVE_BP256` | [ISO/IEC 18013-5:2021 §9.1.5.2](https://www.iana.org/assignments/cose/cose.xhtml#elliptic-curves) |
| brainpoolP320r1 | 257 | EC2 | `Ec2Key::CURVE_BP320` | [ISO/IEC 18013-5:2021 §9.1.5.2](https://www.iana.org/assignments/cose/cose.xhtml#elliptic-curves) |
| brainpoolP384r1 | 258 | EC2 | `Ec2Key::CURVE_BP384` | [ISO/IEC 18013-5:2021 §9.1.5.2](https://www.iana.org/assignments/cose/cose.xhtml#elliptic-curves) |
| brainpoolP512r1 | 259 | EC2 | `Ec2Key::CURVE_BP512` | [ISO/IEC 18013-5:2021 §9.1.5.2](https://www.iana.org/assignments/cose/cose.xhtml#elliptic-curves) |

X25519 and X448 are registered "for use w/ ECDH only": they serve the [key agreement](../key-management/README.md) algorithms
and no signature. The Brainpool curves are registered at IANA by ISO/IEC 18013-5 rather than by an RFC (the link
goes to the registry entry) and are compiled out of some OpenSSL builds, see
[Optional extensions](../introduction/pre-requisite.md#optional-extensions). The names a key may carry instead of these numbers are
listed under [Key parameter forms](key-parameter-forms.md).

- [Key parameter forms](key-parameter-forms.md) — the forms a key parameter may take
- [Ed25519 private keys](ed25519-private-keys.md) — the seed, the expanded form, and the public key
- [Key restrictions (`alg` and `key_ops`)](key-restrictions.md) — how a key refuses an algorithm or an
  operation
- [Validating RSA keys](validating-rsa-keys.md) — the modulus, the exponent and the CRT parameters
- [Validating symmetric keys](validating-symmetric-keys.md) — the length the algorithm requires
- [Key thumbprints](key-thumbprints.md) — the COSE Key Thumbprint of RFC 9679
- [Loading a key from a certificate](loading-a-key-from-a-certificate.md) — from an X.509 certificate to
  a COSE key
