# Project Context

This file is the entry point for anyone (human or coding agent) picking up this codebase fresh. Read this first, then dive into `docs/` for specific topics.

## What this project is

We are building a training dataset for a binary classifier that filters sentences by relevance to environment and agriculture. The end goal is a model that can take any English sentence and say "yes, this is about environment or agriculture" or "no, it isn't". The dataset is stored in the Hugging Face bucket: `https://huggingface.co/buckets/NoeFlandre/training-set-classifier-georeset`.

The full original brief is in `README.md`. This file describes the current state, architecture, and conventions.

## Current state (where we are)

**Done (text-tail pipeline):**

- Project scaffolded with `uv`, Python 3.12, `src/` layout.
- HTML fetching (`src/fetcher.py`).
- HTML to plain text extraction with trafilatura (`src/extractor.py`).
- Sentence splitting and filtering with 4 rules from the README (`src/sentence_filtering.py`).
- Tests for sentence filtering (10 tests, all green).
- 3 sample HTML files in `samples/` with extracted `.txt` and `.filtered.txt` artifacts.
- Deep conceptual understanding of MinHash (see `docs/minhash.md`).

**In progress:**

- MinHash deduplication. Concept understood, code not yet written. Next files to create: `src/dedup.py`, `tests/test_dedup.py`, `scripts/deduplicate_sentences.py`.

**Not started:**

- Upstream: OSM polygon selection, Brave API queries.
- Downstream: LLM labeling, human review for inter-rater agreement.

## Architecture (one-paragraph version)

The data flow is `*.html` to `*.txt` to `*.filtered.txt` to `*.deduped.txt` (each stage persists to disk so it can be re-run independently). See `docs/architecture.md` for module-by-module details.

## How to run

Setup (one time):

```bash
uv sync
```

Run the pipeline so far:

```bash
uv run python scripts/fetch_samples.py
uv run python scripts/extract_text.py
uv run python scripts/filter_sentences.py
```

Run tests:

```bash
uv run pytest tests/
```

## Conventions

- No emoji in code, comments, or docs.
- No em-dashes in prose. Use periods, commas, or parentheses.
- Type hints on all public functions.
- Tunable constants at the top of each module (e.g. `MIN_WORDS = 8` in `sentence_filtering.py`).
- Tests reference the constants, not hardcoded values, so changing a constant does not break tests.
- Thin scripts in `scripts/`, real logic in `src/`. Display helpers (e.g. `preview_text`) stay in scripts, not in `src/`.
- Use `uv add` for dependencies. Never `uv pip install` (so the lockfile and `pyproject.toml` stay in sync).
- Boolean assertions in tests use `is True` or `is False`, never bare `assert is_valid(x)`.

## Key concepts

- MinHash for fuzzy near-duplicate detection. The full concept writeup is in `docs/minhash.md`. Required reading before touching `src/dedup.py`.
- Shingling (n-grams of words) as the set representation of text for Jaccard.
- Locality-Sensitive Hashing (LSH) for fast candidate lookup.

## Current focus: MinHash dedup

The next file to create is `src/dedup.py`. See `docs/progress.md` for the planned micro-steps and the micro-step the user is currently on.

## Files reference

- `README.md` — original project brief (untouched).
- `pyproject.toml` — dependencies (`trafilatura`, `datasketch`, `pytest` dev).
- `docs/architecture.md` — full pipeline architecture, module responsibilities.
- `docs/minhash.md` — MinHash deep dive: problem, Jaccard, the magic property, worked examples, LSH.
- `docs/progress.md` — detailed log of what is done, what is in progress, what is next, plus design decisions.
