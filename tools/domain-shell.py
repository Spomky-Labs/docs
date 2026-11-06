"""Write the pages that send a former documentation domain to docs.spomky-labs.com.

    python3 -I tools/domain-shell.py <directory> <domain> <prefix> <project name>

A domain kept for the addresses already published cannot answer with a 301: GitHub Pages does not issue
one. What it can do is answer everything with a page that redirects. Run this in a clone of the former
repository, on its gh-pages branch emptied of the site, then commit and push:

    git rm -rq .
    python3 -I ~/Projects/docs/tools/domain-shell.py . web-token.spomky-labs.com jwt "JWT Framework"

index.html sends the root to the project. 404.html, which GitHub Pages serves for every other address,
prefixes the path it was asked for: /4.3/jws-creation/ becomes /jwt/4.3/jws-creation/. The versions were
already in those addresses, so they land on a page rather than on a home page.

A redirection at the registrar would be better: a real 301, and the branch and the domain could go.
"""
import sys
from pathlib import Path

out, domain, prefix, name = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
target = f"https://docs.spomky-labs.com/{prefix}/"

STYLE = """    :root { color-scheme: light dark; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; font: 16px/1.5 system-ui, sans-serif;
           background: #F2EFE9; color: #333334; }
    main { box-sizing: border-box; max-width: 42rem; padding: 0 24px; }
    h1 { font-size: 1.5rem; font-weight: 600; margin: 0 0 12px; }
    h1::after { background: #ED6A20; content: ""; display: block; height: 6px; margin-top: 12px; width: 44px; }
    p { margin: 0 0 12px; }
    a { color: inherit; text-underline-offset: 0.2em; }
    code { font-family: ui-monospace, monospace; font-size: 0.9em; }
    @media (prefers-color-scheme: dark) { body { background: #333334; color: #F2EFE9; } }"""

index = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} documentation has moved</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}" + location.search + location.hash);</script>
<style>
{STYLE}
</style>
</head>
<body>
  <main>
    <h1>This documentation has moved</h1>
    <p>The documentations of Slabs share one site. {name} is now at
       <a href="{target}">{target}</a>.</p>
    <p>You are being sent there. <a href="{target}">Go now</a> if nothing happens.</p>
  </main>
</body>
</html>
"""

# Every address of the former site answers here, and keeps its path: /4.3/jws-creation/ becomes
# /jwt/4.3/jws-creation/. The versions were already in those addresses, so they land on a page.
not_found = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{name} documentation has moved</title>
<script>
  (function () {{
    var target = "https://docs.spomky-labs.com/{prefix}" + location.pathname + location.search + location.hash;
    var link = document.getElementById("target");
    if (link) {{ link.href = target; link.textContent = target; }}
    location.replace(target);
  }})();
</script>
<style>
{STYLE}
</style>
</head>
<body>
  <main>
    <h1>This documentation has moved</h1>
    <p>The documentations of Slabs share one site. {name} is now under
       <code>docs.spomky-labs.com/{prefix}/</code>, and this page kept its address there.</p>
    <p>You are being sent to <a id="target" href="{target}">{target}</a>.</p>
  </main>
</body>
</html>
"""

out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(index, encoding="utf-8")
(out / "404.html").write_text(not_found, encoding="utf-8")
(out / "CNAME").write_text(domain + "\n", encoding="utf-8")
(out / ".nojekyll").write_text("", encoding="utf-8")
print(f"{domain} -> {target}")
