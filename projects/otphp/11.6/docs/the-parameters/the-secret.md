# The secret

The shared secret is the credential. It is held as an upper-case
[Base32](https://datatracker.ietf.org/doc/html/rfc4648#section-6) string, which is the encoding
authenticator applications read and the one the provisioning URI carries.

## A generated one

`generate()` draws it from `random_bytes()`. The default is 64 bytes — 512 bits, 103 Base32 characters:

```php
use OTPHP\TOTP;

$totp = TOTP::generate($clock);
echo strlen($totp->getSecret()); // 103
```

A second argument sets the size in bytes:

```php
$totp = TOTP::generate($clock, 20); // 32 characters
$hotp = HOTP::generate(20);         // HOTP takes the size as its first argument
```

| Bytes | Base32 characters | |
|---|---|---|
| 16 | 26 | The minimum worth using |
| 20 | 32 | What RFC 4226 recommends, and what most services issue |
| 32 | 52 | |
| 64 | 103 | The default |

A size below 1 throws `InvalidParameterException`.

!!! tip "Why 20 bytes is often the better choice"

    The strength of the construction is capped by the hash it uses — 160 bits for `sha1`, 256 for
    `sha256` — so a secret longer than that adds nothing an attacker has to work through. What it does add
    is a much denser QR code, which some cameras and some applications read badly. Twenty bytes is the
    size RFC 4226 recommends, and 32 is a reasonable choice next to `sha256`.

## Your own

```php
use OTPHP\TOTP;
use ParagonIE\ConstantTime\Base32;

$secret = Base32::encodeUpper(random_bytes(20));
$totp = TOTP::createFromSecret($secret, $clock);
```

The value is normalised on the way in: it is upper-cased, and trailing `=` padding is stripped. So the
secret you read back may not be character-for-character the string you passed, while decoding to the same
bytes.

Whatever produces it must be a cryptographically secure source. `random_bytes()` is one; `rand()`,
`uniqid()`, a hash of the user's e-mail address and a timestamp are not.

## When it is decoded

The Base32 string is decoded lazily, the first time a code is computed. A secret that is not valid Base32
is therefore accepted by `createFromSecret()` and only fails later, at `now()`, `at()` or `verify()`, with
a `SecretDecodingException`:

```php
use OTPHP\TOTP;
use OTPHP\Exception\SecretDecodingException;

$totp = TOTP::createFromSecret('INVALID!@#$%', $clock); // accepted

try {
    $totp->now();                                       // throws here
} catch (SecretDecodingException $e) {
    // "Unable to decode the secret. Is it correctly base32 encoded?"
}
```

If you validate a secret a user pasted by hand, call `now()` on it and catch that exception; constructing
the object proves nothing.

## Storing it

One secret per account, never shared, never reused for a second purpose. It is a credential that grants
valid codes forever to whoever reads it, so encrypt it at rest with a key kept outside the database, and
keep it out of logs and error reports. See
[Security recommendations](../the-project/security-recommendations.md) and
[What to store](../in-your-application/what-to-store.md).
