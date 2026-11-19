# Fake credentials

In order to prevent username enumeration, random credentials are set when a username is passed but no credential can be listed: the user is unknown, or has no credential.

With the [options helpers](../options-helpers.md#username-enumeration-protection), the request builder uses the generator by default. Use `withFakeCredentialGenerator()` to replace it for one endpoint, or pass `null` to disable it there. The builder does not look the username up: resolve the user in your controller and attach it with `withUser()`.

A very simple service is provided: `Webauthn\SimpleFakeCredentialGenerator`. It derives the list from the username and from a secret, so that a given username always gets the same credentials while an outsider cannot compute them.

!!! danger

    **Security fix in v5.3.5** ([GHSA-gq4g-fpc9-vjfq](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-gq4g-fpc9-vjfq))

    With an empty secret, the generated credentials depend on the username alone and become predictable: an unauthenticated requester can tell a fake response from a real one, which defeats the protection against username enumeration. Building the generator without a secret is deprecated since 5.3.5 and a non-empty secret is required in 6.0.0.

    The bundle injects `%kernel.secret%`, so applications using the default service are not affected. Only a manual instantiation of the generator, in a pure PHP application or in a custom service definition, needs to be fixed.

!!! danger

    **Security fix in v5.3.13** ([GHSA-8gvp-8vj9-p3q7](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-8gvp-8vj9-p3q7))

    The decoys still differed from registered credentials: every decoy ID was 32 bytes long, the transports were drawn at random among six values, and the decoys were seeded with the username as posted, so two spellings of an unknown username got two different lists. Each decoy now takes one of the shapes observed on real authenticators (length of the credential ID and sorted transports). The cache key prefix changes, so the lists cached by previous versions are generated again.

    If your user entity repository finds an account whatever the spelling of its username (a case-insensitive collation, a lowercased lookup), declare a service implementing `Webauthn\UsernameNormalizer`, registered under that interface, that reproduces that lookup exactly. The bundle passes it to the generator, which seeds the decoys with the canonical form. Folding the case in front of a case-sensitive repository would reveal the opposite.

```php linenums="1"
<?php

use Webauthn\SimpleFakeCredentialGenerator;

$generator = new SimpleFakeCredentialGenerator(
    $cacheItemPool, // Optional PSR-6 cache pool
    $applicationSecret,
    $usernameNormalizer, // Optional Webauthn\UsernameNormalizer (new in v5.3.13)
    $shapes // Optional list of Webauthn\FakeCredentialShape replacing the built-in shapes (new in v5.3.13)
);
```

If you want to change the way the fake credentials are generated, you can create a custom service. The service shall implement the `Webauthn\FakeCredentialGenerator` interface.

```php title="src/CustomCredentialGenerator.php" linenums="1"
<?php

namespace App;

use Webauthn\FakeCredentialGenerator;
use Webauthn\PublicKeyCredentialDescriptor;

final readonly class CustomCredentialGenerator implements FakeCredentialGenerator
{
    /**
     * @return PublicKeyCredentialDescriptor[]
     */
    public function generate(Request $request, string $username): array
    {
        // Generate your list of fake credentials.
        // For a given username you should always return the same credentials,
        // and an outsider should not be able to compute them: mix a secret
        // of your own into the generation.
    }
}
```

Then, declare this service in the container and use it in your bundle configuration.

```yaml title="config/packages/webauthn.yaml" linenums="1"
webauthn:
    fake_credential_generator: App\CustomCredentialGenerator
```
