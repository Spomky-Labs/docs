# Authenticator applications

The codes OTPHP produces are read by the applications users already have. What those applications *will*
read is narrower than what the library can produce, and the difference is the most common cause of an
enrolment that silently does not work.

## Google Authenticator

It supports exactly one configuration:

| Parameter | What it accepts |
|---|---|
| Digest | `sha1` |
| Digits | 6 |
| Period | 30 seconds |
| Epoch | 0 |

Any other value is **ignored, not refused**. Hand it a URI with `algorithm=sha512&digits=8&period=10` and
it will scan happily, then show six SHA-1 digits every thirty seconds — codes your server will reject
forever, with nothing anywhere to say why.

So if Google Authenticator is among the applications your users may install, keep the defaults:

```php
use OTPHP\TOTP;

$totp = TOTP::generate($clock)        // sha1, 6 digits, 30 seconds
    ->withLabel('alice@example.com')
    ->withIssuer('My Service');
```

## The others

FreeOTP, Aegis, 2FAS, Ente Auth and the password managers generally read `algorithm`, `digits` and
`period`. `epoch` and custom parameters are another matter: `image` is honoured by FreeOTP and ignored
elsewhere, and no application reads a parameter of your own invention.

Nothing is guaranteed, and nothing announces what it supports. Before you move a live service off the
defaults, test the applications your users actually have.

## Testing an enrolment by hand

The secret below is the one used throughout this documentation and in the RFC test vectors. It is public —
never give it to a real account.

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock)
    ->withLabel('alice@example.com')
    ->withIssuer('My Service');

echo $totp->getProvisioningUri();
echo $totp->now();
echo $totp->expiresIn();
```

Render that URI as a QR code on your own machine — see [QR codes](qr-codes.md) — scan it, and compare the
digits on the phone with the ones `now()` printed. They match, or something in the list above explains why
not.

If they differ by a constant that looks like a whole period, the device's clock is off. Most applications
have a "time correction" or "sync" command for that; a reasonable [window](../one-time-passwords/the-window.md)
covers the rest.

## Say what you support

Users choose their application before they read your documentation. One line next to the QR code — "works
with Google Authenticator, FreeOTP, Aegis, 1Password and other TOTP applications" — prevents most of the
support requests this page describes.
