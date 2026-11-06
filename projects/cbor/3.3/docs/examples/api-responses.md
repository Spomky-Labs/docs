---
description: Answering a request in CBOR instead of JSON
---

# API responses

CBOR has a media type of its own, `application/cbor`, and an answer in it is built the same way as any
other document: a map, encoded, written out.

```php
use CBOR\MapObject;
use CBOR\NegativeIntegerObject;
use CBOR\TextStringObject;
use CBOR\UnsignedIntegerObject;
use InvalidArgumentException;

function encodeToCBOR(array $data): string
{
    $map = MapObject::create();

    foreach ($data as $key => $value) {
        $keyObject = TextStringObject::create((string) $key);
        $valueObject = match (gettype($value)) {
            'string' => TextStringObject::create($value),
            'integer' => $value >= 0
                ? UnsignedIntegerObject::create($value)
                : NegativeIntegerObject::create($value),
            'array' => convertArrayToList($value),
            default => throw new InvalidArgumentException(sprintf('Unsupported type "%s"', gettype($value))),
        };

        $map->add($keyObject, $valueObject);
    }

    return (string) $map;
}

$response = encodeToCBOR([
    'status' => 'success',
    'code' => 200,
    'data' => ['item1', 'item2'],
]);

header('Content-Type: application/cbor');
echo $response;
```

A converter like this one is a decision about your protocol, not a feature of the format: what types you
accept, what you do with a float, whether a date becomes a
[tagged instant](../tags/built-in.md#tag-1-an-epoch-timestamp) or a string. Write the mapping down and
keep both ends to it — which is the whole difference between a binary protocol and a guess.

The way back, for a request body:

```php
use CBOR\Decoder;
use CBOR\StringStream;

// 32 levels of nesting is plenty for a request body
$decoder = Decoder::create(null, null, 32);

try {
    $document = $decoder->decode(StringStream::create($requestBody));
} catch (InvalidArgumentException) {
    http_response_code(400);
    exit;
}

$data = $document->normalize();
```

The depth limit and the `try` block are not optional on a public endpoint: see
[the cost of a hostile document](../guide/decoding.md#the-cost-of-a-hostile-document).
