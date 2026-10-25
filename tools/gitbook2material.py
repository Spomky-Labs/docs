#!/usr/bin/env python3
"""Rewrite the GitBook syntax of a documentation into the syntax of Material for MkDocs.

    python3 -I tools/gitbook2material.py <docs directory>
    python3 -I tools/gitbook2material.py --titles "Web Push,Symfony,Doctrine" <docs directory>

Every Markdown file under the directory is rewritten in place. Only the text outside code blocks is read:
Twig in an example ({% if %}, {% block %}) is code, not GitBook. What is converted:

- {% hint style="x" %} ... {% endhint %}  ->  !!! x, the content indented by four spaces;
- {% code title="f" lineNumbers="true" %} and its fence  ->  the fence with title="f" linenums="1";
- {% content-ref url="x" %} ... {% endcontent-ref %}  ->  the link it holds;
- .gitbook/assets/<file>  ->  assets/images/<file renamed>, relative to the page; the files are moved;
- layout: in the front matter is dropped (Material has no layouts; a landing page hides its sidebars).

With --titles, the script only puts the headings in sentence case, as the Slabs guidelines want every
title on the web: the first word keeps its capital, and so do acronyms (VAPID, JSON), identifiers with an
inner capital (OperationException, JavaScript), inline code, HTTP status lines (404 Not Found) and the
proper nouns given in the list. Every change is printed, to be read before it is committed.

Anything else in {% %} outside a fence, and every HTML element GitBook writes outside a fence, is reported
and left as it is: those are converted by hand, page by page. The script never guesses.
"""

import re
import sys
import unicodedata
from pathlib import Path

FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
HINT_OPEN = re.compile(r'^\s*\{%\s*hint\s+style="(\w+)"\s*%\}\s*$')
HINT_CLOSE = re.compile(r"^\s*\{%\s*endhint\s*%\}\s*$")
CODE_OPEN = re.compile(r"^\s*\{%\s*code\b(.*?)%\}\s*$")
CODE_CLOSE = re.compile(r"^\s*\{%\s*endcode\s*%\}\s*$")
REF_OPEN = re.compile(r'^\s*\{%\s*content-ref\s+url="([^"]*)"\s*%\}\s*$')
REF_CLOSE = re.compile(r"^\s*\{%\s*endcontent-ref\s*%\}\s*$")
ATTRIBUTE = re.compile(r'(\w+)="([^"]*)"')
LIQUID = re.compile(r"\{%.*?%\}")
HTML = re.compile(r"<(figure|img|picture|table|mark|pre|details|div|p|br)\b", re.I)
ASSET = re.compile(r"(?:\.\./)*\.gitbook/assets/([^)\"'\s>]+(?:\s[^)\"'>]+?)?)(?=[)\"'>])")

ADMONITIONS = {"info": "info", "warning": "warning", "danger": "danger", "success": "success", "tip": "tip"}


def slug(name: str) -> str:
    """A file name without spaces, brackets or accents: "Capture d'écran (1).png" -> "capture-d-ecran-1.png"."""
    stem, dot, extension = name.rpartition(".")
    if not dot:
        stem, extension = name, ""
    stem = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return f"{stem}.{extension.lower()}" if extension else stem


