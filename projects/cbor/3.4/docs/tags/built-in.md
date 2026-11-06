---
description: The tags of the IANA registry this library implements, one by one
---

# The built-in tags

The tags of RFC 8949 itself. Each one has a class, a number, and rules about what it may wrap. The rest
of what the library implements — COSE, dates, addresses, typed arrays — is on
[the next page](registry-tags.md), and a number nothing is registered for is still decoded: see
[the IANA registry](registry.md).

## Dates and times

### Tag 0 — a date-time string

A date and time written in the format of RFC 3339.

Class
:   `CBOR\Tag\DatetimeTag`

Specification
:   [RFC 8949 § 3.4.1](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.1)

Accepts
:   `TextStringObject` or `IndefiniteLengthTextStringObject`

Normalizes to
:   `DateTimeImmutable`

```php
use CBOR\Tag\DatetimeTag;
use CBOR\TextStringObject;

$tag = DatetimeTag::create(
    TextStringObject::create('2024-01-15T10:30:00Z')
);

$dateTime = $tag->normalize();
echo $dateTime->format('Y-m-d H:i:s'); // 2024-01-15 10:30:00
```

A date-time that does not exist — `2013-02-30T12:00:00Z`, a twenty-fifth hour — is rejected with an
`InvalidArgumentException` rather than silently rolled over to the following day. A leap second is
accepted and reported as the instant that follows it, since PHP dates cannot hold one.

### Tag 1 — an epoch timestamp

A POSIX timestamp: seconds since 1970-01-01 00:00:00 UTC.

Class
:   `CBOR\Tag\TimestampTag`

Specification
:   [RFC 8949 § 3.4.2](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.2)

Accepts
:   `UnsignedIntegerObject`, `NegativeIntegerObject` or a float object

Normalizes to
:   `DateTimeImmutable`

```php
use CBOR\Tag\TimestampTag;
use CBOR\UnsignedIntegerObject;

$tag = TimestampTag::create(
    UnsignedIntegerObject::create(time())
);

$dateTime = $tag->normalize();
echo $dateTime->format('c');
```

A float timestamp is converted to the nearest microsecond. `NAN`, `INF` and magnitudes no date object can
hold are rejected with an `InvalidArgumentException`.

## Big numbers

An empty byte string is the preferred serialization of zero
([RFC 8949 § 3.4.3](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.3)): tag 2 normalizes it to
`"0"` and tag 3 to `"-1"`.

!!! warning "Both tags are bounded"

    The byte string shall not exceed `MAX_BYTE_LENGTH`, 256 bytes — a 2048-bit integer; a longer one is
    rejected with an `InvalidArgumentException`. Turning it into the decimal string `normalize()` returns
    is a base conversion, which `brick/math` performs in time quadratic in the length on every calculator
    but GMP. Install `ext-gmp` when the input is untrusted.

### Tag 2 — an unsigned bignum

An arbitrarily large positive integer, as a byte string holding its big-endian representation.

Class
:   `CBOR\Tag\UnsignedBigIntegerTag`

Specification
:   [RFC 8949 § 3.4.3](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.3)

Accepts
:   `ByteStringObject` or `IndefiniteLengthByteStringObject`

Normalizes to
:   a numeric string

```php
use CBOR\ByteStringObject;
use CBOR\Tag\UnsignedBigIntegerTag;

$tag = UnsignedBigIntegerTag::create(
    ByteStringObject::create(hex2bin('0123456789ABCDEF'))
);

$value = $tag->normalize(); // "81985529216486895"
```

### Tag 3 — a negative bignum

An arbitrarily large negative integer: the value is −1 minus the unsigned integer the byte string holds.

Class
:   `CBOR\Tag\NegativeBigIntegerTag`

Specification
:   [RFC 8949 § 3.4.3](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.3)

Accepts
:   `ByteStringObject` or `IndefiniteLengthByteStringObject`

Normalizes to
:   a numeric string

```php
use CBOR\ByteStringObject;
use CBOR\Tag\NegativeBigIntegerTag;

// The value is -1 - unsigned_value
$tag = NegativeBigIntegerTag::create(
    ByteStringObject::create(hex2bin('FF'))
);

$value = $tag->normalize(); // "-256"
```

