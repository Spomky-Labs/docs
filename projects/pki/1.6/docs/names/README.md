---
description: 'The X.501 and X.520 layer: distinguished names, attributes, general names, and the comparison rules behind them.'
---

# Names and attributes

A certificate names two parties — the subject and the issuer — and names them with a *distinguished
name*, a structure from the directory specifications rather than from X.509. `SpomkyLabs\Pki\X501`
implements it, after [X.501](https://www.itu.int/rec/T-REC-X.501) and
[X.520](https://www.itu.int/rec/T-REC-X.520).

```php
use SpomkyLabs\Pki\X501\ASN1\Name;

$name = Name::fromString('cn=example.com, o=ACME Ltd, c=FR');

echo $name->toString();                                       // cn=example.com,o=ACME Ltd,c=FR
echo $name->firstValueOf('cn')->stringValue();                // example.com
```

## The shape of a name

A `Name` is a sequence of `RDN`s — relative distinguished names — and each `RDN` is a set of
`AttributeTypeAndValue` pairs. Three levels, because a name is a path through a directory and one step of
that path may need more than one attribute to be unambiguous.

```
Name            cn=example.com, o=ACME Ltd, c=FR
└── RDN         c=FR
    └── ATV     type 2.5.4.6 (countryName), value "FR"
```

Almost every RDN holds exactly one attribute, so the nesting is invisible most of the time. It stops
being invisible when you compare two names: see [Comparing names](comparing-names.md).

!!! note "The string form is written outermost-last"

    `toString()` follows RFC 2253: the RDNs come out in reverse order, so the most specific part is
    written first. `cn=example.com,o=ACME Ltd,c=FR` is a name whose first RDN — in the ASN.1 — is `c=FR`.
    `all()` gives the RDNs in ASN.1 order, not in string order.

## The pieces

| Class | Is |
|---|---|
| `ASN1\Name` | the whole name |
| `ASN1\RDN` | one step: a `SET` of attribute type and value pairs |
| `ASN1\AttributeTypeAndValue` | a type and its value |
| `ASN1\AttributeType` | the type, an OID with a known short name |
| `ASN1\AttributeValue\*` | the value, one class per standard type |
| `DN\DNParser` | the RFC 2253 string form, in and out |
| `MatchingRule\*`, `StringPrep\*` | the comparison rules |

## Attributes elsewhere

The same `Attribute` machinery carries attributes that are not part of a name:

- the extension request of a [certification request](../certification-requests/creating-a-request.md);
- the `subjectDirectoryAttributes` extension of a certificate;
- the attributes an [attribute certificate](../attribute-certificates/README.md) exists to carry.

See [Attributes](attributes.md).

## Names in extensions

A DN is not the only way a certificate names something. `subjectAltName`, `issuerAltName`,
`nameConstraints` and the attribute certificate structures use `GeneralName`, which holds a DNS name, an
email address, a URI, an IP address — or a DN, as one choice among several. See
[General names](general-names.md).

## What to read next

- [Distinguished names](distinguished-names.md) — building and reading one, the string form, the escaping.
- [Attributes](attributes.md) — the standard types, the value classes, collections.
- [General names](general-names.md) — the nine choices and what each one holds.
- [Comparing names](comparing-names.md) — why `==` is wrong and what `equals()` does instead.
