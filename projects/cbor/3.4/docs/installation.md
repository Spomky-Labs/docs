---
description: The package, the versions of PHP it supports and the extensions worth installing
---

# Installation

```bash
composer require spomky-labs/cbor-php
```

In a Symfony application, take [the bundle](bundle/installation.md) instead: it brings this library with
it, registers its services and adds CBOR to the Serializer.

## What it needs

-   PHP 8.0 or later
-   `ext-mbstring`
-   [`brick/math`](https://github.com/brick/math), installed by Composer

## What is worth adding

-   **`ext-gmp`** — big integers, and the big number tags that rest on them, are computed far faster.
    Install it when the data you decode comes from somewhere you do not control: see
    [the cost of a hostile document](guide/decoding.md#the-cost-of-a-hostile-document).
-   **`ext-bcmath`** — required by the decimal fraction and bigfloat tags
    ([tags 4 and 5](tags/built-in.md#fractional-numbers)). `ext-gmp` also serves as a calculator for
    `brick/math`, but these two tags ask for `bcmath` itself.

## Versions

The library follows [semantic versioning](https://semver.org/) strictly, and keeps release branches for
the most recent minor releases. Which ones are supported today is stated in
[RELEASES.md](https://github.com/Spomky-Labs/cbor-php/blob/HEAD/RELEASES.md); how a security report is
handled, in [SECURITY.md](https://github.com/Spomky-Labs/cbor-php/blob/HEAD/SECURITY.md).

This site publishes one version of the documentation per supported branch. The selector in the header
switches between them.
