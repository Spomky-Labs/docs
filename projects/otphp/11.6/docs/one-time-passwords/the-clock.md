# The clock

A time-based password is a function of the current time, so a `TOTP` needs to know what the current time
is. It does not call `time()`: it reads a [PSR-20](https://www.php-fig.org/psr/psr-20/) `ClockInterface`
you give it.

```php
use OTPHP\TOTP;
use Symfony\Component\Clock\NativeClock;

$totp = TOTP::generate(new NativeClock());
```

A HOTP counts uses rather than seconds and takes no clock at all.

## Pass it everywhere a TOTP is built

Four entry points accept it, and all four are optional today:

```php
new TOTP($secret, $clock);
TOTP::generate($clock, $secretSize);
TOTP::createFromSecret($secret, $clock);
Factory::loadFromProvisioningUri($uri, $clock);
```

Omitting it triggers a deprecation notice and falls back to the library's own clock. **In v12.0 it becomes
mandatory**, and omitting it will be a `TypeError`. Pass it now; the deprecation notice reads:

```text
The parameter "$clock" will become mandatory in 12.0.0.
Please set a valid PSR Clock implementation instead of "null".
```

Finding the places that still omit it:

```bash
grep -rn 'TOTP::generate()\|TOTP::createFromSecret(\|new TOTP(\|loadFromProvisioningUri(' --include='*.php' src/
```

## Which implementation

Any PSR-20 one. `symfony/clock` and `lcobucci/clock` both provide one, and a project that already has
either needs nothing more:

```bash
composer require symfony/clock
```

```php
use Symfony\Component\Clock\NativeClock;

$clock = new NativeClock();
```

Inject it into your own services instead of constructing it where you need it. That one habit is what
makes the next section possible.

!!! warning "`OTPHP\InternalClock` is not for your code"

    The library ships a minimal `ClockInterface` and uses it as the fallback when you pass `null`. It is
    marked `@internal`, which puts it outside the backwards compatibility policy: it may change or
    disappear in a minor release. Depend on a clock from your application, not on that class.

## Deciding what time it is, in a test

This is the reason the clock is an argument. With a fixed clock, a TOTP becomes a pure function and its
code becomes an assertable value:

```php
use OTPHP\TOTP;
use Symfony\Component\Clock\MockClock;

// 1519401289 is 2018-02-23 15:54:49 UTC. A timestamp leaves no room for a timezone to surprise you.
$clock = new MockClock(new DateTimeImmutable('@1519401289'));
$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock);

self::assertSame('626112', $totp->now());

$clock->sleep(30);
self::assertSame('567611', $totp->now());
```

The same trick tests the parts that are otherwise awkward: a code at the very end of its period, a device
whose clock drifts by twenty seconds, [a window](the-window.md) that is too wide.

The epoch is the other half of this. It shifts where periods begin, and is covered in
[The period and the epoch](../the-parameters/the-period-and-the-epoch.md).
