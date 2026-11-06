# The counter

A parameter of `HOTP` only. It is the number that replaces the clock: both sides must agree on how many
codes have been consumed.

```php
use OTPHP\HOTP;

$hotp = HOTP::generate()->withCounter(1000);
echo $hotp->getCounter(); // 1000
```

The default is `0`, which is where [RFC 4226](https://datatracker.ietf.org/doc/html/rfc4226) starts and
what to use for a new account. Any value from 0 up is accepted; a negative one throws
`InvalidParameterException`.

It travels in the provisioning URI, so the user's device starts from the same place:

```text
otpauth://hotp/alice%40example.com?counter=1000&secret=JBSWY3DPEHPK3PXP
```

## It moves on its own

This is the one piece of state the library keeps. On a successful `verify()`, the counter is set to **one
past the value that matched**:

```php
$hotp = HOTP::createFromSecret($secret)->withCounter(1000);

$hotp->verify($codeFor1000);  // true
$hotp->getCounter();          // 1001
```

It is why `HOTP` is the only class in the library not marked `@readonly`, and it is deliberate: the code
that was just accepted can never be accepted again by the same object. Every code below the new counter is
burned with it.

`at()` does not move it. Only `verify()` does, and only on success.

## Persist it, or the protection is gone

The object is thrown away at the end of the request. If you do not write the counter back, the next
request starts from the old value and accepts the same code again — which is exactly the replay the
increment exists to prevent.

```php
use OTPHP\HOTP;

$hotp = HOTP::createFromSecret($user->getOtpSecret())
    ->withCounter($user->getOtpCounter());

if (! $hotp->verify($code, null, 5)) {
    return false;
}

$user->setOtpCounter($hotp->getCounter());  // not optional
$entityManager->flush();

return true;
```

Store the provisioning URI instead of the secret and the same rule applies: **write the URI back after
every successful verification**, because the counter it carries has changed. See
[What to store](../in-your-application/what-to-store.md).

## Going out of step, and catching up

Each code the device produces advances *its* counter, whether or not the code reaches you. A button
pressed by accident leaves the device ahead of the server, and its next code will not match the counter
you hold.

The window is the repair: it tests the counters above yours and, on a match, jumps to just past it.

```php
$hotp->verify($code, null, 10);  // tests counter … counter + 10
```

Five to ten covers accidental presses. See [The window](../one-time-passwords/the-window.md).

Verifying against an explicit counter lower than the object's returns `false` immediately, without testing
anything: counters only move forward.
