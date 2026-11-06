---
description: What costs time and memory, and what to do about it
---

# Performance

-   **Build one decoder and keep it.** `Decoder::create()` assembles the tag and simple-value managers
    every time it is called. A decoder holds no state about the document it reads, so one instance serves
    a whole request, or a whole process.
-   **Pick the narrowest type.** The head of an item is as short as the value allows: a small integer in
    an `UnsignedIntegerObject` costs one byte, the same number written as a 64-bit value costs nine.
-   **Build a collection once.** Add the items as you go, rather than rebuilding a list or a map to change
    one entry.
-   **Stream what is large.** [Indefinite-length objects](guide/indefinite-length.md) let a producer start
    writing before it knows the total length, and a reader take it in as it arrives.
-   **Install `ext-gmp`.** It is what `brick/math` uses as its fastest calculator; without it the big
    number tags convert their byte strings in quadratic time. `ext-bcmath` is needed by the decimal
    fraction and bigfloat tags in any case.

## What the decoder costs

Decoding is proportional to the bytes it reads, with two exceptions, both of them tags: the
[big number tags](tags/built-in.md#big-numbers), whose conversion to a decimal string is a base
conversion, and the [fractional number tags](tags/built-in.md#fractional-numbers), whose value expands
with their exponent. Both are bounded for that reason — see
[the cost of a hostile document](guide/decoding.md#the-cost-of-a-hostile-document) — and both bounds can
be made tighter than the defaults by your own validation if your protocol allows it.

Encoding costs one pass over the tree. The head of a list or a map carries the number of items it holds,
which every insertion invalidates: the library recomputes it when the object is written out, not on each
call, so building a large container stays linear.
