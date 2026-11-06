---
description: Looking at what a document actually contains
---

# Debugging

The first question about a CBOR document is usually what is in it. A decoded tree answers that directly:

```php
// The whole shape
var_dump($object);

// Entry by entry, for a map or a list
foreach ($map as $item) {
    echo sprintf(
        "Key: %s, Value: %s\n",
        $item->getKey()->normalize(),
        $item->getValue()->normalize()
    );
}

// What it encodes to
$encoded = (string) $object;
echo 'Hex: ' . bin2hex($encoded) . "\n";
echo 'Length: ' . strlen($encoded) . " bytes\n";
```

Printing the class of each object is often faster than printing its value: `get_class($object)` tells you
whether that number came in as a tagged instant or a plain integer, and whether a string arrived in
definite or indefinite-length form.

## Reading the bytes

A CBOR head is one byte: the three high bits are the major type, the five low bits the additional
information. `bin2hex()` and [the table of major types](concepts/the-data-model.md) are enough to read the
start of a document by hand — `a2` is a map of two entries, `d9 d9 f7` the
[self-described CBOR tag](tags/built-in.md#tag-55799-self-described-cbor).

## Elsewhere

-   [cbor.me](https://cbor.me/) shows a document in its diagnostic notation, both ways round.
-   [cbor.io](https://cbor.io/) lists the specification, the registry and the implementations in other
    languages.

Both are third-party sites: paste nothing into them that you would not publish.
