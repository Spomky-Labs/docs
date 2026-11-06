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

    `Decoder::create()` with no argument knows the fifteen built-in tags. Hand it a `TagManager` and that
    manager is the whole set: a tag 0 then decodes to a `GenericTag`, because nothing registered
    `DatetimeTag` any more. There is no public factory for "the defaults plus mine", so list them:

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
    read may contain: anything else comes back as a `GenericTag` instead of being interpreted.

    `add()` refuses a class whose `getTagId()` is negative, and a second class for a number already
    registered replaces the first: one class per number.

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

Several specifications define their own tag numbers, registered with IANA like any other. None of them has
a class in this version of the library: implement the ones you need the way the pages above describe.

### COSE and CWT

COSE, [RFC 9052](https://datatracker.ietf.org/doc/html/rfc9052), gives one tag per message type, and CWT,
[RFC 8392](https://datatracker.ietf.org/doc/html/rfc8392), one for a token:

| Tag | Structure |
|-----|-----------|
| 16 | `COSE_Encrypt0`, encrypted, single recipient implied |
| 17 | `COSE_Mac0`, MACed, no recipient structure |
| 18 | `COSE_Sign1`, signed by one signer |
| 61 | `CWT_Tag`, a CBOR Web Token |
| 96 | `COSE_Encrypt`, encrypted, with recipients |
| 97 | `COSE_Mac`, MACed, with recipients |
| 98 | `COSE_Sign`, signed, with one or more signatures |

A `COSE_Sign1` is an array of four items — protected header, unprotected header, payload, signature — so
the tag class has something precise to check:

```php
namespace App\CBOR\Tag;

use CBOR\CBORObject;
use CBOR\ListObject;
use CBOR\Tag;
use InvalidArgumentException;

/**
 * Tag 18: COSE_Sign1, a message signed by a single signer.
 *
 * @see https://datatracker.ietf.org/doc/html/rfc9052#section-4.2
 */
final class CoseSign1Tag extends Tag
{
    private const TAG_COSE_SIGN1 = 18;

    public function __construct(int $additionalInformation, ?string $data, CBORObject $object)
    {
        if (! $object instanceof ListObject || count($object) !== 4) {
            throw new InvalidArgumentException('COSE_Sign1 must be an array of 4 elements');
        }

        // [protected, unprotected, payload, signature]
        parent::__construct($additionalInformation, $data, $object);
    }

    public static function getTagId(): int
    {
        return self::TAG_COSE_SIGN1;
    }

    public static function createFromLoadedData(int $additionalInformation, ?string $data, CBORObject $object): Tag
    {
        return new self($additionalInformation, $data, $object);
    }
}
```

The protected header is itself a byte string holding a CBOR map, which is what lets a signature cover the
exact bytes that were signed. Do not decode and re-encode it: keep the byte string as it arrived, as
[tag 24](built-in.md#tag-24-an-encoded-cbor-data-item) does.

A CWT wraps one of those COSE structures, so its own class checks what it was handed:

```php
public function __construct(int $additionalInformation, ?string $data, CBORObject $object)
{
    if (! $object instanceof CoseSign1Tag && ! $object instanceof CoseMac0Tag) {
        throw new InvalidArgumentException('A CWT must wrap a COSE structure');
    }

    parent::__construct($additionalInformation, $data, $object);
}
```

For COSE itself — the headers, the algorithms, the keys, the signature verification — use
[web-auth/cose-lib](https://github.com/web-auth/cose-lib), which is built on this library.

### Other specifications

-   **CoAP**, [RFC 7252](https://datatracker.ietf.org/doc/html/rfc7252), carries CBOR payloads, whose
    content formats may call for tags of their own.
-   **SenML**, [RFC 8428](https://datatracker.ietf.org/doc/html/rfc8428), describes sensor measurements in
    CBOR, with its own labels and semantics.

Before you pick a number for something of your own, look it up in the
[IANA registry](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml): a number already registered
means someone else's reader will misunderstand your documents.
