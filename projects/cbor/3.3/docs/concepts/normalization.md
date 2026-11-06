---
description: Turning a decoded CBOR object into a native PHP value
---

# Normalization

A decoded document is a tree of objects, which says exactly how the data was encoded. An application
usually wants the values instead. Objects that can give them implement the `Normalizable` interface, whose
`normalize()` method returns a native PHP value:

```php
$text = TextStringObject::create('Hello');
$text->normalize(); // string: "Hello"

$int = UnsignedIntegerObject::create(42);
$int->normalize(); // string: "42"

$map = MapObject::create()
    ->add(TextStringObject::create('key'), UnsignedIntegerObject::create(100));
$map->normalize(); // array: ['key' => '100']
```

Normalizing a list or a map normalizes what it holds, so one call on the decoded root gives the whole
document as PHP arrays and scalars.

!!! note "An integer normalizes to a string"

    CBOR integers run to 64 bits unsigned, and the bignum tags further still, which is wider than the
    integers of PHP on every platform. `normalize()` therefore returns a numeric string for every integer,
    small ones included: a value never silently loses its precision on the way out. Cast it yourself when
    you know it fits, or hand the string to `brick/math`.

A few objects have nothing to normalize to, and say so by not implementing the interface: the tags that
only announce how a byte string is meant to be written out, for instance
([tags 21, 22 and 23](../tags/built-in.md#expected-encodings)), hand back the object they wrap through
`getValue()` instead.

Normalization is also where a hostile document can cost the most, because a few tags expand far beyond the
bytes they occupy. The bounds that keep that in check are described in
[the cost of a hostile document](../guide/decoding.md#the-cost-of-a-hostile-document).
