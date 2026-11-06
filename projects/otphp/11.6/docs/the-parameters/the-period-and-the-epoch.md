# The period and the epoch

Two parameters exist on a `TOTP` only. They decide where one code ends and the next begins.

```text
timecode = floor((timestamp - epoch) / period)
```

## The period

How long a code lives, in seconds. The default is 30.

```php
$totp = $totp->withPeriod(60);
echo $totp->getPeriod();   // 60
echo $totp->expiresIn();   // seconds before the current code changes
```

It must be at least 1; otherwise `InvalidParameterException`.

**Thirty seconds is what to use.** Google Authenticator ignores any other value and keeps counting in
thirties, so a different period silently breaks it. A longer period is also a longer window of
opportunity for a stolen code, and a shorter one leaves users retyping codes that expired while they were
reading them.

The period bounds [the window](../one-time-passwords/the-window.md) too: a window must be strictly smaller
than it.

A code does not live for a full period from the moment you show it. It lives until the end of its period,
which may be one second away — that is what `expiresIn()` is for.

## The epoch

Where the counting starts, as a Unix timestamp. The default is `0`, the Unix epoch, which is the `T0` of
[RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238#section-4). Leave it there unless you have the
specific need below.

```php
$totp = $totp->withEpoch(1_519_401_289);
echo $totp->getEpoch();
```

It must be 0 or more. A timestamp earlier than the epoch has no timecode, and asking for one throws
`InvalidParameterException`.

Shifting the epoch shifts every period boundary. Set it to the exact moment a code was produced and that
moment becomes the start of a period, so the code is valid for the whole period that follows rather than
for whatever remained of a boundary-aligned one:

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret($secret, $clock)->withPeriod(5);

$password = $totp->at(1_519_401_289);  // the period holding that second ends at 1519401289
$totp->verify($password, 1_519_401_289); // true
$totp->verify($password, 1_519_401_290); // false — a new period began

$aligned = $totp->withEpoch(1_519_401_289);

$password = $aligned->at(1_519_401_289);  // this period runs from 1519401289 to 1519401293
$aligned->verify($password, 1_519_401_289); // true
$aligned->verify($password, 1_519_401_293); // true
$aligned->verify($password, 1_519_401_294); // false
```

That is useful for a code you send yourself — by e-mail or by text message — where you know when it was
created and want it to live for a known duration. Both sides must agree on the epoch, so it travels in
the provisioning URI like the rest.

!!! warning "A fixed epoch with a fixed secret repeats itself"

    If you store the creation timestamp as the epoch and keep the same secret, the first code of the first
    period is the same every time: same secret, same timecode `0`, same digits. Use a fresh secret for each
    code you generate this way — deriving it from the timestamp is one way — or you will be sending the
    same password over and over.

Google Authenticator does not read the `epoch` parameter. Only use it where you control both ends.
