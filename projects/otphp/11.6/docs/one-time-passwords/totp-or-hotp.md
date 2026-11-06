# TOTP or HOTP?

Both algorithms hash a secret together with a counter and truncate the result to a few digits. They differ
only in where the counter comes from.

| | TOTP | HOTP |
|---|---|---|
| The counter is | the clock, divided into periods | a number you keep, incremented at each use |
| A code is valid | for the length of the period | until it is used |
| Both sides must agree on | the time | how many codes have been consumed |
| Goes out of sync when | a clock drifts | a code is generated but not submitted |
| Used by | nearly every service with a second factor | hardware tokens, and little else |

**You want TOTP.** It is what Google Authenticator, FreeOTP, Aegis, 1Password and the rest show by default,
and what a user expects when you say "authenticator app". Choose HOTP only when something outside your
application already requires it.

## TOTP

The current timecode is the number of whole periods elapsed since the epoch, by default the Unix epoch:

```text
timecode = floor((timestamp - epoch) / period)
```

The code changes when that number does. With the default thirty-second period, it changes at every
multiple of thirty seconds of Unix time — which is why a code shown to the user may have one second of
life left. `expiresIn()` says how many seconds remain.

Synchronisation is a matter of clocks. The server's clock is yours to keep right; the device's clock is
not, and [the window](the-window.md) is what absorbs a small difference.

```php
use OTPHP\TOTP;

$totp = TOTP::generate($clock);
echo $totp->now();
```

## HOTP

The counter starts at zero and advances by one each time a code is accepted. `verify()` performs that
advance itself, and that is deliberate: it is what stops a code from being used twice.

```php
use OTPHP\HOTP;

$hotp = HOTP::generate();

if ($hotp->verify($code)) {
    $user->setOtpCounter($hotp->getCounter()); // persist it, or you lose the protection
}
```

The two sides fall out of step whenever the device produces a code that never reaches the server — a
button pressed in a pocket. [The window](the-window.md) lets the server catch up by looking a few counters
ahead.

Nothing prevents using both, for different purposes, in the same application. They share a parent class
and almost all of their API.
