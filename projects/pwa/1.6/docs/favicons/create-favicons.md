# Create favicons

Favicons are the small icons that appear in browser tabs, bookmarks, and address bars. Providing favicons that look great across all devices, browsers, and operating systems is traditionally complex and time-consuming.

## Why favicons matter

**Brand Recognition:**
- Instant visual identification in crowded browser tabs
- Professional appearance in bookmark lists
- Consistent branding across all platforms

**User Experience:**
- Easier navigation when multiple tabs are open
- Quick identification in browser history
- Better mobile home screen appearance

**Platform Requirements:**
- Each browser and OS expects different sizes
- Multiple formats needed (ICO, PNG, SVG)
- Special icons for touch devices and pinned tabs

!!! info

    Favicons are separate from app icons declared in the Web App Manifest, though they serve similar purposes. The bundle automatically generates both from a single source image.

## Quick setup

With this bundle, generating all necessary favicons takes just seconds. You only need one source file:

**Requirements:**
- Square icon (recommended)
- SVG format (preferred) or PNG (512x512px minimum)
- Transparent background (highly recommended)
- GD or Imagick PHP extension installed

!!! warning

    SVG format is currently only supported by the Imagick processor, and only when ImageMagick was built with
    an SVG delegate. GD cannot rasterize an SVG at all.

!!! info

    Since 1.6.0, selecting a processor whose PHP extension is not loaded fails at configuration time with an
    explicit message, instead of a missing-service error much later in the container compilation.

**Basic configuration:**

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    image_processor: 'pwa.image_processor.imagick' # or 'pwa.image_processor.gd'
  
    favicons:
        enabled: true
        default:
            src: icons/favicon.svg

    startup_images:
        enabled: true # or false: see below
```

**That's it!** The bundle automatically generates all required favicon sizes and formats for:
- Browser tabs (`favicon.ico`, 16x16 and 32x32)
- The iOS home screen (the 180x180 apple-touch-icon)
- Android and Chrome (192x192 and 512x512)
- And, when you ask for them, Windows tiles, the Safari pinned tab and the legacy sizes

See [What gets generated](#what-gets-generated) for the complete list.

!!! warning

    **Enabling the favicons also generates the iOS [startup images](startup-images.md)**: one full-screen PNG
    per iOS screen geometry and orientation, 42 of them, up to 2752x2064 pixels, and 42 more when a `dark`
    theme is configured.

    Relying on this is deprecated since 1.6.0. When `pwa.startup_images.enabled` is left out, the favicons
    trigger a deprecation, and 2.0.0 stops generating the startup images unless they are asked for. Set it
    explicitly: `true` to keep the splash screens, `false` to generate the favicons only.

## Icon source options

The bundle supports three types of icon sources, giving you flexibility in how you provide your favicon:

### 1. Asset Mapper asset (recommended)

Reference icons managed by Symfony's Asset Mapper:

```yaml
pwa:
    favicons:
        default:
            src: icons/favicon.svg  # Relative path within assets/
```

**Advantages:**
- Version control friendly
- Automatic cache busting
- Works with build pipeline

### 2. Absolute file path

Use an existing file from your project directory:

```yaml
pwa:
    favicons:
        default:
            src: /app/files/favicon.svg  # Absolute path (starts with /)
```

**Use cases:**
- Files outside the assets directory
- Dynamic file locations
- Legacy icon files

### 3. Symfony UX icons

Use any icon from the [Symfony UX Icons](https://ux.symfony.com/icons) library:

```yaml
pwa:
    favicons:
        default:
            src: bx:cool  # Format: iconset:icon-name
```

**Advantages:**
- No file needed
- Access to thousands of icons
- Consistent icon library

**Popular icon sets:**
- `heroicons:` - Heroicons
- `fa:` - Font Awesome
- `bx:` - BoxIcons
- `lucide:` - Lucide Icons

## Customization options

### SVG attributes

You can customize any SVG attribute directly to control how your icon is rendered. The bundle allows you to modify fill colors, stroke properties, and any other SVG root attributes:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true
        default:
            src: icons/favicon.svg
            svg_attr:
                fill: '#2196f3'
                stroke: '#ffffff'
                stroke-width: '2'
```

