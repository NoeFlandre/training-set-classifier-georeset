"""

Download a few Wikipedia pages to test trafilatura on

"""

from pathlib import Path

import trafilatura

SAMPLES_DIR = Path("samples")

SOURCES = [
    ("biodiversity.html", "https://en.wikipedia.org/wiki/Biodiversity"),
    ("agriculture.html", "https://en.wikipedia.org/wiki/Agriculture"),
    ("permaculture.html", "https://en.wikipedia.org/wiki/Permaculture"),
]


def fetch_and_save(url: str, output_path: Path) -> None:
    html = trafilatura.fetch_url(url)
    if html is None:
        print(f"Error, could not fetch {url}")
        return
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote {output_path}")


def main():
    item_count = 0
    for filename, url in SOURCES:
        SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        item_count += 1
        print(f"Processing {filename}, item {item_count} / {len(SOURCES)}")
        fetch_and_save(url, SAMPLES_DIR / filename)


if __name__ == "__main__":
    main()
