---
description: The whole library on one page
---

# Quick reference

```php
// Encoding
$text = TextStringObject::create('hello');
$int = UnsignedIntegerObject::create(42);
$list = ListObject::create([$text, $int]);
$map = MapObject::create()->add($text, $int);
$tagged = TimestampTag::create($int);
$encoded = (string) $map;

// Decoding
$decoder = Decoder::create();
$stream = StringStream::create($encoded);
$object = $decoder->decode($stream);
$phpValue = $object->normalize();

// Tags
$timestamp = TimestampTag::create(UnsignedIntegerObject::create(time()));
$decimal = DecimalFractionTag::createFromFloat(3.14);
$datetime = DatetimeTag::create(TextStringObject::create('2024-01-15T10:30:00Z'));
```

## The classes, by major type

| Type | Class | Definite and indefinite |
|------|-------|-------------------------|
| 0 | `UnsignedIntegerObject` | — |
| 1 | `NegativeIntegerObject` | — |
| 2 | `ByteStringObject` | `IndefiniteLengthByteStringObject` |
| 3 | `TextStringObject` | `IndefiniteLengthTextStringObject` |
| 4 | `ListObject` | `IndefiniteLengthListObject` |
| 5 | `MapObject` | `IndefiniteLengthMapObject` |
| 6 | a subclass of `Tag` | — |
| 7 | `TrueObject`, `FalseObject`, `NullObject`, `UndefinedObject`, the float objects | — |

## The calls you need

| What | How |
|------|-----|
| Build any object | `SomeObject::create(…)` |
| Encode | `(string) $object` |
| Decode | `Decoder::create()->decode(StringStream::create($bytes))` |
| Limit the nesting | `Decoder::create(null, null, 32)` |
| To a PHP value | `$object->normalize()` |
| The object a tag wraps | `$tag->getValue()` |
| A tag number | `TagClass::getTagId()` |
| Register your tags | `Decoder::create(TagManager::create([…]))` |
| Count a list or a map | `count($object)` |
| Read a map entry | `$map->get('key')`, `$map->has('key')` |

The tag numbers the library implements are listed in [the IANA registry](tags/registry.md).
