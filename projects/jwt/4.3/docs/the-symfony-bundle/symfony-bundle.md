# Symfony bundle

The JWT Framework Symfony Bundle provides seamless integration of the JWT Framework into your Symfony applications. It leverages Symfony's dependency injection container to automatically configure and wire all services, making it easy to work with JSON Web Tokens in your Symfony projects.

## Why use the Symfony bundle?

The bundle offers several advantages for Symfony developers:

### 🎯 **Zero configuration**
- Auto-discovery of algorithms and services
- Automatic service registration
- Sensible defaults out of the box

### 🔧 **Configuration-driven**
- YAML-based configuration for all components
- Type-safe configuration validation
- Environment variable support

### 📊 **Developer tools**
- Symfony Profiler integration
- Debug toolbar with token inspection
- Data collectors for performance monitoring

### 🔄 **Event system**
- Token lifecycle events
- Hook into token creation and validation
- Perfect for logging and auditing

### 🏭 **Factory services**
- Pre-configured factories for common operations
- Easy creation of builders, loaders, and validators
- Support for multiple configurations

## Installation

!!! info

    The bundle supports Symfony 7.0 and Symfony 8.0.

### With Symfony Flex (Recommended)

The bundle is automatically detected and installed when using Symfony Flex:

```bash
composer require web-token/jwt-bundle
```

!!! info

    As the recipes are third party recipes not officially supported by Symfony, you will be asked whether to execute the recipe or not. When applied, the recipes will display a message: `Web Token Framework is ready.`

After installation, the bundle is automatically registered and ready to use!

### Without Symfony Flex

If you're not using Symfony Flex, you need to register the bundle manually:

```php title="config/bundles.php"
<?php

return [
    // ...
    Jose\Bundle\JoseFramework\JoseFrameworkBundle::class => ['all' => true],
];
```

## Quick start example

After installation, you can configure a simple JWS service:

```yaml title="config/packages/jose.yaml"
jose:
    # Configure the algorithm manager
    jws:
        builders:
            my_jws_builder:
                signature_algorithms: ['HS256']

        verifiers:
            my_jws_verifier:
                signature_algorithms: ['HS256']
```

Then use it in your services:

```php
use Jose\Component\Signature\JWSBuilder;
use Jose\Component\Signature\JWSVerifier;

class TokenService
{
    public function __construct(
        private JWSBuilder $jwsBuilder,
        private JWSVerifier $jwsVerifier
    ) {}

    public function createToken(array $claims): string
    {
        // Your token creation logic
    }
}
```

## Bundle features

The bundle provides comprehensive support for all JWT Framework components. Explore the documentation based on your needs:

### Core features

* **[Algorithm Management](algorithm-management.md)** - Configure signature and encryption algorithms
* **[Key and Key Set Management](key-and-key-set-management/README.md)** - Manage cryptographic keys via configuration
* **[Header and Claim Checkers](header-and-claim-checker-management.md)** - Validate token headers and claims

### Token operations

* **[Signed Tokens (JWS)](signed-tokens/README.md)** - Create and verify signed tokens
  * [JWS Serializers](signed-tokens/jws-serializers.md)
  * [JWS Creation](signed-tokens/jws-creation.md)
  * [JWS Verification](signed-tokens/jws-verification.md)

* **[Encrypted Tokens (JWE)](encrypted-tokens/README.md)** - Create and decrypt encrypted tokens
  * [JWE Serializers](encrypted-tokens/jwe-serializers.md)
  * [JWE Creation](encrypted-tokens/jwe-creation.md)
  * [JWE Decryption](encrypted-tokens/jwe-decryption.md)

### Advanced features

* **[Configuration Helper](configuration-helper.md)** - Programmatic configuration
* **[Events](events.md)** - Token lifecycle events and listeners

## Service auto-wiring

All services created through the bundle configuration are automatically available for auto-wiring. You can inject them by type or by name:

```php
use Jose\Bundle\JoseFramework\Services\JWSBuilderFactory;
use Jose\Bundle\JoseFramework\Services\JWSVerifierFactory;

class MyService
{
    public function __construct(
        JWSBuilderFactory $jwsBuilderFactory,
        JWSVerifierFactory $jwsVerifierFactory
    ) {
        // Services are automatically injected
    }
}
```

### Auto-wiring by interface

Every service you declare in the configuration is aliased both with its concrete class and with its **interface**. Naming the argument after the service picks the right one:

```yaml
jose:
    jws:
        builders:
            builder1:
                signature_algorithms: ['ES256']
        verifiers:
            verifier1:
                signature_algorithms: ['ES256']
```

