---
description: What a CBOR tag is, and how this library encodes and decodes one
---

# Tags

A tag is major type 6: an integer that prefixes a data item and says what that item means. The integer
alone carries the meaning, and which integer means what is held in a registry maintained by IANA.

```text
Tag(tag_number, data_item)
```

`tag_number` identifies the semantics; `data_item` is any CBOR object the tag applies to. Tag 1 in front
of an integer, for instance, says that the integer is not a count but an instant — seconds since the
epoch — which is why `normalize()` on it hands back a `DateTimeImmutable` rather than a number.

The library implements every tag of the registry listed in [the IANA registry](registry.md): the ones
RFC 8949 defines itself, described in [the built-in tags](built-in.md), and some sixty
[more of the registry](registry-tags.md) — the COSE structures, calendar dates, network addresses, typed
arrays. All of them are registered in the decoder by default, and any other number is decoded without
being interpreted. Tags of your own are written the same way the built-in ones are: see
[writing a tag of your own](writing-a-tag.md).

A tag whose content does not match its definition — a URI that is not a text string, a set that is not an
array — is rejected with an `InvalidArgumentException` rather than decoded into something it is not.
Registering the classes costs nothing until they are used: the decoder files them by tag number and only
loads the one a document actually mentions.

## Encoding with a tag

A tag wraps an object:

```php
use CBOR\Tag\TimestampTag;
use CBOR\UnsignedIntegerObject;

// The data
$timestamp = UnsignedIntegerObject::create(time());

// Wrapped in a tag
$tagged = TimestampTag::create($timestamp);

// Encoded
$encoded = (string) $tagged;
```

## Decoding a tag

A decoder recognises every tag it has been given a class for, and returns an object of that class:

```php
use CBOR\Decoder;
use CBOR\StringStream;

$decoder = Decoder::create();
$decoded = $decoder->decode(StringStream::create($encoded));

if ($decoded instanceof TimestampTag) {
    $dateTime = $decoded->normalize();
    echo $dateTime->format('Y-m-d H:i:s');
}
```

## Reading a tagged value

```php
// The wrapped object
$wrappedObject = $tagged->getValue();

// The additional data, if any
$data = $tagged->getData();

// The tag number
$tagId = $tagged::getTagId();
```

Most tags also implement `Normalizable`, which goes straight to the native value and skips the wrapped
object: `normalize()` on a tag 0 returns a `DateTimeImmutable`, on a tag 2 the digits of the big integer.
The ones that do not implement it are the tags whose content needs no conversion — see
[expected encodings](built-in.md#expected-encodings).

## Working with tags well

-   **Prefer a registered tag.** A number from the IANA registry is understood by readers you did not
    write; a private number is understood by yours alone.
-   **Check the type you were handed.** A tag constrains what it may wrap, but a document from elsewhere
    may use a tag number for something else entirely. Verify before you use it.
-   **Expect tags you do not know.** A number nothing is registered for decodes to a
    [`GenericTag`](registry.md#a-tag-the-library-does-not-know); decide what your application does with
    one.
-   **Mind the extensions.** The decimal fraction and bigfloat tags need `ext-bcmath`, and the big number
    tags want `ext-gmp`. See [installation](../installation.md).
-   **Normalize at the edge.** Turn tags into PHP values where the data enters your application, and work
    with the values afterwards.
