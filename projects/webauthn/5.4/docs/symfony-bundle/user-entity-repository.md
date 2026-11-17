# User entity repository

## User entity

Your application certainly has a user repository. Good news: there is no need to modify it!

The User Entity Repository can be completely decoupled from the user entity used by your application.

This repository should be declared as a Symfony service and shall implement `Webauthn\Bundle\Repository\PublicKeyCredentialUserEntityRepositoryInterface`.

Here is an example where the application User Repository is injected. This repository uses Doctrine and provides `findOneBy*` methods.

```php title="src/Repository/WebauthnUserEntityRepository.php" linenums="1"
<?php

declare(strict_types=1);

namespace App\Repository;

use App\Entity\User;
use Webauthn\Bundle\Repository\PublicKeyCredentialUserEntityRepositoryInterface;
use Webauthn\PublicKeyCredentialUserEntity;

final class WebauthnUserEntityRepository implements PublicKeyCredentialUserEntityRepositoryInterface
{
    /**
     * The UserRepository $userRepository is the repository
     * that already exists in the application
     */
    public function __construct(private UserRepository $userRepository)
    {
    }

    public function findOneByUsername(string $username): ?PublicKeyCredentialUserEntity
    {
        /** @var User|null $user */
        $user = $this->userRepository->findOneBy([
            'username' => $username,
        ]);

        return $this->getUserEntity($user);
    }

    public function findOneByUserHandle(string $userHandle): ?PublicKeyCredentialUserEntity
    {
        /** @var User|null $user */
        $user = $this->userRepository->findOneBy([
            'id' => $userHandle,
        ]);

        return $this->getUserEntity($user);
    }

    /**
     * Converts a Symfony User (if any) into a WebAuthn User Entity
     */
    private function getUserEntity(null|User $user): ?PublicKeyCredentialUserEntity
    {
        if ($user === null) {
            return null;
        }

        return new PublicKeyCredentialUserEntity(
            $user->getUsername(),
            $user->getUserIdentifier(),
            $user->getDisplayName(),
            null
        );
    }
}

```

## Registration capability

By default, the User Entity Repository is not able to register any user account. You can add this behavior by implementing the following interfaces:

* `Webauthn\Bundle\Repository\CanRegisterUserEntity`
* `Webauthn\Bundle\Repository\CanGenerateUserEntity`

!!! danger

    **Changed in v5.3.13:** `RequestBodyUserEntityGuesser`, used by the registration endpoint of the firewall, always asks `CanGenerateUserEntity` for a new user entity, whether the username is taken or not, and refuses a generated entity whose user handle already belongs to a user ([GHSA-3chw-82qh-p72w](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-3chw-82qh-p72w)). The user handle you generate must be new and random: a repository that derives it from the username returns the handle of the existing account, and the registration is refused. A repository that does not implement `CanGenerateUserEntity` now gets a `MissingUserEntityException` for an existing username as well.
