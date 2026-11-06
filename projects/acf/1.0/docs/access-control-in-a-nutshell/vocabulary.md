# Vocabulary

Read this page before any other. One word here means the opposite of what the security literature makes you expect, and the choice is deliberate.

## The four fields of a question

Every question is an `AccessRequest`, and it carries four things.

```php
new AccessRequest(
    requester: $token,          // who asks
    attribute: 'EDIT',          // what they want to do
    subject: $post,             // what they want to do it to
    environment: new AccessEnvironment(['ip' => $ip]),  // the circumstances
);
```

They line up with the attribute categories of ABAC and XACML, but two of the names differ:

| This component | XACML calls it |
|---|---|
| `requester` | subject |
| `attribute` | action |
| `subject` | resource |
| `environment` | environment |

## Why `subject` means the resource

**`subject` is the thing being acted upon, not the actor.** That is what it has meant in Symfony for a decade: it is the word every application voter uses, the word of `#[IsGranted]`, the word of the Twig function, and the word of `AuthorizationCheckerInterface::isGranted()`, which this component's Security bridge implements.

Renaming it would not remove the translation, it would move it to that seam, where every existing voter and every existing template would meet it. So `subject` stays, and the actor gets a name of its own: `requester`, which says more plainly than `subject` ever could who is doing the asking.

If you come from XACML, this is the only place you have to make the substitution. If you come from Symfony, there is nothing to substitute.

## The requester is not a user

There is no `UserInterface` anywhere in the contract, and no token either. The requester is `mixed`, and it is whatever your application says it is:

* a Symfony `TokenInterface`, when you have one,
* an object implementing `UserWithRoleInterface`, or simply carrying a `getRoles()` method,
* a machine actor, a service account, an API key,
* a string.

A voter that does not understand a requester abstains. That is the whole protocol. See [Requesters and Actors](requesters.md).

## The three answers, and why there are three

A voter answers with an `AccessOutcome`, which carries a `DecisionVote`:

```php
AccessOutcome::grant('The user owns the post.');
AccessOutcome::deny('Only the author may edit.');
AccessOutcome::abstain('This voter knows nothing about posts.');
```

**Abstaining is a result of its own, not a refusal.** A voter that does not understand the question must say so rather than deny, because a denial is an opinion and silence is not. What happens when every voter abstains is settled once, by configuration, and can be overridden per question. See [Combining Algorithms](combining-algorithms.md).

## The environment

`AccessEnvironment` holds the circumstances of a request: what belongs neither to the requester, nor to the subject, nor to the attribute.

```php
$environment = new AccessEnvironment(['ip' => '10.0.0.1', 'hour' => 22]);

$environment->get('ip');              // '10.0.0.1'
$environment->get('country', 'FR');   // the default, the key being absent
$environment->has('country');         // false
count($environment);                  // 2
```

It is deliberately not silent about a missing key when a rule needs one. A rule that abstains because a key is absent fails open, and no entry point should be able to disable a rule by omission: read the key with `has()` and decide what its absence means, rather than letting `get()` hand you a default you did not think about.

### The keys the component seeds

Each entry point fills in what it knows, and **these four are the only names this component puts there**. Everything else in the bag is yours.

| Constant | Key | Seeded by |
|---|---|---|
| `AccessEnvironment::REQUEST` | `request` | Every web entry point: the access policy listener, the URL rule listener, the `#[IsGranted]` bridge |
| `AccessEnvironment::COMMAND` | `command` | The console entry point |
| `AccessEnvironment::INPUT` | `input` | The console entry point |
| `AccessEnvironment::OUTPUT` | `output` | The console entry point |

`AccessEnvironment::SEEDED_KEYS` holds the four, so an application can tell them from its own.

They are what a `When` condition names: `request.isMethod("POST")` on the web, `input.getOption("force")` on the console. Each entry point pins its own set with a test, because a key silently dropped or renamed is a guard that stops applying rather than a guard that breaks.

### Why the bag stays open

The keys are free on purpose, and this was arbitrated rather than left undecided.

Nothing in the component ever reads a key: the environment is carried through to the expression voter, which publishes it as a variable, to the closure voter, and to the profiler panel. **Its consumers are all string-keyed**, so a PHP type would buy them nothing while costing the library its independence from HttpFoundation and Console, which today it does not require at all.

The mistake typing would catch is already loud where it matters: an expression naming a variable nothing seeded raises at compile time, `Variable "actor" is not valid`. What remains silent is `$environment->get('typo')` in a voter of your own, and typing the four keys above would not have covered that either, your keys being yours.

## A decision is not a boolean

`decide()` hands back an `AccessDecision`, not a `bool`. It carries the verdict, the reason, the votes that were cast and who cast them.

```php
$decision = $accessControlManager->decide($accessRequest);

$decision->isGranted();   // the verdict alone, for callers that only branch on it
$decision->decision;      // the DecisionVote, where an abstention is still an abstention
$decision->reason;        // the strategy's summary, then the reasons that concur with it
$decision->votes;         // a list of CastVote: a voter, and what it answered
```

`isGranted()` answers `false` for an abstention exactly as it does for a refusal, which is what every entry point already does with one. When you need to tell the two apart, read `decision`.

The reason is what makes a denial diagnosable rather than merely final. It is what the profiler panel shows, what the test assertions match on, and what a template can display.
