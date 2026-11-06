---
description: The three keys of the bundle configuration
---

# Configuring the bundle

```yaml
# config/packages/cbor.yaml
cbor:
    max_depth: 1000
    tags:
        - App\Cbor\CustomTag
    other_objects:
        - App\Cbor\CustomObject
```

## The nesting depth

`max_depth` is the [nesting limit](../guide/decoding.md#limiting-the-nesting-depth) the decoder accepts,
`Decoder::DEFAULT_MAX_DEPTH` — 1000 — by default. Decoding is recursive, and a nested array, map or tag
costs one byte per level to write: a payload nested deeply enough exhausts the call stack and takes the PHP
process with it. Past the limit, the document is rejected with an `InvalidArgumentException` instead.

A request body never needs a thousand levels. When the payloads come from somewhere you do not control,
lower it:

```yaml
cbor:
    max_depth: 32
```

## Tags and simple values

`tags` and `other_objects` name the classes the decoder should add to its managers — the subject of
[tags and simple values of your own](extending.md). A class in a directory the container discovers, `src/`
in a standard application, needs no entry here at all: it is autoconfigured.
