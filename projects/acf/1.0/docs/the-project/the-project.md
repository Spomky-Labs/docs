# What is Access Control?

A component that answers one question: **is this requester allowed to perform this action on this subject?**

That is authorization, and nothing else. Authentication is a separate concern with a separate answer, and this component never asks it.

## Why it exists

Authorization in a PHP application tends to end up spread across places that do not know about each other: voters in one component, URL rules in a firewall, an attribute on a controller, an expression in a workflow guard, a function in a template. Each of them re-implements a piece of the same idea, and they drift.

This component holds the idea once:

* **voters** that answer a question,
* **combining algorithms** that turn several answers into one,
* **access policies** declared where they apply,
* **decisions** that say why they were reached.

Everything else, the controller attribute, the URL rule, the template function, the console guard, the workflow guard, is an entry point onto the same machinery.

## It does not need an authentication stack

There is no user in the vocabulary, no token, no firewall. The requester is `mixed`: a Symfony token when you have one, and otherwise a service account, a machine actor, an API key, or a string. A voter that does not understand a requester abstains.

`symfony/security-core` is optional throughout, and the classes that know it live in `AccessControl\Bridge\Security`. An application with Security keeps it and changes nothing; an application without it can express everything the same way.

## It says why

A decision is not a boolean. It carries the verdict, the reason, and who voted which way.

That is what makes a refusal diagnosable six months later, and it is what the profiler panel, the log and the test assertions all read. A denial reaching an HTTP response is still a bare `403`: the diagnostic is available to the developer and withheld from the visitor.

## The failure it is built against

A guard that lets somebody through is the only unacceptable failure, and it is silent. Nothing in a test suite goes red, nothing in a log goes wrong; access rules simply stop applying.

So the component is built to fail loudly instead. What the Symfony bridge cannot absorb raises at compile time rather than at runtime: two combining algorithms named at once, two sets of URL rules, two role hierarchies, contradictory settings, a template function Security would publish that we did not expect. What a reprise cannot do refuses out loud rather than answering `false`, because a refusal a template cannot tell from a real one is the same family of fault.
