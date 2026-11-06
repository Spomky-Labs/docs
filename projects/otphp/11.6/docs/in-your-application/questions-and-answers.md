# Questions and answers

## My codes do not last the full period

They never do, and they are not meant to. A TOTP is valid for *its* period, not for the period that begins
when you ask for it. The boundaries are fixed by the clock:

```text
timecode = floor((timestamp - epoch) / period)
```

With the default thirty seconds, the code changes at every multiple of thirty of Unix time. Ask for one at
second 29 and it has one second left. This loop prints two different codes:

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret($secret, $clock)->withPeriod(10);

for ($i = 0; $i < 10; $i++) {
    echo $totp->now(), "\n";
    sleep(1);
}
```

`expiresIn()` says how many seconds remain. Show it next to the code, and allow a small
[window](../one-time-passwords/the-window.md) for the user who typed one that had just turned over.

## A user's codes are always refused, although their application scanned the QR code

Three usual causes, in order of likelihood:

1. **The device's clock is wrong.** Most applications offer a time correction or sync command. A window of
   a few seconds absorbs the rest.
2. **Your parameters are not the ones their application reads.** Google Authenticator ignores
   `algorithm`, `digits`, `period` and `epoch`, and silently shows six SHA-1 digits every thirty seconds.
   See [Authenticator applications](../configuring-an-application/authenticator-applications.md).
3. **You rebuilt the object with the wrong parameters.** `createFromSecret()` returns the defaults; if the
   account was provisioned with eight digits you must set eight again. This is what
   [storing the provisioning URI](what-to-store.md) prevents.

## Can a code be used twice?

A TOTP, yes — and that is your problem to solve, not the library's. It has no memory: a code it accepted
at the start of a period it accepts again until the period ends, and for the whole
[window](../one-time-passwords/the-window.md) on top. Store the last accepted timecode with the account
and refuse anything that is not newer.

A HOTP, no, provided you persist the counter. `verify()` advances it past the code that matched, so that
code and every earlier one are dead. See [The counter](../the-parameters/the-counter.md).

## Is there a Symfony bundle?

No, and none is needed. The library has no service to configure: build a `TOTP` where you need one and
inject a PSR-20 clock, which `symfony/clock` provides. Two or three lines in your own service is the whole
integration.

## How do I test code that verifies a TOTP?

Inject a clock you control. With a fixed clock the code becomes a constant you can assert:

```php
use OTPHP\TOTP;
use Symfony\Component\Clock\MockClock;

$clock = new MockClock(new DateTimeImmutable('@1519401289'));
$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock);

self::assertSame('626112', $totp->now());
```

See [The clock](../one-time-passwords/the-clock.md).

## Why is the generated secret 103 characters long?

The default is 64 random bytes, and Base32 turns them into 103 characters. It is more than anything needs:
the strength is capped by the digest anyway, and a long secret makes a denser QR code that some cameras
read badly. Pass a size — 20 bytes is what RFC 4226 recommends:

```php
$totp = TOTP::generate($clock, 20);  // 32 characters
```

See [The secret](../the-parameters/the-secret.md).

## Can I use OTPHP for a code sent by e-mail or text message?

You can, with care. Set the [epoch](../the-parameters/the-period-and-the-epoch.md) to the moment you
generate the code and the period to how long it should live, and the code is valid for exactly that span.

Use a **fresh secret for every code**. With a fixed secret and the epoch set to the creation time, the
timecode is always `0` and you would send the same digits every time.

A single-use token in a table is simpler and does the same job. Reach for this only if you have a reason.

## Why was my digest refused?

Because it produces fewer than 19 bytes, or because it is not an HMAC algorithm. The RFC 4226 truncation
reads up to the 19th byte of the digest, so a shorter hash — `md5`, `ripemd128` — would be read past its
end and collapse the code onto a handful of values. Since v11.5 the library refuses rather than compute
that. Use `sha1`, `sha256` or `sha512`. See
[The digest and the digits](../the-parameters/the-digest-and-the-digits.md).

## Why do I get a deprecation notice about `$clock`?

Because a `TOTP` was built without one. It becomes mandatory in v12.0; pass a PSR-20 clock to
`generate()`, `createFromSecret()`, the constructor and `Factory::loadFromProvisioningUri()`. See
[The clock](../one-time-passwords/the-clock.md).

## Why do I get a deprecation notice about `setDigits()`?

Because the mutable setters are deprecated since v11.4 and removed in v12.0, when the classes become
`readonly`. Replace `$otp->setX(…)` with `$otp = $otp->withX(…)` — and do not forget the assignment. See
[From v11 to v12](../migration/from-v11-to-v12.md).

## Can the same object be a TOTP and a HOTP?

No. They are separate classes with separate algorithms, and a provisioning URI names one of the two.
Nothing stops an application from using both for different purposes.