**Common SVG attributes you can modify:**
- `fill`: Main fill color of the icon
- `stroke`: Outline/border color
- `stroke-width`: Width of the stroke
- `opacity`: Overall transparency
- `color`: Used when SVG uses `currentColor`

### Icon scaling and safe zone

Different platforms apply masks to icons (circular, rounded square, etc.). To ensure your icon looks good on all platforms, use the safe zone feature.

**The problem:** Some platforms (especially Android) may crop icons to specific shapes.

**The solution:** Scale down your icon to stay within the safe zone:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true
        default:
            src: assets/icon.svg
            image_scale: 80 # = 80% of the original size
```

**Recommendations:**
- Use `image_scale: 80` (80%) for icons with text or detailed graphics
- Use `image_scale: 100` for simple, centered logos
- Test on different Android devices to verify appearance

!!! success

    The bundle automatically adds transparent padding to maintain the original canvas size while scaling the icon content.

### Background color and rounded corners

Create polished, platform-native looking icons by adding backgrounds and rounded corners:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true
        default:
            src: assets/icon.svg
            background_color: "#ffffff"
            border_radius: 10 # = 10% of the size. 50% is a circle.
```

**Parameters:**
- `background_color`: Hex color code (e.g., `#ffffff` for white)
- `border_radius`: Percentage of icon size (0-50)
  - `0`: Square corners
  - `10`: Slightly rounded (modern look)
  - `25`: Very rounded
  - `50`: Perfect circle

!!! info

    The `border_radius` option only works when `background_color` is set. Without a background, corners remain transparent.

### Dark mode icons

Support dark themes with dedicated dark mode icons. Modern devices automatically switch between light and dark icons based on system theme:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true

        # Light mode icon (shown in light theme)
        default:
            src: assets/icon.svg
            background_color: '#ffffff'

        # Dark mode icon (shown in dark theme)
        dark:
            src: assets/icon_dark.svg
            background_color: '#000000'
```

**How it works:**
- `default`: Light theme icon (used when system is in light mode)
- `dark`: Dark theme icon (used when system is in dark mode)
- Browser automatically switches based on user's system theme preference

!!! info

    When `dark` is defined, `default` becomes the light mode variant. Without `dark`, `default` is used for both themes.

### Apple touch icon

iOS puts the apple-touch-icon on the home screen, and fills its transparent areas with black. A transparent
round logo, right for the browser tabs, shows there as a logo on a black square. Giving the theme a background
color fixes the home screen, and turns the tab icon into a square.

Since 1.6.0, `apple_touch_icon` lets that one icon differ from the other favicons:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true
        default:
            src: assets/logo.png # transparent round logo, used as is for the tab icons
        apple_touch_icon:
            background_color: '#00bc7d'
            image_scale: 80
```

Every key is optional. A value left out is taken from the theme the icon is generated for:

| `apple_touch_icon` … | falls back to … |
| --- | --- |
| `src` | the `src` of that theme |
| `background_color` | the `background_color` of that theme, then `pwa.manifest.background_color` |
| `border_radius` | the `border_radius` of that theme |
| `image_scale` | the `image_scale` of that theme |

The SVG attributes of the theme are always applied, to the icon's own `src` as well.

Only the files declared as `rel="apple-touch-icon"` follow it: the 180x180 icon, plus the 57x57, 60x60, 72x72,
76x76, 114x114, 120x120 and 152x152 ones when `low_resolution` is enabled. `favicon.ico`, the other PNG files,
the Windows tiles, the Safari pinned tab and the [startup images](startup-images.md) are generated exactly as
before. Without the key, nothing changes at all.

!!! info

    A theme without a `background_color` takes the one of the manifest. The tab icons only stay transparent when
    neither the theme nor `pwa.manifest.background_color` declares one.

**Dark mode:** the block is declared once and applies to the apple-touch-icon of every color scheme. The dark
icon keeps the dark `src` and colors for whatever the block leaves out. When the block says enough, for instance
a `src` and a `background_color`, for both icons to come out identical, the file is generated once and linked
for each scheme.

