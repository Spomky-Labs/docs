# The parameters

An OTP object is a bag of named parameters. The password it produces is a function of all of them, so two
objects that differ in any one produce different codes — and a user whose application holds the first
cannot authenticate against the second.

| Parameter | Applies to | Default | Page |
|---|---|---|---|
| `secret` | both | 64 random bytes | [The secret](the-secret.md) |
| `algorithm` | both | `sha1` | [The digest and the digits](the-digest-and-the-digits.md) |
| `digits` | both | `6` | [The digest and the digits](the-digest-and-the-digits.md) |
| `period` | TOTP | `30` seconds | [The period and the epoch](the-period-and-the-epoch.md) |
| `epoch` | TOTP | `0` | [The period and the epoch](the-period-and-the-epoch.md) |
| `counter` | HOTP | `0` | [The counter](the-counter.md) |
| `label` | both | none | [The label and the issuer](the-label-and-the-issuer.md) |
| `issuer` | both | none | [The label and the issuer](the-label-and-the-issuer.md) |
| anything else | both | — | [Custom parameters](custom-parameters.md) |

The first group changes the digits. The label and the issuer do not: they name the account in the
authenticator application and appear only in the provisioning URI. Setting them on a verification-only
object is pointless, and leaving them unset makes `getProvisioningUri()` throw.

## Reading them

```php
$totp->getSecret();
$totp->getDigest();
$totp->getDigits();
$totp->getPeriod();        // TOTP
$totp->getEpoch();         // TOTP
$hotp->getCounter();       // HOTP
$totp->getLabel();         // null if unset
$totp->getIssuer();        // null if unset

$totp->getParameters();            // all of them, as an array
$totp->hasParameter('image');
$totp->getParameter('image');      // ParameterNotFoundException if absent
```

## Writing them

Every parameter has a `with*()` method. Each returns a **new object**, leaving the one you called it on
untouched, so they chain and the original stays usable:

```php
use OTPHP\TOTP;

$base = TOTP::generate($clock);

$configured = $base
    ->withDigest('sha256')
    ->withDigits(8)
    ->withLabel('alice@example.com');

$base->getDigits();        // 6 — unchanged
$configured->getDigits();  // 8
```

Forgetting the assignment is the one mistake this style invites:

```php
$totp->withDigits(8);         // does nothing you can observe
$totp = $totp->withDigits(8); // this is what you meant
```

The full list: `withSecret()`, `withDigest()`, `withDigits()`, `withLabel()`, `withIssuer()`,
`withIssuerIncludedAsParameter()`, `withParameter()`, plus `withPeriod()` and `withEpoch()` on a TOTP and
`withCounter()` on a HOTP.

## The deprecated setters

Each `with*()` has a `set*()` twin that mutates the object in place and returns nothing. They are
deprecated since v11.4 and **removed in v12.0**, when the classes become `readonly`:

```php
// Deprecated
$totp->setDigits(8);

// What to write
$totp = $totp->withDigits(8);
```

Finding them in a project:

```bash
grep -rn -- '->set[A-Z]' --include='*.php' src/
```

[From v11 to v12](../migration/from-v11-to-v12.md) has the full mapping and the patterns worth knowing.

## They are validated when they are set

A parameter is checked by its own validator the moment you set it, not when the code is generated. An
invalid value throws immediately — `InvalidParameterException` for most of them,
`InvalidLabelException` for the label and the issuer:

```php
$totp->withDigits(0);          // InvalidParameterException: Digits must be between 1 and 10.
$totp->withDigest('md5');      // InvalidParameterException: too short for the truncation
$totp->withLabel('a:b:c');     // InvalidLabelException
```

See [Exceptions](../in-your-application/exceptions.md).
