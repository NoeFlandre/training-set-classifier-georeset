"""

Download a few Wikipedia pages to test trafilatura on

"""

from src.config import SAMPLES_DIR, SOURCES
from src.fetcher import fetch_and_save


def main():
    item_count = 0
    for filename, url in SOURCES:
        SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        item_count += 1
        print(f"Processing {filename}, item {item_count} / {len(SOURCES)}")
        fetch_and_save(url, SAMPLES_DIR / filename)


if __name__ == "__main__":
    main()
