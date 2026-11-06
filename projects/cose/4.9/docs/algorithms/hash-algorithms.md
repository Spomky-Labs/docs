---
description: 'The hash algorithms of RFC 9054, a registry of their own, and the SHAKE sponges.'
---

# Hash algorithms

The hash algorithms of [RFC 9054](https://www.rfc-editor.org/rfc/rfc9054.html), in `Cose\Algorithm\Hash`. COSE
names a hash by one of these identifiers wherever a digest travels in a message: the `x5t` header parameter of
[RFC 9360](https://www.rfc-editor.org/rfc/rfc9360.html) carries `[hashAlg, hashValue]`, the COSE Key Thumbprint of
[RFC 9679](https://www.rfc-editor.org/rfc/rfc9679.html) is computed with one, and so is the hash envelope of
[RFC 9995](https://www.rfc-editor.org/rfc/rfc9995.html).

| Algorithm | Identifier | Class | Digest | IANA recommendation | Reference |
|-----------|------------|-------|--------|---------------------|-----------|
| SHA-1 | -14 | `SHA1` | 20 bytes | Filter Only | [RFC 9054 §3.1](https://www.rfc-editor.org/rfc/rfc9054#section-3.1) |
| SHA-256/64 | -15 | `SHA256_64` | 8 bytes, SHA-256 truncated | Filter Only | [RFC 9054 §3.2](https://www.rfc-editor.org/rfc/rfc9054#section-3.2) |
| SHA-256 | -16 | `SHA256` | 32 bytes | Yes | [RFC 9054 §3.2](https://www.rfc-editor.org/rfc/rfc9054#section-3.2) |
| SHA-512/256 | -17 | `SHA512_256` | 32 bytes, a distinct SHA-2 function, not SHA-512 truncated | Yes | [RFC 9054 §3.2](https://www.rfc-editor.org/rfc/rfc9054#section-3.2) |
| SHAKE128 | -18 | `SHAKE128` | 32 bytes | Yes | [RFC 9054 §3.3](https://www.rfc-editor.org/rfc/rfc9054#section-3.3) |
| SHA-384 | -43 | `SHA384` | 48 bytes | Yes | [RFC 9054 §3.2](https://www.rfc-editor.org/rfc/rfc9054#section-3.2) |
| SHA-512 | -44 | `SHA512` | 64 bytes | Yes | [RFC 9054 §3.2](https://www.rfc-editor.org/rfc/rfc9054#section-3.2) |
| SHAKE256 | -45 | `SHAKE256` | 64 bytes | Yes | [RFC 9054 §3.3](https://www.rfc-editor.org/rfc/rfc9054#section-3.3) |

Every class has `create()`, `identifier()`, `hash(string $data): string`, the digest as raw bytes, and
`length(): int`, the number of bytes `hash()` returns.

```php
use Cose\Algorithm\Hash\SHA256;
use Cose\Algorithm\Hash\SHAKE256;
use Cose\Algorithm\Manager;

$digest = SHA256::create()->hash($certificateDer); // 32 bytes: the value of an x5t [-16, h'…']

// A hash registers in a Manager like any other algorithm, so an identifier read from a message resolves to it
$manager = Manager::create()->add(SHA256::create(), SHAKE256::create());
$algorithm = $manager->get(-16);
```

The two maps of `Algorithms` (`COSE_ALGORITHM_MAP`, `COSE_HASH_MAP`) still describe signature identifiers only: they
answer "which digest does OpenSSL sign with", which SHA-256/64 and the SHAKE functions have no answer to. A hash
identifier resolves through a `Manager`.

## Filter only, as a type

[RFC 9054 §2](https://www.rfc-editor.org/rfc/rfc9054#section-2) distinguishes two uses of a hash function.
*Filtering* is picking, among a collection of certificates or keys, the candidates whose fingerprint matches, after
which each candidate is still checked for real, by verifying the signature with its key, so a collision costs
nothing. Using the digest *as an integrity primitive*, where it stands for the data, needs collision resistance.
SHA-1 has a published collision and SHA-256/64 keeps 64 bits: both are fine for the first use and not for the
second, which the IANA registry records with the recommendation *Filter Only*.

The library records it in the type system rather than with a runtime flag:

- `Cose\Algorithm\Hash\FilterOnlyHash` is implemented by all eight algorithms;
- `Cose\Algorithm\Hash\Hash` extends it and is implemented by the six IANA recommends: `SHA256`, `SHA512_256`,
  `SHAKE128`, `SHA384`, `SHA512`, `SHAKE256`.

A parameter typed `Hash` therefore refuses `SHA1` and `SHA256_64` (PHPStan and Psalm report it, and PHP throws a
`TypeError` at the call) while a parameter typed `FilterOnlyHash` accepts all eight. Type the parameter after
what the digest is used for:

```php
use Cose\Algorithm\Hash\FilterOnlyHash;
use Cose\Algorithm\Hash\Hash;
use Cose\Algorithm\Hash\SHA1;
use Cose\Algorithm\Hash\SHA256;

/** Which of these certificates might be the one the thumbprint names? Each is verified afterwards. */
function candidates(FilterOnlyHash $hash, string $thumbprint, array $certificates): array
{
    return array_filter($certificates, static fn (string $der): bool => hash_equals($thumbprint, $hash->hash($der)));
}

/** The digest stands for the data: nothing checks it afterwards. */
function commitment(Hash $hash, string $data): string
{
    return $hash->hash($data);
}

candidates(SHA1::create(), $thumbprint, $certificates);   // accepted
commitment(SHA256::create(), $data);                      // accepted
commitment(SHA1::create(), $data);                        // rejected by PHPStan/Psalm; TypeError at runtime
```

Compare a digest with `hash_equals()`, as above, never with `===`.

Two names look like truncations and only one is: **SHA-256/64** is SHA-256 cut to its first 8 bytes, defined by
RFC 9054 itself; **SHA-512/256** is a SHA-2 function of its own (FIPS 180-4 §5.3.6), run with initial values that
differ from SHA-512's, so its digest shares nothing with the first 32 bytes of a SHA-512.

## SHAKE128 and SHAKE256

PHP has no SHAKE primitive: `hash_algos()` lists the fixed-length `sha3-*` functions only, and `openssl_digest()`
can neither set the output length of an extendable-output function nor, on the OpenSSL 3 builds checked, produce one.
The two classes therefore compute the Keccak sponge of FIPS 202 in PHP (`Cose\Algorithm\Hash\Keccak`, internal),
which is checked against PHP's own `sha3-256` and against the NIST example vectors in the test suite. A certificate
or a key is a few hundred bytes, so the cost is negligible. The sponge works on 64-bit integers:
`SHAKE128::isSupported()` and `SHAKE256::isSupported()` are `false` on a 32-bit build, where `hash()` throws a
`RuntimeException`.

RFC 9054 registers no identifier for other output lengths: SHAKE128 (-18) always yields 32 bytes and SHAKE256 (-45)
64 bytes.

[`examples/11-hash-algorithms.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/11-hash-algorithms.php) runs the eight identifiers, a certificate
thumbprint as `x5t` carries it, and the *Filter Only* type.