class Page:
    def __init__(self, path: Path, docs: Path):
        self.path = path
        self.docs = docs
        self.reports: list[str] = []
        self.assets: set[str] = set()

    def report(self, number: int, message: str) -> None:
        self.reports.append(f"{self.path.relative_to(self.docs)}:{number}: {message}")

    def asset(self, match: re.Match) -> str:
        from urllib.parse import unquote

        name = unquote(match.group(1))
        self.assets.add(name)
        depth = len(self.path.relative_to(self.docs).parts) - 1
        return "../" * depth + "assets/images/" + slug(name)

    def convert(self, lines: list[str], offset: int = 0) -> list[str]:
        out: list[str] = []
        fence: str | None = None
        pending_code: dict[str, str] | None = None
        index = 0
        while index < len(lines):
            line = lines[index]
            number = offset + index + 1
            match = FENCE.match(line)

            if fence is not None:
                out.append(line)
                if match and match.group(2).startswith(fence) and not match.group(3).strip():
                    fence = None
                index += 1
                continue

            if match:
                fence = match.group(2)[0] * len(match.group(2))
                if pending_code is not None:
                    attributes = []
                    if pending_code.get("title"):
                        attributes.append(f'title="{pending_code["title"]}"')
                    if pending_code.get("lineNumbers") == "true":
                        attributes.append('linenums="1"')
                    info = match.group(3).strip()
                    line = f"{match.group(1)}{match.group(2)}{info}" + (" " + " ".join(attributes) if attributes else "")
                    pending_code = None
                out.append(line)
                index += 1
                continue

            if HINT_OPEN.match(line):
                style = HINT_OPEN.match(line).group(1)
                kind = ADMONITIONS.get(style)
                if kind is None:
                    self.report(number, f'hint style "{style}" has no admonition')
                    kind = "note"
                body, end = self.block(lines, index + 1, HINT_OPEN, HINT_CLOSE)
                if end is None:
                    self.report(number, "hint without endhint, left as it is")
                    out.append(line)
                    index += 1
                    continue
                converted = self.convert(body, offset + index + 1)
                while converted and not converted[0].strip():
                    converted.pop(0)
                while converted and not converted[-1].strip():
                    converted.pop()
                if out and out[-1].strip():
                    out.append("")
                out.append(f"!!! {kind}")
                out.append("")
                out.extend(("    " + l) if l.strip() else "" for l in converted)
                if end + 1 < len(lines) and lines[end + 1].strip():
                    out.append("")
                index = end + 1
                continue

            if CODE_OPEN.match(line):
                pending_code = dict(ATTRIBUTE.findall(CODE_OPEN.match(line).group(1)))
                index += 1
                continue

            if CODE_CLOSE.match(line):
                index += 1
                continue

            if REF_OPEN.match(line):
                body, end = self.block(lines, index + 1, REF_OPEN, REF_CLOSE)
                if end is None:
                    self.report(number, "content-ref without endcontent-ref, left as it is")
                    out.append(line)
                    index += 1
                    continue
                out.extend(l for l in body if l.strip())
                index = end + 1
                continue

            if LIQUID.search(line):
                self.report(number, "GitBook syntax left as it is: " + LIQUID.search(line).group(0))
            if HTML.search(line):
                self.report(number, "HTML to convert by hand: " + line.strip()[:100])

            out.append(ASSET.sub(self.asset, line))
            index += 1

        if pending_code is not None:
            self.report(offset + len(lines), "code block announced and never opened")
        return out

    def block(self, lines: list[str], start: int, opening: re.Pattern, closing: re.Pattern):
        """The lines up to the closing tag that matches, nested blocks and fences included."""
        depth, fence = 1, None
        for index in range(start, len(lines)):
            match = FENCE.match(lines[index])
            if fence is not None:
                if match and match.group(2).startswith(fence) and not match.group(3).strip():
                    fence = None
                continue
            if match:
                fence = match.group(2)[0] * len(match.group(2))
                continue
            if opening.match(lines[index]):
                depth += 1
            elif closing.match(lines[index]):
                depth -= 1
                if depth == 0:
                    return lines[start:index], index
        return lines[start:], None

    def run(self) -> bool:
        text = self.path.read_text(encoding="utf-8")
        front, body = "", text
        if text.startswith("---\n"):
            end = text.find("\n---\n", 4)
            if end != -1:
                front, body = text[: end + 5], text[end + 5 :]
                front = re.sub(r"^layout:.*\n", "", front, flags=re.M)
                if front.strip() == "---\n---":
                    front = ""
        lines = body.split("\n")
        converted = "\n".join(self.convert(lines, front.count("\n")))
        converted = re.sub(r"\n{3,}", "\n\n", converted)
        result = front + converted
        if result != text:
            self.path.write_text(result, encoding="utf-8")
            return True
        return False


