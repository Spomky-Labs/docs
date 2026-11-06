---
description: 'The forms a COSE key parameter may take, and what the library accepts.'
---

# Key parameter forms

RFC 9052 and RFC 9053 type `kty` and `crv` as `tstr / int`, so the same key reaches this library under several
shapes. The `Key` classes settle them all at construction time:

- a key type or a curve given as the numeric string spomky-labs/cbor-php produces when it decodes a CBOR integer
  (`'2'`, `'-1'`) is stored as the integer it denotes, so `Key::type()` always compares equal to `Key::TYPE_EC2` and
  friends, whether the key was decoded from CBOR or built by hand;
- a key type may also be given by name: the names of the IANA
  [COSE Key Types](https://www.iana.org/assignments/cose/cose.xhtml#key-type) registry, `OKP`, `EC2`, `RSA`,
  `Symmetric` and `AKP`, or the JOSE spellings `EC` and `oct` a key converted from a JWK carries. `Key::typeIs(Key::TYPE_EC2)`
  answers for every form, while `type()` keeps returning the form supplied;
- a curve may be given by name: `P-256`, `P-384`, `P-521`, `secp256k1`, `brainpoolP256r1` and so on. `curve()`
  returns the form the key carries, and `Ec2Key::curveId()` / `OkpKey::curveId()` return the value of the IANA
  [COSE Elliptic Curves](https://www.iana.org/assignments/cose/cose.xhtml#elliptic-curves) registry whatever that
  form is. The algorithm classes compare the latter, so a key that names its curve signs and verifies exactly like
  the same key that numbers it.

```php
use Cose\Key\Ec2Key;

$key = Ec2Key::create([
    Ec2Key::TYPE => Ec2Key::TYPE_EC2,
    Ec2Key::DATA_CURVE => Ec2Key::CURVE_NAME_SECP256K1, // or Ec2Key::CURVE_P256K
    Ec2Key::DATA_X => $x,
    Ec2Key::DATA_Y => $y,
]);

$key->curve();   // 'secp256k1', as supplied
$key->curveId(); // 8, the registry value
```

Curve 8 is named `secp256k1` by [RFC 8812, section 4.2](https://datatracker.ietf.org/doc/html/rfc8812#section-4.2).
`Ec2Key::CURVE_NAME_P256K` (`'P-256K'`), the spelling of a draft that was renamed before its first revision, is
deprecated but still accepted.

- the `y` of an `Ec2Key` may be a boolean: the *sign bit* of the compressed point encoding that
  [RFC 9053 §7.1.1](https://www.rfc-editor.org/rfc/rfc9053#section-7.1.1) allows for a public key: "if the sign
  bit is zero, then encode y as a CBOR false value; otherwise, encode y as a CBOR true value", the sign bit being
  the parity of `y` (SEC 1 §2.3.3). The point is decompressed when the key is built: the square root of
  x³ + ax + b modulo the field prime, a single modular exponentiation since every supported curve has p ≡ 3 (mod 4),
  checked against the curve equation so that an `x` on no point of the curve is refused. `y()`,
  `getUncompressedCoordinates()` and `asPEM()` return the coordinate; `getData()` keeps the boolean, so that the map
  round-trips unchanged. All eight curves of the table above are supported, and `PublicKeyLoader` reads a compressed
  `subjectPublicKey` (`0x02` / `0x03`, RFC 5480 §2.2) the same way, handing back a key that carries the uncompressed
  point.

```php
use Cose\Key\Ec2Key;

$key = Ec2Key::create([
    Ec2Key::TYPE => Ec2Key::TYPE_EC2,
    Ec2Key::DATA_CURVE => Ec2Key::CURVE_P256,
    Ec2Key::DATA_X => $x,
    Ec2Key::DATA_Y => true, // the sign bit: y is odd
]);

$key->y();                 // the 32-byte coordinate, decompressed
$key->get(Ec2Key::DATA_Y); // true, as supplied
```

Anything else (a float, a numeric string that is not an integer, a name no registry defines, an `x` that is not a
byte string, a sign bit that names no point of the curve) is refused by the constructor with an
`InvalidArgumentException`, before any of it is used.
