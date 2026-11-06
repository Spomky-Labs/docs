---
description: 'The post-quantum signatures of RFC 9964: ML-DSA-44, 65 and 87, the AKP key type and the platform gate.'
---

# ML-DSA

[RFC 9964](https://www.rfc-editor.org/rfc/rfc9964.html) registers ML-DSA, the module-lattice signature scheme of
FIPS 204, for COSE, the first post-quantum signature in the registry, together with the key type it is carried
in, AKP (see [Key types](../keys/README.md#key-types)). The three parameter sets live in the `Cose\Algorithm\Signature\MLDSA`
namespace.

| Algorithm | Identifier | Description | Reference |
|-----------|------------|-------------|-----------|
| ML-DSA-44 | -48 | ML-DSA with the FIPS 204 parameter set of security category 2; 1312-byte public key, 2420-byte signature | [RFC 9964 §5](https://www.rfc-editor.org/rfc/rfc9964#section-5) |
| ML-DSA-65 | -49 | ML-DSA with the parameter set of security category 3; 1952-byte public key, 3309-byte signature | [RFC 9964 §5](https://www.rfc-editor.org/rfc/rfc9964#section-5) |
| ML-DSA-87 | -50 | ML-DSA with the parameter set of security category 5; 2592-byte public key, 4627-byte signature | [RFC 9964 §5](https://www.rfc-editor.org/rfc/rfc9964#section-5) |

The three are *pure* ML-DSA (FIPS 204 algorithm 2) with the empty context string, which is all RFC 9964 allows:
HashML-DSA is not registered (§7.2 explains why), and a non-empty `ctx` is forbidden (§5). The private key is the
32-byte seed of FIPS 204 (§4) and nothing else: the expanded private key of FIPS 204 is not a representation the RFC
allows, and `AkpKey` refuses a `priv` of that size.

## Keys

An ML-DSA key is an `AkpKey`: `kty` 7, the **required** `alg` naming the parameter set, `pub` (-1) holding the
encoded public key of FIPS 204 §7.2, and, on the signing side, `priv` (-2) holding the seed. The algorithm expands
a seed into the key pair, which is how a key is generated, from `random_bytes(32)`, and how a stored seed is
turned back into a key:

```php
use Cose\Algorithm\Signature\MLDSA\MLDSA65;
use Cose\Key\AkpKey;
use Cose\Key\Key;

$algorithm = MLDSA65::create();

$key = $algorithm->keyPairFromSeed(random_bytes(32));   // AkpKey: alg -49, pub (1952 bytes), priv (the seed)
$key->pub();                                            // FIPS 204 pkEncode() output
$key->priv();                                           // the 32-byte seed
$key->toPublic();                                       // the same key without "priv"

// The key as it travels, or as a stored credential is rebuilt:
$key = AkpKey::create([
    Key::TYPE => Key::TYPE_AKP,
    Key::ALG => MLDSA65::ID,
    AkpKey::DATA_PUB => $pub,
    AkpKey::DATA_PRIV => $seed,   // omitted on the verifying side
]);
```

`Key::createFromData()` dispatches `kty` 7, as the integer, the `'7'` string cbor-php decodes it to, or the name
`AKP`, to `AkpKey`. `asPEM()` writes the RFC 9881 forms OpenSSL reads: a seed-only PrivateKeyInfo (the `seed [0]`
choice of `ML-DSA-PrivateKey`) for a private key, a SubjectPublicKeyInfo for a public one. `PublicKeyLoader` reads
the SubjectPublicKeyInfo back, from a bare structure or from the certificate a classical CA issued for the key, into
an `AkpKey` carrying the `alg` the OID names. A certificate *signed* with ML-DSA cannot be read yet:
spomky-labs/pki-framework does not know the ML-DSA signature algorithm identifiers.

## Signing and verifying

```php
$signature = $algorithm->sign((string) $toBeSigned, $key);                          // 3309 bytes for ML-DSA-65
$isValid = $algorithm->verify((string) $toBeSigned, $key->toPublic(), $signature);  // bool
```

Signing is randomised (the *hedged* variant of FIPS 204, OpenSSL's default): two signatures over the same input
differ, and both verify.

## What is checked before OpenSSL is called

- `AkpKey` rejects, when the key is built, a `pub` whose length is not the one of the parameter set named by `alg`
  and a `priv` that is not 32 bytes (RFC 9964 §4, §5, §7.3: "the seed length check MUST be performed"). A malformed
  key is therefore refused when it is first seen, as the [verification contract](../signing/the-verification-contract.md)
  promises for every key type.
- The algorithm refuses an AKP key without `alg`: the type says nothing about the algorithm, and §3 makes the
  parameter REQUIRED. It also refuses a key whose `alg` is another parameter set, whether or not the
  [key restrictions](../keys/key-restrictions.md) are enforced: for this key type, `alg` is what `crv` is to
  an EC2 key, not a usage restriction laid over it. With the restrictions enforced, `key_ops` is checked as for any
  algorithm.
- When the key carries both halves, the public key is recomputed from the seed and compared in constant time: a
  mismatched pair (§7.4, whose consequences "can range from operations failing to private key compromise") is
  rejected on both `sign()` and `verify()`.
- A signature of any length other than the table's is invalid (FIPS 204 algorithm 3, step 1): `verify()` returns
  `false` without loading the key.

## The platform gate

ML-DSA is computed by OpenSSL, which ships it in its default provider as of **3.5**, and needs the digest-less
`openssl_sign()` that PHP only offers as of **8.4**. `OPENSSL_VERSION_TEXT` reports the headers PHP was compiled
against, not the library it loaded (a PHP built against 3.0 and running on 3.5 is common), so the OpenSSL check is
a runtime probe: an ML-DSA key is loaded once per process. `MLDSA44::isSupported()`, which the three classes share,
answers for both conditions; `create()` throws a `RuntimeException` naming the missing piece. Register the
algorithms conditionally when the platform is not known in advance:

```php
use Cose\Algorithm\Signature\MLDSA\MLDSA44;
use Cose\Algorithm\Signature\MLDSA\MLDSA65;
use Cose\Algorithm\Signature\MLDSA\MLDSA87;

if (MLDSA44::isSupported()) {
    $manager->add(MLDSA44::create(), MLDSA65::create(), MLDSA87::create());
}
```

The thumbprint of an AKP key is computed over `kty`, `alg` and `pub` (RFC 9964 §6), see
[Key thumbprints](../keys/key-thumbprints.md). [`examples/16-ml-dsa.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/16-ml-dsa.php) reproduces the
COSE example of RFC 9964 Appendix A, thumbprint included, and signs a COSE_Sign1 with a fresh key.