HEADING = re.compile(r"^(#{1,6} )(.+)$")
STATUS = re.compile(r"^\d{3} [A-Z]")


def sentence_case(title: str, names: list[str]) -> str:
    if STATUS.match(title):
        return title
    protected: dict[str, str] = {}

    def protect(match: re.Match) -> str:
        key = f"\x00{len(protected)}\x00"
        protected[key] = match.group(0)
        return key

    text = re.sub(r"`[^`]*`", protect, title)
    for name in sorted(names, key=len, reverse=True):
        text = re.sub(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", protect, text)

    words = re.split(r"(\s+)", text)
    first = True
    for index, word in enumerate(words):
        if not word.strip() or "\x00" in word:
            if word.strip():
                first = word.endswith(":")
            continue
        letters = re.sub(r"[^A-Za-z]", "", word)
        keep = (
            first
            or (letters.isupper() and len(letters) > 1)
            or re.search(r"[a-z][A-Z]", word)
            or re.match(r"^[A-Z][a-z]*[A-Z]", word)
        )
        if not keep:
            words[index] = word[:1].lower() + word[1:] if word[:1].isupper() and word[1:2].islower() or len(word) == 1 else word
            if "-" in words[index]:
                words[index] = "-".join(part[:1].lower() + part[1:] if part[1:2].islower() else part for part in words[index].split("-"))
        elif first and "-" in word:
            head, *rest = word.split("-")
            words[index] = "-".join([head] + [part[:1].lower() + part[1:] if part[1:2].islower() else part for part in rest])
        # After a number ("1.") or a colon ("Step 9:"), the next word starts a sentence again.
        first = bool(re.match(r"^\d+\.$", word) or word.endswith(":"))
    text = "".join(words)
    for key, value in protected.items():
        text = text.replace(key, value)
    return text


def titles(docs: Path, names: list[str]) -> int:
    for path in sorted(docs.rglob("*.md")):
        if path.name == "SUMMARY.md" or "overrides" in path.parts:
            continue
        lines = path.read_text(encoding="utf-8").split("\n")
        fence = None
        for number, line in enumerate(lines):
            match = FENCE.match(line)
            if fence is not None:
                if match and match.group(2).startswith(fence) and not match.group(3).strip():
                    fence = None
                continue
            if match:
                fence = match.group(2)[0] * len(match.group(2))
                continue
            heading = HEADING.match(line)
            if heading:
                title = sentence_case(heading.group(2), names)
                if title != heading.group(2):
                    print(f"{path.relative_to(docs)}:{number + 1}: {heading.group(2)}  ->  {title}")
                    lines[number] = heading.group(1) + title
        path.write_text("\n".join(lines), encoding="utf-8")
    return 0


def main() -> int:
    arguments = sys.argv[1:]
    if len(arguments) == 3 and arguments[0] == "--titles":
        return titles(Path(arguments[2]).resolve(), [n.strip() for n in arguments[1].split(",") if n.strip()])
    if len(arguments) != 1:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    docs = Path(arguments[0]).resolve()
    changed, reports, assets = 0, [], set()
    for path in sorted(docs.rglob("*.md")):
        if "overrides" in path.parts:
            continue
        page = Page(path, docs)
        changed += page.run()
        reports.extend(page.reports)
        assets |= page.assets

    source = docs / ".gitbook" / "assets"
    target = docs / "assets" / "images"
    moved = 0
    for name in sorted(assets):
        origin = source / name
        if origin.exists():
            target.mkdir(parents=True, exist_ok=True)
            origin.rename(target / slug(name))
            moved += 1
        else:
            reports.append(f"asset not found: .gitbook/assets/{name}")
    leftovers = sorted(p.name for p in source.iterdir()) if source.exists() else []

    print(f"{changed} pages rewritten, {moved} images moved to assets/images/")
    if leftovers:
        print(f"{len(leftovers)} files of .gitbook/assets no page uses: " + ", ".join(leftovers))
    for line in reports:
        print("  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
