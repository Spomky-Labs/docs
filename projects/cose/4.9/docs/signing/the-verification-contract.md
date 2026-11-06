---
description: 'What verify() returns, what it throws, and where an unusable key is rejected.'
---

# The verification contract

`Cose\Algorithm\Signature\Signature::verify()` is total for every condition the governing specifications define as an
"invalid signature" outcome. A malformed, truncated, over-long or out-of-range signature, and key material that the
crypto layer cannot decode (a point that is not on the named curve, a public key that is not a valid group element)
all return `false`. No PHP warning is raised on the way.

It throws an `InvalidArgumentException` when the key cannot be used with the algorithm at all: its key type or its
curve does not match, or, when the algorithm was asked to enforce them (see
[Key restrictions](../keys/key-restrictions.md)), the key itself forbids the algorithm or the operation.
Structurally invalid key components (an empty or zero RSA modulus, an `x`, `y` or `d` whose length does not fit the
curve) are rejected earlier, by the `Key` constructors, so the exception is raised when the key is first seen rather
than at every verification.

```php
use Cose\Key\Key;
use InvalidArgumentException;

try {
    // Throws only when $key is an RSA key, an EC key on another curve, …
    $key = Key::createFromData($credentialPublicKey);
} catch (InvalidArgumentException $e) {
    // The credential cannot be used with this algorithm: reject it at registration.
}

// From here on, verification is a plain boolean, whatever the client sent.
$isValid = $algorithm->verify($data, $key, $signature);
```

`sign()` throws an `InvalidArgumentException` when the key is public, when the crypto layer cannot load it, or when the
signature operation itself fails, for instance for an RSA modulus too short for the digest.
