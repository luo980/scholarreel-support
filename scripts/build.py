#!/usr/bin/env python3
"""Validate and build the static ScholarReel support site (standard library only)."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "site"
DESTINATION = ROOT / "dist"
EXPECTED = {"index.html": "zh-Hans", "privacy/index.html": "zh-Hans", "en/index.html": "en", "en/privacy/index.html": "en"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = ""
        self.in_title = False
        self.has_viewport = False
        self.ids = set()
        self.references = []
        self.h1_count = 0
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html": self.lang = attrs.get("lang")
        if tag == "title": self.in_title = True
        if tag == "meta" and attrs.get("name") == "viewport": self.has_viewport = True
        if tag == "h1": self.h1_count += 1
        if tag in {"script", "form", "iframe"}: self.errors.append(f"Unexpected active element: {tag}")
        if "id" in attrs:
            if attrs["id"] in self.ids: self.errors.append(f"Duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "img" and not attrs.get("alt"): self.errors.append("Image needs descriptive alt text")
        for key in ("href", "src"):
            if key in attrs: self.references.append(attrs[key])

    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False

    def handle_data(self, data):
        if self.in_title: self.title += data


def main():
    errors = []
    pages = {}
    for name, language in EXPECTED.items():
        path = SOURCE / name
        if not path.is_file():
            errors.append(f"Missing required page: {name}")
            continue
        content = path.read_text(encoding="utf-8")
        page = Page()
        page.feed(content)
        pages[path.resolve()] = page
        if not content.lstrip().lower().startswith("<!doctype html>"): errors.append(f"{name}: Missing HTML doctype")
        if page.lang != language: errors.append(f"{name}: Incorrect page language")
        if not page.title.strip(): errors.append(f"{name}: Missing title")
        if not page.has_viewport: errors.append(f"{name}: Missing responsive viewport")
        if page.h1_count != 1: errors.append(f"{name}: Expected one main heading")
        if "luo980@gmail.com" not in content: errors.append(f"{name}: Missing support contact")
        for marker in ("【待填写", "TODO", "PLACEHOLDER", "内部核对记录", "本地草稿"):
            if marker in content: errors.append(f"{name}: Unfinished/private content: {marker}")
        errors.extend(f"{name}: {message}" for message in page.errors)

    for path, page in pages.items():
        for reference in page.references:
            parsed = urlsplit(reference)
            if parsed.scheme in {"https", "mailto"}: continue
            if parsed.scheme or parsed.netloc:
                errors.append(f"{path.relative_to(SOURCE)}: Unsupported URL: {reference}")
                continue
            if parsed.path.startswith("/"):
                errors.append(f"{path.relative_to(SOURCE)}: Use a project-safe relative URL: {reference}")
                continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if target.is_dir(): target /= "index.html"
            if not target.is_relative_to(SOURCE.resolve()) or not target.is_file():
                errors.append(f"{path.relative_to(SOURCE)}: Broken local link: {reference}")
                continue
            if parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                errors.append(f"{path.relative_to(SOURCE)}: Missing anchor: {reference}")

    if errors:
        print("Site validation failed:\n" + "\n".join(f"- {item}" for item in errors), file=sys.stderr)
        return 1
    if DESTINATION.exists(): shutil.rmtree(DESTINATION)
    shutil.copytree(SOURCE, DESTINATION)
    (DESTINATION / ".nojekyll").touch()
    print(f"Validated {len(pages)} localized pages, their local links and accessibility metadata.")
    print(f"Built {sum(1 for p in DESTINATION.rglob('*') if p.is_file())} static files in {DESTINATION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
