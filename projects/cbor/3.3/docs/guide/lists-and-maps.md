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

// A map may also be built from MapItem objects. Duplicate keys are rejected,
// as are two keys of different major types that resolve to the same offset.
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

`get()`, `has()` and `remove()` take the normalized key, not the key object: `'name'` for a text string,
`1` for an integer.

!!! note "Order is kept"

    A map keeps its entries in the order they were added, and encodes them in that order. CBOR does not
    require a particular order; if a protocol asks for one — a canonical or deterministic encoding — it is
    for you to add the entries accordingly.
