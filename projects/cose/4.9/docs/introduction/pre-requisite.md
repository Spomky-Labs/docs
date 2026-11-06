---
description: 'The PHP version and the extensions COSE needs, and the ones that decide which algorithms a platform can run.'
---

# Prerequisites

## PHP and required extensions

- PHP 8.1 or higher
- ext-json
- ext-openssl
- [brick/math](https://github.com/brick/math)
- [spomky-labs/pki-framework](https://github.com/Spomky-Labs/pki-framework) `^1.6.2`, the only supported
  line of that package; its release notes close 27 security advisories affecting `<= 1.6.1` and declare
  `1.0.x` through `1.5.x` end of life
- [spomky-labs/aes-key-wrap](https://github.com/Spomky-Labs/aes-key-wrap) `^7.0`, the AES Key Wrap of
  RFC 3394, for the `A128KW`/`A192KW`/`A256KW` and `ECDH-*+A*KW` algorithms; it requires ext-mbstring

[spomky-labs/cbor-php](https://github.com/Spomky-Labs/cbor-php) `^3.4` is a suggestion rather than a
requirement, and every application that reads or writes a COSE message needs it; see
[Installation](installation.md#the-cbor-package).

## Optional extensions

Depending on what you use:

- **ext-sodium**: required by every Ed25519 algorithm (`EdDSA` -8, `Ed25519` -8 and -19, `Ed256` -260,
  `Ed512` -261) and to recompute an OKP public key from its private key. Sodium ships with PHP and is
  enabled by default, but a build can leave it out: creating one of these algorithms then throws a
  `RuntimeException` instead of reporting valid signatures as invalid. Call `EdDSA::isSupported()` when
  the platform is not known in advance.
- **ext-gmp** or **ext-bcmath**: see [Performance](installation.md#performance).

## The algorithms that depend on the platform

Some algorithms depend on the platform beyond the extensions, and each says so through a static
`isSupported()`:

| Algorithm | Needs | Check |
|---|---|---|
| `Ed448` (-53) | PHP 8.4 or later: Ed448 is not covered by sodium and PHP only wires OpenSSL up for Edwards curves as of 8.4 | `Ed448::isSupported()` |
| `MLDSA44` (-48), `MLDSA65` (-49), `MLDSA87` (-50) | PHP 8.4 or later **and** OpenSSL 3.5 or later loaded at runtime; the check probes the library actually loaded, not the headers PHP was built against; see [ML-DSA](../algorithms/ml-dsa.md#the-platform-gate) | `MLDSA44::isSupported()` (one gate for the three) |
| `ESB256`, `ESB320`, `ESB384`, `ESB512` | An OpenSSL build with the Brainpool curves; they are compiled out of some builds and of every FIPS provider | `ESB256::isSupported()` (each class) |
| The eight AES-CCM algorithms | An OpenSSL build with AES-CCM | `A128CCM_16_64::isSupported()` (any of the eight) |
| `ChaCha20Poly1305` (24) | The sodium extension, or OpenSSL's `chacha20-poly1305` | `ChaCha20Poly1305::isSupported()` |
| `SHAKE128` (-18), `SHAKE256` (-45) | A 64-bit build of PHP, the Keccak sponge being computed in PHP | `SHAKE128::isSupported()` |
| ECDH on a Brainpool curve | Same OpenSSL build as `ESB*` | `EllipticCurveDiffieHellman::isCurveSupported()` |

`create()` throws a `RuntimeException` naming what is missing on a platform without it. A registry that
has to work on an unknown platform guards those registrations:

```php
use Cose\Algorithm\Manager;
use Cose\Algorithm\Signature\FullySpecified\ESB256;
use Cose\Algorithm\Signature\FullySpecified\ESB320;
use Cose\Algorithm\Signature\FullySpecified\ESB384;
use Cose\Algorithm\Signature\FullySpecified\ESB512;

$manager = Manager::create();
foreach ([ESB256::class, ESB320::class, ESB384::class, ESB512::class] as $brainpool) {
    if ($brainpool::isSupported()) {
        $manager->add($brainpool::create());
    }
}
```
