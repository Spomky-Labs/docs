---
description: One-time passwords for PHP, after RFC 6238 and RFC 4226.
---

# OTPHP

**OTPHP** computes and checks one-time passwords: the six digits an authenticator application shows your
users for a second factor.

It implements both algorithms the specifications define. `TOTP` is time-based
([RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238)) and is what almost every service uses. `HOTP`
is counter-based ([RFC 4226](https://datatracker.ietf.org/doc/html/rfc4226)), the algorithm TOTP is built
on. The codes are read by Google Authenticator, FreeOTP, Aegis, 1Password and the others.

```php
use OTPHP\TOTP;

// Enrolment: one secret per account, stored with the account.
$totp = TOTP::generate($clock)
    ->withLabel('alice@example.com')
    ->withIssuer('My Service');

$user->setOtpSecret($totp->getSecret());
$uri = $totp->getProvisioningUri(); // the content of the QR code the user scans
```

```php
use OTPHP\TOTP;

// Sign-in: the code the user typed, against the secret you stored.
$totp = TOTP::createFromSecret($user->getOtpSecret(), $clock);

if (! $totp->verify($code)) {
    throw new BadCredentialsException('Wrong code.');
}
```

## One package

```bash
composer require spomky-labs/otphp
```

It needs PHP 8.1 or later and nothing else of consequence: a Base32 codec, the `psr/clock` interface, and
the deprecation contracts. No framework, no container, no database.

## What it does not do

It does the arithmetic and nothing around it. Storing secrets, rendering QR codes, rate-limiting attempts
and remembering which codes were already used are your application's work, and
[Security recommendations](the-project/security-recommendations.md) says what that work is. A library that
only hands you the right digits cannot protect an account on its own.

## Where to start

* [Installation](the-project/installation.md) to try it now.
* [TOTP or HOTP?](one-time-passwords/totp-or-hotp.md) if you are not sure which one you want. You almost
  certainly want TOTP.
* [What to store](in-your-application/what-to-store.md) before you design your table. Storing the secret
  alone will cost you the day you change the number of digits.
* [Security recommendations](the-project/security-recommendations.md) before you ship.
