---
description: Three custom tags, from the simplest to one that validates what it is given
---

# Three tags, written out

The three tags below follow [the steps of the previous page](writing-a-tag.md) through to working code: a
tag that marks a text string, one that carries a structure, and one that enforces a set of rules on what
it is given.

The numbers they use are illustrations. Look yours up in the
[IANA registry](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml) before you settle on it: a
number already registered means a reader you did not write will misread your documents.

## An email tag

A tag that marks text strings as email addresses.

```php
namespace App\CBOR\Tag;

use CBOR\CBORObject;
use CBOR\IndefiniteLengthTextStringObject;
use CBOR\Normalizable;
use CBOR\Tag;
use CBOR\TextStringObject;
use InvalidArgumentException;

/**
 * Tag 64000: Email Address (any number the IANA registry leaves unassigned)
 * Marks a text string as an RFC 5322 email address
 */
final class EmailTag extends Tag implements Normalizable
{
    private const TAG_EMAIL = 64000;

    public function __construct(
        int $additionalInformation,
        ?string $data,
        CBORObject $object
    ) {
        if (!$object instanceof TextStringObject
            && !$object instanceof IndefiniteLengthTextStringObject) {
            throw new InvalidArgumentException(
                'EmailTag only accepts text strings'
            );
        }

        // Validate email format
        $email = $object->getValue();
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException(
                'Invalid email address format'
            );
        }

        parent::__construct($additionalInformation, $data, $object);
    }

    public static function getTagId(): int
    {
        return self::TAG_EMAIL;
    }

    public static function createFromLoadedData(
        int $additionalInformation,
        ?string $data,
        CBORObject $object
    ): Tag {
        return new self($additionalInformation, $data, $object);
    }

    public static function create(CBORObject $object): self
    {
        [$ai, $data] = self::determineComponents(self::TAG_EMAIL);
        return new self($ai, $data, $object);
    }

    public static function createFromEmail(string $email): self
    {
        return self::create(TextStringObject::create($email));
    }

    public function normalize(): string
    {
        /** @var TextStringObject|IndefiniteLengthTextStringObject $object */
        $object = $this->object;
        return $object->normalize();
    }

    public function getEmail(): string
    {
        return $this->normalize();
    }
}
```

### Using it

```php
use CBOR\Tag\EmailTag;

// Create
$email = EmailTag::createFromEmail('user@example.com');
$encoded = (string) $email;

// Decode
$decoder = Decoder::create();
$decoded = $decoder->decode(StringStream::create($encoded));

if ($decoded instanceof EmailTag) {
    echo $decoded->getEmail(); // user@example.com
}
```

## Geographic coordinates

A tag for WGS84 coordinates (latitude, longitude, altitude).

```php
namespace App\CBOR\Tag;

use CBOR\CBORObject;
use CBOR\ListObject;
use CBOR\Normalizable;
use CBOR\Tag;
use CBOR\OtherObject\DoublePrecisionFloatObject;
use InvalidArgumentException;

/**
 * Tag 103: Geographic Coordinates (WGS-84)
 * Array of [latitude, longitude, altitude (optional)]
 */
final class GeoCoordinatesTag extends Tag implements Normalizable
{
    private const TAG_GEO_COORDINATES = 103;

    public function __construct(
        int $additionalInformation,
        ?string $data,
        CBORObject $object
    ) {
        if (!$object instanceof ListObject) {
            throw new InvalidArgumentException(
                'GeoCoordinatesTag requires a ListObject'
            );
        }

        $count = count($object);
        if ($count < 2 || $count > 3) {
            throw new InvalidArgumentException(
                'GeoCoordinates must have 2 or 3 elements [lat, lon, alt?]'
            );
        }

        // Validate latitude
        $lat = $object->get(0);
        if (!$this->isNumeric($lat)) {
            throw new InvalidArgumentException('Latitude must be numeric');
        }

        // Validate longitude
        $lon = $object->get(1);
        if (!$this->isNumeric($lon)) {
            throw new InvalidArgumentException('Longitude must be numeric');
        }

        // Validate altitude if present
        if ($count === 3) {
            $alt = $object->get(2);
            if (!$this->isNumeric($alt)) {
                throw new InvalidArgumentException('Altitude must be numeric');
            }
        }

        parent::__construct($additionalInformation, $data, $object);
    }

    private function isNumeric(CBORObject $object): bool
    {
        return $object instanceof UnsignedIntegerObject
            || $object instanceof NegativeIntegerObject
            || $object instanceof DoublePrecisionFloatObject
            || $object instanceof SinglePrecisionFloatObject;
    }

    public static function getTagId(): int
    {
        return self::TAG_GEO_COORDINATES;
    }

    public static function createFromLoadedData(
        int $additionalInformation,
        ?string $data,
        CBORObject $object
    ): Tag {
        return new self($additionalInformation, $data, $object);
    }

    public static function create(CBORObject $object): self
    {
        [$ai, $data] = self::determineComponents(self::TAG_GEO_COORDINATES);
        return new self($ai, $data, $object);
    }

    public static function createFromCoordinates(
        float $latitude,
        float $longitude,
        ?float $altitude = null
    ): self {
        $list = ListObject::create([
            DoublePrecisionFloatObject::createFromFloat($latitude),
            DoublePrecisionFloatObject::createFromFloat($longitude),
        ]);

        if ($altitude !== null) {
            $list->add(DoublePrecisionFloatObject::createFromFloat($altitude));
        }

        return self::create($list);
    }

    /**
     * @return array{latitude: float, longitude: float, altitude: float|null}
     */
    public function normalize(): array
    {
        /** @var ListObject $list */
        $list = $this->object;

        $result = [
            'latitude' => (float) $list->get(0)->normalize(),
            'longitude' => (float) $list->get(1)->normalize(),
            'altitude' => null,
        ];

        if (count($list) === 3) {
            $result['altitude'] = (float) $list->get(2)->normalize();
        }

        return $result;
    }

    public function getLatitude(): float
    {
        /** @var ListObject $list */
        $list = $this->object;
        return (float) $list->get(0)->normalize();
    }

    public function getLongitude(): float
    {
        /** @var ListObject $list */
        $list = $this->object;
        return (float) $list->get(1)->normalize();
    }

    public function getAltitude(): ?float
    {
        /** @var ListObject $list */
        $list = $this->object;

        if (count($list) === 3) {
            return (float) $list->get(2)->normalize();
        }

        return null;
    }
}
```