```php
use Jose\Component\Signature\JWSBuilderInterface;
use Jose\Component\Signature\JWSVerifierInterface;

class MyService
{
    public function __construct(
        JWSBuilderInterface $builder1JwsBuilder,   // jose.jws_builder.builder1
        JWSVerifierInterface $verifier1JwsVerifier, // jose.jws_verifier.verifier1
    ) {
    }
}
```

The argument name is the service name followed by the kind of service: `builder1` + `JwsBuilder`. The same convention applies to `JwsLoader`, `JweBuilder`, `JweDecrypter`, `JweLoader`, `NestedTokenBuilder` and `NestedTokenLoader`.

!!! info

    Interfaces were introduced in 4.3. Prefer them over the concrete classes: they are what the library type-hints internally, so a decorator can be injected in place of any service. Type-hinting the concrete class keeps working.

The key factory is aliased the same way:

```php
use Jose\Component\KeyManagement\JWKFactoryInterface;

public function __construct(private JWKFactoryInterface $jwkFactory) {}
```

### Decorating a service

Because every service is described by an interface, decorating one is standard Symfony:

```php
#[AsDecorator('jose.jws_loader.jws_loader1')]
final readonly class LoggingJwsLoader implements JWSLoaderInterface
{
    public function __construct(
        #[AutowireDecorated] private JWSLoaderInterface $inner,
        private LoggerInterface $logger,
    ) {
    }

    public function loadAndVerify(string $token, JWK|JWKSet $keys, ?string $payload = null): LoadingResult
    {
        $result = $this->inner->loadAndVerify($token, $keys, $payload);
        $this->logger->info('Token verified', ['kid' => $result->getKey()->find('kid')]);

        return $result;
    }

    // ... the remaining methods of the interface delegate to $this->inner
}
```

!!! warning

    Extending the concrete classes — `JWSLoader`, `JWEDecrypter`… — is deprecated since 4.3 and raises a notice. Implement the interface and decorate instead. The bundle itself did the same: its event dispatching services are decorators now, and the inheritance based ones are deprecated. They keep their class names, their service ids and their behaviour, so **no configuration change is needed**.

## Configuration split across several files

A service may be configured in more than one place: a `when@prod` block, a second file such as `config/packages/prod/jose.yaml`, or another bundle through the [`ConfigurationHelper`](configuration-helper.md). Since 4.2.7, Symfony merges the alias lists of such a service as follows:

* **checker lists add up**: the checkers of a later list are added to the earlier ones, and an alias listed twice is kept once. This applies to the `claims` and `headers` lists of `checkers`, to the `header_checkers` of the JWS and JWE loaders, and to the `jws_header_checkers` and `jwe_header_checkers` of the nested token loaders;
* **algorithm and serializer lists are replaced**: the last list wins, so that a later configuration cannot widen what a service accepts by accident. This applies to the `signature_algorithms` and `encryption_algorithms` lists of the builders, verifiers, decrypters and loaders, to the `serializers` of the loaders, and to the `jws_serializers` and `jwe_serializers` of the nested token builders and loaders. An empty list replaces nothing;
* the lists of the `selective_disclosure` verifiers, holders and issuers follow the same rules: `header_checkers`, `key_binding_header_checkers` and `claim_checkers` add up, `signature_algorithms` and `key_binding_signature_algorithms` are replaced;
* the `serializers` lists of `jws.serializers` and `jwe.serializers` add up, as they always did.

```yaml
# config/packages/jose.yaml
jose:
    checkers:
        claims:
            api:
                claims: ['exp', 'iat', 'nbf']
    jws:
        verifiers:
            api:
                signature_algorithms: ['RS256', 'HS256']

# config/packages/prod/jose.yaml
jose:
    checkers:
        claims:
            api:
                claims: ['aud_api'] # In prod, the manager checks exp, iat, nbf and aud_api
    jws:
        verifiers:
            api:
                signature_algorithms: ['ES256'] # In prod, the verifier only accepts ES256
```

!!! warning

    Before 4.2.7, these lists were merged position by position. With the configuration above, `aud_api` replaced `exp` in the claim checker manager, and the verifier kept accepting `HS256`. If your configuration is split, check the result with `php bin/console debug:config jose`.

Aliases given under a name, as a mapping rather than a list, are merged by name as before.

## Configuration reference

For a complete configuration reference, run:

```bash
php bin/console config:dump-reference jose
```

## Next steps

- **New to the bundle?** Start with [Algorithm Management](algorithm-management.md)
- **Need to sign tokens?** Check [Signed Tokens](signed-tokens/README.md)
- **Need to encrypt tokens?** Check [Encrypted Tokens](encrypted-tokens/README.md)
- **Advanced configuration?** See [Configuration Helper](configuration-helper.md)
