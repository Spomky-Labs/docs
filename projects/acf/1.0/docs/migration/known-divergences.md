# Known divergences

Everything here is deliberate and measured. Nothing on this page is a bug, and nothing is expected to change quietly.

## Refused out loud

These raise rather than degrading. A refusal a caller cannot tell from a real one is the same family of fault as a guard that lets somebody through, so the component would rather stop the build than answer something plausible.

**Field level ACL.** `is_granted('EDIT', $post, 'title')` goes through `symfony/acl`, whose `FieldVote` no voter here understands. The Twig function raises. An application using it cannot install the bundle.

**The same thing declared twice.** Two combining algorithms named at once, two sets of URL rules, two role hierarchies, two contradictory values of `allow_if_all_abstain`: all raise at compile time. Ignoring a key it cannot handle is how a bridge quietly loosens access, and four of the seven shapes of `security.access_decision_manager` did exactly that before this rule was applied.

**A template function Security adds later.** The bundle names the functions it delegates rather than borrowing the extension wholesale, so a function added in a future Symfony release would be left out. The list is checked against Security's own extension and a stranger raises at build time.

**A workflow guard nobody can apply.** With neither Security nor this bundle able to answer it, the container refuses to build rather than compiling into a transition nobody guards.

## Named differently on purpose

**The combining algorithms** carry their XACML names, not Security's. The correspondence is exact and [documented](../access-control-in-a-nutshell/combining-algorithms.md#the-four-algorithms).

**`access_control_decision()`**, and not `access_decision()`. The shapes diverge: `decision` here is an enum where Security's is a boolean, `reason` is a property where Security's is `getMessage()`. A function whose return type depended on the installed bundles would be a trap, so both are published side by side.

**`access_control.rules`**, and not `access_control.access_control`, which is what the key would have read as under this component's root.

## Known and accepted

**`access_decision().strategy` on an application algorithm.** When Security's own function is answered through this component's adapter, an application strategy that is `Stringable` is reported by its string rather than by its class. Reading it back from a definition is not possible, and the string is what the developer wrote.

**`access_decision().votes[].voter`** names the decision manager for every vote rather than the individual voter. An `AccessOutcome` does not know which voter produced it: the pairing lives on the decision, in `CastVote`, because the manager is the only place that knows both. Reading this component's own [`access_control_decision()`](../symfony-bundle/templates.md) gives you the real voters.

**The console exit code is 113 and is not configurable.** It is `ConsoleCommandEvent::RETURN_CODE_DISABLED`, what the console already means by "this command was not allowed to run". An exit status is read by the scripts the application owns, and the [escape hatch](../symfony-bundle/console.md#choosing-your-own-exit-code) is a listener on `ConsoleEvents::ERROR`.

**A denial says nothing in the response.** The reason reaches the profiler, the log and the tests, and never the visitor. Use the `message` of an access policy for text a visitor should read.

**`AccessDeniedException` carries no attributes, subject or decision.** Security's exception has `setAttributes()`, `setSubject()` and `setAccessDecision()`; this one has none of them. Nothing in Symfony reads those accessors, so the loss is confined to application code that does.

**`role_prefix` has no equivalent in SecurityBundle**, where `'ROLE_'` comes from a constructor default and can only be changed by redefining the service.

## Required but never used

`symfony/security-core` has to be **installed** for a workflow guard to compile, even in an application that has no Security. Symfony's `FrameworkExtension` refuses the guard before this bundle's compiler pass replaces the listener. The proper fix is a generic extension point upstream, not a mention of a package that lives outside Symfony. See [Workflow Guards](../symfony-bundle/workflow.md).

## Cosmetic

`debug:container` may report `access_control.voter`, `access_control.strategy` and `access_control.policy_handler` as unused tags. FrameworkBundle's list of known tags does not include them, this bundle living outside the Symfony repository.
