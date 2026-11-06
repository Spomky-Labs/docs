---
description: 'How a key that declares its own alg and key_ops refuses an algorithm or an operation.'
---

# Key restrictions (`alg` and `key_ops`)

A COSE key may restrict itself. [RFC 9052, section 7.1](https://www.rfc-editor.org/rfc/rfc9052.html#section-7.1) gives
it two parameters for that: `alg` (label 3) pins it to one algorithm ("If the algorithms do not match, then this key
object MUST NOT be used to perform the cryptographic operation") and `key_ops` (label 4) pins it to a set of
operations, whose values are those of Table 5: `sign` (1), `verify` (2), `encrypt` (3), `decrypt` (4), `wrap key`
(5), `unwrap key` (6), `derive key` (7), `derive bits` (8), `MAC create` (9) and `MAC verify` (10) for the algorithms
this library implements. [RFC 9053](https://www.rfc-editor.org/rfc/rfc9053.html#section-2.1) repeats both as a
per-algorithm requirement for ECDSA (§2.1), EdDSA (§2.2), HMAC (§3.1), AES-CBC-MAC (§3.2), the content encryption
algorithms (§4.1 to §4.3) and the key management algorithms (§6).

For the signature and MAC algorithms, enforcing them is **opt-in**, so that a key which used to work keeps working.
Ask an algorithm, or a whole `Manager`, to enforce the restrictions, and it refuses the key with an
`InvalidArgumentException` whenever the key forbids what is being done with it. The
[content encryption](../algorithms/content-encryption-algorithms.md) and
[key management](../key-management/key-restrictions.md) algorithms, which have no such history, enforce them from the
start and take `withKeyRestrictionsEnforced(false)` to stop:

```php
use Cose\Algorithm\Manager;
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Algorithm\Signature\RSA\RS256;

$algorithm = ES256::create()->withKeyRestrictionsEnforced();

// …or for every algorithm of a manager at once
$manager = Manager::create()
    ->add(ES256::create(), RS256::create())
    ->withKeyRestrictionsEnforced();

// The key says "alg": -7 and "key_ops": [2], i.e. ES256, verification only
$isValid = $algorithm->verify($data, $key, $signature); // fine
$signature = $algorithm->sign($data, $key);             // InvalidArgumentException: the key does not allow "sign"
```

`withKeyRestrictionsEnforced()` returns a new algorithm and leaves the one it is called on untouched, so a manager
that enforces the restrictions can live next to one that does not. `enforcesKeyRestrictions()` says which one you are
holding, and `withKeyRestrictionsEnforced(false)` turns it off again.

This matters when the algorithm is chosen from the message rather than from the key. A verifier that reads `alg` from
the protected header and looks it up with `Manager::get()` has, without enforcement, no reason to refuse an RS1
(RSASSA-PKCS1-v1_5 with SHA-1) signature made under a key that says it is for RS256, nor a 64 bit HMAC tag under a key
that says it is for HMAC 256/256. With enforcement, the key itself rejects the downgrade.

The restrictions can also be read and applied without going through an algorithm:

```php
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Key\Key;

$key->alg();    // -7; throws when "alg" is absent or is not an algorithm identifier
$key->keyOps(); // [2] or ['verify'], null when the key carries no "key_ops"

// Throws an InvalidArgumentException naming the restriction that is not satisfied
$key->assertUsableWith(ES256::ID, Key::OP_VERIFY);

// …or ask without the exception
$isUsable = $key->isUsableWith(ES256::ID, Key::OP_SIGN);
```

Three details are worth knowing:

- **Identifiers are compared as they are.** A key with `alg` = `ES256` (-7) is refused by `ESP256` (-9), and one with
  `alg` = `EdDSA` (-8) is refused by the fully-specified `Ed25519` (-19), even though the cryptography is the same.
  [RFC 9864, section 7](https://www.rfc-editor.org/rfc/rfc9864.html#section-7) asks for it: "A cryptographic key MUST
  be used with only a single algorithm unless the use of the same key with different algorithms is proven secure."
  A key meant to serve both carries no `alg` at all.
- **`key_ops` accepts both spellings.** COSE writes the operations as the integers of Table 5; a key converted from a
  JWK may carry the text names JOSE uses (`"sign"`, `"verify"`, `"MAC create"`, `"MAC verify"`). Both are recognised.
- **An operation may go by two names.** RFC 9053 §4 lets a content encryption key list `encrypt` *or* `wrap key` to
  encrypt, and `decrypt` *or* `unwrap key` to decrypt. `Key::assertUsableWithAny($alg, Key::OP_ENCRYPT, Key::OP_WRAP_KEY)`
  passes on either and fails naming both; `assertUsableWith()` is its single-operation form.

`Key::alg()` is strict about the value it reads: an `alg` that is not an integer, the text `'RS256'` for instance,
throws instead of being cast to `0`, an identifier no algorithm is registered under. An integer written as a string
(`'-7'`) is accepted, as the key constructors do for `kty` and `crv`.
