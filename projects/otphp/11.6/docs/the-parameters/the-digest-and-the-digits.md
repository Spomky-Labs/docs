# The digest and the digits

Two parameters shape the code itself: the hash the HMAC uses, and how many of the resulting digits are
kept. Both must match on the server and in the user's application, exactly.

## The digest

The default is `sha1`. That is not an oversight: in HMAC, SHA-1 has no known weakness that matters here,
and it is what every authenticator application supports.

```php
$totp = $totp->withDigest('sha256');
echo $totp->getDigest();
```

**Use `sha1`, `sha256` or `sha512`.** They are the three values
[RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238) defines, the three the `otpauth://` key URI
format names, and in practice the only three an authenticator application will read. `SHA-2` is
preferable where you control both ends.

The value is accepted if `hash_hmac_algos()` lists it **and** its output is at least 19 bytes. Anything
else throws `InvalidParameterException`:

```php
$totp->withDigest('md5');      // 16 bytes: rejected
$totp->withDigest('crc32');    // not an HMAC algorithm: rejected
$totp->withDigest('sha3-256'); // accepted by the library; no application will read it
```

!!! danger "Why short digests are refused, since v11.5"

    The RFC 4226 truncation reads four bytes starting at an offset taken from the low four bits of the
    last digest byte — an offset anywhere from 0 to 15 — so it reads up to the 19th byte. With a 16-byte
    hash such as MD5, that read runs past the end of the digest, and the generated code collapses onto a
    small set of values that barely depend on the secret. It is a real weakness in the verification path,
    not a theoretical one.

    Before v11.5 the library accepted `md5` and produced those codes. An account provisioned that way was
    never interoperable and was never safe: re-enrol it with a supported algorithm. Upgrading turns the
    silent weakness into an exception, which is the point. See
    [From v11 to v12](../migration/from-v11-to-v12.md).

## The digits

The default is 6, which is what users expect and what every application displays.

```php
$totp = $totp->withDigits(8);
```

**The accepted range is 1 to 10.** Outside it, `InvalidParameterException`:

```php
$totp->withDigits(0);  // "Digits must be between 1 and 10."
$totp->withDigits(11); // same
```

Ten is not an arbitrary limit. The truncation yields a 31-bit number, at most 2 147 483 647, so the
eleventh digit would carry no entropy at all — and `10 ** $digits` would overflow PHP's integer range on
the way. The library refuses rather than produce a code that only looks longer.

Codes are zero-padded on the left, so six digits always render as six characters:

```php
echo $totp->at(1_519_401_289); // "626112" — and "042…" would keep its leading zero
```

Going above 6 is safe as long as the user's application follows; Google Authenticator ignores the
parameter and keeps showing six. See
[Authenticator applications](../configuring-an-application/authenticator-applications.md).

## Changing them later

Both appear in the provisioning URI, so a change affects only the accounts enrolled after it. Every
earlier account keeps the parameters it was provisioned with, and will stop authenticating if you switch
the server to new ones without re-enrolling. This is the single best reason to store the whole
provisioning URI rather than the secret alone: see
[What to store](../in-your-application/what-to-store.md).
