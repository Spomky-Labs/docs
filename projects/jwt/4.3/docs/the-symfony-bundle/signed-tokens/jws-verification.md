# JWS verification

## JWS verifier factory service

A `JWSVerifierFactory` is available as a service in your application container:

```php
<?php
use Jose\Bundle\JoseFramework\Services\JWSVerifierFactory;

$jwsVerifierFactory = $container->get(JWSVerifierFactory::class);
```

With this factory, you will be able to create the JWSVerifier you need:

```php
$jwsVerifier = $jwsVerifierFactory->create(['HS256']);
```

You can now use the JWSVerifier as explained in the JWS Creation section.

!!! info

    Reminder: it is important to check the token headers. See the checker section of this documentation.

## JWS verifier as service

There is also another way to create a JWSVerifier object: using the bundle configuration.

```yaml
jose:
    jws:
        verifiers:
            verifier1:
                signature_algorithms: ['HS256', 'RS256', 'ES256']
                is_public: true
```

With the previous configuration, the bundle will create a public JWS Verifier service named `jose.jws_verifier.verifier1` with selected signature algorithms.

```php
<?php
$jwsVerifier = $container->get('jose.jws_verifier.verifier1');
```

## Custom tags

You can add custom tags and attributes to the services you create.

```yaml
jose:
    jws:
        verifiers:
            verifier1:
                signature_algorithms: ['HS256', 'RS256', 'ES256']
                tags:
                    tag_name1: ~
                    tag_name2: {attribute1: 'foo'}
```

## JWS loader service

The [`JWSLoaderFactory`](../../the-components/signed-tokens-jws/jws-loading.md) is available as a public service. You can retrieve it using the container or inject it into your services. It will help you to create `JWSLoader` objects on demand.

```php
<?php
use Jose\Bundle\JoseFramework\Services\JWSLoaderFactory;

$jwsLoaderFactory = $container->get(JWSLoaderFactory::class);
```

!!! warning

    The factory services of the bundle are the classes of the `Jose\Bundle\JoseFramework\Services` namespace. Do not register the factories of the library, such as `Jose\Component\Signature\JWSLoaderFactory`, as services of your own: autowiring gives them no header checker manager factory, because the one of the bundle is another class, and the loaders they create check no header parameter. Since 4.2.7, they throw when header checkers are requested, and since 4.3 creating them that way is deprecated, see [Without a header checker manager factory](../../the-components/signed-tokens-jws/jws-loading.md#without-a-header-checker-manager-factory). The factory services of the bundle always have a header checker manager factory.

You can also create `JWSLoader` objects as services using the configuration of the bundle.

```yaml
jose:
    jws:
        loaders:
            jws_loader1:
                serializers: ['jws_compact']
                signature_algorithms: ['HS256']
                header_checkers: ['alg']
                is_public: true
```

### Maximum number of signatures

Since 4.3, a loader accepts a `max_signatures` option: a token with more signatures is rejected before any of them is processed.

```yaml
jose:
    jws:
        loaders:
            jws_loader1:
                serializers: ['jws_compact', 'jws_json_general']
                signature_algorithms: ['HS256']
                header_checkers: ['alg']
                max_signatures: 10
```

Without it, the number of signatures is not limited, but loading a token with more than 10 signatures triggers a deprecation: 10 becomes the default maximum in 5.0. See [Maximum number of signatures](../../the-components/signed-tokens-jws/jws-loading.md#maximum-number-of-signatures).

### Configuration helper

A loader can also be created using the [`ConfigurationHelper`](../configuration-helper.md).

```php
<?php
use Jose\Bundle\JoseFramework\Helper\ConfigurationHelper;

...
ConfigurationHelper::addJWSLoader($container, 'jws_loader1', ['jws_compact'], ['HS256'], ['alg'], true);
```
