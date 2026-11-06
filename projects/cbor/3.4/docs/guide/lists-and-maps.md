---
description: Working with CBOR arrays and maps
---

# Lists and maps

An array (major type 4) is a `ListObject`, a map (major type 5) a `MapObject`. Both are `Countable` and
`IteratorAggregate`, and both normalize to a PHP array.

## Lists

```php
$list = ListObject::create();

// Add items
$list->add(UnsignedIntegerObject::create(1));
$list->add(TextStringObject::create('two'));

// Access items
$first = $list->get(0);
$count = $list->count();

// Check existence
if ($list->has(1)) {
    // …
}

// Remove items
$list->remove(0);

// Array access
$list[0] = UnsignedIntegerObject::create(42);
$value = $list[0];

// Iteration
foreach ($list as $item) {
    // …
}

// Normalize to a PHP array
$phpArray = $list->normalize();
```

## Maps

A map holds `MapItem` objects, each one a key and a value, both of them CBOR objects: a map key is not
restricted to a string.

```php
$map = MapObject::create();

// Add key-value pairs
$map->add(
    TextStringObject::create('name'),
    TextStringObject::create('Alice')
);

// A map may also be built from MapItem objects. Duplicate keys are rejected.
$map = MapObject::create([
    MapItem::create(TextStringObject::create('name'), TextStringObject::create('Alice')),
    MapItem::create(UnsignedIntegerObject::create(1), UnsignedIntegerObject::create(2)),
]);

// Access values
$name = $map->get('name');

// Check existence
if ($map->has('name')) {
    // …
}

// Remove entries
$map->remove('name');

// Count entries
$count = $map->count();

// Iteration
foreach ($map as $item) {
    $key = $item->getKey();
    $value = $item->getValue();
}

// Normalize to a PHP array
$phpArray = $map->normalize();
```

`get()`, `has()`, `remove()` and `normalize()` address entries by the PHP array offset the key normalizes
to: an integer or a string. `'name'` for a text string, `1` for an integer — not the key object itself.

RFC 8949 allows any data item as a key, and the map keeps every key it is given — a float, a boolean,
`null`, a list, a map, a tag — in order, so that a document decodes, iterates and re-encodes exactly as it
was read. Such a key has no offset of its own: its entry is reached by iterating, and `normalize()`
refuses the map with an `InvalidArgumentException`. The same goes for two keys of different major types
that resolve to the same offset, the integer `1` and the text string `"1"` for instance: both are kept,
neither is reachable through `get()`, and `normalize()` refuses to pick one.

!!! note "Order is kept"

    A map keeps its entries in the order they were added, and encodes them in that order. CBOR does not
    require a particular order; if a protocol asks for one — a canonical or deterministic encoding — it is
    for you to add the entries accordingly.
