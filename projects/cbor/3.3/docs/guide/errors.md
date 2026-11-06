---
description: What the library throws, and when
---

# Error handling

The library uses the exceptions of PHP itself, with no hierarchy of its own to catch:

```php
use InvalidArgumentException;
use RuntimeException;

try {
    $decoder = Decoder::create();
    $object = $decoder->decode($stream);
} catch (InvalidArgumentException $e) {
    // The document is not valid CBOR, or a value is outside the bounds the library enforces
    error_log('CBOR decoding error: ' . $e->getMessage());
} catch (RuntimeException $e) {
    // An extension the data asks for is missing
    error_log('Runtime error: ' . $e->getMessage());
}
```

`InvalidArgumentException` is what a malformed or hostile document raises:

-   a head that announces more bytes than the stream holds, or a break where none belongs;
-   nesting deeper than [the limit the decoder was given](decoding.md#limiting-the-nesting-depth);
-   a value outside [the bounds that keep a document affordable](decoding.md#the-cost-of-a-hostile-document);
-   a map with a duplicate key;
-   a tag whose content is not what the tag allows — a date-time string that is not a date, a decimal
    fraction that is not a pair of integers.

`RuntimeException` means the environment is short of something, not that the data is wrong: a decimal
fraction or a bigfloat arrived and `ext-bcmath` is not installed, for instance.

Both are raised while building objects too, not only while decoding: `DatetimeTag::create()` with a text
string that is not an RFC 3339 date-time fails at once, rather than on the far side of the wire.

!!! tip "Decode inside a try block, always"

    Every byte of an incoming document is attacker-controlled, including the ones that decide how much
    work the decoder does. Catch `InvalidArgumentException` around `decode()` and treat it as a rejected
    request, not as a bug.
