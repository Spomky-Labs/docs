---
description: 'RsaKeyValidator: the modulus length, the exponent and the CRT parameters.'
---

# Validating RSA keys

The RSA algorithms reject, on their own, any key whose public parameters are not those
[RFC 8017, section 3.1](https://datatracker.ietf.org/doc/html/rfc8017#section-3.1) defines: an odd modulus and a
public exponent that is an odd integer between 3 and `n - 1`. `sign()` throws and `verify()` returns `false` for
such a key; nothing has to be done to get that behaviour.

The modulus length is a different matter. [RFC 8812](https://datatracker.ietf.org/doc/html/rfc8812) defers to
[RFC 8230, section 6.1](https://www.rfc-editor.org/rfc/rfc8230#section-6.1), which requires a modulus of 2048 bits or
larger and expects implementations to handle up to 16K bits. Both bounds are applied automatically, before the
algorithm computes anything with the key.

The **upper** bounds are not negotiable: every RSA algorithm rejects a key whose modulus is longer than
`RsaKeyValidator::MAXIMUM_MODULUS_LENGTH` (16384) bits or whose public exponent is longer than
`RsaKeyValidator::MAXIMUM_EXPONENT_LENGTH` (256) bits. `verify()` returns `false` for such a key and `sign()` throws
an `InvalidArgumentException`. The cost of an RSA operation grows with the size of the key it is given, and a
verifier takes that key from whoever produced the message.

The **minimum** modulus length is applied automatically too, with `RsaKeyValidator::create()`. Because legacy
authenticators holding 1024 bit keys still exist, a key below `RsaKeyValidator::MINIMUM_MODULUS_LENGTH` (2048) bits
only emits an `E_USER_WARNING` (`RsaKeyValidator::WEAK_KEY_MESSAGE`, filled in with the reason) and the operation
goes through:

```php
use Cose\Algorithm\Signature\RSA\RS256;

// Warns: "The RSA key does not satisfy RFC 8230 section 6.1: The modulus of the key is 1024 bits long; …"
// The signature is still verified, so no deployment breaks on upgrade.
$isValid = RS256::create()->verify($data, $weakKey, $signature);
```

As of the next major version, that warning becomes an `InvalidArgumentException` on `sign()` and a `false` on
`verify()`.

A caller that has to accept weaker keys passes the algorithm a validator carrying the bound it accepts. Writing the
bound down is the acknowledgement: a key below *it* is still refused, right away and with an exception, because you
chose that bound; only the implicit default is on the warn-then-throw schedule.

```php
use Cose\Algorithm\Signature\RSA\PS256;
use Cose\Algorithm\Signature\RSA\RS1;
use Cose\Algorithm\Signature\RSA\RS256;
use Cose\Key\RsaKeyValidator;

// Legacy authenticators: 1024 bit keys accepted silently, anything below still rejected
$algorithm = RS256::create(RsaKeyValidator::create(minimumModulusLength: 1024));
$algorithm = PS256::create(RsaKeyValidator::create(minimumModulusLength: 1024));

// RS1 keeps its acknowledgement flag first
$algorithm = RS1::create(true, RsaKeyValidator::create(minimumModulusLength: 1024));

// A policy stricter than the RFC, enforced now rather than in the next major version
$algorithm = RS256::create(RsaKeyValidator::create(minimumModulusLength: 3072, maximumModulusLength: 8192));
```

Every RSA algorithm takes it: `RS256`, `RS384`, `RS512`, `PS256`, `PS384` and `PS512` as their only argument, `RS1`
after its `acknowledgeInsecureAlgorithm` flag.

The validator can also be run on its own, on a key you are about to store:

```php
use Cose\Key\RsaKey;
use Cose\Key\RsaKeyValidator;

$key = RsaKey::create($data);

// Throws an InvalidArgumentException when the key does not comply
RsaKeyValidator::create()->check($key);

// …or ask without the exception
$isAcceptable = RsaKeyValidator::create()->isValid($key);

// The modulus and exponent lengths, in bits, are available on their own
$modulusLength = RsaKeyValidator::modulusLength($key);
$exponentLength = RsaKeyValidator::exponentLength($key);

// The bounds the algorithms apply on their own, should you want to run them earlier
RsaKeyValidator::checkLengthBounds($key);

// The public parameter constraints alone, without any modulus length policy:
// throws an InvalidArgumentException unless the modulus is odd and 3 <= e < n
RsaKeyValidator::checkPublicParameters($key);
```

`check()` and `isValid()` cover the public parameter constraints as well as the length bounds. Every check is
performed on the octet strings of the key, so rejecting an oversized key costs no more than reading it.
