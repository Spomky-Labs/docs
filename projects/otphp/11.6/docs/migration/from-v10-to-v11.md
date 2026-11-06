# From v10 to v11

Nothing to change in your code. The release requires PHP 8.1 or later, and no API changed.

One behaviour did, and it is one you may be passing a value to.

## The TOTP window is no longer counted in periods

**In v10**, the window was a number of periods, applied on both sides. The range went from
`timestamp - window × period` to `timestamp + window × period`: with a window of 5 and a period of 30,
every code in the five periods before and the five after was accepted — eleven codes in all.

**In v11**, the window is a number of **seconds**, and three timestamps are tested:
`timestamp - window`, `timestamp`, `timestamp + window`. It models clock drift rather than a range of
periods. The window must be strictly smaller than the period; a larger one throws
`InvalidParameterException`.

```php
// v10: with a 30-second period, this accepted 11 codes
$totp->verify($code, null, 5);

// v11: this accepts the code of the current period, and of the previous
// or the next one if 20 seconds of drift reach into it
$totp->verify($code, null, 20);
```

So a window value carried over from v10 means something quite different now: with a thirty-second
period, a window of 5 went from accepting eleven codes to accepting the current one — and a neighbouring
one only in the five seconds either side of a boundary. A value that was legal there may also be refused
now, since any window equal to or greater than the period throws. Re-read every call that passes a third
argument. See [The window](../one-time-passwords/the-window.md).

The HOTP window is unchanged: it is still a number of counters, scanned upwards from the current one.
