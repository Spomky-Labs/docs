# Exceptions

Every exception the library throws implements `OTPHP\Exception\OTPExceptionInterface`, and every one of
them also extends a standard PHP exception. So you can catch the library as a whole, catch one precise
failure, or keep the `catch (InvalidArgumentException)` you already had — all three work.

```php
use OTPHP\Exception\OTPExceptionInterface;

try {
    $otp = Factory::loadFromProvisioningUri($uri, $clock);
} catch (OTPExceptionInterface $e) {
    // anything this library refuses
}
```

| Exception | Extends | Thrown when |
|---|---|---|
| `InvalidParameterException` | `InvalidArgumentException` | A parameter has an invalid value |
| `InvalidLabelException` | `InvalidArgumentException` | A label or issuer breaks the key URI grammar |
| `InvalidProvisioningUriException` | `InvalidArgumentException` | An `otpauth://` URI cannot be read |
| `ParameterNotFoundException` | `InvalidArgumentException` | A parameter that was never set is read |
| `SecretDecodingException` | `RuntimeException` | A secret is not valid Base32 |

A wrong code is not an exception. `verify()` returns `false`.

## `InvalidParameterException`

The one you will meet most. It carries the name and the value that were refused, as public readonly
properties:

```php
use OTPHP\Exception\InvalidParameterException;

try {
    $totp = $totp->withDigits($request->get('digits'));
} catch (InvalidParameterException $e) {
    $e->getMessage();      // "Digits must be between 1 and 10."
    $e->parameterName;     // "digits"
    $e->parameterValue;    // 0
}
```

It covers `secret`, `algorithm`, `digits`, `period`, `epoch`, `counter`, `secretSize`, `timestamp`,
`leeway` and the internal `timecode`. The rules each of them enforces are on the pages of
[The parameters](../the-parameters/the-parameters.md).

## `InvalidLabelException`

Same shape, with `labelName` and `labelValue`:

```php
use OTPHP\Exception\InvalidLabelException;

try {
    $totp = $totp->withLabel('user:invalid:format');
} catch (InvalidLabelException $e) {
    $e->getMessage();   // "Neither issuer nor account name in label may contain a colon."
    $e->labelName;      // "label"
    $e->labelValue;     // "user:invalid:format"
}
```

It is also what `getProvisioningUri()` throws when no label and no issuer are set, and when the label
contains a colon. See [The label and the issuer](../the-parameters/the-label-and-the-issuer.md).

## `InvalidProvisioningUriException`

From the factory: a scheme that is not `otpauth`, a missing host, path or query, a type other than `totp`
or `hotp`, or no `secret`.

```php
use OTPHP\Exception\InvalidProvisioningUriException;

try {
    $otp = Factory::loadFromProvisioningUri('invalid-uri', $clock);
} catch (InvalidProvisioningUriException $e) {
    $e->getMessage();   // "Not a valid OTP provisioning URI"
}
```

A URI whose *shape* is right but whose values are not throws the exception of the offending parameter
instead — `algorithm=md5` throws `InvalidParameterException`. Catch `OTPExceptionInterface` if you only
want to know that the URI was unusable.

## `ParameterNotFoundException`

`getParameter()` throws rather than returning `null`, so a typo cannot pass for an absent value:

```php
use OTPHP\Exception\ParameterNotFoundException;

try {
    $totp->getParameter('nonexistent');
} catch (ParameterNotFoundException $e) {
    $e->parameterName;  // "nonexistent"
}
```

`hasParameter()` asks the same question without the exception.

## `SecretDecodingException`

A `RuntimeException`, not an `InvalidArgumentException`, because of **when** it happens: the secret is
decoded the first time a code is computed, not when it is set. An invalid secret is accepted by
`createFromSecret()` and fails at `now()`, `at()` or `verify()`.

```php
use OTPHP\Exception\SecretDecodingException;

$totp = TOTP::createFromSecret('INVALID!@#', $clock);   // no exception here

try {
    $totp->now();                                       // here
} catch (SecretDecodingException $e) {
    // "Unable to decode the secret. Is it correctly base32 encoded?"
}
```

To validate a secret a user typed, generate a code from it. Constructing the object proves nothing.

## Catching precisely

```php
use OTPHP\Exception\InvalidParameterException;
use OTPHP\Exception\InvalidProvisioningUriException;

try {
    $otp = Factory::loadFromProvisioningUri($uri, $clock);
    $valid = $otp->verify($code);
} catch (InvalidProvisioningUriException $e) {
    $logger->error('Stored provisioning URI is unusable.', ['user' => $user->getId()]);
} catch (InvalidParameterException $e) {
    $logger->error('Refused parameter.', ['name' => $e->parameterName]);
}
```

Two habits worth keeping. **Do not put the message in an HTTP response**: these messages exist to be read
by you, and `$e->parameterValue` may hold the secret. **Do not log the URI or the secret** — see
[Security recommendations](../the-project/security-recommendations.md).

## Nothing to migrate

These classes arrived without breaking anything. Each extends the standard exception that was thrown
before, the messages are unchanged, and existing `catch (InvalidArgumentException)` and
`catch (RuntimeException)` blocks keep working. Move to the specific types when it helps you, at your own
pace.
