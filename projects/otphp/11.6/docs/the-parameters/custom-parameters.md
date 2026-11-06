# Custom parameters

Any name that is not one of the library's own can be set on an OTP object. It is kept, it appears in the
provisioning URI, and it comes back when the factory reads that URI.

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock)
    ->withLabel('alice@example.com')
    ->withParameter('foo', 'bar');

echo $totp->getProvisioningUri();
```

```text
otpauth://totp/alice%40example.com?foo=bar&secret=JBSWY3DPEHPK3PXP
```

Reading it:

```php
$totp->hasParameter('foo');   // true
$totp->getParameter('foo');   // "bar"
$totp->getParameters();        // every parameter, the library's own included
```

`getParameter()` throws `ParameterNotFoundException` for a name that was never set — it does not return
`null`. Ask `hasParameter()` first, or catch it.

A custom parameter never changes the digits. Only the secret, the digest, the digits and the counter or
the period and the epoch do that.

## The `image` parameter

The one custom parameter with an established meaning. FreeOTP and a few others load it as the icon of the
account:

```php
$totp = $totp->withParameter('image', 'https://example.com/logo.png');
```

```text
otpauth://totp/alice%40example.com?image=https%3A%2F%2Fexample.com%2Flogo.png&secret=JBSWY3DPEHPK3PXP
```

It is not part of the key URI format, and no list of the applications that honour it is maintained. An
application that does not read it ignores it, so the cost of setting it is nothing.

## What not to put there

Everything in a provisioning URI reaches the user's device and lives in whatever backup that device makes.
It is also, in most applications, exportable as plain text. Store identifiers if you must, nothing
confidential, and nothing you rely on coming back unchanged: the URI is held by the user, not by you.
