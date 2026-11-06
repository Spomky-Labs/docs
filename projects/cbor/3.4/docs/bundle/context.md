---
description: The serialization context keys that change how CBOR is written
---

# The context options

Five keys of the serialization context change how a document is written. Each one is the context form of a
flag of [`Encoder`](../guide/encoding.md#from-php-values).

```php
// A float on four bytes rather than eight
$cbor = $serializer->serialize($data, 'cbor', [
    'cbor_single_precision_float' => true,
]);

// Arrays in their indefinite-length form
$cbor = $serializer->serialize([1, 2, 3], 'cbor', [
    'cbor_indefinite_list' => true,
]);

// Maps in their indefinite-length form
$cbor = $serializer->serialize(['a' => 1], 'cbor', [
    'cbor_indefinite_map' => true,
]);

// Text strings in their indefinite-length form
$cbor = $serializer->serialize('Hello', 'cbor', [
    'cbor_indefinite_text_string' => true,
]);
```

| Key | What it does |
|-----|--------------|
| `cbor_single_precision_float` | writes a float on 32 bits instead of 64 |
| `cbor_indefinite_text_string` | writes text strings in their [indefinite-length](../guide/indefinite-length.md) form |
| `cbor_indefinite_byte_string` | the same, for byte strings |
| `cbor_indefinite_list` | the same, for arrays |
| `cbor_indefinite_map` | the same, for maps |

All five take a boolean and default to `false`. They can be combined, and each one applies to the whole
document rather than to one item of it.

!!! note "Single precision loses digits"

    `cbor_single_precision_float` halves the room a float takes, and keeps about seven significant decimal
    digits instead of sixteen. It is the right choice for a sensor reading and the wrong one for an amount
    of money — for which neither float is right: use a
    [decimal fraction](../tags/built-in.md#tag-4-a-decimal-fraction).
