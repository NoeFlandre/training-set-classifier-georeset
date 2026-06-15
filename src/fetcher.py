from pathlib import Path

import trafilatura


def fetch_and_save(url: str, output_path: Path) -> None:
    html = trafilatura.fetch_url(url)
    if html is None:
        print(f"Error, could not fetch {url}")
        return
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote {output_path}")
