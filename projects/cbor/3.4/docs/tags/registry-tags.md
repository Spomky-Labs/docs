---
description: COSE and CWT, calendar dates, network addresses, typed arrays and the rest of the registry
---

# More tags of the registry

Beyond the tags [RFC 8949 defines itself](built-in.md), the library implements a good part of the IANA
registry: the COSE and CWT structures, calendar dates, network addresses, the typed arrays and their
shapes, and twenty more. All of them are registered in the decoder by default.

## COSE and CWT

The six COSE structures of [RFC 9052](https://datatracker.ietf.org/doc/html/rfc9052) and the CBOR Web
Token tag of [RFC 8392](https://datatracker.ietf.org/doc/html/rfc8392) that wraps them. Each one describes
the shape of the structure and gives access to its parts; **verifying a signature or a MAC is not done
here** and needs a COSE implementation such as
[web-auth/cose-lib](https://github.com/web-auth/cose-lib).

| Tag | Structure | Class | Content |
|-----|-----------|-------|---------|
| 16 | COSE_Encrypt0 | `CoseEncrypt0Tag` | [protected, unprotected, ciphertext] |
| 17 | COSE_Mac0 | `CoseMac0Tag` | [protected, unprotected, payload, tag] |
| 18 | COSE_Sign1 | `CoseSign1Tag` | [protected, unprotected, payload, signature] |
| 61 | CWT | `CwtTag` | a COSE structure, tagged or not, or a bare claims set |
| 96 | COSE_Encrypt | `CoseEncryptTag` | [protected, unprotected, ciphertext, recipients] |
| 97 | COSE_Mac | `CoseMacTag` | [protected, unprotected, payload, tag, recipients] |
| 98 | COSE_Sign | `CoseSignTag` | [protected, unprotected, payload, signatures] |

```php
use CBOR\Decoder;
use CBOR\StringStream;
use CBOR\Tag\CoseSign1Tag;

$object = Decoder::create()->decode(StringStream::create($encoded));

if ($object instanceof CoseSign1Tag) {
    // The protected header is signed as it was written, so it travels wrapped in a byte string.
    $algorithm = $object->getProtectedHeaderAsMap()->normalize()[1] ?? null;
    $payload = $object->getPayload();     // ByteStringObject, or NullObject when detached
    $signature = $object->getSignature();
}
```

Two shapes a stricter reading would turn away are accepted on purpose:

-   **a detached payload**, which COSE writes as `null`: the content travels out of band and only the
    signature comes with the structure;
-   **an absent protected header**, which COSE writes as an empty byte string:
    `getProtectedHeaderAsMap()` answers an empty `MapObject` rather than failing to parse zero bytes.

To build one, `createFromComponents()` takes the parts and serializes the protected header for you:

```php
$tag = CoseSign1Tag::createFromComponents(
    $protectedHeader,    // MapObject; encoded into the byte string COSE signs
    $unprotectedHeader,  // MapObject
    ByteStringObject::create($payload),
    ByteStringObject::create($signature)
);
```

## Calendar dates

A calendar day is not an instant: a birthday or an expiry date is the same day everywhere, and pinning it
to a moment moves it across a day boundary depending on where it is read.
[RFC 8943](https://datatracker.ietf.org/doc/html/rfc8943) gives it two tags of its own.

| Tag | Description | Class | Accepts |
|-----|-------------|-------|---------|
| 100 | Days since 1970-01-01 | `DateTag` | `UnsignedIntegerObject`, `NegativeIntegerObject` |
| 1004 | RFC 3339 full-date, `YYYY-MM-DD` | `DateStringTag` | `TextStringObject` |

```php
use CBOR\Tag\DateTag;
use CBOR\UnsignedIntegerObject;

$tag = DateTag::create(UnsignedIntegerObject::create(19737));
echo $tag->normalize()->format('Y-m-d'); // 2024-01-15
```

PHP has no date-only type, so both normalize to **midnight UTC** — the reading that keeps the day intact —
and neither is affected by the ambient time zone. A day that does not exist, `2013-02-30`, is rejected
rather than rolled over into the next month.

## Network addresses

| Tag | Description | Class | Accepts |
|-----|-------------|-------|---------|
| 52 | IPv4 address, prefix or zoned address | `Ipv4Tag` | `ByteStringObject`, or a two-item `ListObject` |
| 54 | IPv6 address, prefix or zoned address | `Ipv6Tag` | `ByteStringObject`, or a two-item `ListObject` |
| 260 | Network address: IPv4, IPv6 or MAC | `NetworkAddressTag` | a 4, 6 or 16 byte `ByteStringObject` |
| 261 | Network address prefix | `NetworkAddressPrefixTag` | a single-entry `MapObject` |

Tags 52 and 54 come from [RFC 9164](https://datatracker.ietf.org/doc/html/rfc9164) and carry three shapes
under one number, told apart by their first item: a byte string is an address, `[length, bytes]` is a
prefix whose trailing zero bytes may be left out, and `[bytes, zone]` is an address with the zone that
scopes it.

```php
use CBOR\Tag\Ipv6Tag;

echo Ipv6Tag::createFromAddress('2001:db8::1')->normalize(); // 2001:db8::1
// A prefix normalizes with its length, a zoned address with its zone:
// "2001:db8::/32", "fe80::1%eth0"
```

Tags 260 and 261 are the earlier form, which tells the family from the length of the byte string. RFC 9164
supersedes them: prefer 52 and 54 for anything new.

## Typed arrays

[RFC 8746](https://datatracker.ietf.org/doc/html/rfc8746) packs an array of numbers of one fixed type into
a single byte string: a megabyte of samples travels as a megabyte instead of as three. The tag number
gives the element type, so the only thing the content has to satisfy is being a whole number of elements
long.

| Tags | Element | Classes, in `CBOR\Tag\TypedArray` |
|------|---------|-----------------------------------|
| 64, 68 | uint8, uint8 clamped | `Uint8ArrayTag`, `Uint8ClampedArrayTag` |
| 65, 69 | uint16 big, little endian | `Uint16BigEndianArrayTag`, `Uint16LittleEndianArrayTag` |
| 66, 70 | uint32 big, little endian | `Uint32BigEndianArrayTag`, `Uint32LittleEndianArrayTag` |
| 67, 71 | uint64 big, little endian | `Uint64BigEndianArrayTag`, `Uint64LittleEndianArrayTag` |
| 72 | sint8 | `Sint8ArrayTag` |
| 73, 77 | sint16 big, little endian | `Sint16BigEndianArrayTag`, `Sint16LittleEndianArrayTag` |
| 74, 78 | sint32 big, little endian | `Sint32BigEndianArrayTag`, `Sint32LittleEndianArrayTag` |
| 75, 79 | sint64 big, little endian | `Sint64BigEndianArrayTag`, `Sint64LittleEndianArrayTag` |
| 80, 84 | binary16 big, little endian | `Float16BigEndianArrayTag`, `Float16LittleEndianArrayTag` |
| 81, 85 | binary32 big, little endian | `Float32BigEndianArrayTag`, `Float32LittleEndianArrayTag` |
| 82, 86 | binary64 big, little endian | `Float64BigEndianArrayTag`, `Float64LittleEndianArrayTag` |
| 83, 87 | binary128 big, little endian | `Float128BigEndianArrayTag`, `Float128LittleEndianArrayTag` |

```php
use CBOR\ByteStringObject;
use CBOR\Tag\TypedArray\Uint16BigEndianArrayTag;

$tag = Uint16BigEndianArrayTag::create(ByteStringObject::create("\x00\x01\x00\x02"));

count($tag);          // 2
$tag->normalize();    // [1, 2]
```

Normalized, they give a list of `int` or `float`. A uint64 above `PHP_INT_MAX` comes back as a decimal
string rather than as a negative integer.

!!! note "binary128 is the exception"

    PHP has no quadruple precision float, and returning a binary64 would quietly drop fifteen digits, so
    tags 83 and 87 do not implement `Normalizable`. Use `getChunks()`, which hands back the 16 bytes of
    each element.

### Arrays with a shape

The same RFC folds a flat array — a plain one or a typed array — into a shape, as `[dimensions, values]`.

| Tag | Order | Class |
|-----|-------|-------|
| 40 | Row-major, last index varies fastest | `RowMajorMultiDimensionalArrayTag` |
| 1040 | Column-major, first index varies fastest | `ColumnMajorMultiDimensionalArrayTag` |

```php
// 40([[2, 3], [1, 2, 3, 4, 5, 6]])
$tag->getDimensions();  // [2, 3]
$tag->normalize();      // [[1, 2, 3], [4, 5, 6]]
// The same values under tag 1040 fold the other way: [[1, 3, 5], [2, 4, 6]]
```

`normalize()` rejects a document whose dimensions do not account for exactly the number of values it
carries.

Tag 41, `HomogeneousArrayTag`, belongs to the same RFC. It is a hint that every item of an array has the
same type; the array normalizes as it would untagged, and homogeneity is not checked, since what counts as
"the same type" is the application's data model rather than CBOR's major types.

## The rest

| Tag | Description | Class | Accepts |
|-----|-------------|-------|---------|
| 25 | String reference | `StringReferenceTag` | `UnsignedIntegerObject` |
| 26 | Serialised Perl object | `PerlObjectTag` | `ListObject` opening with a text string |
| 27 | Serialised language-independent object | `LanguageIndependentObjectTag` | `ListObject` opening with a text string |
| 28 | Shareable value | `ShareableTag` | any object |
| 29 | Shared value reference | `SharedReferenceTag` | `UnsignedIntegerObject` |
| 30 | Rational number | `RationalNumberTag` | two-item `ListObject`, [numerator, denominator] |
| 35 | Regular expression | `RegexpTag` | `TextStringObject` |
| 37 | Binary UUID | `UuidTag` | a 16 byte `ByteStringObject` |
| 38 | Language-tagged string | `LanguageTaggedStringTag` | two-item `ListObject`, [language, text] |
| 39 | Identifier | `IdentifierTag` | any object |
| 42 | IPLD content identifier, a CID | `IpldContentIdentifierTag` | `ByteStringObject` |
| 63 | Encoded CBOR sequence | `CBORSequenceTag` | `ByteStringObject` |
| 256 | String reference namespace | `StringReferenceNamespaceTag` | any object |
| 257 | Binary MIME message | `BinaryMimeTag` | `ByteStringObject` |
| 258 | Mathematical finite set | `SetTag` | `ListObject` |
| 259 | Explicit map | `ExplicitMapTag` | `MapObject` |
| 1001 | Extended time | `ExtendedTimeTag` | `MapObject` |
| 1002 | Duration | `DurationTag` | `MapObject` |
| 1003 | Period | `PeriodTag` | `ListObject` |

A few of them are worth a word.

**Tag 37, a UUID**, normalizes to the canonical `8-4-4-4-12` form and can be built from it:

```php
use CBOR\Tag\UuidTag;

$tag = UuidTag::createFromUuidString('01234567-89ab-cdef-0123-456789abcdef');
echo $tag->normalize(); // 01234567-89ab-cdef-0123-456789abcdef
```

**Tag 30, a rational number**, normalizes to lowest terms, as `"numerator/denominator"` — or as the
numerator alone when the denominator reduces to 1. Either part may be a bignum
([tags 2 and 3](built-in.md#big-numbers)), which is the point of the tag: a ratio such as 1/3 has no exact
decimal or binary floating point form.

**Tag 63, a CBOR sequence**, is to a sequence what
[tag 24](built-in.md#tag-24-an-encoded-cbor-data-item) is to a single item. `getSequence()` decodes the
byte string into the items it holds:

```php
$items = $tag->getSequence(); // CBORObject[]
```

**Tag 258, a set**, returns its items in the order they were written. Nothing in CBOR keeps a duplicate
out of an array, so a repeated item is left for the application to notice — and, most often, to reject the
document over, since a set that carries one is not what it claims to be.

**Tags 25, 28, 29 and 256, string references and value sharing**, are recorded rather than resolved. The
table a reference points into is built while the whole document is read, which is outside the scope of any
single tag, so the index is returned as it stands and the marked value normalizes as it would untagged.

**Tags 1001, 1002 and 1003, [RFC 9581](https://datatracker.ietf.org/doc/html/rfc9581)**, are returned as
the map or array they are. The components they allow — a leap second, a time scale that is not UTC, a
resolution below the microsecond — do not all fit `DateTimeImmutable` or `DateInterval`, and flattening
them into one would drop whichever does not.
