---
description: Where the public keys and details are stored
---

# Credential record repository

The Credential Record can be stored the way you want. As the `Webauthn\CredentialRecord` class can be converted into JSON, it could be stored in a filesystem.

It is up to you to create a credential record repository. This service shall implement `Webauthn\Bundle\Repository\CredentialRecordRepositoryInterface`.

!!! warning

    **Renamed in v5.3.0:** `PublicKeyCredentialSource` has been renamed to `CredentialRecord` and `PublicKeyCredentialSourceRepositoryInterface` to `CredentialRecordRepositoryInterface`. The old names are deprecated and will be removed in 6.0.

!!! info

    **Fixed in v5.3.7:** the bundle aliases the deprecated `PublicKeyCredentialSourceRepositoryInterface` to your repository only when that repository actually implements it. Symfony refuses an interface alias whose target does not implement the interface, so a repository following the deprecation and implementing `CredentialRecordRepositoryInterface` alone made the container invalid. Applications whose repository still implements the legacy interface keep the alias, and code type-hinting it keeps working.

!!! warning

    Doctrine users: the field type for `transports` and `other_ui` changed from `array` to `json` (`array` is now deprecated) between the bundle v4.x and 5.0.

    Please make sure to reflect the changes to your data model.

    Here is an example for Postgres:

    ```sql
    ALTER TABLE [/*TABLE NAME HERE*/] ALTER transports TYPE JSON USING transports::JSON
    ALTER TABLE [/*TABLE NAME HERE*/] ALTER other_ui TYPE JSON USING other_ui::JSON

    ```

## Registration capability

By default, the User Entity Repository is not able to register any user account. You can add this behavior by implementing the interface `Webauthn\Bundle\Repository\CanRegisterUserEntity`.

## Doctrine

In general, Symfony applications use Doctrine. The bundle does not provide the entity or the repository: you map an entity of your application and convert it from and to `Webauthn\CredentialRecord` in your repository, as for the [user entity](user-entity-repository.md).

!!! warning

    **Deprecated in v5.4.0:** the Doctrine mapping of `Webauthn\CredentialRecord`, `Webauthn\PublicKeyCredentialUserEntity` and `Webauthn\PublicKeyCredentialEntity` provided by the bundle. It is removed in 6.0.0. An entity extending one of these classes triggers a deprecation when Doctrine loads its metadata, and is refused in 6.0.0. Map an entity of your application as shown below.

### The entity

This is the most simple example. Feel free to add custom fields that fit your needs e.g. `created_at` or `is_revoked`.

The bundle registers the Doctrine types used by the columns: `base64` for the binary strings, `trust_path` and `aaguid`. The signature counter is an unsigned 32-bit integer, hence the `BIGINT` column.

```php title="src/Entity/WebauthnCredential.php" linenums="1"
<?php

declare(strict_types=1);

namespace App\Entity;

use App\Repository\WebauthnCredentialRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Uid\Ulid;
use Symfony\Component\Uid\Uuid;
use Webauthn\CredentialRecord;
use Webauthn\TrustPath\TrustPath;

#[ORM\Entity(repositoryClass: WebauthnCredentialRepository::class)]
#[ORM\Table(name: 'webauthn_credentials')]
class WebauthnCredential
{
    #[ORM\Id]
    #[ORM\Column(unique: true)]
    private string $id;

    #[ORM\Column(type: 'base64')]
    private string $publicKeyCredentialId;

    #[ORM\Column]
    private string $type;

    /**
     * @var string[]
     */
    #[ORM\Column(type: Types::JSON)]
    private array $transports;

    #[ORM\Column]
    private string $attestationType;

    #[ORM\Column(type: 'trust_path')]
    private TrustPath $trustPath;

    #[ORM\Column(type: 'aaguid', length: 36)]
    private Uuid $aaguid;

    #[ORM\Column(type: 'base64')]
    private string $credentialPublicKey;

    #[ORM\Column]
    private string $userHandle;

    #[ORM\Column(type: Types::BIGINT)]
    private int $counter;

    /**
     * @var array<string, mixed>|null
     */
    #[ORM\Column(type: Types::JSON, nullable: true)]
    private ?array $otherUI;

    #[ORM\Column(nullable: true)]
    private ?bool $backupEligible;

    #[ORM\Column(nullable: true)]
    private ?bool $backupStatus;

    #[ORM\Column(nullable: true)]
    private ?bool $uvInitialized;

    #[ORM\Column(nullable: true)]
    private ?string $rpId;

    private function __construct()
    {
        $this->id = Ulid::generate();
    }

    public static function fromCredentialRecord(CredentialRecord $record): self
    {
        $credential = new self();
        $credential->publicKeyCredentialId = $record->publicKeyCredentialId;
        $credential->type = $record->type;
        $credential->transports = $record->transports;
        $credential->attestationType = $record->attestationType;
        $credential->trustPath = $record->trustPath;
        $credential->aaguid = $record->aaguid;
        $credential->credentialPublicKey = $record->credentialPublicKey;
        $credential->userHandle = $record->userHandle;
        $credential->otherUI = $record->otherUI;
        $credential->rpId = $record->rpId;
        $credential->update($record);

        return $credential;
    }

    public function update(CredentialRecord $record): void
    {
        $this->counter = $record->counter;
        $this->backupEligible = $record->backupEligible;
        $this->backupStatus = $record->backupStatus;
        $this->uvInitialized = $record->uvInitialized;
    }

    public function toCredentialRecord(): CredentialRecord
    {
        return CredentialRecord::create(
            $this->publicKeyCredentialId,
            $this->type,
            $this->transports,
            $this->attestationType,
            $this->trustPath,
            $this->aaguid,
            $this->credentialPublicKey,
            $this->userHandle,
            $this->counter,
            $this->otherUI,
            $this->backupEligible,
            $this->backupStatus,
            $this->uvInitialized,
            $this->rpId,
        );
    }

    public function getId(): string
    {
        return $this->id;
    }
}
```

