# Verifying a password

`verify()` answers one question: does this code match this secret, at this moment. It returns a boolean
and never throws for a wrong code.

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret($user->getOtpSecret(), $clock);

if (! $totp->verify($code)) {
    // wrong code
}
```

The comparison itself uses `hash_equals()`, so a wrong code takes the same time to reject whatever digit
it got wrong.

## Its three arguments

The signature is the same for both algorithms, and the second argument is what differs:

```php
public function verify(string $otp, null|int $input = null, null|int $window = null): bool;
```

| | TOTP | HOTP |
|---|---|---|
| `$input` | A Unix timestamp. Defaults to the clock's | A counter. Defaults to the object's |
| `$window` | Seconds of accepted clock drift | How many counters ahead to look |

Leave both at `null` and you get the strictest check: the code of the current period, or of the current
counter, and nothing else.

## TOTP

```php
$totp->verify($code);                   // at the current second
$totp->verify($code, 1_519_401_289);    // at that second instead
$totp->verify($code, null, 10);         // allowing ten seconds of drift
```

A TOTP has no state, so verifying it changes nothing. The same code passes again for the rest of its
period, and for the whole window on top of it — **your application is what must refuse it a second time**.
See [Security recommendations](../the-project/security-recommendations.md).

It throws `InvalidParameterException` when the timestamp is negative, when the window is not smaller than
the period, or when the window would push the timestamp below zero.

## HOTP

```php
$hotp = HOTP::createFromSecret($user->getOtpSecret())
    ->withCounter($user->getOtpCounter());

if ($hotp->verify($code, null, 5)) {
    $user->setOtpCounter($hotp->getCounter()); // required
    $entityManager->flush();
}
```

A HOTP *is* stateful. On success, `verify()` sets the counter to one past the value that matched, so the
accepted code — and every code before it — can never be accepted again. `HOTP` is the one class in the
library that is not `@readonly`, for exactly this reason.

That protection only survives if you write the new counter back. Read it with `getCounter()` after a
successful verification and persist it; a request that forgets to will accept the same code again.

Passing a counter lower than the object's returns `false` without testing anything: counters move
forward only.

## Which codes are accepted

Exactly one, unless you pass a window — and then a few more, in a way worth knowing precisely. See
[The window](the-window.md).
