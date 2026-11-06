---
description: Installing PKI Framework with Composer, and the versions that receive fixes.
---

# Installation

The library is distributed on
[Packagist](https://packagist.org/packages/spomky-labs/pki-framework); the source lives on
[GitHub](https://github.com/Spomky-Labs/pki-framework).

```bash
composer require spomky-labs/pki-framework
```

There is no bundle, no configuration file and no service to register. Every class is constructed through
a static factory — `create()`, `fromPEM()`, `fromDER()`, `fromASN1()` — and nothing is read from the
environment.

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\X509\Certificate\Certificate;

require 'vendor/autoload.php';

$certificate = Certificate::fromPEM(PEM::fromFile('server.crt'));
```

Everything lives under the `SpomkyLabs\Pki` namespace, autoloaded with PSR-4 from `src/`.

## Versions

A release line is named `1.x`, maintained on a branch named `1.x.x`. **Only the latest stable line
receives fixes, security fixes included**, and nothing is backported to an older one: upgrade before you
report a problem. The lines currently maintained are listed in
[`SECURITY.md`](https://github.com/Spomky-Labs/pki-framework/blob/HEAD/SECURITY.md).

This documentation is published once per maintained line. The version selector in the header of the site
switches between them, and the root of the site leads to the newest one.

## Reporting a vulnerability

**Do not open a public issue, pull request or discussion for a security problem.** Report it privately,
either through
[GitHub private vulnerability reporting](https://github.com/Spomky-Labs/pki-framework/security/advisories/new)
or by email to `security AT spomky-labs.com`. What a report should contain, and what happens next, are in
the [security policy](https://github.com/Spomky-Labs/pki-framework/security/policy).
