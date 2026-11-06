---
description: Implementing a CBOR tag of your own, from the number to the tests
---

# Writing a tag of your own

Every tag in this library, the built-in ones included, is a class extending `CBOR\Tag`. Writing one is
the same work: pick a number, extend the class, say what the tag accepts, and say what it normalizes to.
This page is the recipe; [three tags, written out](examples.md) follows it through to working code.

## When to write one

Write a tag of your own when you need to:

-   implement a tag another specification defines, and that the library does not ship — a content
    format of CoAP, the labels of SenML;
-   give your own data a meaning the major types do not carry;
-   encode a structure that has rules about its shape, and have them checked on the way in;
-   interoperate with a system that already uses a registered tag;
-   make a document shorter, by letting the tag say what a key or a wrapper would otherwise have to.

## The shape of a tag class

Every tag of this library extends the abstract `CBOR\Tag` class. The shape is always this one:

```php
namespace App\CBOR\Tag;

use CBOR\CBORObject;
use CBOR\Tag;

class MyCustomTag extends Tag
{
    // Required: Return the IANA tag number
    public static function getTagId(): int
    {
        return 1234; // Your tag number
    }

    // Required: Create tag from decoded data
    public static function createFromLoadedData(
        int $additionalInformation,
        ?string $data,
        CBORObject $object
    ): Tag {
        return new self($additionalInformation, $data, $object);
    }

    // Optional: Convenience constructor
    public static function create(CBORObject $object): self
    {
        [$ai, $data] = self::determineComponents(self::getTagId());
        return new self($ai, $data, $object);
    }
}
```

### The methods that matter

#### Required

-   `getTagId()` returns the tag number the class stands for.
-   `createFromLoadedData()` is the factory the decoder calls.

#### Optional

-   `create()`, the convenience method that wraps an object in the tag.
-   `normalize()`, which turns the tag into a native PHP value; declare `Normalizable` with it.
-   Validation in the constructor, which is where a tag says what it accepts.

## Step by step

### 1. Choose a number

A tag number is not yours to invent freely: a tag means something because a reader elsewhere knows the
number. CBOR has no private-use range — look yours up in the
[IANA registry](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml) before you settle on it.

-   **Documents that stay inside your own systems** can use any number nothing has registered. Take a high
    one, and write down what it means where the rest of your protocol is written down.
-   **Documents that travel further** need a number of their own. The registry gives out the numbers from
    256 up on a first-come, first-served basis; below that, a registration needs a specification.

```php
private const TAG_MY_CUSTOM = 64000;
```

### 2. Extend `Tag`

```php
namespace App\CBOR\Tag;

use CBOR\CBORObject;
use CBOR\Tag;

final class MyCustomTag extends Tag
{
    private const TAG_NUMBER = 1234;

    public static function getTagId(): int
    {
        return self::TAG_NUMBER;
    }

    public static function createFromLoadedData(
        int $additionalInformation,
        ?string $data,
        CBORObject $object
    ): Tag {
        return new self($additionalInformation, $data, $object);
    }
}
```

### 3. Validate what it wraps

Validate the wrapped object in the constructor:

```php
use InvalidArgumentException;
use CBOR\TextStringObject;

public function __construct(
    int $additionalInformation,
    ?string $data,
    CBORObject $object
) {
    // Validate that the object is the expected type
    if (!$object instanceof TextStringObject) {
        throw new InvalidArgumentException(
            'MyCustomTag only accepts TextStringObject'
        );
    }

    // Add custom validation
    $value = $object->getValue();
    if (strlen($value) < 5) {
        throw new InvalidArgumentException(
            'Value must be at least 5 characters'
        );
    }

    parent::__construct($additionalInformation, $data, $object);
}
```

### 4. Normalize to a PHP value

Implement the `Normalizable` interface to convert to PHP types:

```php
use CBOR\Normalizable;

final class MyCustomTag extends Tag implements Normalizable
{
    public function normalize(): mixed
    {
        /** @var TextStringObject $object */
        $object = $this->object;

        // Custom transformation logic
        return strtoupper($object->getValue());
    }
}
```

### 5. Add the convenience you want

```php
public static function create(CBORObject $object): self
{
    [$ai, $data] = self::determineComponents(self::TAG_NUMBER);
    return new self($ai, $data, $object);
}

public static function createFromString(string $value): self
{
    return self::create(TextStringObject::create($value));
}
```

## Going further

### Nested tags

Tags can wrap other tagged values:

```php
// Timestamp wrapped in a custom "audit log" tag
$timestamp = TimestampTag::create(UnsignedIntegerObject::create(time()));
$auditLog = AuditLogTag::create($timestamp);
```

### Performance

- **Lazy Validation**: Validate only when necessary
- **Caching**: Cache normalized values if normalization is expensive
- **Type Checking**: Use `instanceof` checks sparingly

### Error handling

```php
public function __construct(
    int $additionalInformation,
    ?string $data,
    CBORObject $object
) {
    try {
        // Validation logic
        $this->validate($object);
    } catch (\Exception $e) {
        throw new InvalidArgumentException(
            sprintf('Invalid %s: %s', static::class, $e->getMessage()),
            0,
            $e
        );
    }

    parent::__construct($additionalInformation, $data, $object);
}
```

## Writing a tag well

1. **Use Appropriate Tag Numbers**: Check IANA registry to avoid conflicts
2. **Validate Early**: Validate in the constructor to fail fast
3. **Document Thoroughly**: Include RFC references and usage examples
4. **Implement Normalizable**: Make tags easy to work with
5. **Type-Safe**: Use strict types and type hints
6. **Test Extensively**: Test validation, encoding, and decoding
7. **Handle Edge Cases**: Consider null values, empty collections, etc.
8. **Follow Specifications**: When implementing standard tags, follow specs exactly
