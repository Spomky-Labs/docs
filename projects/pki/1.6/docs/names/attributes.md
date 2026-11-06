---
description: Attribute types and values, the collections that hold them, and writing a value class of your own.
---

# Attributes

An attribute is a type and one or more values. The same structure appears in a distinguished name, in the
extension request of a certification request, in the `subjectDirectoryAttributes` extension, and as the
payload of an attribute certificate.

## Types

`AttributeType` wraps an OID and knows the short names of the standard types:

```php
use SpomkyLabs\Pki\X501\ASN1\AttributeType;

$type = AttributeType::fromName('cn');
$type->oid();        // "2.5.4.3"
$type->typeName();   // "commonName"

$type = AttributeType::create('2.5.4.3');
AttributeType::attrNameToOID('emailAddress');   // "1.2.840.113549.1.9.1"
```

The table covers X.520 (`2.5.4.*`), the LDAP attributes of RFC 4519 and RFC 2798 — `uid`, `mail`, `dc`,
`memberOf` — and the PKCS #9 `emailAddress`. Names are matched case-insensitively, and several types have
aliases: `mail` is also `rfc822Mailbox`, `dc` is also `domainComponent`, `email` is also `emailAddress`
and `pkcs9email`. An OID passed where a name is expected is returned as it is.

`typeName()` falls back to the OID for a type with no entry, so it is always safe to print.

## Values

| Class, under `ASN1\AttributeValue` | Type |
|---|---|
| `CommonNameValue` | `cn` |
| `SurnameValue` | `sn` |
| `GivenNameValue` | `givenName` |
| `NameValue` | `name` |
| `PseudonymValue` | `pseudonym` |
| `TitleValue` | `title` |
| `DescriptionValue` | `description` |
| `OrganizationNameValue` | `o` |
| `OrganizationalUnitNameValue` | `ou` |
| `LocalityNameValue` | `l` |
| `StateOrProvinceNameValue` | `st` |
| `CountryNameValue` | `c` |
| `SerialNumberValue` | `serialNumber` |
| `UnknownAttributeValue` | anything else |

Each is built with `create()` and read with `stringValue()`:

```php
use SpomkyLabs\Pki\X501\ASN1\AttributeValue\CommonNameValue;

$value = CommonNameValue::create('example.com');
$value->stringValue();      // "example.com"
$value->oid();              // "2.5.4.3"
$value->rfc2253String();    // the escaped string form
echo $value;                // the same as stringValue()
```

### The string type a value is written in

Most of these are `DirectoryString` values, which means their ASN.1 type is a choice: `UTF8String`,
`PrintableString`, `BMPString`, `UniversalString` or `TeletexString`. `create()` writes a `UTF8String`
unless you say otherwise:

```php
use SpomkyLabs\Pki\X501\ASN1\AttributeValue\Feature\DirectoryString;

$value = CommonNameValue::create('example.com', DirectoryString::PRINTABLE);
```

Three types are not a directory string and are always written as a `PrintableString`: `countryName`,
`serialNumber` and `dnQualifier`. `Name::fromString()` applies that rule for you — which is why a country
code round-trips as a `PrintableString` and a common name as a `UTF8String`.

!!! note "The string type is part of the encoding, not of the meaning"

    Two names that differ only in the string type of a value are still equal, because comparison
    transcodes before it compares. See [Comparing names](comparing-names.md). The type still matters for
    an exact byte comparison, and for a peer that re-encodes what you sent.

### Values of an unknown type

An attribute whose OID has no class comes back as `UnknownAttributeValue`, which keeps the element as it
was. Nothing is lost, and nothing throws:

```php
$value->oid();           // the OID you were given
$value->stringValue();   // the element, as a string where that makes sense
```

If you later write a class for that type, `Attribute::castValues()` converts in place:

```php
$attribute = $attribute->castValues(MyAttributeValue::class);
```

The class must derive from `AttributeValue` and declare the same OID.

## Collections

`Attribute` holds a type and its values:

```php
use SpomkyLabs\Pki\X501\ASN1\Attribute;

$attribute = Attribute::fromAttributeValues(CommonNameValue::create('example.com'));

$attribute->type();      // AttributeType
$attribute->oid();
$attribute->first();     // the first value
$attribute->values();    // all of them
count($attribute);
```

Two collections hold attributes, and they differ only in the ASN.1 they encode to:

| Class, under `ASN1\Collection` | Encodes to |
|---|---|
| `SequenceOfAttributes` | a `SEQUENCE OF` |
| `SetOfAttributes` | a `SET OF` |

Both share the `AttributeCollection` API:

```php
$attributes->has('cn');
$attributes->firstOf('cn');          // an Attribute
$attributes->allOf('cn');            // Attribute[]
$attributes->all();
$attributes = $attributes->withAdditional($attribute);
$attributes = $attributes->withUnique($attribute);   // replaces any attribute of the same type
count($attributes);

foreach ($attributes as $attribute) {
}
```

`withUnique()` is what you want for an attribute that must appear once: it replaces rather than appends.

## Writing a value class

Extend `AttributeValue`, or `DirectoryString` when the syntax is a directory string, and implement the
four abstract methods plus `fromASN1()`:

```php
use SpomkyLabs\Pki\ASN1\Element;
use SpomkyLabs\Pki\ASN1\Type\Primitive\UTF8String;
use SpomkyLabs\Pki\ASN1\Type\UnspecifiedType;
use SpomkyLabs\Pki\X501\ASN1\AttributeValue\AttributeValue;
use SpomkyLabs\Pki\X501\MatchingRule\CaseIgnoreMatch;
use SpomkyLabs\Pki\X501\MatchingRule\MatchingRule;

final class EmployeeNumberValue extends AttributeValue
{
    public const OID = '1.3.6.1.4.1.99999.1';

    private function __construct(private readonly string $value)
    {
        parent::__construct(self::OID);
    }

    public static function create(string $value): self
    {
        return new self($value);
    }

    public static function fromASN1(UnspecifiedType $el): self
    {
        return self::create($el->asUTF8String()->string());
    }

    public function toASN1(): Element
    {
        return UTF8String::create($this->value);
    }

    public function stringValue(): string
    {
        return $this->value;
    }

    public function equalityMatchingRule(): MatchingRule
    {
        return CaseIgnoreMatch::create(Element::TYPE_UTF8_STRING);
    }

    public function rfc2253String(): string
    {
        return $this->value;
    }
}
```

`equalityMatchingRule()` is what [name comparison](comparing-names.md) uses, so choosing it is choosing
how two of your values compare. Then `toAttribute()` and `toAttributeTypeAndValue()` come for free from
the base class.