## Fractional numbers

### Tag 4 — a decimal fraction

A number written as **mantissa × 10^exponent**.

Class
:   `CBOR\Tag\DecimalFractionTag`

Specification
:   [RFC 8949 § 3.4.4](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.4)

Requires
:   `ext-bcmath`

Accepts
:   `ListObject` or `IndefiniteLengthListObject` of exactly two elements, `[exponent, mantissa]`

Normalizes to
:   the exact decimal value, as a string

```php
use CBOR\ListObject;
use CBOR\NegativeIntegerObject;
use CBOR\Tag\DecimalFractionTag;
use CBOR\UnsignedIntegerObject;

// From an exponent and a mantissa: 1234 × 10^-2 = 12.34
$tag = DecimalFractionTag::createFromExponentAndMantissa(
    NegativeIntegerObject::create(-2),  // exponent
    UnsignedIntegerObject::create(1234) // mantissa
);

echo $tag->normalize(); // "12.34"

// From a PHP float
$tag = DecimalFractionTag::createFromFloat(3.14159, precision: 5);
echo $tag->normalize(); // "3.14159"

// From the list itself
$tag = DecimalFractionTag::create(
    ListObject::create([
        NegativeIntegerObject::create(-2),
        UnsignedIntegerObject::create(1234),
    ])
);
```

### Tag 5 — a bigfloat

A number written as **mantissa × 2^exponent**.

Class
:   `CBOR\Tag\BigFloatTag`

Specification
:   [RFC 8949 § 3.4.4](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.4)

Requires
:   `ext-bcmath`

Accepts
:   `ListObject` of exactly two elements, `[exponent, mantissa]`

Normalizes to
:   the value as a string

```php
use CBOR\NegativeIntegerObject;
use CBOR\Tag\BigFloatTag;
use CBOR\UnsignedIntegerObject;

// 5 × 2^-2 = 1.25
$tag = BigFloatTag::createFromExponentAndMantissa(
    NegativeIntegerObject::create(-2), // exponent, base 2
    UnsignedIntegerObject::create(5)   // mantissa
);

echo $tag->normalize(); // "1.25"

// From a PHP float
$tag = BigFloatTag::createFromFloat(3.14159);
```

!!! warning "The exponent is bounded"

    Its absolute value shall not exceed `MAX_ABSOLUTE_EXPONENT`, 1024; beyond it the tag is rejected with
    an `InvalidArgumentException`. Writing `10^e` down takes about `e` digits, and `2^-e` exactly `e`, so
    an unbounded exponent lets a six-byte item expand into kilobytes.

## Expected encodings

Tags 21, 22 and 23 say how the byte string they wrap is meant to be written out when the data is converted
to a text format such as JSON. They are a hint and nothing more: the byte string is stored as it is, and
the conversion is left to the application. None of the three implements `Normalizable`; each hands back the
object it wraps through `getValue()`.

All three accept a `ByteStringObject` or an `IndefiniteLengthByteStringObject`, and all three are specified
in [RFC 8949 § 3.4.5.2](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.5.2).

| Tag | Expected encoding | Class |
|-----|-------------------|-------|
| 21 | base64url | `CBOR\Tag\Base64UrlEncodingTag` |
| 22 | base64 | `CBOR\Tag\Base64EncodingTag` |
| 23 | base16, that is hexadecimal | `CBOR\Tag\Base16EncodingTag` |

```php
use CBOR\ByteStringObject;
use CBOR\Tag\Base64UrlEncodingTag;

$tag = Base64UrlEncodingTag::create(
    ByteStringObject::create('Hello World!')
);

$bytes = $tag->getValue()->normalize(); // "Hello World!"
$encoded = rtrim(strtr(base64_encode($bytes), '+/', '-_'), '='); // "SGVsbG8gV29ybGQh"
```

## Semantic tags

### Tag 32 — a URI

The text string holds a URI, as defined by RFC 3986.

Class
:   `CBOR\Tag\UriTag`

Specification
:   [RFC 8949 § 3.4.5.3](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.5.3)

Accepts
:   `TextStringObject` or `IndefiniteLengthTextStringObject`

