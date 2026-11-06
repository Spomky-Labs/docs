# Installation

```bash
composer require spomky-labs/otphp
```

That is all. The library has no service to register, no configuration file and no bundle.

## Requirements

* **PHP 8.1 or later**. The only extension the library calls into is `hash`, which is bundled with PHP
  and cannot be turned off.
* **A PSR-20 clock**, for TOTP. See below.

Three dependencies come with the package, all small:

| Package | What it is for |
|---|---|
| `paragonie/constant_time_encoding` | Base32, encoded and decoded without a timing side channel |
| `psr/clock` | The `ClockInterface` a TOTP reads the time from |
| `symfony/deprecation-contracts` | The function that emits the deprecation notices |

## A clock, for TOTP

A time-based password needs to know what time it is, and the library does not decide that for you: you
pass a [PSR-20](https://www.php-fig.org/psr/psr-20/) clock. **It becomes mandatory in v12.0**, so pass it
now.

```bash
composer require symfony/clock
```

```php
use OTPHP\TOTP;
use Symfony\Component\Clock\NativeClock;

$totp = TOTP::generate(new NativeClock());
```

Any PSR-20 implementation will do; `lcobucci/clock` is another. In your own services, inject the clock
rather than building one where you need it — that is what makes a test able to decide what time it is. See
[The clock](../one-time-passwords/the-clock.md).

HOTP counts uses, not seconds, and needs no clock.

## Checking it works

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', new NativeClock());

echo $totp->now();          // six digits
echo $totp->expiresIn();    // the seconds left before they change
```

`JBSWY3DPEHPK3PXP` is the secret of every example in these pages and in the RFC test vectors. It is
public. Never give it to a real account.
