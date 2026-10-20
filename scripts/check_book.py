"""Check source references and rendered relative links using the standard library.

Run after `quarto render`, or use --source-only before a render.
External web links are deliberately not fetched by this check.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from collections import Counter
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
errors = []
sources = sorted(ROOT.glob("*.qmd"))
bibfile = ROOT / "assets/bibliography.bib"
if not bibfile.exists():
    sys.exit("Missing assets/bibliography.bib")
bibkeys = re.findall(r"@\w+\s*\{\s*([^,\s]+)", bibfile.read_text())
for key, n in Counter(bibkeys).items():
    if n != 1:
        errors.append(f"duplicate bibliography key: {key}")
labels = []
texts = {}
for path in sources:
    source = path.read_text()
    texts[path] = source
    labels.extend(re.findall(r"\{#([\w:-]+)", source))
    if len(re.findall(r"^\s*\$\$", source, re.M)) % 2:
        errors.append(f"unbalanced display math: {path.name}")
for key, n in Counter(labels).items():
    if n != 1:
        errors.append(f"duplicate source label: {key}")
known = set(bibkeys) | set(labels)
for path, source in texts.items():
    for key in re.findall(r"(?<![\w/])@([A-Za-z][\w:-]*)", source):
        key = key.rstrip(":")
        if key not in known:
            errors.append(f"undefined citation or cross-reference @{key}: {path.name}")

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.links = path, set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for name in ("href", "src", "poster"):
            if attrs.get(name):
                self.links.append(attrs[name])
        if "quarto-unresolved-ref" in attrs.get("class", ""):
            errors.append(f"unresolved reference marker in {self.path.name}")

if "--source-only" not in sys.argv:
    pages = {}
    for path in SITE.rglob("*.html"):
        page = Page(path)
        page.feed(path.read_text())
        pages[path.resolve()] = page
    for source in sources:
        expected = SITE / (source.stem + ".html")
        if expected.resolve() not in pages:
            errors.append(f"missing rendered chapter: {expected.relative_to(ROOT)}")
    pdf = SITE / "random-quantum-circuits.pdf"
    if not pdf.exists() or pdf.read_bytes()[:5] != b"%PDF-":
        errors.append("missing or invalid combined PDF")
    for path, page in pages.items():
        for link in page.links:
            u = urlsplit(link)
            if u.scheme or u.netloc:
                continue
            target = path if not u.path else (path.parent / unquote(u.path)).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"broken local link in {path.name}: {link}")
            elif u.fragment and target.suffix == ".html":
                targetpage = pages.get(target.resolve())
                if targetpage and unquote(u.fragment) not in targetpage.ids:
                    errors.append(f"missing anchor in {path.name}: {link}")
    index = pages.get((SITE / "index.html").resolve())
    if index and not any("random-quantum-circuits.pdf" in s for s in index.links):
        errors.append("book home page has no PDF download link")
    print(f"Checked {len(pages)} rendered HTML pages and the combined PDF.")

print(f"Checked {len(sources)} QMD sources, {len(labels)} labels, {len(bibkeys)} bibliography entries.")
if errors:
    for message in sorted(set(errors)):
        print("ERROR:", message)
    sys.exit(1)
print("Book checks passed.")
