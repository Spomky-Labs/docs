#!/usr/bin/env python3
"""Copy a mark of the Slabs design kit for a website, without its metadata.

    python3 -I tools/web-svg.py <source.svg> <target.svg>

The master files, and some files of the web set, carry a C2PA manifest, a title, a role and a label. A
website takes the drawing alone, as the web set of the kit does: the link around the image carries the
accessible name. The script keeps the viewBox and every element of the drawing, in order, and checks that
the drawing it writes is the one it read.
"""

import re
import sys
from pathlib import Path

DRAWING = re.compile(r"<(?:path|rect|circle|ellipse|g|/g|polygon|polyline|line|use|defs|/defs)\b[^>]*>")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    source = Path(sys.argv[1]).read_text(encoding="utf-8")
    match = re.match(r"\s*(?:<\?xml[^>]*>\s*)?<svg([^>]*)>(.*)</svg>\s*$", source, re.S)
    if not match:
        print(f"{sys.argv[1]}: not an SVG document", file=sys.stderr)
        return 1
    attributes, body = match.groups()
    view_box = re.search(r'viewBox="[^"]*"', attributes).group(0)
    clean = re.sub(r"<(metadata|title|desc)\b.*?</\1>", "", body, flags=re.S).strip()
    if DRAWING.findall(body) != DRAWING.findall(clean) or "c2pa" in clean:
        print(f"{sys.argv[1]}: the drawing would change, nothing written", file=sys.stderr)
        return 1
    output = f'<svg xmlns="http://www.w3.org/2000/svg" {view_box}>{clean}</svg>\n'
    Path(sys.argv[2]).write_text(output, encoding="utf-8")
    print(f"{sys.argv[2]}: {len(source)} -> {len(output)} bytes, {len(DRAWING.findall(clean))} elements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
