---
description: Building and reading a distinguished name, the RFC 2253 string form, and multi-valued RDNs.
---

# Distinguished names

## From a string

The quickest way in, and what you will use most:

```php
use SpomkyLabs\Pki\X501\ASN1\Name;

$name = Name::fromString('cn=example.com, o=ACME Ltd, c=FR');
```

The short names come from the LDAP attribute registry and are matched case-insensitively, so `CN`, `cn`
and `commonName` are the same type. An OID works too, for a type with no short name:

```php
$name = Name::fromString('2.5.4.3=example.com');
```

A name the parser does not recognise raises `OutOfBoundsException` with the name in the message.

### Escaping

RFC 2253 reserves `,` `=` `+` `<` `>` `#` `;`, and a value holding one has to escape it. `DNParser` does
it for you:

```php
use SpomkyLabs\Pki\X501\DN\DNParser;

$value = DNParser::escapeString('ACME Ltd, Paris');     // ACME Ltd\, Paris
$name = Name::fromString('o=' . $value . ',c=FR');
```

!!! warning "Never build a DN by concatenating values you did not escape"

    An unescaped comma in a value does not fail: it ends the RDN and starts another one, so
    `o=ACME Ltd, Paris` parses as two attributes and the name you get is not the name you meant. Escape
    every value you interpolate, or build the name from objects.

A value may also be written as a hex string — `cn=#0C0B6578616D706C652E636F6D` — which the parser reads
as a DER element and keeps as it was. That is how a value whose string type matters survives a round
trip.

## From objects

Building a name from objects skips the string form, and its escaping, entirely:

```php
use SpomkyLabs\Pki\X501\ASN1\AttributeValue\CommonNameValue;
use SpomkyLabs\Pki\X501\ASN1\AttributeValue\CountryNameValue;
use SpomkyLabs\Pki\X501\ASN1\AttributeValue\OrganizationNameValue;
use SpomkyLabs\Pki\X501\ASN1\Name;
use SpomkyLabs\Pki\X501\ASN1\RDN;

$name = Name::create(
    RDN::fromAttributeValues(CountryNameValue::create('FR')),
    RDN::fromAttributeValues(OrganizationNameValue::create('ACME Ltd, Paris')),
    RDN::fromAttributeValues(CommonNameValue::create('example.com'))
);

echo $name->toString();   // cn=example.com,o=ACME Ltd\, Paris,c=FR
```

Note the order: `Name::create()` takes the RDNs in **ASN.1 order**, outermost first, which is the reverse
of how the string form reads them.

## Reading one

```php
$name = $certificate->tbsCertificate()->subject();

echo $name->toString();                         // the RFC 2253 string
count($name);                                   // how many RDNs
$name->all();                                   // RDN[], in ASN.1 order

$name->firstValueOf('cn')->stringValue();       // the first common name
$name->countOfType('cn');                       // how many there are
```

`firstValueOf()` throws `RangeException` when the type is absent, and when one RDN carries it more than
once — an ambiguous question gets an error rather than an arbitrary answer. Ask first:

```php
if ($name->countOfType('cn') === 1) {
    $cn = $name->firstValueOf('cn')->stringValue();
}
```

Walking the structure yourself:

```php
foreach ($name as $rdn) {
    foreach ($rdn as $attributeTypeAndValue) {
        $attributeTypeAndValue->oid();                      // "2.5.4.3"
        $attributeTypeAndValue->type()->typeName();         // "commonName"
        $attributeTypeAndValue->value()->stringValue();     // "example.com"
    }
}
```

## Multi-valued RDNs

One RDN may hold several attributes, which means one step of the name needs all of them to be
unambiguous:

```php
use SpomkyLabs\Pki\X501\ASN1\AttributeValue\CommonNameValue;
use SpomkyLabs\Pki\X501\ASN1\AttributeValue\OrganizationalUnitNameValue;

$rdn = RDN::fromAttributeValues(
    CommonNameValue::create('J. Smith'),
    OrganizationalUnitNameValue::create('Sales')
);

echo $rdn->toString();   // cn=J. Smith+ou=Sales
```

The `+` is how RFC 2253 joins them, and `Name::fromString()` reads it back. `$rdn->allOf('cn')` returns
every value of one type within the RDN.

Rare in practice, and worth knowing about for one reason: it is where name comparison stops being a
string comparison. See [Comparing names](comparing-names.md).

## The empty name

`Name::create()` with no arguments is a valid, empty name. RFC 5280 allows it for a subject, provided
the certificate carries a `subjectAltName` marked critical. `TBSCertificate::fromCSR()` starts from one
for the issuer, which `withIssuerCertificate()` then fills in.

## To and from ASN.1

```php
$sequence = $name->toASN1();
$name = Name::fromASN1($sequence);

$der = $name->toASN1()->toDER();
```

`Name` has no `fromDER()`: decode the `Sequence` first.
