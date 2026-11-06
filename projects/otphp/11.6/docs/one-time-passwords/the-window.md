# The window

The third argument of `verify()` widens what counts as valid. It exists for two real problems — a phone
whose clock is a few seconds off, and a hardware token whose button was pressed in a pocket — and for
nothing else. Each unit of window is another code an attacker gets to guess with, so keep it small.

By default it is `null`: one code is tested, and that is all.

## TOTP: seconds of drift

For a TOTP the window is a number of **seconds**, not of periods. Three timestamps are tested, in this
order:

```text
timestamp - window
timestamp
timestamp + window
```

So a window accepts the previous code when `timestamp - window` falls into the previous period, and the
next one when `timestamp + window` falls into the next. It does not accept everything in between — the
range is sampled at three points, not scanned.

```php
// At second 1476822005, with a 30-second period, the current period runs from 1476822000
// to 1476822029. The previous code was the one of 1476821970 to 1476821999.

$totp->verify($previousCode);            // false: only 1476822005 is tested
$totp->verify($previousCode, null, 5);   // false: 1476822000 is still in the current period
$totp->verify($previousCode, null, 20);  // true: 1476821985 is in the previous one
```

**The window must be smaller than the period.** A window equal to or larger than it would reach past the
adjacent periods and is rejected with `InvalidParameterException`:

```php
$totp = TOTP::createFromSecret($secret, $clock)->withPeriod(30);

$totp->verify($code, null, 30); // InvalidParameterException
```

A window that would make `timestamp - window` negative is rejected too.

How much to allow: enough to cover a device whose clock was never synchronised, which in practice is a few
seconds to half a period. The sign of the window does not matter — it is taken as an absolute value.

## HOTP: counters ahead

For a HOTP the window is a number of **counters**, and they are scanned one by one from the current
counter upwards:

```text
counter, counter + 1, …, counter + window
```

```php
$hotp = HOTP::createFromSecret($secret)->withCounter(1000);

$hotp->verify($codeFor1003);          // false: only 1000 is tested
$hotp->verify($codeFor1003, null, 5); // true: 1000 to 1005 are tested
```

The first match wins, and the counter moves to just past it: after the second call above, `getCounter()`
returns `1004`. The codes that were skipped are gone for good, which is the point — it is how the server
catches up with a device that produced codes nobody submitted.

A window of five to ten covers accidental presses. A very large one turns a single stolen code into a
valid one for a long stretch of the counter space.

## A note for readers coming from v10

In version 10 the TOTP window was a number of *periods*, applied on both sides: a window of 5 with a
30-second period accepted the five codes before and the five after. Version 11 changed it to the seconds
of drift described above. If you carried a window value across that upgrade, re-read it — see
[From v10 to v11](../migration/from-v10-to-v11.md).
