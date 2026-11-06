# Creating an OTP

There are two moments in the life of an account where you build an OTP object, and they call different
methods: **enrolment**, where the secret does not exist yet, and **verification**, where it does.

## At enrolment: a new secret

`generate()` draws a secret from `random_bytes()` and returns an object around it.

```php
use OTPHP\TOTP;
use OTPHP\HOTP;

$totp = TOTP::generate($clock);     // 64 random bytes, Base32-encoded
$hotp = HOTP::generate();           // HOTP needs no clock

$secret = $totp->getSecret();       // what you store with the account
```

A second argument sets the size of the secret, in bytes:

```php
$totp = TOTP::generate($clock, 20); // 20 bytes, 32 Base32 characters
```

See [The secret](../the-parameters/the-secret.md) for what size to pick and why the default is large.

## At verification: an existing secret

`createFromSecret()` takes the Base32 secret you stored.

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret($user->getOtpSecret(), $clock);
```

The object comes with the default parameters — `sha1`, six digits, a thirty-second period — so if you
provisioned the account with anything else, you must set it back:

```php
$totp = TOTP::createFromSecret($user->getOtpSecret(), $clock)
    ->withDigest('sha256')
    ->withDigits(8);
```

Carrying those three lines around is how parameters drift apart. The alternative is to store the whole
provisioning URI and let [the factory](../configuring-an-application/the-factory.md) rebuild the object
from it. [What to store](../in-your-application/what-to-store.md) compares the two.

## Setting the parameters

Every parameter has a `with*()` method that returns a new object, so they chain:

```php
use OTPHP\TOTP;

$totp = TOTP::generate($clock)
    ->withLabel('alice@example.com')
    ->withIssuer('My Service')
    ->withDigest('sha256')
    ->withDigits(8)
    ->withPeriod(30);
```

The matching `set*()` methods mutate the object in place. They are deprecated since v11.4 and **removed in
v12.0**, when the classes become `readonly`. Write `with*()` in new code; see
[From v11 to v12](../migration/from-v11-to-v12.md).

## The deprecated constructors

`TOTP::create()` and `HOTP::create()` take every parameter positionally and have been deprecated since
v11.1:

```php
// Deprecated since v11.1
$totp = TOTP::create('JBSWY3DPEHPK3PXP', 30, 'sha1', 6);

// What to write instead
$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock)
    ->withPeriod(30)
    ->withDigest('sha1')
    ->withDigits(6);
```

The constructors themselves are not public API: `new TOTP(...)` works but says nothing about which
parameters the object ends up with. Use the static methods.
