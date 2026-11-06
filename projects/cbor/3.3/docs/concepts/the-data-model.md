---
description: The eight major types of CBOR and the PHP classes that stand for them
---

# The data model

A CBOR data item is one of eight major types, numbered 0 to 7. Every one of them has a class in this
library, and some have two: one for the definite-length encoding, one for the
[indefinite-length](../guide/indefinite-length.md) form.

| Type | Description | PHP classes |
|------|-------------|-------------|
| 0 | Unsigned integer | `UnsignedIntegerObject` |
| 1 | Negative integer | `NegativeIntegerObject` |
| 2 | Byte string | `ByteStringObject`, `IndefiniteLengthByteStringObject` |
| 3 | Text string | `TextStringObject`, `IndefiniteLengthTextStringObject` |
| 4 | Array | `ListObject`, `IndefiniteLengthListObject` |
| 5 | Map | `MapObject`, `IndefiniteLengthMapObject` |
| 6 | Tag | subclasses of `Tag`, see [tags](../tags/overview.md) |
| 7 | Simple value or float | `TrueObject`, `FalseObject`, `NullObject`, the float objects |

Every class lives in the `CBOR` namespace, the tags in `CBOR\Tag`, and the simple values and floats in
`CBOR\OtherObject`.

## The hierarchy of classes

```text
CBORObject (interface)
└── AbstractCBORObject (abstract)
    ├── UnsignedIntegerObject
    ├── NegativeIntegerObject
    ├── ByteStringObject
    ├── IndefiniteLengthByteStringObject
    ├── TextStringObject
    ├── IndefiniteLengthTextStringObject
    ├── ListObject
    ├── IndefiniteLengthListObject
    ├── MapObject
    ├── IndefiniteLengthMapObject
    ├── Tag (abstract)
    │   ├── DatetimeTag
    │   ├── TimestampTag
    │   ├── DecimalFractionTag
    │   ├── BigFloatTag
    │   ├── … the other built-in tags
    │   └── GenericTag
    └── OtherObject (abstract)
        ├── TrueObject
        ├── FalseObject
        ├── NullObject
        ├── UndefinedObject
        ├── DoublePrecisionFloatObject
        └── …
```

Two things are true of every object of that tree, whatever its type:

-   it is built by a static `create()` method, never by `new`;
-   casting it to a string encodes it, because each one implements `__toString()`.

Most of them also implement `Normalizable`, which turns a decoded object into a native PHP value. That is
the subject of [normalization](normalization.md).
