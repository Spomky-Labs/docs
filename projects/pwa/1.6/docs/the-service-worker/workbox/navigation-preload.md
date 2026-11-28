# Navigation preload

Navigation Preload is a feature that speeds up navigation requests by allowing the browser to make network requests in parallel with service worker boot-up. Without Navigation Preload, the browser must wait for the service worker to start before making network requests, which can introduce latency.

## How it works

When a user navigates to a page:

1. **Without Navigation Preload**: Browser waits for the service worker to start → Service worker makes the network request → Response is returned
2. **With Navigation Preload**: Browser starts the service worker AND makes the network request simultaneously → Faster response

This can significantly improve perceived performance, especially on devices where service worker startup is slow.

## When to use navigation preload

Navigation Preload is beneficial when:

- Your service worker uses a **NetworkFirst** or **NetworkOnly** strategy for navigation requests
- You are **not** precaching HTML pages
- You want to reduce the latency introduced by service worker startup

## When NOT to use navigation preload

!!! warning

    **Do not enable Navigation Preload if you are precaching HTML pages.** If you're using the [offline fallbacks](../offline-fallback.md) (`pwa.serviceworker.offline_fallback`) with a page fallback or `preload_urls` to warm cache HTML pages, Navigation Preload would be redundant and may cause unnecessary network requests.

This is why Navigation Preload is **disabled by default** in this bundle.

`navigation_preload` is a Workbox option. Without Workbox, the bundle never enables navigation preload, and the `fetch` listener of the offline fallbacks fetches each navigation itself, without reading `event.preloadResponse`: if your own source enables navigation preload, every navigation that listener answers is fetched twice. See [Without Workbox](../offline-fallback.md#without-workbox).

## Configuration

To enable Navigation Preload:

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        workbox:
            navigation_preload: true
```

## Browser support

Navigation Preload is supported in modern browsers including Chrome, Edge, and Opera. Firefox and Safari do not currently support this feature, but Workbox handles this gracefully by falling back to standard behavior.

## Further reading

- [Workbox Navigation Preload Documentation](https://developer.chrome.com/docs/workbox/modules/workbox-navigation-preload/)
- [Speed up Service Worker with Navigation Preloads](https://web.dev/navigation-preload/)
