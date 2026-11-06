---
description: CBOR as a format of the Symfony Serializer
---

# The Serializer integration

The bundle registers CBOR as a format of the Serializer, so `cbor` is used wherever `json` would be:

```php
use Symfony\Component\Serializer\SerializerInterface;

final class PayloadController
{
    public function __construct(
        private readonly SerializerInterface $serializer,
    ) {
    }

    public function __invoke(): Response
    {
        $data = [
            'name' => 'John Doe',
            'age' => 30,
            'active' => true,
            'tags' => ['developer', 'symfony'],
        ];

        return new Response(
            $this->serializer->serialize($data, 'cbor'),
            200,
            ['Content-Type' => 'application/cbor'],
        );
    }
}
```

The way back takes the type you want out of it:

```php
$data = $this->serializer->deserialize($request->getContent(), 'array', 'cbor');
```

## Objects

Any object the normalizers of Symfony can handle goes through, and comes back:

```php
$cbor = $this->serializer->serialize($person, 'cbor');

$person = $this->serializer->deserialize($cbor, Person::class, 'cbor');
```

The object is normalized to an array first, by Symfony, and that array is what CBOR encodes — so the
groups, the name converters and the attributes of your normalizers all apply as usual.

## What it carries

-   **Scalars**: `int`, `float`, `string`, `bool`, `null`
-   **Arrays**: a list becomes a CBOR array, anything else a CBOR map
-   **Objects**: whatever the normalizers of Symfony can turn into an array
-   **Enums**: a backed enum travels as its value, a unit enum as its name
-   **Dates**: through the normalizers of Symfony, as the format you configured there
-   **Nested structures**: arrays of objects, objects holding arrays, as deep as you like

A string that is valid UTF-8 is written as a CBOR text string and anything else as a byte string, which is
[the mapping of `Encoder`](../guide/encoding.md#from-php-values): the bundle hands your value to it.

## Enums

```php
enum Status: string
{
    case ACTIVE = 'active';
    case INACTIVE = 'inactive';
}

$this->serializer->serialize(Status::ACTIVE, 'cbor'); // the text string "active"

enum Color
{
    case RED;
    case GREEN;
}

$this->serializer->serialize(Color::RED, 'cbor');     // the text string "RED"
```

A unit enum has no value to carry, so its name travels instead. Nothing marks either one as an enum in the
document: what comes back is a string, and turning it into the case again is `Status::from($value)` on your
side.
