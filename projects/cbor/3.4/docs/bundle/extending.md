---
description: Registering your own tag classes and simple values with the container
---

# Tags and simple values of your own

A tag class — see [writing a tag of your own](../tags/writing-a-tag.md) — joins the decoder through the
container. There are two ways to get it there, and one thing to know about both: **tag classes are not
services.** The decoder instantiates them itself, with the data of each item it reads, so registering one
only ever means naming its class. A class registered for a number the library already handles replaces the
built-in one.

## By discovery

A class implementing `CBOR\Tag\TagInterface` that lives where the container looks — `src/` in a standard
application — needs nothing at all: the bundle autoconfigures every implementation with the `cbor.tag`
service tag, and takes the class of that definition without ever building it.

## By configuration

A class the container does not discover is named in the configuration:

```yaml
# config/packages/cbor.yaml
cbor:
    tags:
        - App\Cbor\CustomTag
```

or given the service tag by hand:

```yaml
services:
    App\Cbor\CustomTag:
        tags: ['cbor.tag']
```

## Simple values and floats

Major type 7 — the simple values, the floats, the break code — works the same way, with
`CBOR\OtherObjectInterface`, usually by extending `CBOR\OtherObject`, the `other_objects` key and the
`cbor.other_object` service tag:

```yaml
cbor:
    other_objects:
        - App\Cbor\CustomObject
```

```yaml
services:
    App\Cbor\CustomObject:
        tags: ['cbor.other_object']
```
