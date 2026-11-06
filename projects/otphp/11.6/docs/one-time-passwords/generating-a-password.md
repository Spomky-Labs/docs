# Generating a password

Your server normally generates codes only to compare them with what a user typed, which `verify()` does
for you. The methods below are for the cases where you need the code itself: a test, a diagnostic page, or
an OTP you send yourself through another channel.

## The current code

`now()`, on a TOTP, reads the clock and returns the code of the current period.

```php
use OTPHP\TOTP;

$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock);

echo $totp->now();       // the six digits of the current period
```

## How long it lasts

`expiresIn()` returns the number of seconds before the code changes.

```php
echo $totp->expiresIn(); // 17, say
```

It is the remainder of the period, not a countdown from when you asked. A code read one second before the
boundary lives for one second, which is why an interface that shows the code should show this number next
to it — and why a user who types the code of the previous period is not being careless. See
[The window](the-window.md).

## A code at a given input

`at()` takes the input directly: a Unix timestamp for a TOTP, a counter value for a HOTP.

```php
use OTPHP\TOTP;
use OTPHP\HOTP;

$totp = TOTP::createFromSecret('JBSWY3DPEHPK3PXP', $clock);
echo $totp->at(1_519_401_289);  // "626112": the code of the period holding that second

$hotp = HOTP::createFromSecret('JBSWY3DPEHPK3PXP');
echo $hotp->at(0);              // "282760", the first code
echo $hotp->at(1);              // "996554", the second
```

`at()` does not move anything. Calling it on a HOTP leaves the counter where it was; only `verify()`
advances it.

Both reject a negative input, and a TOTP also rejects a timestamp earlier than its epoch: there is no
period before the beginning. Both throw `InvalidParameterException`.

## How the digits are computed

For the record, since it explains two constraints you will meet elsewhere. The library follows
[RFC 4226 §5.3](https://datatracker.ietf.org/doc/html/rfc4226#section-5.3): it computes
`HMAC(secret, input)`, reads the low four bits of the last byte of the digest as an offset, takes the four
bytes at that offset, masks the top bit off, and keeps the last *n* decimal digits of the 31-bit number
that remains.

That offset can be as high as 15, so the truncation reads up to the 19th byte — which is why a digest
shorter than 19 bytes is refused. And 31 bits hold at most ten digits, which is why ten is the maximum.
See [The digest and the digits](../the-parameters/the-digest-and-the-digits.md).
