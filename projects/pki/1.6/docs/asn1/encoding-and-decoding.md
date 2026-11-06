---
description: DER in and out, reading several elements from one string, and carrying an encoding you do not want to decode.
---

# Encoding and decoding

The library speaks the Distinguished Encoding Rules. DER is BER with every choice removed — one encoding
per value — which is what makes a signature over a structure meaningful.

## Out

`toDER()` on any element:

```php
use SpomkyLabs\Pki\ASN1\Type\Constructed\Sequence;
use SpomkyLabs\Pki\ASN1\Type\Primitive\Integer;

$der = Sequence::create(Integer::create(1), Integer::create(2))->toDER();
```

Every structure of the X.509 layer has a `toASN1()` that gives you its `Sequence`, so `toDER()` follows
from it:

```php
$der = $certificate->toASN1()->toDER();   // the same bytes as $certificate->toDER()
```

## In

`Element::fromDER()` decodes one element:

```php
use SpomkyLabs\Pki\ASN1\Element;

$element = Element::fromDER($der);
```

Called on a concrete class, it also asserts the type:

```php
use SpomkyLabs\Pki\ASN1\Type\Constructed\Sequence;

$sequence = Sequence::fromDER($der);   // UnexpectedValueException if the data is not a SEQUENCE
```

Anything malformed raises `DecodeException`, and nothing else escapes `fromDER()`: the type-specific
decoders reach into large-number arithmetic, into constructors and into string validation, any of which
may signal malformed input in its own way, and the exception is normalised on the way out with the
original kept as its previous.

```php
use SpomkyLabs\Pki\ASN1\Exception\DecodeException;

try {
    $element = Element::fromDER($bytes);
} catch (DecodeException $e) {
    // not DER, or not DER shaped the way this type is
}
```

## Several elements in one string

`fromDER()` takes an offset by reference and moves it past what it read, so a concatenation is read in a
loop:

```php
$offset = 0;
$elements = [];

while ($offset < strlen($der)) {
    $elements[] = Element::fromDER($der, $offset);
}
```

To split a structure without decoding its children, `Structure::explodeDER()` returns the DER of each
one:

```php
use SpomkyLabs\Pki\ASN1\Type\Structure;

foreach (Structure::explodeDER($der) as $childDer) {
    // one encoded child at a time
}
```

## Carrying an encoding you do not want to decode

`DERData` is an element whose content is DER you already hold. It encodes to exactly those bytes and
decodes nothing:

```php
use SpomkyLabs\Pki\ASN1\DERData;
use SpomkyLabs\Pki\ASN1\Type\Constructed\Sequence;

$sequence = Sequence::create(DERData::create($opaqueDer));
```

Use it to put a structure the library does not model inside one it does — the value of a private
extension, for instance — without a round trip through types you would have to write.

## Indefinite length

BER allows a constructed element to declare no length and end with an end-of-contents marker. DER does
not. The library reads both and lets you ask and set:

```php
$element->hasIndefiniteLength();              // what was read
$element = $element->withIndefiniteLength();  // encode it that way
```

Leave it alone for anything you sign or send: a structure whose length is indefinite is not DER, and a
verifier that re-encodes it will not get your bytes back.

## Tag checks

```php
$element->tag();                            // the tag number
$element->isType(Element::TYPE_SEQUENCE);   // a question
$element->expectType(Element::TYPE_SEQUENCE); // an assertion, throws otherwise
$element->isTagged();                       // not a universal type
Element::tagToName(Element::TYPE_SEQUENCE); // "SEQUENCE", for an error message
```

`expectType()` accepts the [pseudotypes](the-types.md#pseudotypes) as well as the real ones.
