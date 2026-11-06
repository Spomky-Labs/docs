---
description: Reading CBOR bytes back, and the bounds that keep an untrusted document affordable
---

# Decoding

A decoder reads a [stream](streams.md) and returns the object tree it holds.

```php
use CBOR\Decoder;
use CBOR\StringStream;

$binaryData = hex2bin('6548656c6c6f');
$stream = StringStream::create($binaryData);

$object = Decoder::create()->decode($stream);

if ($object instanceof TextStringObject) {
    echo $object->getValue();  // "Hello"
    echo $object->normalize(); // "Hello"
}
```

## Building a decoder

`Decoder::create()` with no argument knows every tag the library ships with and every simple value. A
decoder can also be given exactly what it should recognise, and nothing else:

```php
use CBOR\Decoder;
use CBOR\OtherObject\OtherObjectManager;
use CBOR\Tag\TagManager;

$tagManager = TagManager::create()
    ->add(TimestampTag::class)
    ->add(DatetimeTag::class);

$otherObjectManager = OtherObjectManager::create()
    ->add(TrueObject::class)
    ->add(FalseObject::class)
    ->add(NullObject::class);

$decoder = Decoder::create($tagManager, $otherObjectManager);
```

A tag number the manager does not know is not an error: it comes back as a
[`GenericTag`](../tags/registry.md#a-tag-the-library-does-not-know), which keeps the number and the value
without interpreting them. Registering your own classes is described in
[registering a tag](../tags/registering.md).

A decoder holds no state about the document it read, so build one once and reuse it.

## Limiting the nesting depth

Decoding is recursive: a deeply nested data item — thousands of nested arrays, maps or tags — can exhaust
the call stack. The decoder therefore rejects data nested deeper than `Decoder::DEFAULT_MAX_DEPTH`, 1000
levels, with an `InvalidArgumentException`.

When the data comes from an untrusted source, a much lower limit is wise:

```php
// Accept at most 32 levels of nested arrays, maps and tags
$decoder = Decoder::create(null, null, 32);
```

## The cost of a hostile document

Normalizing a decoded object turns it into native PHP values, and a few tags expand far beyond the bytes
they occupy. Two bounds keep that expansion proportionate to the input:

-   `DecimalFractionTag::MAX_ABSOLUTE_EXPONENT` and `BigFloatTag::MAX_ABSOLUTE_EXPONENT`, both 1024, cap
    the exponent of tags 4 and 5. Writing `10^e` down takes about `e` digits, so an unbounded exponent
    turns a six-byte item into kilobytes.
-   `UnsignedBigIntegerTag::MAX_BYTE_LENGTH` and `NegativeBigIntegerTag::MAX_BYTE_LENGTH`, both 256 bytes
    — a 2048-bit integer — cap the byte string of tags 2 and 3.

A value outside either bound is rejected with an `InvalidArgumentException`.

A map key is normalized as the map is built, so both bounds apply during `decode()` itself, not only when
you call `normalize()` later.

!!! warning "Install `ext-gmp` for untrusted input"

    Without it, `brick/math` converts the byte string of a big number to its decimal form in time
    quadratic in the length, which is several orders of magnitude slower than GMP. A document full of
    256-byte bignums is cheap to write and expensive to read.

## Telling what you got

The tree a decoder returns says what the document actually contained, so `instanceof` is how you read it:

```php
$object = $decoder->decode($stream);

// The major type
if ($object instanceof UnsignedIntegerObject) {
    echo 'Unsigned integer: ' . $object->getValue();
}

// A tag
if ($object instanceof TimestampTag) {
    echo 'Timestamp: ' . $object->normalize()->format('Y-m-d');
}

// Anything that gives a native value
if ($object instanceof Normalizable) {
    $phpValue = $object->normalize();
}

// All of it at once
$value = match (true) {
    $object instanceof TextStringObject => $object->getValue(),
    $object instanceof UnsignedIntegerObject => (int) $object->getValue(),
    $object instanceof ListObject => $object->normalize(),
    default => null,
};
```

Check the type before you trust the shape: a document from elsewhere holds what its sender chose, not what
your application expects.
