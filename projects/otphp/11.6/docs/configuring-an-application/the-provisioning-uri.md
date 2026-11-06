# The provisioning URI

An authenticator application is configured by a single string: an `otpauth://` URI holding the secret and
every parameter needed to reproduce the codes. It is what a QR code carries.

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock)
    ->withLabel('alice@example.com')
    ->withIssuer('My Service');

echo $totp->getProvisioningUri();
```

```text
otpauth://totp/My%20Service%3Aalice%40example.com?issuer=My%20Service&secret=JBSWY3DPEHPK3PXP
```

Its shape is the
[key URI format](https://github.com/google/google-authenticator/wiki/Key-Uri-Format) Google Authenticator
defined:

```text
otpauth://<type>/<issuer>:<account>?<parameters>
```

The type is `totp` or `hotp`. The path is the label, with the issuer joined in front of it by a colon when
there is one. The parameters carry the rest, sorted by name.

## A label is required

`getProvisioningUri()` throws `InvalidLabelException` when neither a label nor an issuer is set: there
would be nothing to name the account with. Set the label before you call it. See
[The label and the issuer](../the-parameters/the-label-and-the-issuer.md).

## Defaults are left out

A parameter at its default value is omitted, because an application that does not read it will assume the
same default anyway:

```php
$totp->withPeriod(30)->getProvisioningUri();  // no "period="
$totp->withPeriod(60)->getProvisioningUri();  // "period=60"
$totp->withEpoch(0)->getProvisioningUri();    // no "epoch="
```

A fully specified TOTP looks like this:

```text
otpauth://totp/My%20Service%3Aalice%40example.com?algorithm=sha512&digits=8&issuer=My%20Service&period=10&secret=JBSWY3DPEHPK3PXP
```

And a HOTP carries its counter, which is never omitted:

```text
otpauth://hotp/alice%40example.com?counter=1000&secret=JBSWY3DPEHPK3PXP
```

## It is the secret, written out

Treat the URI exactly as you treat the secret. It goes to the user's browser once, over TLS, in a page
that is not cached; it does not go into a log, an exception message, an analytics event or a third-party
service. [QR codes](qr-codes.md) is about the last of those.

## It round-trips

Everything the URI holds — the custom parameters included — can be read back into an equivalent object:

```php
use OTPHP\Factory;

$otp = Factory::loadFromProvisioningUri($uri, $clock);
```

Which makes the URI a reasonable thing to store, instead of the secret and a scattering of columns. See
[The factory](the-factory.md) and [What to store](../in-your-application/what-to-store.md).
