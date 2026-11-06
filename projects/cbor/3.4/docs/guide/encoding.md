---
description: From a PHP value, or from objects you build yourself, to CBOR bytes
---

# Encoding

There are two ways round. `Encoder` takes a native PHP value and hands back the bytes; building the
objects yourself takes longer and lets you say exactly what goes on the wire.

## From PHP values

```php
use CBOR\Encoder;

$encoder = new Encoder();

$encoder->encode(['name' => 'Alice', 'age' => 30]);
// a2 646e616d65 65416c696365 63616765 181e — a map of two entries

$encoder->encode([1, 2, 3]);   // 83 01 02 03 — an array
$encoder->encode('héllo');     // 66 … — a text string: the string is valid UTF-8
$encoder->encode("\x00\xff");  // 42 00ff — a byte string: this one is not
$encoder->encode(1.5);         // fb … — a double
$encoder->encode(null);        // f6
```

The mapping it applies:

| PHP | CBOR |
|-----|------|
| `int` | unsigned or negative integer, by sign |
| `float` | double precision float |
| `string` that is valid UTF-8 | text string |
| any other `string` | byte string |
| a list array | array |
| any other array | map |
| `true`, `false`, `null` | the matching simple value |
| a `CBORObject` | itself, untouched |

Anything else — an object, an enum, a resource — raises an `InvalidArgumentException`. The last row is
what makes the two ways round meet: an object you built by hand can sit inside an array you hand to
`encode()`, which is how a [tagged value](../tags/overview.md) joins an otherwise plain structure.

```php
use CBOR\Tag\TimestampTag;
use CBOR\UnsignedIntegerObject;

$encoder->encode([
    'temperature' => 23,
    'at' => TimestampTag::create(UnsignedIntegerObject::create(time())),
]);
```

Five flags change how it writes, combined with `|` in the second argument:

```php
$encoder->encode(1.5, Encoder::FLOAT_FORMAT_SINGLE_PRECISION);  // fa 3fc00000, four bytes instead of eight
$encoder->encode([1, 2], Encoder::INDEFINITE_LIST_LENGTH);      // 9f 01 02 ff
$encoder->encode(['a' => [1]], Encoder::INDEFINITE_MAP_LENGTH | Encoder::INDEFINITE_LIST_LENGTH);
```

`FLOAT_FORMAT_SINGLE_PRECISION` writes a float on four bytes rather than eight;
`INDEFINITE_TEXT_STRING_LENGTH`, `INDEFINITE_BYTE_STRING_LENGTH`, `INDEFINITE_LIST_LENGTH` and
`INDEFINITE_MAP_LENGTH` write the [indefinite-length](indefinite-length.md) form of each kind. A flag
applies to the whole document, not to one item of it.

In a Symfony application, [the bundle](../bundle/serializer.md) wires this encoder into the Serializer,
and these flags become [options of the serialization context](../bundle/context.md).

## Building the objects yourself

Every class provides a static `create()` method:

```php
// Integers
$uint = UnsignedIntegerObject::create(42);
$nint = NegativeIntegerObject::create(-42);

// Strings
$text = TextStringObject::create('Hello World');
$bytes = ByteStringObject::create('binary data');

// Collections
$list = ListObject::create([
    UnsignedIntegerObject::create(1),
    UnsignedIntegerObject::create(2),
]);

$map = MapObject::create()
    ->add(TextStringObject::create('name'), TextStringObject::create('Alice'))
    ->add(TextStringObject::create('age'), UnsignedIntegerObject::create(30));

// Tags
$timestamp = TimestampTag::create(UnsignedIntegerObject::create(time()));
```

A list and a map are described in [lists and maps](lists-and-maps.md); the tags, in
[tags](../tags/overview.md).

## To bytes

Every object implements `__toString()`, so casting it encodes it:

```php
$object = TextStringObject::create('Hello');
$encoded = (string) $object;
// or
$encoded = $object->__toString();

echo bin2hex($encoded); // "6548656c6c6f"
```

Encoding the outermost object encodes everything it holds. The result is a binary string: send it as
`application/cbor`, store it, sign it.

## Choosing a type

Nothing guesses for you, which is the point: the type you pick is the type that goes on the wire. Two
rules cover most cases.

-   Pick the narrowest integer class that holds the value. `UnsignedIntegerObject` writes the shortest
    head CBOR allows for the number you give it.
-   Pick a byte string for bytes and a text string for text. A `TextStringObject` is meant to hold valid
    UTF-8; binary data belongs in a `ByteStringObject`, where it costs nothing to carry.

When a value needs to say what it *means* — an instant rather than a number, a URI rather than a string —
wrap it in a [tag](../tags/overview.md).
