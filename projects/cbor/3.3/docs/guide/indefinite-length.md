---
description: Strings, lists and maps whose length is not known in advance
---

# Indefinite-length objects

CBOR can encode a string, an array or a map without announcing its length: the item opens, its parts
follow, and a break marks the end. It is what lets a producer start writing before it knows how much there
is to write.

Four classes carry that form, and build up the same way as their definite-length counterparts:

```php
// Indefinite-length text string
$text = IndefiniteLengthTextStringObject::create()
    ->append('Hello')
    ->append(' ')
    ->append('World');

echo $text->getValue(); // "Hello World"

// Indefinite-length byte string
$bytes = IndefiniteLengthByteStringObject::create()
    ->append('part1')
    ->append('part2');

// Indefinite-length list
$list = IndefiniteLengthListObject::create()
    ->add(UnsignedIntegerObject::create(1))
    ->add(UnsignedIntegerObject::create(2));

// Indefinite-length map
$map = IndefiniteLengthMapObject::create()
    ->add(TextStringObject::create('key1'), UnsignedIntegerObject::create(1))
    ->add(TextStringObject::create('key2'), UnsignedIntegerObject::create(2));
```

Indefinite-length lists and maps are `Countable`, just like their definite-length counterparts, so
`count()` works whichever encoding a document uses:

```php
$decoded = $decoder->decode(StringStream::create($data));
$count = count($decoded);
```

The same holds for normalization and iteration: code that reads a decoded document does not need to know
which of the two forms it was written in. The decoder returns the class matching what it read, and both
classes answer the same calls.