### Using it

```php
use CBOR\Tag\GeoCoordinatesTag;

// Create coordinates for Paris, France
$coords = GeoCoordinatesTag::createFromCoordinates(
    48.8566,  // latitude
    2.3522,   // longitude
    35.0      // altitude (meters)
);

$normalized = $coords->normalize();
/*
[
    'latitude' => 48.8566,
    'longitude' => 2.3522,
    'altitude' => 35.0
]
*/

echo $coords->getLatitude();  // 48.8566
echo $coords->getLongitude(); // 2.3522
echo $coords->getAltitude();  // 35.0
```

## A tag that validates

A tag with multiple validation rules and transformation logic.

```php
namespace App\CBOR\Tag;

use CBOR\CBORObject;
use CBOR\MapObject;
use CBOR\Normalizable;
use CBOR\Tag;
use CBOR\TextStringObject;
use CBOR\UnsignedIntegerObject;
use InvalidArgumentException;

/**
 * Tag 1000: User Profile
 * Structured user profile with validation
 */
final class UserProfileTag extends Tag implements Normalizable
{
    private const TAG_USER_PROFILE = 1000;

    private const REQUIRED_KEYS = ['username', 'email', 'age'];

    public function __construct(
        int $additionalInformation,
        ?string $data,
        CBORObject $object
    ) {
        if (!$object instanceof MapObject) {
            throw new InvalidArgumentException(
                'UserProfileTag requires a MapObject'
            );
        }

        // Validate required keys
        foreach (self::REQUIRED_KEYS as $key) {
            if (!$object->has($key)) {
                throw new InvalidArgumentException(
                    "Missing required key: {$key}"
                );
            }
        }

        // Validate username
        $username = $object->get('username');
        if (!$username instanceof TextStringObject) {
            throw new InvalidArgumentException('Username must be a text string');
        }
        if (strlen($username->getValue()) < 3) {
            throw new InvalidArgumentException('Username must be at least 3 characters');
        }

        // Validate email
        $email = $object->get('email');
        if (!$email instanceof TextStringObject) {
            throw new InvalidArgumentException('Email must be a text string');
        }
        if (!filter_var($email->getValue(), FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException('Invalid email format');
        }

        // Validate age
        $age = $object->get('age');
        if (!$age instanceof UnsignedIntegerObject) {
            throw new InvalidArgumentException('Age must be an unsigned integer');
        }
        $ageValue = (int) $age->getValue();
        if ($ageValue < 0 || $ageValue > 150) {
            throw new InvalidArgumentException('Age must be between 0 and 150');
        }

        parent::__construct($additionalInformation, $data, $object);
    }

    public static function getTagId(): int
    {
        return self::TAG_USER_PROFILE;
    }

    public static function createFromLoadedData(
        int $additionalInformation,
        ?string $data,
        CBORObject $object
    ): Tag {
        return new self($additionalInformation, $data, $object);
    }

    public static function create(CBORObject $object): self
    {
        [$ai, $data] = self::determineComponents(self::TAG_USER_PROFILE);
        return new self($ai, $data, $object);
    }

    public static function createFromArray(array $profile): self
    {
        $map = MapObject::create()
            ->add(
                TextStringObject::create('username'),
                TextStringObject::create($profile['username'])
            )
            ->add(
                TextStringObject::create('email'),
                TextStringObject::create($profile['email'])
            )
            ->add(
                TextStringObject::create('age'),
                UnsignedIntegerObject::create($profile['age'])
            );

        return self::create($map);
    }

    public function normalize(): array
    {
        /** @var MapObject $map */
        $map = $this->object;

        return [
            'username' => $map->get('username')->normalize(),
            'email' => $map->get('email')->normalize(),
            'age' => (int) $map->get('age')->normalize(),
        ];
    }
}
```

### Using it

```php
use CBOR\Tag\UserProfileTag;

// Create from array
$profile = UserProfileTag::createFromArray([
    'username' => 'john_doe',
    'email' => 'john@example.com',
    'age' => 30,
]);

// Validation happens automatically
try {
    $invalid = UserProfileTag::createFromArray([
        'username' => 'jo', // Too short!
        'email' => 'invalid-email',
        'age' => 30,
    ]);
} catch (InvalidArgumentException $e) {
    echo $e->getMessage(); // "Username must be at least 3 characters"
}
```
