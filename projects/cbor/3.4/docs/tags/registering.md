---
description: Making a decoder aware of your tag, testing it, and the tags other specifications define
---

# Registering and testing a tag

A tag class encodes on its own, but a decoder only returns it if it has been told the class exists.

## Telling the decoder about it

```php
use CBOR\Decoder;
use CBOR\Tag\TagManager;

$tagManager = TagManager::create()
    ->add(EmailTag::class)
    ->add(GeoCoordinatesTag::class)
    ->add(UserProfileTag::class);

$decoder = Decoder::create($tagManager);
```

`add()` asks each class for its own number, which means loading it. `register()` takes the number up
front and only names the class, so the autoloader is left alone until that tag actually turns up in a
document — which is how the library registers over seventy tags without loading seventy classes per
request:

```php
$tagManager = TagManager::create()
    ->register(64000, EmailTag::class)
    ->register(103, GeoCoordinatesTag::class);
```

The number is taken at face value: nothing checks that the class agrees with it, since checking is
exactly what would load the class. Keep the two in step yourself.

## Using it

```php
// Encoding
$email = EmailTag::createFromEmail('user@example.com');
$encoded = (string) $email;

// Decoding
$decoded = $decoder->decode(StringStream::create($encoded));

if ($decoded instanceof EmailTag) {
    echo $decoded->getEmail();
}
```

!!! warning "A manager you build replaces the default set"

    `Decoder::create()` with no argument knows every tag of
    [the registry table](registry.md), over seventy classes. Hand it a `TagManager` and that manager is the
    whole set: a tag 0 then decodes to a `GenericTag`, because nothing registered `DatetimeTag` any more.
    There is no public factory for "the defaults plus mine", so list the tags your documents may hold —
    the fifteen of RFC 8949 and yours, for instance:

    ```php
    use CBOR\Tag\Base16EncodingTag;
    use CBOR\Tag\Base64EncodingTag;
    use CBOR\Tag\Base64Tag;
    use CBOR\Tag\Base64UrlEncodingTag;
    use CBOR\Tag\Base64UrlTag;
    use CBOR\Tag\BigFloatTag;
    use CBOR\Tag\CBOREncodingTag;
    use CBOR\Tag\CBORTag;
    use CBOR\Tag\DatetimeTag;
    use CBOR\Tag\DecimalFractionTag;
    use CBOR\Tag\MimeTag;
    use CBOR\Tag\NegativeBigIntegerTag;
    use CBOR\Tag\TimestampTag;
    use CBOR\Tag\UnsignedBigIntegerTag;
    use CBOR\Tag\UriTag;

    $tagManager = TagManager::create([
        DatetimeTag::class, TimestampTag::class,
        UnsignedBigIntegerTag::class, NegativeBigIntegerTag::class,
        DecimalFractionTag::class, BigFloatTag::class,
        Base64UrlEncodingTag::class, Base64EncodingTag::class, Base16EncodingTag::class,
        CBOREncodingTag::class,
        UriTag::class, Base64UrlTag::class, Base64Tag::class, MimeTag::class,
        CBORTag::class,
    ])
        ->add(EmailTag::class)
        ->add(GeoCoordinatesTag::class);
    ```

    Registering only your own tags is a sound choice too, when you know exactly what the documents you
    read may contain: anything else comes back as a `GenericTag` instead of being interpreted. So is
    keeping the default decoder and letting your own tag arrive as a `GenericTag`, when your application
    writes that tag but never has to read it back.

    Either method refuses a negative number, and a second class for a number already registered
    replaces the first: one class per number.

## Testing it

```php
use PHPUnit\Framework\TestCase;

class EmailTagTest extends TestCase
{
    public function testCreateFromValidEmail(): void
    {
        $tag = EmailTag::createFromEmail('test@example.com');

        $this->assertInstanceOf(EmailTag::class, $tag);
        $this->assertSame('test@example.com', $tag->getEmail());
    }

    public function testRejectsInvalidEmail(): void
    {
        $this->expectException(InvalidArgumentException::class);
        EmailTag::createFromEmail('not-an-email');
    }

    public function testEncodingAndDecoding(): void
    {
        $original = EmailTag::createFromEmail('test@example.com');
        $encoded = (string) $original;

        $tagManager = TagManager::create()->add(EmailTag::class);
        $decoder = Decoder::create($tagManager);

        $decoded = $decoder->decode(StringStream::create($encoded));

        $this->assertInstanceOf(EmailTag::class, $decoded);
        $this->assertSame('test@example.com', $decoded->getEmail());
    }
}
```

## Tags from other specifications

**COSE and CWT are built in** since 3.4.0: `CoseEncrypt0Tag` (16), `CoseMac0Tag` (17), `CoseSign1Tag`
(18), `CoseEncryptTag` (96), `CoseMacTag` (97), `CoseSignTag` (98) and `CwtTag` (61) are registered in the
decoder by default. See [COSE and CWT](registry-tags.md#cose-and-cwt) for what they give access to.

They describe the structure only. Verifying a signature or a MAC, and everything about keys and
algorithms, belongs to a COSE implementation —
[web-auth/cose-lib](https://github.com/web-auth/cose-lib), which also ships the algorithm registry of
RFC 9053.

Two other specifications rest on CBOR without defining tags the library ships:

-   **CoAP**, [RFC 7252](https://datatracker.ietf.org/doc/html/rfc7252), carries CBOR payloads, whose
    content formats may call for tags of their own.
-   **SenML**, [RFC 8428](https://datatracker.ietf.org/doc/html/rfc8428), describes sensor measurements in
    CBOR, with its own labels and semantics.

Before you pick a number for something of your own, look it up in the
[IANA registry](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml): a number already registered
means someone else's reader will misunderstand your documents.
