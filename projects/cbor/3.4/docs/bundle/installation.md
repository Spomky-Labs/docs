---
description: Installing and registering the Symfony bundle
---

# Installing the bundle

[spomky-labs/cbor-bundle](https://github.com/Spomky-Labs/cbor-bundle) wires this library into a Symfony
application: CBOR becomes a format of the Serializer, and the encoder and decoder become services.
Version 3.2 of the bundle is the one that pairs with version 3.4 of the library.

```bash
composer require spomky-labs/cbor-bundle
```

## What it needs

-   PHP 8.3 or later
-   Symfony 6.4, 7.x or 8.x
-   `spomky-labs/cbor-php` 3.4 or later, which Composer installs with it

## Registering it

Symfony Flex registers the bundle. Without Flex, add it to `config/bundles.php`:

```php
return [
    // …
    SpomkyLabs\CborBundle\SpomkyLabsCborBundle::class => ['all' => true],
];
```

It works as it stands: the only thing worth setting is
[the nesting depth](configuration.md#the-nesting-depth), and that only matters for payloads you did not
write yourself.
