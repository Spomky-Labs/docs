# From v8.3 to v9

Only the way objects are built changed.

Along with it: every class became `final`, the minimum PHP version became 7.1, strict type hints were
added throughout, and HHVM stopped being tested.

## Constructors became private

Build objects through the static methods.

```php
use OTPHP\TOTP;

// Before
$otp = new TOTP();

// After
$otp = TOTP::create();
```

`create()` has itself been deprecated since v11.1, in favour of `generate()` and `createFromSecret()`. If
you are coming from v8.3 today, go straight to those — see
[Creating an OTP](../one-time-passwords/creating-an-otp.md).

## The label left the constructor

It was the first argument; it has a method of its own.

```php
use OTPHP\TOTP;

// Before
$otp = new TOTP($label);

// After
$otp = TOTP::create();
$otp->setLabel($label);
```

The other parameters are unchanged.

`setLabel()` is in turn deprecated since v11.4; `withLabel()` replaces it. See
[The label and the issuer](../the-parameters/the-label-and-the-issuer.md).
