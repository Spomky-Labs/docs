---
description: Every ASN.1 type PKI Framework implements, the PHP it maps to, and the ones with a shape of their own.
---

# The types

Every universal type of X.690 has a class under `SpomkyLabs\Pki\ASN1\Type`. Each is built with
`create()`, each knows its tag, and each is immutable.

## Primitive types

| ASN.1 type | Class | Built from | Read with |
|---|---|---|---|
| `BOOLEAN` | `Primitive\Boolean` | `bool` | `value(): bool` |
| `INTEGER` | `Primitive\Integer` | `int`, numeric `string`, `BigInteger` | `number(): string`, `intNumber(): int`, `getValue(): BigInteger` |
| `ENUMERATED` | `Primitive\Enumerated` | as `Integer` | as `Integer` |
| `BIT STRING` | `Primitive\BitString` | `string` and a count of unused bits | `string()`, `numBits()`, `testBit()`, `range()` |
| `OCTET STRING` | `Primitive\OctetString` | `string` | `string()` |
| `NULL` | `Primitive\NullType` | nothing | — |
| `OBJECT IDENTIFIER` | `Primitive\ObjectIdentifier` | dotted `string` | `oid(): string` |
| `RELATIVE-OID` | `Primitive\RelativeOID` | dotted `string` | `oid(): string` |
| `ObjectDescriptor` | `Primitive\ObjectDescriptor` | `string` | `descriptor(): string` |
| `REAL` | `Primitive\Real` | `fromFloat()`, `fromString()` | `floatVal()`, `mantissa()`, `exponent()`, `base()` |
| `EOC` | `Primitive\EOC` | nothing | — |

An `INTEGER` never comes back as a PHP integer unless you ask for one. A serial number or an RSA modulus
does not fit, so `number()` returns a decimal string and `getValue()` a
[brick/math](https://github.com/brick/math) `BigInteger`. `intNumber()` throws when the value does not
fit in a PHP integer.

## String types

Each carries the character set its tag promises, and refuses a string outside it.

| ASN.1 type | Class |
|---|---|
| `UTF8String` | `Primitive\UTF8String` |
| `PrintableString` | `Primitive\PrintableString` |
| `NumericString` | `Primitive\NumericString` |
| `IA5String` | `Primitive\IA5String` |
| `VisibleString` | `Primitive\VisibleString` |
| `GeneralString` | `Primitive\GeneralString` |
| `GraphicString` | `Primitive\GraphicString` |
| `BMPString` | `Primitive\BMPString` |
| `UniversalString` | `Primitive\UniversalString` |
| `T61String` | `Primitive\T61String` |
| `VideotexString` | `Primitive\VideotexString` |
| `CharacterString` | `Primitive\CharacterString` |

They all extend `BaseString`, so `string()` gives the value and `(string)` works. The `StringType`
interface marks them, and the time types with them, for a signature that takes any of them.

```php
use SpomkyLabs\Pki\ASN1\Type\Primitive\PrintableString;

$string = PrintableString::create('FR');
echo $string->string();    // FR
echo $string;              // FR
```

A `PrintableString` built from a value its character set forbids throws rather than encode something a
peer would read differently.

## Time types

| ASN.1 type | Class |
|---|---|
| `UTCTime` | `Primitive\UTCTime` |
| `GeneralizedTime` | `Primitive\GeneralizedTime` |

Both extend `BaseTime`: `create(DateTimeImmutable)` in, `dateTime(): DateTimeImmutable` out, and
`fromString()` for the ASN.1 spelling.

```php
use SpomkyLabs\Pki\ASN1\Type\Primitive\GeneralizedTime;

$time = GeneralizedTime::create(new DateTimeImmutable('2030-01-01 12:00:00', new DateTimeZone('UTC')));
echo $time->string();     // 20300101120000Z
```

`UTCTime` writes a two-digit year, which is why RFC 5280 asks for it only before 2050 and
`GeneralizedTime` after. `UTCTime::CENTURY_PIVOT` is where the library splits the two centuries when it
reads one. [`Time`](../certificates/reading-a-certificate.md#validity) in the X.509 layer picks the right
one for you.

## Constructed types

| ASN.1 type | Class |
|---|---|
| `SEQUENCE`, `SEQUENCE OF` | `Constructed\Sequence` |
| `SET`, `SET OF` | `Constructed\Set` |
| a string in constructed form | `Constructed\ConstructedString` |

```php
use SpomkyLabs\Pki\ASN1\Type\Constructed\Set;
use SpomkyLabs\Pki\ASN1\Type\Primitive\Integer;

$set = Set::create(Integer::create(3), Integer::create(1));
$set = $set->sortedSetOf();   // DER requires the members of a SET OF to be sorted
```

`ConstructedString` is a string encoded as a sequence of fragments, which BER allows and DER does not.
The library reads one and gives you `strings()`, the fragments, or `string()`, the whole value.

## Pseudotypes

Three tags are not ASN.1 types but expectations you can pass to `expectType()`:

| Constant | Matches |
|---|---|
| `Element::TYPE_STRING` | any string type |
| `Element::TYPE_TIME` | `UTCTime` or `GeneralizedTime` |
| `Element::TYPE_CONSTRUCTED_STRING` | a string in constructed form |

```php
$element->expectType(Element::TYPE_STRING);
```

## Bit flags

A `BIT STRING` that carries named flags — `keyUsage`, for one — is easier to read through `Flags`:

```php
use SpomkyLabs\Pki\ASN1\Util\Flags;

$flags = Flags::fromBitString($bitString, 9);
$flags->test(0);           // the first bit, as the specification numbers them
echo $flags->string();     // the bits as a byte string
```

The extensions that carry flags already do this for you: see
[`KeyUsageExtension`](../certificates/extensions.md#key-usage).
