# Configuration

The Service Worker is a Javascript file you can declare in the configuration file. It will be automatically served by the bundle as long as your template file uses the [Twig `pwa` method](../installation.md).

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker: "sw.js"
```

`"sw.js"` is served by Asset Mapper and refers to the file in `/assets/sw.js` folder of your project. It can be stored elsewhere if needed.

!!! info

    To start, just put an empty file. It will be automatically populated by the bundle and will evolves depending on your application needs.

The following example is exactly the same:

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
```

!!! warning

    As it has an impact on the Twig pages, you may need to clear the cache when the service worker is enabled.

By default, the public URL of the service worker will be /sw.js. You can change this URL using the dest configuration option.

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        dest: "/foo/service-worker.js"
```

### Service worker initialization

The Service Worker initialization script uses either Workbox Window if enabled or a smiliar Vanilla JS script.

When Workbox is enabled, its initialization script typically loads from an external URL. However, for improved performance and security, we advise installing it via Asset Mapper instead of relying on remote loading.

```sh
symfony console importmap:require workbox-window
```

The two other options are also available:

### Other options

The Service worker section has other options you may be interested in.

#### Scope

The `scope` parameter defaults to `/`. It is a string representing the service worker's registration scope. It should be aligned with the [Manifest scope](../the-manifest/application-information/scope.md).

#### Cache

The `use_cache` parameter is enable by default. It is a boolean that sets how the HTTP cache is used for service worker script resources during updates.

#### Skip waiting

The `skip_waiting` parameter is disabled by default. It ensures that any new versions of a service worker will take over the page and become activated immediately. It is safe in general, but may create issues when the old service worker is handling events while it is updated.

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        dest: "/foo/service-worker.js"
        scope: "/"
        use_cache: true
        skip_waiting: false
```

### Updates

With Workbox enabled, the registration script injected by `{{ pwa() }}` tells the page what happens to its
service worker through two events. Both are `CustomEvent`s dispatched on `window`, and both carry the
`workbox.Workbox` instance in `event.detail.wb`, which is also exposed as `window.workbox` once the service
worker is registered.

| Event | Dispatched when | Cancelable |
| --- | --- | --- |
| `sw:update-available` | A new service worker is installed and waits for the current one to let go | No |
| `sw:controller-changed` | A new service worker took control of the page, right before the page is reloaded | Yes |

Without Workbox, the registration script dispatches neither event and never reloads the page.

#### A new version is waiting

With `skip_waiting: false`, a new service worker waits until every tab using the current one is closed. The
page can ask it to take over instead: `messageSkipWaiting()` sends the `SKIP_WAITING` message the generated
service worker listens to.

```javascript title="assets/app.js" linenums="1"
window.addEventListener('sw:update-available', (event) => {
    if (confirm('A new version is available. Use it now?')) {
        event.detail.wb.messageSkipWaiting();
    }
});
```

#### The page is about to be reloaded

When a new service worker takes control of the page, the script reloads it, so that the page and its service
worker come from the same version. The page is not reloaded on a first visit, when a service worker takes
control of a page no service worker controlled yet: nothing was updated.

With `skip_waiting: true`, a deploy reloads every open tab, and a half-filled form with it. Since 1.6.0, the
cancelable `sw:controller-changed` event is dispatched right before the reload, and the page is reloaded only
if no listener called `preventDefault()` on it:

```javascript title="assets/app.js" linenums="1"
window.addEventListener('sw:controller-changed', (event) => {
    if (formHasUnsavedChanges()) {
        event.preventDefault();
        showReloadToast(() => window.location.reload());
    }
});
```

When the reload is prevented, the page is left as it is, and reloading it is up to your application, for
instance once the form is saved. Should the controller change again, the event is dispatched again.

!!! warning

    Call `preventDefault()` synchronously, in the listener itself. The script reads the outcome as soon as the
    event is dispatched: a call made after an `await` comes too late, and the page is already reloading.

### Compiling the service worker

The service worker is compiled using the `pwa:compile` command:

```sh
php bin/console pwa:compile
```

**Options:**
- `--context-only` - Compile only assets that depend on the application context (e.g., the manifest). Useful for locale-specific compilations.
- `--no-screenshots` - Skip screenshot generation during compilation.

### Background Fetch

The Background Fetch API allows your PWA to handle long-running downloads in the background. Configure it in the workbox section:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        workbox:
            background_fetch:
                enabled: true
                success_url: 'app_download_success'  # Route name or URL
                progress_url: 'app_download_progress'
                success_message: 'Download complete!'
                failure_message: 'Download failed.'
                db_name: 'bgfetch-completed'
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `success_url` | URL/route | - | URL to open when download completes |
| `progress_url` | URL/route | - | URL to display download progress |
| `success_message` | string | `null` | Success notification message, translated with the [translation domain](../experimental-features/translations.md#the-translation-domain) |
| `failure_message` | string | `null` | Failure notification message, translated with the [translation domain](../experimental-features/translations.md#the-translation-domain) |
| `db_name` | string | `bgfetch-completed` | IndexedDB name for download storage |

!!! info

    Background Fetch is supported in Chromium-based browsers. It handles downloads that would otherwise be interrupted when the user closes the tab.
