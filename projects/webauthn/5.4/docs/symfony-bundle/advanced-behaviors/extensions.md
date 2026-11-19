# Extensions

## Extension output checker

An Extension Output Checker will check the extension output.

It must implement the interface `Webauthn\AuthenticationExtensions\ExtensionOutputChecker` and throw an exception of type `Webauthn\AuthenticationExtension\ExtensionOutputError` in case of error.

!!! info

    Devices may ignore the extension inputs. The extension outputs are therefore not guaranteed.

In the previous example, we asked for the location of the device and we expect to receive geolocation data in the extension output.

```php linenums="1"
<?php

declare(strict_types=1);

namespace Acme\Extension;

use Webauthn\AuthenticationExtensions\ExtensionOutputChecker;
use Webauthn\AuthenticationExtensions\ExtensionOutputError;

final class LocationExtensionOutputChecker
{
    public function check(AuthenticationExtensionsClientInputs $inputs, AuthenticationExtensionsClientOutputs $outputs): void
    {
        if (!$inputs->has('uvm') || $inputs->get('uvm') !== true) {
            return;
        }

        if (!$outputs->has('uvm')) {
            //You may simply return but here we consider it is a mandatory extension output.
            throw new ExtensionOutputError(
                $inputs->get('uvm'),
                'The User Verification Method is missing'
            );
        }

        $uvm = $outputs->get('uvm');
        //... Proceed with the output
    }
}
```

With the [options helpers](../options-helpers.md), pass the extensions to `withExtensions()`. The list replaces the extensions of the options.

```php linenums="1"
use Webauthn\AuthenticationExtensions\AuthenticationExtension;

return $this->options
    ->forRequest('example.com')
    ->withExtensions([AuthenticationExtension::create('uvm', true)])
    ->build($request);
```

!!! warning

    **Deprecated in v5.4.0:** the creation and request profiles below are removed in 6.0.0. See [From 5.3 to 5.4](../../migration/from-v5.3-to-v5.4.md).

```yaml title="config/packages/webauthn.yaml" linenums="1"
webauthn:
    …
    creation_profiles:
        default:
            rp:
                name: 'My Application'
                id: 'example.com'
            extensions:
                uvm: true
    request_profiles:
        default:
            rp_id: 'example.com'
            extensions:
                uvm: true
```
