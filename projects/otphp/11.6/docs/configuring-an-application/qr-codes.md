# QR codes

A user configures their application by scanning a QR code whose content is
[the provisioning URI](the-provisioning-uri.md). OTPHP does not draw that image: it hands you the string
and leaves the rendering to a library of your choice.

**Render it on your own server.** The URI contains the secret, and sending it to a third party to be drawn
hands over the second factor of that account.

## With BaconQrCode

[BaconQrCode](https://github.com/Bacon/BaconQrCode) renders to PNG; its `GDLibRenderer` needs the `gd`
extension.

```bash
composer require bacon/bacon-qr-code:^3.0
```

```php
use BaconQrCode\Renderer\GDLibRenderer;
use BaconQrCode\Writer;
use OTPHP\TOTP;

$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock)
    ->withLabel('alice@example.com')
    ->withIssuer('My Service');

$writer = new Writer(new GDLibRenderer(250));
$png = $writer->writeString($totp->getProvisioningUri());

echo '<img alt="" src="data:image/png;base64,' . base64_encode($png) . '">';
```

## With endroid/qr-code

[endroid/qr-code](https://github.com/endroid/qr-code) has a builder and can return a data URI directly.

```bash
composer require endroid/qr-code
```

```php
use Endroid\QrCode\Builder\Builder;
use Endroid\QrCode\Writer\PngWriter;
use OTPHP\TOTP;

$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock)
    ->withLabel('alice@example.com')
    ->withIssuer('My Service');

$result = (new Builder(
    writer: new PngWriter(),
    data: $totp->getProvisioningUri(),
    size: 250,
))->build();

echo '<img alt="" src="' . $result->getDataUri() . '">';
```

A data URI keeps the image out of your routes and off your disk, which is one fewer place the secret can
be fetched from later. If you do serve it from a URL instead, make that URL single-use and bound to the
authenticated session.

## Show the secret as text too

Some users cannot scan — a desktop password manager, a camera that will not focus, an application that
imports keys by hand. Print the Base32 secret next to the image, in groups of four characters, and say
which issuer and account it belongs to.

## Online generators

`getQrCodeUri()` builds the address of an external service, with the provisioning URI substituted into it.
Both arguments are required: the template, and the placeholder to replace.

```php
$url = $totp->getQrCodeUri(
    'https://api.qrserver.com/v1/create-qr-code/?data=[DATA]&size=300x300&ecc=M',
    '[DATA]'
);

echo '<img alt="" src="' . $url . '">';
```

!!! danger "This sends the secret to someone else"

    The URL-encoded provisioning URI travels to that service, in the query string of a request your user's
    browser makes. It may be logged by the service, cached by anything in between, and kept for as long as
    they please — and from it, anyone can generate valid codes for that account.

    The method exists because it predates the alternatives. Use a local renderer. If a QR service is truly
    the only option available to you, satisfy yourself first that it neither caches nor logs what it is
    given, and understand that you are trusting it with a credential.

## Confirm before you enable

Showing the QR code is not enrolment. Ask the user for one code produced by their application, verify it,
and only then mark the factor as active. A code that fails here usually means a clock that is wrong on the
device, which is worth saying in the error message.
