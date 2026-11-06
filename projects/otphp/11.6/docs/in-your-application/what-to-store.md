# What to store

To check a code you must rebuild the same object the user's application holds. Which means your database
has to remember not only the secret, but every parameter that went into it. There are two ways to do that,
and the easy one has a cost you pay later.

## The columns approach

Store the secret, and keep the parameters in your code:

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret($user->getOtpSecret(), $clock)
    ->withDigest('sha1')
    ->withDigits(6)
    ->withPeriod(30);

$totp->verify($code);
```

This works, for exactly as long as those three values never change. The day you decide that six digits
should become eight, or that `sha1` should become `sha256`, or that thirty seconds should become twenty,
**every existing account stops authenticating** — their applications keep producing codes for the old
configuration, and your server now computes the new one. Custom parameters set at enrolment are lost the
same way.

If you take this route, store the parameters as columns rather than constants, and read them back per
account. That is the whole of the problem: the parameters belong to the enrolment, not to the current
version of your code.

## The provisioning URI approach

Store [the provisioning URI](../configuring-an-application/the-provisioning-uri.md) itself. It holds the
secret and every parameter, custom ones included, in one text column:

```php
use OTPHP\Factory;

$otp = Factory::loadFromProvisioningUri($user->getProvisioningUri(), $clock);

$otp->verify($code);
```

A change of policy now affects only the accounts enrolled after it. Old URIs keep working, and you can
re-provision them at your own pace — the next time each user signs in, for instance.

This is the approach to take.

!!! warning "For HOTP, write it back"

    A successful `verify()` advances the counter, and the URI you stored still carries the old one. Save
    the new URI after every successful verification, or the counter never moves and the replay protection
    is not there:

    ```php
    if ($otp->verify($code, null, 5)) {
        $user->setProvisioningUri($otp->getProvisioningUri());
        $entityManager->flush();
    }
    ```

    A TOTP has no such state and needs no write.

## Either way

**Encrypt the column.** Secret or URI, it is a credential that yields valid codes to anyone who reads it,
and unlike a password hash it cannot be made useless by a one-way function. Encrypt at rest, with a key
that does not live in the same database.

**Keep a little state of your own**, which no column above gives you:

| What | Why |
|---|---|
| The last accepted timecode, or code | So a TOTP cannot be replayed within its period |
| A failure counter, per account | So six digits are not brute-forced at leisure |
| Whether enrolment was confirmed | So a QR code nobody scanned does not lock the account |
| When the factor was added | For the security page, and for support |

[Security recommendations](../the-project/security-recommendations.md) covers each of these.
