from __future__ import annotations

"""Fetch Columbia Undergraduate Admissions pages into local markdown files.

AAC uses a local RAG index built from official pages.
This script downloads a small curated set of Columbia Undergraduate Admissions pages
and stores them as Markdown under data/columbia_docs/.

Run:
  python -m scripts.fetch_columbia_docs
"""

import re
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup


URLS: List[str] = [
    "https://undergrad.admissions.columbia.edu/apply/process",
    "https://undergrad.admissions.columbia.edu/resources",
    "https://undergrad.admissions.columbia.edu/faq",
    "https://undergrad.admissions.columbia.edu/apply",
    "https://undergrad.admissions.columbia.edu/academics",
]

OUT_DIR = Path("data/columbia_docs")


def _slug(url: str) -> str:
    path = url.split("undergrad.admissions.columbia.edu/", 1)[-1]
    path = path.strip("/") or "home"
    path = path.replace("/", "_")
    path = re.sub(r"[^a-zA-Z0-9_]+", "_", path)
    return f"columbia_{path}.md"


def _html_to_markdown(url: str, html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = (soup.title.get_text(" ", strip=True) if soup.title else "Columbia Admissions")
    text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    body = "\n".join(lines)

    return (
        f"# {title}\n\n"
        f"Source: {url}\n\n"
        "---\n\n"
        f"{body}\n"
    )


def fetch_all() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for url in URLS:
        # Use a common browser user-agent to avoid basic bot blocks.
        r = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/121.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        r.raise_for_status()
        out_path = OUT_DIR / _slug(url)
        out_path.write_text(_html_to_markdown(url, r.text), encoding="utf-8")
        print(f"Wrote {out_path}")


def main() -> None:
    fetch_all()
    print(f"\nDone. Saved {len(URLS)} pages to {OUT_DIR}.")


if __name__ == "__main__":
    main()
