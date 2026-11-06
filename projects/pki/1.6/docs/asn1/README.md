---
description: 'The ASN.1 layer of PKI Framework: elements, DER, and the UnspecifiedType that makes you say what you expected.'
---

# ASN.1 and DER

Everything in a public key infrastructure is an ASN.1 structure encoded with the Distinguished Encoding
Rules of [X.690](https://www.itu.int/rec/T-REC-X.690). `SpomkyLabs\Pki\ASN1` is that layer, and the rest
of the library is built on it.

You rarely need it to read a certificate — [`Certificate`](../certificates/reading-a-certificate.md) does
that for you. You need it when you meet a structure the library does not model: a private extension, an
`OtherName`, an attribute whose syntax is yours.

## Elements

Every type is an `Element`. An element knows its tag and can encode itself:

```php
use SpomkyLabs\Pki\ASN1\Element;
use SpomkyLabs\Pki\ASN1\Type\Constructed\Sequence;
use SpomkyLabs\Pki\ASN1\Type\Primitive\Integer;
use SpomkyLabs\Pki\ASN1\Type\Primitive\ObjectIdentifier;
use SpomkyLabs\Pki\ASN1\Type\Primitive\UTF8String;

$sequence = Sequence::create(
    ObjectIdentifier::create('1.3.6.1.4.1.99999.1'),
    Integer::create(42),
    UTF8String::create('hello')
);

$der = $sequence->toDER();
$again = Element::fromDER($der);

$again->tag() === Element::TYPE_SEQUENCE;   // true
```

There is no constructor to call: every type is built with `create()`, and decoded with `fromDER()`.

## UnspecifiedType

Decoding gives back something whose type is not known until you look at it. Rather than hand you an
`Element` to test by hand, the library hands you an `UnspecifiedType`: a wrapper whose `as*()` methods
each assert one type and return it.

```php
use SpomkyLabs\Pki\ASN1\Type\UnspecifiedType;

$element = UnspecifiedType::fromDER($der);

$sequence = $element->asSequence();              // UnexpectedValueException if it is not one
$oid = $sequence->at(0)->asObjectIdentifier();   // at() returns an UnspecifiedType too
$count = $sequence->at(1)->asInteger()->intNumber();
$text = $sequence->at(2)->asUTF8String()->string();
```

`Structure::at()` returns an `UnspecifiedType`, so reading into a structure reads as a chain of
assertions. Each one throws `UnexpectedValueException` when the material is not shaped the way the page
of the specification says it is — which is what you want when the material came from outside.

`$element->asUnspecified()` goes the other way, from an `Element` you already hold.

## Structures

`Sequence` and `Set` extend `Structure`, which is `Countable` and `IteratorAggregate`, and immutable like
everything else:

```php
$sequence = Sequence::create(Integer::create(1));

$sequence = $sequence->withAppended(Integer::create(2));
$sequence = $sequence->withReplaced(0, Integer::create(0));
$sequence = $sequence->withoutElement(1);

count($sequence);                 // 1
$sequence->has(0, Element::TYPE_INTEGER);  // true: present, and of that type
```

`Structure::explodeDER()` splits the DER of a structure into the DER of each of its children, without
decoding them.

## What to read next

- [The types](the-types.md) — every ASN.1 type the library implements, and the PHP it maps to.
- [Encoding and decoding](encoding-and-decoding.md) — DER in and out, offsets, `DERData`, indefinite
  length.
- [Tagging](tagging.md) — implicit and explicit tags, context-specific, application and private classes.
- [Decoding untrusted input](untrusted-input.md) — the limits to set before you decode what a stranger
  sent.