**Low resolution:** without the block, the 72x72 file is a single file, declared both as an `icon` and as an
`apple-touch-icon`. With the block, it splits in two: the icon keeps the theme, and the apple-touch-icon gets
the block.

## Platform-specific features

### Safari pinned tab icon

Safari's pinned tabs use a special monochrome icon. Configure it with a single color:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true
        default:
            src: assets/icon.svg
        safari_pinned_tab_color: "#f5ef06"
        use_silhouette: true
        potrace: "/path/to/potrace" # Optional, only if in a non-conventional folder
```

**Silhouette mode:**

Generates a single-color silhouette of your icon, perfect for Safari's minimalist pinned tab design.

!!! warning

    Silhouette mode requires [potrace](https://en.wikipedia.org/wiki/Potrace) to be installed on your system. Install it via your package manager (e.g., `apt install potrace` on Debian/Ubuntu).

### Windows tiles

Enable special tiles for Windows 8/10 Start Menu and taskbar:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true
        default:
            src: assets/icon.svg
        tile_color: "#f5ef06"
```

**What gets generated:**
- Small tile (70x70)
- Medium tile (150x150)
- Wide tile (310x150)
- Large tile (310x310)
- A 144x144 tile image, and the `browserconfig.xml` file declaring them all

!!! info

    Windows tiles ignore `background_color` and `border_radius` options. The tile color is applied as a flat background by Windows itself.

## Legacy browser support

### Low resolution icons

By default, the bundle generates icons optimized for modern devices. Enable additional icon sizes for legacy browsers and older devices:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true
        default:
            src: assets/icon.svg
        low_resolution: true
```

**Additional sizes generated:**
- Apple touch icons: 57x57, 72x72 and 114x114 (before iOS 6), 60x60, 76x76, 120x120 and 152x152 (before iOS 7)
- Icons: 36x36, 48x48, 72x72, 96x96, 144x144, 256x256 and 384x384

!!! warning

    Enabling `low_resolution` increases compilation time and generates more files. Only enable if you need legacy browser support.

## Complete configuration example

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true

        # Light mode theme
        default:
            src: assets/icon.svg
            background_color: '#ffffff'
            border_radius: 18
            image_scale: 80
            svg_attr:
                fill: '#2196f3'
                stroke: '#ffffff'

        # Dark mode theme
        dark:
            src: assets/icon_dark.svg
            background_color: '#000000'
            border_radius: 18
            image_scale: 80
            svg_attr:
                fill: '#ffffff'
                stroke: '#2196f3'

        # The iOS home screen icon, opaque
        apple_touch_icon:
            background_color: '#2196f3'
            border_radius: 1 # the smallest radius: iOS rounds the corners itself
            image_scale: 80

        # Platform-specific
        safari_pinned_tab_color: '#2196f3'
        use_silhouette: true
        tile_color: '#2196f3'

        # Additional options
        low_resolution: false
        potrace: 'potrace'

    # The iOS startup images, generated from the same source
    startup_images:
        enabled: true
```

!!! warning

    **Deprecated since 1.6.0:** `use_start_image` moved out of this section. It now only seeds
    `pwa.startup_images.enabled` — see [Startup Images](startup-images.md).

!!! warning

    **Deprecated options:** The following flat options are deprecated since 1.3.0 and will be removed in 2.0:

    - `src` → use `default.src`
    - `src_dark` → use `dark.src`
    - `background_color` → use `default.background_color`
    - `background_color_dark` → use `dark.background_color`
    - `border_radius` → use `default.border_radius` and/or `dark.border_radius`
    - `image_scale` → use `default.image_scale` and/or `dark.image_scale`

    Migrate to the `default` and `dark` structure for full control and future compatibility.

## What gets generated

When you compile favicons, the bundle creates the following files. Apart from `favicon.ico`, every name
carries a hash of what the file is made of: change the source image or an option, and the URL changes with it.

**Always:**

| File | Declared as |
| --- | --- |
| `/favicon.ico` (16x16) | `icon`. Browsers fetch this path by convention, which is why it has no hash |
| `/pwa/favicon-16x16-<hash>.png`, `/pwa/favicon-32x32-<hash>.png` | `icon` |
| `/pwa/favicon-180x180-<hash>.png` | `apple-touch-icon` |
| `/pwa/favicon-192x192-<hash>.png`, `/pwa/favicon-512x512-<hash>.png` | `icon` |

