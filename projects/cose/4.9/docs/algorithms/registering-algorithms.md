---
description: 'Building a Manager, and why the set of acceptable algorithms is the operator''s.'
---

# Registering algorithms

`Cose\Algorithm\Manager` registers each algorithm under the identifier it declares, and
`Cose\Algorithm\ManagerFactory` registers algorithms under aliases so that a `Manager` can be generated from a subset
of them.

```php
use Cose\Algorithm\Manager;
use Cose\Algorithm\ManagerFactory;
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Algorithm\Signature\RSA\RS256;

$manager = Manager::create()->add(ES256::create(), RS256::create());

$factory = ManagerFactory::create()
    ->add('ES256', ES256::create())
    ->add('RS256', RS256::create());
$manager = $factory->generate('ES256');
```

A later registration for an identifier, or, on the factory, for an alias, that is already taken replaces the earlier
one. When the replacement is an instance of **another** class, that is a misconfiguration rather than an intent:
`list()` keeps reporting a single entry, and which verifier answers for the identifier is decided by registration order
alone, which in a Symfony application means by the service container. Such a replacement therefore emits an
`E_USER_WARNING`. Registering the same class twice stays silent, so a container that autoconfigures an algorithm more
than once keeps working.

As of the next major version, a duplicate bound to a different class will throw an `InvalidArgumentException`, and an
explicit `replace()` will be the way to override a registration on purpose.

`Manager::withKeyRestrictionsEnforced()` returns a manager whose every algorithm enforces the `alg` and `key_ops` of
the key, see [Key restrictions](../keys/key-restrictions.md).
