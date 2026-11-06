---
description: 'Installing COSE with Composer, the CBOR package the message classes come from, and the versions that receive fixes.'
---

# Installation

```bash
composer require web-auth/cose-lib
```

The library is distributed on [Packagist](https://packagist.org/packages/web-auth/cose-lib); the source
lives on [GitHub](https://github.com/web-auth/cose-lib).

## The CBOR package

The COSE message classes, `CBOR\Tag\CoseSign1Tag` and its siblings, come from
[spomky-labs/cbor-php](https://github.com/Spomky-Labs/cbor-php), a suggestion of this package rather than
a hard requirement. Every application that reads or writes a COSE message needs it:

```bash
composer require "spomky-labs/cbor-php:^3.4"
```

3.4.0 is the floor this library declares (`conflict: <3.4.0`). Two things come from there rather than from
here. The CBOR decoder enforces the header-map rules of
[RFC 9052](https://datatracker.ietf.org/doc/html/rfc9052): a label appearing twice in a map makes the
message malformed ([§3](https://datatracker.ietf.org/doc/html/rfc9052#section-3),
[§9](https://datatracker.ietf.org/doc/html/rfc9052#section-9)), and nesting is bounded so that a crafted
header cannot exhaust the memory of the process. And, since 3.4.0, the six COSE message classes
themselves. Nothing in this library re-checks either rule.

## Performance

**ext-gmp** (recommended) or **ext-bcmath** is worth installing, but no longer required for RSA
verification to be cheap: `RsaKey::asPem()`, `RsaKeyValidator` and the public operation of every RSA
algorithm are computed without `brick/math`. Signing with RSASSA-PSS (`PS256`, `PS384`, `PS512`) still
uses it for the blinding of the private exponentiation, and falls back to a pure PHP calculator when
neither extension is loaded, which is the configuration of the stock `php` and `php-fpm` Docker images.

PS256, PS384 and PS512 sign with a private key, so the exponentiation is a side-channel target. A
two-prime key carrying the full CRT quintuple (the shape almost every key store produces) is exponentiated
by OpenSSL, which blinds the base and runs `BN_mod_exp_mont_consttime`. Its CRT parameters are checked
against the modulus first, so an inconsistent key is reported rather than silently repaired. Multi-prime
keys ([RFC 8230 §4](https://www.rfc-editor.org/rfc/rfc8230#section-4)) and keys reduced to `(n, e, d)`
have no PEM representation and keep the in-process exponentiation; their base is blinded, which hides it
from an observer, but `gmp_powm()`, `bcpowmod()` and the native brick/math loop are not constant-time, so
prefer a full two-prime key when signing with a long-lived key on a shared host.

## Running the test suite

In the project QA container (nothing to install):

```bash
castor phpunit
```

Or directly, on a host that provides PHPUnit 11 as `phpunit-11`:

```bash
composer test
```

The suite covers every algorithm against the published vectors of its primitive, the structures against
the RFC 9052 Appendix C vectors, the EU digital COVID certificate flow, every program of
[`examples/`](https://github.com/web-auth/cose-lib/tree/HEAD/examples), and the interoperability fixtures
of the IETF COSE working group, [cose-wg/Examples](https://github.com/cose-wg/Examples), vendored under
[`tests/fixtures/cose-wg/`](https://github.com/web-auth/cose-lib/tree/HEAD/tests/fixtures/cose-wg). Every
fixture this library has an algorithm for is decoded, rebuilt into its `Sig_structure`, `MAC_structure` or
`Enc_structure`, compared with the bytes the working group's generator produced, verified or decrypted,
and produced again; the fixtures the generator broke on purpose are asserted to be rejected. Fixtures for
algorithms the library does not implement (the three RSAES-OAEP ones) are reported as skipped with the
identifier, so `phpunit --display-skipped` lists what is left.

## The versions that receive fixes

The maintained branches are listed in
[`RELEASES.md`](https://github.com/web-auth/cose-lib/blob/HEAD/RELEASES.md#minor-release-support-matrix),
which the [security policy](https://github.com/web-auth/cose-lib/security/policy) refers to rather than
restating. The version selector at the top of this site carries one entry per documented line.
