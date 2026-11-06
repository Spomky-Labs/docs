---
description: The encoder, the decoder and the managers, as services
---

# Using the services directly

The Serializer is one way in. The encoder and the decoder are services of their own, for the code that has
bytes rather than a request.

```php
use SpomkyLabs\CborBundle\CBORDecoder;
use SpomkyLabs\CborBundle\CBOREncoder;

final class MyService
{
    public function __construct(
        private readonly CBOREncoder $encoder,
        private readonly CBORDecoder $decoder,
    ) {
    }
}
```

Both are public, and both have an alias for a definition written by hand:

```php
final class MyService
{
    public function __construct(
        #[Autowire(service: 'cbor.encoder')]
        private readonly CBOREncoder $encoder,
        #[Autowire(service: 'cbor.decoder')]
        private readonly CBORDecoder $decoder,
    ) {
    }
}
```

`CBOREncoder` is the class the Serializer uses: it implements the `EncoderInterface` and
`DecoderInterface` of Symfony, so it answers `encode()` and `decode()` with a format and a context.
`CBORDecoder::decode()` is simpler — it takes the bytes and returns the object tree, [stream](../guide/streams.md)
included:

```php
$document = $this->decoder->decode($bytes);
$value = $document->normalize();
```

## The managers

The decoder is built with a [tag manager](../tags/registering.md) and an other-object manager that know
every tag class the library implements from the IANA registry — dates, big numbers, UUIDs, COSE messages
and CBOR Web Tokens, typed arrays, IP addresses — and every simple value and float of major type 7. Both
are services, injectable through their interface:

```php
use CBOR\OtherObject\OtherObjectManagerInterface;
use CBOR\Tag\TagManagerInterface;

final class MyService
{
    public function __construct(
        private readonly TagManagerInterface $tagManager,
        private readonly OtherObjectManagerInterface $otherObjectManager,
    ) {
    }
}
```

`CBOR\Decoder` itself is a service too, built with those managers and with the
[`max_depth`](configuration.md#the-nesting-depth) of the configuration.
