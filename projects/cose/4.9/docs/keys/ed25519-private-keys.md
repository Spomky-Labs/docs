---
description: 'The seed, the expanded form, and recomputing the public key from the private one.'
---

# Ed25519 private keys

[RFC 8032, section 5.1.5](https://www.rfc-editor.org/rfc/rfc8032#section-5.1.5) defines the Ed25519 public key `A` as a
function of the private seed, and [section 5.1.6](https://www.rfc-editor.org/rfc/rfc8032#section-5.1.6) puts that `A`
into the challenge the signature is built on. `sign()` therefore always recomputes the key pair from `d` and never
signs under a public key handed to it: a `-2` (`x`) that contradicts `d` is refused with an
`InvalidArgumentException`, because signing under two different `x` values for one seed discloses the private key.

[RFC 9053, section 7.2](https://www.rfc-editor.org/rfc/rfc9053#section-7.2) makes `x` RECOMMENDED, not REQUIRED, for a
private key, "it can be recomputed from the required elements", so an `OkpKey` may carry `crv` and `d` alone. That is
the safest way to build a signing key, since nothing can then hand it an `x` inconsistent with the seed:

```php
use Cose\Algorithm\Signature\EdDSA\Ed25519;
use Cose\Key\OkpKey;

$key = OkpKey::create([
    OkpKey::TYPE => OkpKey::TYPE_OKP,
    OkpKey::DATA_CURVE => OkpKey::CURVE_ED25519,
    OkpKey::DATA_D => $seed, // 32 bytes, RFC 8032 section 5.1.5
]);

$signature = Ed25519::create()->sign($data, $key);
$publicKey = $key->x();          // recomputed from $seed
$publicCoseKey = $key->toPublic(); // carries the recomputed x, without d
```

`x()` recomputes the public key for the curves sodium covers, Ed25519 and X25519. Ed448 and X448 have no derivation
primitive in PHP, so a key on those curves still has to carry its `x`.