!!! info

    Do not forget to update your database schema!

### The repository

!!! warning

    **Deprecation Notice (v5.2.0):** The `DoctrineCredentialSourceRepository` class is deprecated and will be removed in version 6.0.0. The repository below does not extend it.

The repository implements `Webauthn\Bundle\Repository\CredentialRecordRepositoryInterface`, and `Webauthn\Bundle\Repository\CanSaveCredentialRecord` to store the new credentials and the updated counters. Feel free to add your own methods.

```php title="src/Repository/WebauthnCredentialRepository.php" linenums="1"
<?php

declare(strict_types=1);

namespace App\Repository;

use App\Entity\WebauthnCredential;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;
use Webauthn\Bundle\Repository\CanSaveCredentialRecord;
use Webauthn\Bundle\Repository\CredentialRecordRepositoryInterface;
use Webauthn\CredentialRecord;
use Webauthn\PublicKeyCredentialUserEntity;

/**
 * @extends ServiceEntityRepository<WebauthnCredential>
 */
final class WebauthnCredentialRepository extends ServiceEntityRepository implements CredentialRecordRepositoryInterface, CanSaveCredentialRecord
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, WebauthnCredential::class);
    }

    public function saveCredentialRecord(CredentialRecord $credentialRecord): void
    {
        $credential = $this->findOneBy([
            'publicKeyCredentialId' => $credentialRecord->publicKeyCredentialId,
        ]);
        if ($credential === null) {
            $this->getEntityManager()->persist(WebauthnCredential::fromCredentialRecord($credentialRecord));
        } else {
            $credential->update($credentialRecord);
        }
        $this->getEntityManager()->flush();
    }

    public function findOneByCredentialId(string $publicKeyCredentialId): ?CredentialRecord
    {
        return $this->findOneBy([
            'publicKeyCredentialId' => $publicKeyCredentialId,
        ])?->toCredentialRecord();
    }

    /**
     * @return CredentialRecord[]
     */
    public function findAllForUserEntity(PublicKeyCredentialUserEntity $publicKeyCredentialUserEntity): array
    {
        return array_map(
            static fn (WebauthnCredential $credential): CredentialRecord => $credential->toCredentialRecord(),
            $this->findBy([
                'userHandle' => $publicKeyCredentialUserEntity->id,
            ])
        );
    }
}
```

The ceremonies update the counter, the backup status and the user verification flag of a credential record. `update()` copies them to the entity, the other members never change.

This repository should be declared as a Symfony service.

!!! info

    With Symfony autowiring and autoconfiguration, this is usually done automatically

```yaml title="config/services.yaml"
services:
    App\Repository\WebauthnCredentialRepository: ~
```

### Moving from an entity extending `CredentialRecord`

Up to 5.3, this page showed an entity extending `Webauthn\CredentialRecord`. Such an entity gets its columns from the Doctrine mapping of the bundle.

The entity above declares the same properties as `CredentialRecord`, so it maps to the same columns. Keep the name of your table and your identifier as they are. Once the migration of 5.4.0 has run (see [From 5.3 to 5.4](../migration/from-v5.3-to-v5.4.md)), the columns already match and the switch requires no schema change.

The repository now converts the entity from and to `CredentialRecord`. Code of your application that used the entity as a credential record calls `toCredentialRecord()` instead.
