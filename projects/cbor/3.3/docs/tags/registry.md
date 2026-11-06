---
description: Which tag numbers the library implements, and what happens to the others
---

# The IANA registry

Tag numbers are held in the
[CBOR tags registry](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml) of IANA. The library
implements the ones below; every other number still decodes, as a tag that keeps its number without
interpreting it.

| Tag | Meaning | Class | Specification |
|-----|---------|-------|---------------|
| 0 | Date-time string, RFC 3339 | `DatetimeTag` | RFC 8949 § 3.4.1 |
| 1 | Epoch timestamp | `TimestampTag` | RFC 8949 § 3.4.2 |
| 2 | Unsigned bignum | `UnsignedBigIntegerTag` | RFC 8949 § 3.4.3 |
| 3 | Negative bignum | `NegativeBigIntegerTag` | RFC 8949 § 3.4.3 |
| 4 | Decimal fraction | `DecimalFractionTag` | RFC 8949 § 3.4.4 |
| 5 | Bigfloat | `BigFloatTag` | RFC 8949 § 3.4.4 |
| 21 | base64url expected | `Base64UrlEncodingTag` | RFC 8949 § 3.4.5.2 |
| 22 | base64 expected | `Base64EncodingTag` | RFC 8949 § 3.4.5.2 |
| 23 | base16 expected | `Base16EncodingTag` | RFC 8949 § 3.4.5.2 |
| 24 | Encoded CBOR data item | `CBOREncodingTag` | RFC 8949 § 3.4.5.1 |
| 32 | URI | `UriTag` | RFC 8949 § 3.4.5.3 |
| 33 | base64url encoded text | `Base64UrlTag` | RFC 8949 § 3.4.5.2 |
| 34 | base64 encoded text | `Base64Tag` | RFC 8949 § 3.4.5.2 |
| 36 | MIME message | `MimeTag` | RFC 8949 § 3.4.5.3 |
| 55799 | Self-described CBOR | `CBORTag` | RFC 8949 § 3.4.6 |

Every class is in the `CBOR\Tag` namespace, and each one is described in
[the built-in tags](built-in.md).

## A tag the library does not know

A tag number no class is registered for is not an error: the decoder returns a `GenericTag`, which keeps
the head and the object the tag wrapped, so a document survives a round trip through code that does not
understand all of it. Its `normalize()` normalizes the wrapped item on its own, since the number carries
no meaning the library knows.

`GenericTag::getTagId()` returns `-1`, because the class stands for no number in particular. The number
itself is in the head of the item: it is the additional information when that is 23 or less, and the
big-endian payload `getData()` returns otherwise.

```php
use CBOR\CBORObject;
use CBOR\Tag\GenericTag;

function tagNumberOf(GenericTag $tag): int
{
    $ai = $tag->getAdditionalInformation();
    if ($ai <= 23) {
        return $ai;
    }

    $data = (string) $tag->getData();

    return match ($ai) {
        CBORObject::LENGTH_1_BYTE => ord($data),
        CBORObject::LENGTH_2_BYTES => unpack('n', $data)[1],
        CBORObject::LENGTH_4_BYTES => unpack('N', $data)[1],
        CBORObject::LENGTH_8_BYTES => unpack('J', $data)[1],
    };
}

$decoded = $decoder->decode(StringStream::create(hex2bin('d904d201')));

$decoded instanceof GenericTag;   // true
tagNumberOf($decoded);            // 1234
$decoded->getValue();             // UnsignedIntegerObject, the tagged item
```

When a number matters to your application, give it a class of its own —
[writing a tag of your own](writing-a-tag.md) — and [register that class](registering.md) with the
decoder. The decoder then hands you that class instead of a `GenericTag`, and `getTagId()` answers
properly.
