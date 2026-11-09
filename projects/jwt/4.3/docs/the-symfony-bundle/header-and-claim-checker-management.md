# Header and claim checker management

## Checker manager factory services

The Symfony Bundle provides Header and Claim Checker Manager Factory services.&#x20;

```php
<?php

use Jose\Bundle\JoseFramework\Services\HeaderCheckerManagerFactory;
use Jose\Bundle\JoseFramework\Services\ClaimCheckerManagerFactory;

$headerCheckerManagerFactory = $container->get(HeaderCheckerManagerFactory::class);
$headerCheckerManager = $headerCheckerManagerFactory->create([...]);

$claimCheckerManagerFactory = $container->get(ClaimCheckerManagerFactory::class);
$claimCheckerManager = $claimCheckerManagerFactory->create([...]);
```

## Checker manager services

You can create Header and Claim Checker Managers using the bundle configuration.

```yaml
jose:
    checkers:
        claims:
            checker1:
                is_public: true
                claims: [...]
        headers:
            checker1:
                is_public: true
                headers: [...]
```

With the previous configuration, the bundle will create public Header and Claim Checker Managers named `jose.header_checker.checker1` and `jose.claim_checker.checker1` with selected checkers.

When a manager is configured in more than one place, for instance in a `when@prod` block or by another bundle, its checker lists add up: see [Configuration split across several files](symfony-bundle.md#configuration-split-across-several-files).

!!! warning

    A manager holds one checker per claim or header parameter. Since 4.3, a manager that receives two different checkers of the same claim or header parameter triggers a deprecation, and it is not possible in 5.0: only the last one is kept, the other one never runs. The bundle lists aliases, so the notice names the claim or header parameter and the classes of the two checkers. This happens, for instance, with `claims: ['exp', 'max_lifetime']` when `max_lifetime` is a `CallableChecker` of the `exp` claim, or when `headers:` lists a `typ` checker next to the `typ:` option described below. Combine the rules in a single checker, see [One checker per claim](../the-components/claim-checker.md#one-checker-per-claim).

### Explicit typing

Since 4.3, a header checker manager can declare the media types accepted for the `typ` header parameter (see [Explicit Typing](../the-components/header-checker.md#explicit-typing-with-the-typ-header)). The bundle registers a `TypeChecker` service with the alias `typ.<name>` and adds it to the manager.

```yaml
jose:
    checkers:
        headers:
            access_token:
                headers: ['alg']
                typ: ['at+jwt'] # A single string is accepted too
```

The alias `typ.access_token` can be reused in any other manager or loader, e.g. in the `header_checkers` option of a JWS loader.

Remember that the checker only rejects a wrong `typ`: to reject tokens without any, list `typ` in the mandatory header parameters when calling `check()`.

## Custom header or claim checker

Some claim or header checkers are provided by this framework, but it is important to create custom checkers that fit your application requirements.

In the following example, we will assume that the class exist and implement either `Jose\Component\Checker\HeaderChecker` or `Jose\Component\Checker\ClaimChecker`.

```yaml
services
    Acme\Checker\CustomHeaderChecker:
        public: false
        tags:
            - { name: 'jose.checker.header', alias: 'foo' }
    Acme\Checker\CustomClaimChecker:
        public: false
        tags:
            - { name: 'jose.checker.claim', alias: 'bar' }
```

These checkers will be loaded by the factories and you will be able to create a header or a claim checker manager using the aliases `foo` or `bar`.

### One service per alias

An alias names one service. When two services are tagged with the same alias, the factory keeps the one tagged last, and the other one is never used. The services of the application are defined before those of the bundle, so an application checker tagged with an alias the bundle already uses (`exp`, `iat`, `nbf`) is replaced by the checker of the bundle.

!!! warning

    Since 4.3, tagging two services with the same alias is deprecated, and it is not possible in 5.0. This applies to the `jose.checker.header`, `jose.checker.claim` and [`jose.algorithm`](algorithm-management.md#custom-algorithm) tags. The service tagged last is still the one kept. The notice is triggered while the container is compiled: in debug mode, `debug:container --deprecations` and the profiler show it. One service tagged twice with the same alias, or under several aliases, triggers nothing.

Give each service an alias of its own:

```yaml
services:
    app.protected_exp_header_checker:
        class: Jose\Component\Checker\ExpirationTimeChecker
        arguments: { $clock: '@Psr\Clock\ClockInterface', $protectedHeaderOnly: true }
        tags:
            - { name: 'jose.checker.header', alias: 'exp_protected' }

jose:
    checkers:
        headers:
            api:
                headers: ['exp_protected']
```

To replace a service of the bundle instead, either:

* redefine it under its own id, the class name: the service definitions of the application replace those of the bundle. Your definition replaces the whole service, so give it the tags it needs;
* or [decorate it](https://symfony.com/doc/current/service_container/service_decoration.html): the factory then receives the decorator under the same alias.

```yaml
services:
    Jose\Component\Checker\ExpirationTimeChecker:
        arguments: { $clock: '@Psr\Clock\ClockInterface', $protectedHeaderOnly: true }
        tags:
            - { name: 'jose.checker.claim', alias: 'exp' }
            - { name: 'jose.checker.header', alias: 'exp' }
```

## Custom tags

You can add custom tags and attributes to the header and claim checker managers.

```yaml
jose:
    checkers:
        claims:
            checker1:
                claims: [...]
                tags:
                    tag_name1: ~
                    tag_name2: {attribute1: 'foo'}
```
