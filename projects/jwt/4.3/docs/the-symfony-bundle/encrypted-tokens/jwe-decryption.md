# JWE decryption

## JWE decrypter factory service

A `JWEDecrypterFactory` is available as a service in your application container:

```php
<?php
use Jose\Bundle\JoseFramework\Services\JWEDecrypterFactory;

$jweDecrypterFactory = $container->get(JWEDecrypterFactory::class);
```

With this factory, you will be able to create the JWEDecrypter you need:

```php
$jweDecrypter = $jweDecrypterFactory->create(['A256GCMKW', 'A256CBC-HS256']);
```

You can now use the JWEDecrypter as explained in the JWE Creation section.

!!! info

    Reminder: it is important to check the token headers. See the checker section of this documentation.

## JWE decrypter as service

There is also another way to create a JWEDecrypter object: using the bundle configuration.

```yaml
jose:
    jwe:
        decrypters:
            decrypter1:
                encryption_algorithms: ['A256GCMKW', 'A256CBC-HS256']
                is_public: true
```

With the previous configuration, the bundle will create a public JWE Decrypter service named `jose.jwe_decrypter.decrypter1` with selected encryption algorithms.

```php
<?php
$jweDecrypter = $container->get('jose.jwe_decrypter.decrypter1');
```

## Custom tags

You can add custom tags and attributes to the services you create.

```yaml
jose:
    jwe:
        decrypters:
            decrypter1:
                encryption_algorithms: ['A256GCMKW', 'A256CBC-HS256']
                tags:
                    tag_name1: ~
                    tag_name2: {attribute1: 'foo'}
```

## JWE loader service

The [`JWELoaderFactory`](../../the-components/encrypted-tokens-jwe/jwe-loading.md) is available as a public service. You can retrieve it using the container or inject it into your services. It will help you to create `JWELoader` objects on demand.

```php
<?php
use Jose\Bundle\JoseFramework\Services\JWELoaderFactory;

$jweLoaderFactory = $container->get(JWELoaderFactory::class);
```

!!! warning

    The factory services of the bundle are the classes of the `Jose\Bundle\JoseFramework\Services` namespace. Do not register the factories of the library, such as `Jose\Component\Encryption\JWELoaderFactory`, as services of your own: autowiring gives them no header checker manager factory, because the one of the bundle is another class, and the loaders they create check no header parameter. Since 4.2.7, they throw when header checkers are requested, and since 4.3 creating them that way is deprecated, see [Without a header checker manager factory](../../the-components/encrypted-tokens-jwe/jwe-loading.md#without-a-header-checker-manager-factory). The factory services of the bundle always have a header checker manager factory.

You can also create `JWELoader` objects as services using the configuration of the bundle.

```yaml
jose:
    jwe:
        loaders:
            jwe_loader1:
                serializers: ['jwe_compact']
                encryption_algorithms: ['A256GCMKW', 'A256CBC-HS256']
                header_checkers: ['alg', 'enc']
                is_public: true
```

### Maximum number of recipients

Since 4.3, a loader accepts a `max_recipients` option: a token with more recipients is rejected before any of them is processed.

```yaml
jose:
    jwe:
        loaders:
            jwe_loader1:
                serializers: ['jwe_compact', 'jwe_json_general']
                encryption_algorithms: ['A256GCMKW', 'A256CBC-HS256']
                header_checkers: ['alg', 'enc']
                max_recipients: 10
```

Without it, the number of recipients is not limited, but loading a token with more than 10 recipients triggers a deprecation: 10 becomes the default maximum in 5.0. See [Maximum number of recipients](../../the-components/encrypted-tokens-jwe/jwe-loading.md#maximum-number-of-recipients).

### Configuration helper

A loader can also be created using the [`ConfigurationHelper`](../configuration-helper.md).

```php
<?php
use Jose\Bundle\JoseFramework\Helper\ConfigurationHelper;

...
ConfigurationHelper::addJWELoader($container, 'jwe_loader1', ['jwe_compact'], ['A256GCMKW', 'A256CBC-HS256'], ['alg', 'enc'], true);
```
