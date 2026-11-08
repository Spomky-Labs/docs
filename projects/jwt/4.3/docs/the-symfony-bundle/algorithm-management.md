# Algorithm management

## Algorithm manager factory service

The Symfony Bundle provides an Algorithm Manager Factory service. The available algorithms depends on the components installed on your application.

```php
<?php

use Jose\Component\Core\AlgorithmManagerFactory;

$algorithmManagerFactory = $container->get(AlgorithmManagerFactory::class);
$algorithmManager = $algorithmManagerFactory->create(['RS256', 'HS512']);
```

## Custom algorithm

This factory handles all algorithms services tagged with `jose.algorithm`.

Example:

```yaml
services:
    Acme\Bundle\Algorithm\FooAlgorihtm:
        tags:
            - {'name': 'jose.algorithm', 'alias': 'FOO'}
```

Your algorithm will be available through the algorithm manager factory service and the alias `FOO`.

!!! warning

    An alias names one algorithm service: give your algorithm an alias that no other service uses. Since 4.3, tagging two services with the same alias is deprecated, and it is not possible in 5.0: the service tagged last replaces the other one, and the algorithms of the bundle are tagged after those of the application. See [One service per alias](header-and-claim-checker-management.md#one-service-per-alias).

## PBES2-\* algorithms

When installed, the `PBES2-*` algorithms are available through the algorithm manager factory. They have the default configuration, i.e. a salt of 64 bytes and a count of 4096. If these values do not fit your needs, you can create a new algorithm service with your own values:

```yaml
services:
    my.custom.PBES2HS256A128KW.algorithm:
        class: Jose\Component\Encryption\Algorithm\KeyEncryption\PBES2HS256A128KW
        arguments:
            - 128   # salt size
            - 10240 # counts
        tags:
            - {'name': 'jose.algorithm', 'alias': 'Ultra-Secured PBES2-HS256+A128KW'}
```

You can now use your custom alias:

```php
$algorithmManager = $algorithmManagerFactory->create(['Ultra-Secured PBES2-HS256+A128KW']);
```

To change the parameters of an algorithm of the bundle under its standard alias instead, redefine its service under its own id, the class name, with its tag. The service definitions of the application replace those of the bundle:

```yaml
services:
    Jose\Component\Encryption\Algorithm\KeyEncryption\PBES2HS256A128KW:
        arguments:
            - 128   # salt size
            - 10240 # counts
        tags:
            - {'name': 'jose.algorithm', 'alias': 'PBES2-HS256+A128KW'}
```
