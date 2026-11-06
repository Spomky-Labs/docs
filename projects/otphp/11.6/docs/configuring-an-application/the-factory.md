# The factory

`Factory` does the opposite of `getProvisioningUri()`: it reads an `otpauth://` URI and returns the object
it describes, with every parameter already set.

```php
use OTPHP\Factory;

$otp = Factory::loadFromProvisioningUri(
    'otpauth://totp/My%20Service%3Aalice%40example.com?issuer=My%20Service&secret=JBSWY3DPEHPK3PXP',
    $clock
);

$otp->verify($code);
```

It is the only public method of the class, and it is static.

## What you get back

A `TOTP` for `otpauth://totp/…`, a `HOTP` for `otpauth://hotp/…`. The declared return type is
`OTPInterface`, so narrow it when you need the methods of one or the other:

```php
use OTPHP\TOTPInterface;

$otp = Factory::loadFromProvisioningUri($uri, $clock);

if (! $otp instanceof TOTPInterface) {
    throw new LogicException('A time-based password was expected.');
}

echo $otp->expiresIn();
```

The clock is only used by a TOTP, and is optional today. **It becomes mandatory in v12.0**; omitting it
emits a deprecation notice. See [The clock](../one-time-passwords/the-clock.md).

## Everything comes back

The digest, the digits, the period, the epoch, the counter, the label, the issuer — and the custom
parameters, unchanged:

```php
$otp = Factory::loadFromProvisioningUri(
    'otpauth://totp/alice%40example.com?secret=JBSWY3DPEHPK3PXP&foo=bar',
    $clock
);

$otp->getParameter('foo');  // "bar"
```

Which is what makes storing the URI a complete record of an enrolment, rather than a secret plus a
promise that nothing was configured differently. See
[What to store](../in-your-application/what-to-store.md).

## The issuer, when the URI says it twice

The key URI format puts the issuer in two places — in front of the label, and as a query parameter — and
some providers put *different* values in them. Microsoft Office 365 is the one you will meet.

Since v11.4, **the query parameter wins**:

```php
$otp = Factory::loadFromProvisioningUri(
    'otpauth://totp/Microsoft%3Aalice%40example.com?secret=JBSWY3DPEHPK3PXP&issuer=Office365',
    $clock
);

$otp->getLabel();   // "alice@example.com"
$otp->getIssuer();  // "Office365"
```

Either way the prefix is stripped from the label, so `getLabel()` is the account name alone.

## What it refuses

`InvalidProvisioningUriException` — which extends `InvalidArgumentException` — for a URI that is not one:

* a scheme other than `otpauth`;
* a missing host, path or query string;
* a type that is neither `totp` nor `hotp`;
* no `secret` parameter.

A parameter that is present but invalid throws the exception of that parameter instead:
`InvalidParameterException` for `algorithm=md5` or `digits=0`, `InvalidLabelException` for a label that
cannot be split. See [Exceptions](../in-your-application/exceptions.md).

```php
use OTPHP\Exception\OTPExceptionInterface;

try {
    $otp = Factory::loadFromProvisioningUri($uri, $clock);
} catch (OTPExceptionInterface $e) {
    // anything the library refuses, under one marker interface
}
```

Always wrap the call when the URI came from outside your own storage — a user pasting a URI, an import
from another system. A valid-looking `otpauth://` string is easy to produce and easy to get wrong.
