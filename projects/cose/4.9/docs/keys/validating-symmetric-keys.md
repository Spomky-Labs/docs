---
description: 'The length a symmetric key must have for the algorithm that uses it.'
---

# Validating symmetric keys

[RFC 9053, section 3.1](https://www.rfc-editor.org/rfc/rfc9053#section-3.1) requires implementations "creating and
validating MAC values" to validate the key type, the key length and the algorithm. The first two constraints admit no
exception and are applied by the MAC algorithms themselves: `hash()` and `verify()` throw an
`InvalidArgumentException` when the key is not symmetric, or when its `k` is missing, is not a PHP string or is empty.
The AES-CBC-MAC algorithms add the length: RFC 9053 §3.2 ties it to the identifier, so a `k` that is not exactly
16 bytes (AES-MAC 128/64 and 128/128) or 32 bytes (AES-MAC 256/64 and 256/128) is refused the same way, before
OpenSSL is reached: it is the wrong key rather than a weak one; `AesCbcMac::keyLength()` and `tagLength()` give the
lengths in bytes. The content encryption and key wrap algorithms do the same with `keyLength()`.

`SymmetricKey` applies the same contract at construction time, where the mistake is easiest to attribute. A value
decoded from CBOR has to be normalized first, a `CBOR\ByteStringObject` not being a byte string.

```php
use Cose\Key\SymmetricKey;

// Throws an InvalidArgumentException: "k" is typed as a bstr by RFC 9053, section 7.3
SymmetricKey::create([
    SymmetricKey::TYPE => SymmetricKey::TYPE_OCT,
    SymmetricKey::DATA_K => ByteStringObject::create($secret), // use ->getValue() instead
]);
```

The **minimum** HMAC key length is a policy decision and stays opt-in, as it does for RSA moduli: a key shorter than
the output of the hash function (32 bytes for HS256 and HS256/64, 48 for HS384, 64 for HS512) is only "strongly
discouraged" by [RFC 2104, section 3](https://www.rfc-editor.org/rfc/rfc2104#section-3), and deployments do key HS384
and HS512 with 32 bytes. Such a key emits an `E_USER_WARNING` at every `hash()`/`verify()` call unless the algorithm
is created with `acknowledgeShortKey: true`; the next major version will throw instead.

```php
use Cose\Algorithm\Mac\HS512;
use Cose\Key\SymmetricKeyValidator;

// No warning: the risk is acknowledged
$algorithm = HS512::create(acknowledgeShortKey: true);

// The length RFC 2104 does not discourage for this algorithm, in bytes (32, 48 or 64)
$minimumKeyLength = $algorithm->minimumKeyLength();

// Throws an InvalidArgumentException when the key is shorter
SymmetricKeyValidator::create($minimumKeyLength)->check($key);

// …or ask without the exception
$isAcceptable = SymmetricKeyValidator::create()->isValid($key);

// The key length, in bytes, on its own
$keyLength = SymmetricKeyValidator::keyLength($key);

// The checks the algorithms apply on their own, should you want to run them earlier
SymmetricKeyValidator::checkKeyValue($key);
```

`SymmetricKeyValidator` accepts any `Key`, not only a `SymmetricKey`: `Key::create()` and `Key::createFromData()` with
an integer `kty` build a generic `Key` that never goes through the `SymmetricKey` constructor.