**With `low_resolution: true`:** the same `/pwa/favicon-<width>x<height>-<hash>.png` files for the
[additional sizes](#low-resolution-icons).

**With `tile_color`:** `/pwa/favicon-70x70-<hash>.png`, `150x150`, `310x310`, `310x150` and `144x144`, and
`/pwa/browserconfig-<hash>.xml`.

**With `safari_pinned_tab_color` and `use_silhouette: true`:** `/pwa/safari-pinned-tab-<hash>.svg`.

**With a `dark` theme:** every `icon` and `apple-touch-icon` PNG file is generated a second time from the dark
theme, and each link gets a `media="(prefers-color-scheme: light)"` or `media="(prefers-color-scheme: dark)"`
condition. `favicon.ico`, the tiles and the Safari pinned tab are generated once, from the `default` theme.

Unless `pwa.startup_images.enabled` is `false`, the [startup images](startup-images.md) are generated too.

**HTML tags injected by `{{ pwa() }}`**, here with `tile_color`, `safari_pinned_tab_color` and `use_silhouette`:

```html
<link rel="icon" sizes="16x16" type="image/x-icon" href="/favicon.ico">
<link rel="icon" sizes="16x16" type="image/png" href="/pwa/favicon-16x16-….png">
<link rel="icon" sizes="32x32" type="image/png" href="/pwa/favicon-32x32-….png">
<link rel="apple-touch-icon" sizes="180x180" type="image/png" href="/pwa/favicon-180x180-….png">
<link rel="icon" sizes="192x192" type="image/png" href="/pwa/favicon-192x192-….png">
<link rel="icon" sizes="512x512" type="image/png" href="/pwa/favicon-512x512-….png">
<meta name="msapplication-TileImage" content="/pwa/favicon-144x144-….png">
<meta name="msapplication-config" content="/pwa/browserconfig-….xml">
<link rel="mask-icon" href="/pwa/safari-pinned-tab-….svg" color="#2196f3">
```

## Best practices

1. **Use SVG when possible**: Scales perfectly to all sizes without quality loss
2. **Transparent backgrounds**: Works on any platform background color
3. **Simple designs**: Complex details may not be visible at small sizes (16x16)
4. **Test safe zone**: Ensure important elements stay within 80% of icon area
5. **Dark mode support**: Provide dark icons for better user experience
6. **Skip legacy support**: Unless you have specific requirements, modern icons are sufficient

## Troubleshooting

### Icons not appearing

**Check:**
1. Icon file exists at specified path
2. File format is supported (SVG, PNG)
3. Compilation ran successfully (`php bin/console pwa:compile`)
4. HTML includes `{{ pwa() }}` function
5. If the icons return a 404 and your application is served from a sub-directory, see [Applications Served From A Sub-Directory](../deployment.md#applications-served-from-a-sub-directory)

### Silhouette not generating

**Requirements:**
- `potrace` must be installed
- Icon must have clear shapes (not gradients)
- Use `potrace` parameter if in custom location

### Black corners on the iOS home screen icon

**Cause:** iOS fills the transparent areas of the apple-touch-icon with black. A transparent background shows
black, and so do the corners a `border_radius` cuts out.

**Fix:** give the apple-touch-icon an opaque background of its own, without touching the other favicons:

```yaml title="config/packages/pwa.yaml" linenums="1"
pwa:
    favicons:
        enabled: true
        default:
            src: assets/logo.png
        apple_touch_icon:
            background_color: '#ffffff'
```

iOS rounds the corners of a home screen icon itself. The block only overrides what it declares, so a
`border_radius` of the theme cannot be removed there: set it to `1`, the smallest value. See
[Apple touch icon](#apple-touch-icon), then recompile with `php bin/console pwa:compile`.

### Dark icons not switching

**Verify:**
- Device/browser supports dark mode
- Both `default` and `dark` sections are configured
- Icons have been recompiled
- System theme is actually changing (test in browser DevTools)
