# Console commands

A command is guarded the same way a controller is, by declaring the policy on it.

```php
use AccessControl\Attribute\AccessPolicy;

#[AsCommand(name: 'app:import')]
#[AccessPolicy('ROLE_IMPORTER', message: 'This command is reserved to importers.')]
final class ImportCommand extends Command
{
    // ...
}
```

The listener reads the attribute at `ConsoleEvents::COMMAND` and refuses before the command runs. On `__invoke()` rather than on the class, it works the same.

## Who is asking, in a console

There is no token in a console. The component asks the same `RequesterProviderInterface` as everywhere else, and the default implementation hands over a fixed requester, typically a service account:

```yaml
services:
    AccessControl\Requester\StaticRequesterProvider:
        arguments:
            $requester: '@App\Security\ServiceAccount'

    access_control.requester_provider:
        alias: AccessControl\Requester\StaticRequesterProvider
```

See [Requesters and Actors](../access-control-in-a-nutshell/requesters.md#telling-the-component-who-is-asking).

## Conditions on the invocation

`When` reads the console context, so a policy can depend on an option:

```php
use AccessControl\Attribute\When;
use Symfony\Component\ExpressionLanguage\Expression;

#[When(new Expression('input.getOption("force")'), [
    new AccessPolicy('ROLE_ADMIN'),
])]
```

Only the forced run needs `ROLE_ADMIN`; the ordinary one steps aside. On the web, the same attribute reads `request` instead. See [Access Policies](../pure-php/access-policies.md#when).

## The exit code is 113

A denial leaves as an exception rather than by disabling the command, so its reason reaches the terminal and `ConsoleEvents::ERROR` is dispatched at all.

The exception carries `ConsoleCommandEvent::RETURN_CODE_DISABLED`, which is **113**, and which is what the console already means by "this command was not allowed to run". An HTTP status has no place here: a `403` would come out as `255`, exit statuses being capped at 255.

**It is deliberately not configurable.** An exit status is read by the scripts the application owns, not by the policy that refused.

## Choosing your own exit code

The console already offers the way out, and it has the last word:

```php
use Symfony\Component\Console\ConsoleEvents;
use Symfony\Component\Console\Event\ConsoleErrorEvent;

final class AccessDeniedExitCode implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [ConsoleEvents::ERROR => 'onError'];
    }

    public function onError(ConsoleErrorEvent $event): void
    {
        if ($event->getError() instanceof AccessDeniedExceptionInterface) {
            $event->setExitCode(77);
        }
    }
}
```

`setExitCode()` writes the value onto the exception as well, so it wins. It can branch on the command or on the requester, which no setting of ours would have allowed.

This escape hatch exists because the refusal is an exception. Disabling the command instead would dispatch no `ERROR` event and there would be nothing to hook onto.

## Under `--profile`

The console guard runs there too. It has to be said because it once did not: the console hands over a wrapped command, a `TraceableCommand` or a `LazyCommand`, which carries none of the original's attributes. A listener reflecting on the wrapper finds nothing and lets the command through, silently, while every unit test passes on a bare command the console never actually provides.
