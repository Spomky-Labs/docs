---
description: Encoding readings for a link that counts its bytes
---

# Sensor data

The case CBOR was designed for: a measurement, an instant, and as few bytes as possible on the wire.

```php
use CBOR\MapObject;
use CBOR\Tag\DecimalFractionTag;
use CBOR\Tag\TimestampTag;
use CBOR\TextStringObject;
use CBOR\UnsignedIntegerObject;

$sensorData = MapObject::create()
    ->add(
        TextStringObject::create('temperature'),
        DecimalFractionTag::createFromFloat(23.5)
    )
    ->add(
        TextStringObject::create('humidity'),
        UnsignedIntegerObject::create(65)
    )
    ->add(
        TextStringObject::create('timestamp'),
        TimestampTag::create(UnsignedIntegerObject::create(time()))
    );

$encoded = (string) $sensorData;
```

Two choices are worth noticing.

The temperature goes in as a [decimal fraction](../tags/built-in.md#tag-4-a-decimal-fraction) rather than
a float: 23.5 stays 23.5, where a binary float would carry a value that only prints as 23.5. It needs
`ext-bcmath` at both ends.

The instant is [tagged](../tags/built-in.md#tag-1-an-epoch-timestamp), so the reader gets a
`DateTimeImmutable` without being told which of the numbers in the map was a date.

Shorter still: integer keys instead of text ones. `1`, `2`, `3` cost one byte each where
`"temperature"` costs twelve, which is how CoAP and SenML payloads are written — at the price of needing
the table of meanings on both sides.

```php
$sensorData = MapObject::create()
    ->add(UnsignedIntegerObject::create(1), DecimalFractionTag::createFromFloat(23.5))
    ->add(UnsignedIntegerObject::create(2), UnsignedIntegerObject::create(65))
    ->add(UnsignedIntegerObject::create(3), TimestampTag::create(UnsignedIntegerObject::create(time())));
```
