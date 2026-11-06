---
description: The Symfony bundle that exposes the decoder as a service
---

# The Symfony bundle

[spomky-labs/cbor-bundle](https://github.com/Spomky-Labs/cbor-bundle) wires this library into a Symfony
application. Version 3.1 of the bundle is the one that pairs with version 3.3 of the library: it exposes
the decoder as a service, and lets the container register tag classes of your own.

```bash
composer require spomky-labs/cbor-bundle
```

Symfony Flex registers it. Without Flex, add it to `config/bundles.php`:

```php
return [
    // …
    SpomkyLabs\CborBundle\SpomkyLabsCborBundle::class => ['all' => true],
];
```

## Decoding

`SpomkyLabs\CborBundle\CBORDecoder` takes the bytes and returns the object tree, so the
[stream](guide/streams.md) is handled for you:

```php
use SpomkyLabs\CborBundle\CBORDecoder;

final class PayloadController
{
    public function __construct(
        private readonly CBORDecoder $decoder,
    ) {
    }

    public function __invoke(Request $request): Response
    {
        $document = $this->decoder->decode($request->getContent());

        return $this->json($document->normalize());
    }
}
```

`CBOR\Decoder` itself is a service too, for the calls the wrapper does not cover.

## Configuration

One option, the [nesting depth](guide/decoding.md#limiting-the-nesting-depth) the decoder accepts:

```yaml
# config/packages/cbor.yaml
cbor:
    max_depth: 1000 # the default
```

Lower it when the payloads come from somewhere you do not control:

```yaml
cbor:
    max_depth: 32
```

## Tags of your own

A class implementing `CBOR\Tag\TagInterface` — see [writing a tag of your own](tags/writing-a-tag.md) —
joins the decoder's tag manager when its service carries the `cbor.tag` tag. Major type 7 items work the
same way, with `CBOR\OtherObjectInterface` and `cbor.other_object`:

```yaml
services:
    App\Cbor\CustomTag:
        tags: ['cbor.tag']

    App\Cbor\CustomObject:
        tags: ['cbor.other_object']
```

The container only reads the class of such a service definition; the decoder instantiates it itself, with
the data of the item it is reading.

!!! tip "The next version does much more"

    Version 3.2 of the bundle integrates CBOR into the Symfony Serializer — `$serializer->serialize($data,
    'cbor')`, objects, enums, and the encoding options as context keys. It requires version 3.4 of the
    library, so it is documented in [the 3.4 version of this site](https://cbor.spomky-labs.com/latest/bundle/installation/).
