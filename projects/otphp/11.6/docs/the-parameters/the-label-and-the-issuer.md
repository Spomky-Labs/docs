# The label and the issuer

These two name the account inside the user's authenticator application. They have no effect on the digits
— they exist for the provisioning URI, where they become the line the user reads in their list of
accounts.

| | What it holds | Example |
|---|---|---|
| Label | The account | `alice@example.com` |
| Issuer | The service | `My Service` |

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock)
    ->withLabel('alice@example.com')
    ->withIssuer('My Service');
```

Set the issuer. A user with accounts on four services, all labelled with the same e-mail address, cannot
tell the four entries apart without it.

## Neither may contain a colon

The `otpauth://` format uses a colon to separate the issuer from the account inside the path, so a colon
in either value would be ambiguous. Both `:` and its encoded forms `%3A` and `%3a` are refused, with
`InvalidLabelException`.

!!! warning "Do not build the `issuer:account` form yourself"

    A label such as `My Service:alice@example.com` passes `withLabel()` — it looks like the
    `issuer ":" accountname` grammar, which is valid in a URI the library *reads*. But building the URI
    rejects it, so the failure surfaces later, at `getProvisioningUri()`:

    ```php
    $totp = $totp->withLabel('My Service:alice@example.com'); // accepted
    $totp->getProvisioningUri();                              // InvalidLabelException
    ```

    Put the account in the label, the service in the issuer, and let the library join them.

## What the URI looks like

With both set, the issuer appears twice: as the prefix of the path, and as a query parameter. That
duplication is what the
[key URI format](https://github.com/google/google-authenticator/wiki/Key-Uri-Format#label) asks for, and
applications differ in which one they read.

```php
echo $totp->getProvisioningUri();
```

```text
otpauth://totp/My%20Service%3Aalice%40example.com?issuer=My%20Service&secret=JBSWY3DPEHPK3PXP
```

To keep the prefix and drop the query parameter:

```php
$totp = $totp->withIssuerIncludedAsParameter(false);
echo $totp->getProvisioningUri();
```

```text
otpauth://totp/My%20Service%3Aalice%40example.com?secret=JBSWY3DPEHPK3PXP
```

There is rarely a reason to. Keep both unless an application you must support chokes on the parameter.

## At least one of them is required

Building a provisioning URI with neither throws `InvalidLabelException`:
*The label is not set. Either label or issuer must be set.* An object with only an issuer produces a URI
whose path is that issuer, which is legal but tells the user nothing about which account it is.

Nothing requires a label for verification. An object built only to check a code can leave both unset.

## Reading them back

The factory undoes the join: the prefix of the path is removed from the label and becomes the issuer.

```php
$otp = Factory::loadFromProvisioningUri(
    'otpauth://totp/My%20Service%3Aalice%40example.com?issuer=My%20Service&secret=JBSWY3DPEHPK3PXP',
    $clock
);

$otp->getLabel();   // "alice@example.com"
$otp->getIssuer();  // "My Service"
```

When the prefix and the parameter disagree — which Microsoft Office 365 does, among others — **the
parameter wins**. See [The factory](../configuring-an-application/the-factory.md).
