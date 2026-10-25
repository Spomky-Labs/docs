#!/usr/bin/env python3
"""Rewrite the GitBook syntax of a documentation into the syntax of Material for MkDocs.

    python3 -I tools/gitbook2material.py <docs directory>
    python3 -I tools/gitbook2material.py --titles "Web Push,Symfony,Doctrine" <docs directory>
    python3 -I tools/gitbook2material.py --nav <docs directory>

Every Markdown file under the directory is rewritten in place. Only the text outside code blocks is read:
Twig in an example ({% if %}, {% block %}) is code, not GitBook. What is converted:

- {% hint style="x" %} ... {% endhint %}  ->  !!! x, the content indented by four spaces;
- {% code title="f" lineNumbers="true" %} and its fence  ->  the fence with title="f" linenums="1";
- {% content-ref url="x" %} ... {% endcontent-ref %}  ->  the link it holds;
- .gitbook/assets/<file>  ->  assets/images/<file renamed>, relative to the page; the files are moved;
- layout: in the front matter is dropped (Material has no layouts; a landing page hides its sidebars);
- <mark style="color:…">: the colour goes, the guidelines never let a colour carry a meaning; a red mark
  keeps its insistence in bold, any other mark leaves its text alone;
- <p>a</p><p>b</p> in a cell of a table: a<br>b;
- a <table> GitBook writes on one line: a Markdown table, with its code, emphasis, bold and links;
- a relative link to a directory that holds a README.md: a link to that README.md, which MkDocs wants;
- an image path GitBook writes between angle brackets because it holds spaces, (<…/images (1).jpeg>);
- a <figure> GitBook writes on one line: a figure of Material, <figure markdown="span"> holding a Markdown
  image (whose path MkDocs rewrites, unlike the src of an HTML <img>) and its caption;
- a code block GitBook exported as HTML, <pre class="language-x" data-title="f" data-line-numbers><code>,
  with its highlighted lines in <strong>: a fence with title, linenums and hl_lines.

With --titles, the script only puts the headings in sentence case, as the Slabs guidelines want every
title on the web: the first word keeps its capital, and so do acronyms (VAPID, JSON), identifiers with an
inner capital (OperationException, JavaScript), inline code, HTTP status lines (404 Not Found) and the
proper nouns given in the list. Every change is printed, to be read before it is committed.

With --nav, the script prints the nav: block of mkdocs.yml for the SUMMARY.md of the directory: a "##"
heading becomes a section, in sentence case; a page with pages under it becomes a section of the same
title that opens with the page; every other page is listed by its path, and the navigation takes its
title from the first heading of the page.

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

MARK = re.compile(r'<mark\s+style="[^"]*?color:\s*([a-z]+)[^"]*"\s*>(.*?)</mark>', re.S)
TABLE_LINE = re.compile(r"^\s*<table\b.*</table>\s*$")
PRE_OPEN = re.compile(r'^\s*<pre class="language-([\w+-]+)"([^>]*)><code[^>]*>(.*)$', re.S)
FIGURE = re.compile(
    r'^\s*<figure>\s*<img\s+src="([^"]+)"(?:\s+alt="([^"]*)")?(?:\s+width="(\d+)")?[^>]*>'
    r'(?:\s*<figcaption>\s*(?:<p>)?(.*?)(?:</p>)?\s*</figcaption>)?\s*</figure>\s*$'
)
ANGLE_ASSET = re.compile(r"\(<((?:\.\./)*\.gitbook/assets/[^>]+)>\)")


def html_pre(lines: list[str]) -> str:
    """The lines of a <pre> block, from the opening line to the one holding </code></pre>, as a fence."""
    import html

    first = PRE_OPEN.match(lines[0])
    language, attributes = first.group(1), first.group(2)
    body = [first.group(3)] + lines[1:]
    body[-1] = body[-1][: body[-1].index("</code></pre>")]
    code, highlighted, strong = [], [], False
    for number, line in enumerate(body, 1):
        bold = False
        for token in re.split(r"(</?strong>)", line):
            if token == "<strong>":
                strong = True
            elif token == "</strong>":
                strong = False
            elif strong and re.sub(r"<[^>]+>", "", token).strip():
                bold = True
        if bold:
            highlighted.append(number)
        code.append(html.unescape(re.sub(r"<[^>]+>", "", line)))
    while code and not code[-1].strip():
        code.pop()
    title = re.search(r'data-title="([^"]*)"', attributes)
    info = [language]
    if title and title.group(1):
        info.append(f'title="{title.group(1)}"')
    if "data-line-numbers" in attributes:
        info.append('linenums="1"')
    if highlighted:
        info.append('hl_lines="' + " ".join(str(n) for n in highlighted if n <= len(code)) + '"')
    return "\n".join(["```" + " ".join(info)] + code + ["```"])


def unmark(text: str) -> str:
    def replace(match: re.Match) -> str:
        colour, inner = match.group(1), match.group(2).strip()
        if colour != "red" or not inner:
            return inner
        if re.fullmatch(r"(\*\*.*\*\*|<strong>.*</strong>)", inner, re.S):
            return inner
        return f"**{inner}**"

    return MARK.sub(replace, text)


def cell_paragraphs(text: str) -> str:
    """<p>a</p><p>b</p> -> a<br>b, empty paragraphs dropped."""
    text = re.sub(r"<p>\s*</p>", "", text)
    if "<p>" not in text:
        return text
    parts = [part.strip() for part in re.findall(r"<p>(.*?)</p>", text, re.S)]
    rest = re.sub(r"<p>.*?</p>", "", text, flags=re.S).strip()
    return "<br>".join([p for p in parts if p] + ([rest] if rest else []))


def inline_markdown(html_text: str) -> str:
    text = cell_paragraphs(unmark(html_text))
    text = re.sub(r"<code>(.*?)</code>", lambda m: "`" + m.group(1).replace("`", "\\`") + "`", text, flags=re.S)
    text = re.sub(r"<(strong|b)>(.*?)</\1>", r"**\2**", text, flags=re.S)
    text = re.sub(r"<(em|i)>(.*?)</\1>", r"*\2*", text, flags=re.S)
    text = re.sub(r'<a\s+href="([^"]*)"[^>]*>(.*?)</a>', r"[\2](\1)", text, flags=re.S)
    text = re.sub(r"<br\s*/?>", "<br>", text)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def html_table(line: str) -> str | None:
    rows = re.findall(r"<tr>(.*?)</tr>", line, re.S)
    if not rows:
        return None
    table = [[inline_markdown(cell) for cell in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)] for row in rows]
    width = max(len(row) for row in table)
    table = [row + [""] * (width - len(row)) for row in table]
    lines = ["| " + " | ".join(table[0]) + " |", "|" + "---|" * width]
    lines += ["| " + " | ".join(row) + " |" for row in table[1:]]
    return "\n".join(lines)


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
        return self.asset_path(match.group(1))

    def asset_path(self, raw: str) -> str:
        from urllib.parse import unquote

        name = unquote(raw)
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

            if PRE_OPEN.match(line):
                end = next((i for i in range(index, len(lines)) if "</code></pre>" in lines[i]), None)
                if end is None:
                    self.report(number, "<pre> without </code></pre>, left as it is")
                else:
                    if out and out[-1].strip():
                        out.append("")
                    out.append(html_pre(lines[index : end + 1]))
                    if end + 1 < len(lines) and lines[end + 1].strip():
                        out.append("")
                    index = end + 1
                    continue

            figure = FIGURE.match(line)
            if figure:
                source, alt, width, caption = figure.groups()
                source = ASSET.sub(self.asset, source)
                image = f"![{alt or caption or ''}]({source})" + (f'{{ width="{width}" }}' if width else "")
                if out and out[-1].strip():
                    out.append("")
                out.append('<figure markdown="span">')
                out.append("  " + image)
                if caption:
                    out.append(f"  <figcaption>{caption}</figcaption>")
                out.append("</figure>")
                index += 1
                continue

            if TABLE_LINE.match(line):
                table = html_table(line)
                if table is not None:
                    if out and out[-1].strip():
                        out.append("")
                    out.append(ASSET.sub(self.asset, table))
                    index += 1
                    continue
            line = unmark(line)
            if line.lstrip().startswith("|"):
                line = "|".join(cell_paragraphs(cell) for cell in line.split("|"))

            if LIQUID.search(line):
                self.report(number, "GitBook syntax left as it is: " + LIQUID.search(line).group(0))
            if HTML.search(re.sub(r"<br>", "", line)):
                self.report(number, "HTML to convert by hand: " + line.strip()[:100])

            line = ANGLE_ASSET.sub(lambda m: "(" + self.asset_path(m.group(1).split(".gitbook/assets/", 1)[1]) + ")", line)
            out.append(self.directory_links(ASSET.sub(self.asset, line)))
            index += 1

        if pending_code is not None:
            self.report(offset + len(lines), "code block announced and never opened")
        return out

    def directory_links(self, line: str) -> str:
        def replace(match: re.Match) -> str:
            target, anchor = match.group(1), match.group(2) or ""
            if re.match(r"^[a-z]+:", target) or target.startswith("/"):
                return match.group(0)
            if (self.path.parent / target / "README.md").is_file():
                return f"]({target}README.md{anchor})"
            return match.group(0)

        return re.sub(r"\]\(([^)\s#]+/)(#[^)\s]*)?\)", replace, line)

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

    def lower(word: str) -> str:
        """Lowers the first letter of each part of a word ("(Registration)", "Cross-Origin", "a/Decoding")
        when the rest of the part is in lower case: an acronym or a name with an inner capital stays."""
        def part(chunk: str) -> str:
            match = re.search(r"[A-Za-z]", chunk)
            if not match:
                return chunk
            i = match.start()
            rest = chunk[i + 1 :]
            if chunk[i].isupper() and (not rest or rest[:1].islower()) and not re.search(r"[A-Z]", rest):
                return chunk[:i] + chunk[i].lower() + rest
            return chunk
        return re.sub(r"[^-/]+", lambda m: part(m.group(0)), word)

    words = re.split(r"(\s+)", text)
    first = True
    for index, word in enumerate(words):
        if not word.strip():
            continue
        if "\x00" in word:
            first = word.endswith(":")
            continue
        if not re.search(r"[A-Za-z0-9]", word):
            continue  # an emoji or a sign does not start the sentence
        letters = re.sub(r"[^A-Za-z]", "", word)
        acronym = letters.isupper() and len(letters) > 1
        if first:
            head, sep, tail = word.partition("-") if "-" in word else (word, "", "")
            words[index] = head + (sep + lower(tail) if sep else "")
        elif not acronym:
            words[index] = lower(word)
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


def nav(docs: Path, names: list[str]) -> int:
    """A "##" heading becomes a section; a page with pages under it becomes a section that opens with it."""
    groups: list[tuple[str | None, list]] = [(None, [])]
    stack: list[tuple[int, list]] = []
    for line in (docs / "SUMMARY.md").read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^##\s+(.+)$", line)
        item = re.match(r"^(\s*)[*-]\s+\[([^\]]*)\]\(([^)]+)\)", line)
        if heading or line.strip() == "---":
            groups.append((heading.group(1).strip() if heading else None, []))
            stack = []
        elif item:
            depth = len(item.group(1).replace("\t", "  "))
            node = {"title": item.group(2), "path": item.group(3), "children": []}
            while stack and stack[-1][0] >= depth:
                stack.pop()
            (stack[-1][1] if stack else groups[-1][1]).append(node)
            stack.append((depth, node["children"]))

    def emit(nodes: list, indent: str) -> None:
        for node in nodes:
            if node["children"]:
                print(f'{indent}- "{sentence_case(node["title"], names)}":')
                print(f'{indent}    - {node["path"]}')
                emit(node["children"], indent + "    ")
            else:
                print(f"{indent}- {node['path']}")

    print("nav:")
    for title, nodes in groups:
        if not nodes:
            continue
        if title is None:
            emit(nodes, "  ")
        else:
            print(f'  - "{sentence_case(title, names)}":')
            emit(nodes, "      ")
    return 0


def main() -> int:
    arguments = sys.argv[1:]
    if len(arguments) == 2 and arguments[0] == "--nav":
        return nav(Path(arguments[1]).resolve(), [])
    if len(arguments) == 3 and arguments[0] == "--nav":
        return nav(Path(arguments[2]).resolve(), [n.strip() for n in arguments[1].split(",") if n.strip()])
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
