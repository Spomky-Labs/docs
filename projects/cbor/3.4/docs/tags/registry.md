---
description: Which tag numbers the library implements, and what happens to the others
---

# The IANA registry

Tag numbers are held in the
[CBOR tags registry](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml) of IANA. The library
implements the ones below, and registers all of them in the decoder by default. The registry is open
ended, and most of what is missing from the table is specific to one application: any other number still
decodes, as a tag that keeps its number without interpreting it.

| Tag | Meaning | Class | Specification |
|-----|---------|-------|---------------|
| 0 | Date-time string, RFC 3339 | `DatetimeTag` | RFC 8949 § 3.4.1 |
| 1 | Epoch timestamp | `TimestampTag` | RFC 8949 § 3.4.2 |
| 2 | Unsigned bignum | `UnsignedBigIntegerTag` | RFC 8949 § 3.4.3 |
| 3 | Negative bignum | `NegativeBigIntegerTag` | RFC 8949 § 3.4.3 |
| 4 | Decimal fraction | `DecimalFractionTag` | RFC 8949 § 3.4.4 |
| 5 | Bigfloat | `BigFloatTag` | RFC 8949 § 3.4.4 |
| 16 | COSE_Encrypt0 | `CoseEncrypt0Tag` | RFC 9052 |
| 17 | COSE_Mac0 | `CoseMac0Tag` | RFC 9052 |
| 18 | COSE_Sign1 | `CoseSign1Tag` | RFC 9052 |
| 21 | base64url expected | `Base64UrlEncodingTag` | RFC 8949 § 3.4.5.2 |
| 22 | base64 expected | `Base64EncodingTag` | RFC 8949 § 3.4.5.2 |
| 23 | base16 expected | `Base16EncodingTag` | RFC 8949 § 3.4.5.2 |
| 24 | Encoded CBOR data item | `CBOREncodingTag` | RFC 8949 § 3.4.5.1 |
| 25 | String reference | `StringReferenceTag` | stringref |
| 26 | Serialised Perl object | `PerlObjectTag` | IANA registry |
| 27 | Serialised language-independent object | `LanguageIndependentObjectTag` | IANA registry |
| 28 | Shareable value | `ShareableTag` | value sharing |
| 29 | Shared value reference | `SharedReferenceTag` | value sharing |
| 30 | Rational number | `RationalNumberTag` | IANA registry |
| 32 | URI | `UriTag` | RFC 8949 § 3.4.5.3 |
| 33 | base64url encoded text | `Base64UrlTag` | RFC 8949 § 3.4.5.2 |
| 34 | base64 encoded text | `Base64Tag` | RFC 8949 § 3.4.5.2 |
| 35 | Regular expression | `RegexpTag` | RFC 7049 |
| 36 | MIME message | `MimeTag` | RFC 8949 § 3.4.5.3 |
| 37 | Binary UUID | `UuidTag` | RFC 4122 |
| 38 | Language-tagged string | `LanguageTaggedStringTag` | IANA registry |
| 39 | Identifier | `IdentifierTag` | IANA registry |
| 40 | Multi-dimensional array, row-major | `RowMajorMultiDimensionalArrayTag` | RFC 8746 |
| 41 | Homogeneous array | `HomogeneousArrayTag` | RFC 8746 |
| 42 | IPLD content identifier | `IpldContentIdentifierTag` | IANA registry |
| 52 | IPv4 address or prefix | `Ipv4Tag` | RFC 9164 |
| 54 | IPv6 address or prefix | `Ipv6Tag` | RFC 9164 |
| 61 | CBOR Web Token | `CwtTag` | RFC 8392 |
| 63 | Encoded CBOR sequence | `CBORSequenceTag` | RFC 8742 |
| 64 to 87 | Typed arrays | `CBOR\Tag\TypedArray\*` | RFC 8746 |
| 96 | COSE_Encrypt | `CoseEncryptTag` | RFC 9052 |
| 97 | COSE_Mac | `CoseMacTag` | RFC 9052 |
| 98 | COSE_Sign | `CoseSignTag` | RFC 9052 |
| 100 | Date, days since the epoch | `DateTag` | RFC 8943 |
| 256 | String reference namespace | `StringReferenceNamespaceTag` | stringref |
| 257 | Binary MIME message | `BinaryMimeTag` | IANA registry |
| 258 | Mathematical finite set | `SetTag` | IANA registry |
| 259 | Explicit map | `ExplicitMapTag` | IANA registry |
| 260 | Network address, legacy | `NetworkAddressTag` | RFC 9164 app. A |
| 261 | Network address prefix, legacy | `NetworkAddressPrefixTag` | RFC 9164 app. A |
| 1001 | Extended time | `ExtendedTimeTag` | RFC 9581 |
| 1002 | Duration | `DurationTag` | RFC 9581 |
| 1003 | Period | `PeriodTag` | RFC 9581 |
| 1004 | Date string | `DateStringTag` | RFC 8943 |
| 1040 | Multi-dimensional array, column-major | `ColumnMajorMultiDimensionalArrayTag` | RFC 8746 |
| 55799 | Self-described CBOR | `CBORTag` | RFC 8949 § 3.4.6 |

Every class is in the `CBOR\Tag` namespace, the typed arrays in `CBOR\Tag\TypedArray`. The tags of
RFC 8949 itself are described in [the built-in tags](built-in.md), the others in
[more tags of the registry](registry-tags.md).

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