Normalizes to
:   the URI, as a string

```php
use CBOR\Tag\UriTag;
use CBOR\TextStringObject;

$tag = UriTag::create(
    TextStringObject::create('https://example.com/path?query=value')
);

$uri = $tag->normalize(); // "https://example.com/path?query=value"
```

### Tags 33 and 34 — text that is already encoded

The text string holds data that has already been encoded, base64url for tag 33 and base64 for tag 34.
Where tags 21 and 22 announce an encoding still to be applied, these two describe text as it stands.

Both accept a `TextStringObject` or an `IndefiniteLengthTextStringObject`, and both are specified in
[RFC 8949 § 3.4.5.2](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.5.2).

| Tag | Content | Class |
|-----|---------|-------|
| 33 | base64url encoded text | `CBOR\Tag\Base64UrlTag` |
| 34 | base64 encoded text | `CBOR\Tag\Base64Tag` |

```php
use CBOR\Tag\Base64UrlTag;
use CBOR\TextStringObject;

$tag = Base64UrlTag::create(
    TextStringObject::create('SGVsbG8gV29ybGQh')
);
```

### Tag 36 — a MIME message

The string holds a MIME message, an email among other things.

Class
:   `CBOR\Tag\MimeTag`

Specification
:   [RFC 8949 § 3.4.5.3](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.5.3)

Accepts
:   `TextStringObject`, `IndefiniteLengthTextStringObject`, `ByteStringObject` or
    `IndefiniteLengthByteStringObject`

```php
use CBOR\Tag\MimeTag;
use CBOR\TextStringObject;

$mimeMessage = "Content-Type: text/plain\r\n\r\nHello World!";

$tag = MimeTag::create(
    TextStringObject::create($mimeMessage)
);
```

## Special CBOR tags

### Tag 24 — an encoded CBOR data item

The byte string holds a CBOR document of its own, not yet decoded. It is how a signed or encrypted
payload travels: the bytes must stay exactly as they were to be verified.

Class
:   `CBOR\Tag\CBOREncodingTag`

Specification
:   [RFC 8949 § 3.4.5.1](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.5.1)

Accepts
:   `ByteStringObject`

```php
use CBOR\ByteStringObject;
use CBOR\Tag\CBOREncodingTag;
use CBOR\UnsignedIntegerObject;

// Encode a CBOR object
$innerObject = UnsignedIntegerObject::create(42);
$encoded = (string) $innerObject;

// Wrap it in tag 24
$tag = CBOREncodingTag::create(
    ByteStringObject::create($encoded)
);

// Decode it whenever you need it
$decoder = Decoder::create();
$decoded = $decoder->decode(StringStream::create($tag->getValue()->getValue()));
```

### Tag 55799 — self-described CBOR

A magic number that marks the start of a CBOR document, so that a reader can tell what it is holding
without parsing it. Encoded, it is the three bytes `d9 d9 f7`.

Class
:   `CBOR\Tag\CBORTag`

Specification
:   [RFC 8949 § 3.4.6](https://datatracker.ietf.org/doc/html/rfc8949#section-3.4.6)

Accepts
:   any `CBORObject`

Normalizes to
:   whatever the wrapped object normalizes to

```php
use CBOR\MapObject;
use CBOR\Tag\CBORTag;
use CBOR\TextStringObject;

$data = MapObject::create()
    ->add(TextStringObject::create('key'), TextStringObject::create('value'));

$selfDescribed = CBORTag::create($data);

// Encoded, this starts with the bytes d9 d9 f7
$encoded = (string) $selfDescribed;

// The wrapped object
$innerObject = $selfDescribed->getValue();

// Or straight through to the wrapped value
$value = $selfDescribed->normalize();
```

!!! warning "`SelfDescribeCBORTag` is deprecated"

    `CBOR\Tag\SelfDescribeCBORTag` also declares tag 55799, and was documented here until 3.3.5. A tag
    manager registers one class per tag number, and `CBORTag` is the one the default decoder uses, so
    decoding a self-described document always yields a `CBORTag`. Use `CBORTag`; `SelfDescribeCBORTag`
    will be removed in 4.0.0. Its `getCBORObject()` is a duplicate of the inherited `getValue()`.
