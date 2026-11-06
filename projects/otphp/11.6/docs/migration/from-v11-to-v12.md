# From v11 to v12

Three changes. One has already landed, in v11.5; the other two are deprecations in v11.4 that become
breaking in v12.0. All three can be dealt with today, on v11, which is the point of this page.

| Change | Lands in | Impact |
|---|---|---|
| Digests shorter than 19 bytes are refused | **v11.5** | Only configurations using one, such as `md5` |
| The `set*()` methods go, classes become `readonly` | v12.0 | High, if you use setters |
| The PSR-20 clock becomes mandatory for TOTP | v12.0 | High, for every TOTP |

Upgrading to the latest v11 with no deprecation notices left means v12.0 will be a version bump and
nothing more.

## Short digests are refused, since v11.5

This one is already in effect, and it is a security fix, not a deprecation. A digest shorter than 19 bytes
is rejected by both entry points:

```php
// Direct configuration
TOTP::generate($clock)->withDigest('md5');
// InvalidParameterException

// A provisioning URI
Factory::loadFromProvisioningUri(
    'otpauth://totp/Foo%3Aalice%40example.com?algorithm=md5&secret=JDDK4U6G3BJLEZ7Y',
    $clock
);
// InvalidProvisioningUriException
```

**Why.** The RFC 4226 truncation reads four bytes at an offset between 0 and 15 — up to the 19th byte of
the digest. With a 16-byte hash it reads past the end, and the code collapses onto a small set of values
that barely depend on the secret. That is a real weakness in the verification path. Such algorithms are
also outside RFC 4226 and RFC 6238, and no authenticator application reads them.

The validation now uses `hash_hmac_algos()` rather than `hash_algos()`, which additionally rejects
non-HMAC algorithms such as `crc32` and `adler32`. Those used to pass validation and then fail inside
`hash_hmac()`.

**What to do.** Move to a supported digest:

```php
// Before
$totp = $totp->withDigest('md5');

// After
$totp = $totp->withDigest('sha256');
```

Accounts provisioned with `md5` were never safe and never interoperable. **They must be re-enrolled**;
their secrets cannot simply be re-labelled with a new algorithm, because the codes would change. See
[The digest and the digits](../the-parameters/the-digest-and-the-digits.md).

## The setters go, and the classes become `readonly`

Every `set*()` method is deprecated since v11.4 and **removed in v12.0**. Each has an immutable twin that
returns a new object instead of mutating the one you hold.

| Deprecated | Replacement |
|---|---|
| `setSecret(string): void` | `withSecret(string): self` |
| `setDigits(int): void` | `withDigits(int): self` |
| `setDigest(string): void` | `withDigest(string): self` |
| `setLabel(string): void` | `withLabel(string): self` |
| `setIssuer(string): void` | `withIssuer(string): self` |
| `setIssuerIncludedAsParameter(bool): void` | `withIssuerIncludedAsParameter(bool): self` |
| `setParameter(string, mixed): void` | `withParameter(string, mixed): self` |
| `setPeriod(int): void` (TOTP) | `withPeriod(int): self` |
| `setEpoch(int): void` (TOTP) | `withEpoch(int): self` |
| `setCounter(int): void` (HOTP) | `withCounter(int): self` |

```php
use OTPHP\TOTP;

// v11.3 and earlier
$totp = TOTP::generate($clock);
$totp->setLabel('alice@example.com');
$totp->setIssuer('My Service');
$totp->setDigits(8);

// v11.4 and later
$totp = TOTP::generate($clock)
    ->withLabel('alice@example.com')
    ->withIssuer('My Service')
    ->withDigits(8);
```

!!! warning "Reassign the result"

    A `with*()` call whose result is thrown away does nothing you can see. This is the one mistake the
    change introduces, and no deprecation notice will catch it:

    ```php
    $otp->withDigits(8);         // lost
    $otp = $otp->withDigits(8);  // kept
    ```

### Patterns

```php
// Several parameters
$otp = $otp->withSecret('NEWSECRET')->withDigits(8);

// Conditionally
if ($useCustomLabel) {
    $otp = $otp->withLabel($customLabel);
}

// Advancing a HOTP counter
$hotp = $hotp->withCounter($hotp->getCounter() + 1);
```

### Finding them

```bash
grep -rn -- '->set[A-Z]' --include='*.php' src/ | grep -v vendor
```

A test that the migration worked, rather than one that only exercises the new names:

```php
$original = TOTP::generate($clock);
$modified = $original->withLabel('alice@example.com');

self::assertNotSame($original, $modified);
self::assertNull($original->getLabel());
self::assertSame('alice@example.com', $modified->getLabel());
```

### One exception: HOTP keeps mutating

`HOTP::verify()` advances the counter on success, and will keep doing so. `HOTP` is the one class not
marked `@readonly`, because that mutation is what prevents a code from being accepted twice. It is not
something to migrate away from — but you do have to persist the new counter. See
[The counter](../the-parameters/the-counter.md).

## The clock becomes mandatory

A `TOTP` reads the time from a [PSR-20](https://www.php-fig.org/psr/psr-20/) `ClockInterface`. Passing
`null` works today, emits a deprecation notice, and falls back to the library's internal clock. **In
v12.0 the argument is required.**

Four places take it:

```php
new TOTP($secret, $clock);
TOTP::generate($clock, $secretSize);
TOTP::createFromSecret($secret, $clock);
Factory::loadFromProvisioningUri($uri, $clock);
```

```php
use OTPHP\TOTP;
use Symfony\Component\Clock\NativeClock;

// Deprecated
$totp = TOTP::generate();

// What to write
$totp = TOTP::generate(new NativeClock());
```

The notice to watch for in your logs:

```text
The parameter "$clock" will become mandatory in 12.0.0.
Please set a valid PSR Clock implementation instead of "null".
```

### Which implementation

Any PSR-20 one, from your application rather than from the library:

```bash
composer require symfony/clock
```

```php
use Symfony\Component\Clock\NativeClock;
use Symfony\Component\Clock\MockClock;

$clock = new NativeClock();                                     // production
$clock = new MockClock(new DateTimeImmutable('@1519401289'));   // tests
```

`lcobucci/clock` works just as well. `OTPHP\InternalClock` is marked `@internal` and sits outside the
backwards compatibility policy — it is the fallback the library uses for you, not a class to depend on.
See [The clock](../one-time-passwords/the-clock.md).

### Finding the calls

```bash
grep -rn 'TOTP::generate()\|TOTP::create(\|new TOTP(\|loadFromProvisioningUri(' --include='*.php' src/
```

Then run your test suite and read the deprecation notices. None left means nothing left to do.

HOTP is unaffected: it counts uses, not seconds.

## The timeline

| Version | What happened |
|---|---|
| v11.1 | `create()` deprecated, in favour of `generate()` and `createFromSecret()` |
| v11.3 | The clock argument introduced, optional |
| v11.4 | `with*()` added, `set*()` deprecated; a deprecation notice when no clock is passed |
| v11.5 | Digests shorter than 19 bytes, and non-HMAC algorithms, refused |
| v12.0 | Classes `readonly`, `set*()` removed, the clock mandatory |

## If something is stuck

Search the [existing issues](https://github.com/Spomky-Labs/otphp/issues), then open
[a new one](https://github.com/Spomky-Labs/otphp/issues/new) with the version you are on, the code that
breaks and the message you get. A security issue goes to `security@spomky-labs.com` instead.
