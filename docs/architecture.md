# Architecture

## Pipeline overview

The training set is built in stages. Each stage takes input from disk, processes it, and writes output to disk. Stages are independent: you can re-run any stage without re-running the previous ones.

The full data flow:

```
URL  -->  *.html  -->  *.txt  -->  *.filtered.txt  -->  *.deduped.txt  -->  (LLM labels)
        [fetch]      [extract]    [filter]            [dedup]            [label]
```

## Pipeline stages

### Stage 1: Fetch HTML (DONE)

`scripts/fetch_samples.py` reads URLs from `src.config.SOURCES` and saves raw HTML to `samples/*.html`.

Library: `trafilatura.fetch_url` for HTTP, `pathlib.Path.write_text` for disk I/O.

### Stage 2: Extract text (DONE)

`scripts/extract_text.py` reads `samples/*.html`, calls `extract_text()` from `src.extractor`, writes the result to `samples/*.txt`.

Library: `trafilatura.extract` with `favor_recall=True, include_comments=False, include_tables=False`. The `favor_recall=True` flag tells trafilatura to err on the side of including text (we filter later). We may switch to `favor_precision=True` once we know what the output looks like on real data.

If extraction returns `None`, the script prints a warning and skips the file (no crash).

### Stage 3: Filter sentences (DONE)

`scripts/filter_sentences.py` reads `samples/*.txt`, splits into sentences, applies the 4 rules from the README, writes accepted sentences to `samples/*.filtered.txt` (one per line).

Rules (from `src/sentence_filtering.is_valid_sentence`):

- Word count in `[MIN_WORDS, MAX_WORDS]` = `[8, 80]`.
- Ends with terminal punctuation: `.`, `!`, or `?`.
- Does NOT end with `...`.
- Symbol-to-word ratio strictly less than `MAX_SYMBOL_RATIO` = `0.20`.

Sentence splitting is regex-based: `re.split(r"(?<=[.?!])\s+", text)`. This is intentionally simple. We may upgrade to NLTK's `sent_tokenize` or `pysbd` if it proves too naive on real data.

### Stage 4: Deduplicate (TODO)

`scripts/deduplicate_sentences.py` will read `samples/*.filtered.txt`, compute MinHash signatures, find near-duplicates (Jaccard above some threshold), and write unique sentences to `samples/*.deduped.txt`.

Library: `datasketch.MinHash` for signatures, `datasketch.MinHashLSH` for the index. Threshold: `0.7` (tunable). Number of permutations: `128` (standard).

### Stage 5: LLM labeling (NOT STARTED)

Will send each sentence to an LLM (provider TBD) and ask for a binary relevance label. Output: probably `*.labeled.jsonl` or similar.

### Stage 6: Human review (NOT STARTED)

A held-out set is labeled manually. Used to compute inter-rater agreement (Cohen's kappa) between LLM and human labels.

## Module structure

```
src/
├── __init__.py
├── config.py                 # Paths, sample URLs
├── fetcher.py                # HTTP fetching
├── extractor.py              # HTML to text
├── sentence_filtering.py     # Sentence rules
└── dedup.py                  # MinHash dedup (TODO)
```

### `src/config.py`

Pure configuration, no logic. Holds:

- `SAMPLES_DIR = Path("samples")`
- `SOURCES = [(filename, url), ...]`

When we add environment variables (Brave API key, Hugging Face bucket name), they will live here.

### `src/fetcher.py`

Only knows about HTTP and disk I/O. No HTML parsing. Exports:

- `fetch_and_save(url, output_path) -> None`

### `src/extractor.py`

Only knows about HTML to text. Exports:

- `extract_text(html) -> str | None`

Returns `None` on failure. Callers must check for `None`.

### `src/sentence_filtering.py`

Only knows about sentence rules. Exports:

- `split_sentences(text) -> list[str]`
- `is_valid_sentence(sentence) -> bool`
- `filter_sentences(sentences) -> list[str]`

Tunable constants at the top: `MIN_WORDS = 8`, `MAX_WORDS = 80`, `MAX_SYMBOL_RATIO = 0.20`.

### `src/dedup.py` (TODO)

Will export:

- `shingles(text, n=3) -> set[str]`
- `make_minhash(shingles, num_perm=128) -> MinHash`
- `find_duplicates(sentences, threshold=0.7) -> list[str]`

## Separation of concerns (the big idea)

| Module       | Knows about                | Does NOT know about           |
|--------------|----------------------------|--------------------------------|
| `config.py`  | Paths, source lists        | HTTP, HTML, extraction, dedup  |
| `fetcher.py` | URLs, HTTP, disk writes    | Trafilatura, text processing   |
| `extractor.py` | Trafilatura, HTML parsing | URLs, where files live         |
| `sentence_filtering.py` | Sentence rules        | HTML, URLs, file locations     |
| `dedup.py` (TODO) | MinHash, shingling        | Other concerns                 |

This separation means swapping out trafilatura for another library only touches `extractor.py`. Switching from local files to a database only touches `config.py` and `fetcher.py`. The scripts in `scripts/` are thin and do not need to change.

## Dependency management

All dependencies are in `pyproject.toml`:

- `trafilatura` for HTML extraction.
- `datasketch` for MinHash and LSH.
- `pytest` (dev) for testing.

`uv.lock` is committed for reproducibility. `uv sync` recreates the exact environment.

## Testing strategy

Tests live in `tests/test_*.py`. We use pytest.

- Boundary tests reference the constants, not hardcoded values.
- Each rule has a test that proves it works in isolation.
- Sanity tests (positive controls) ensure the function is not always returning the same thing.
- Tests that depend on multiple rules use a long sentence (e.g. exactly `MAX_WORDS` words) so only the rule under test can cause rejection.
