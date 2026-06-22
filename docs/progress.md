# Progress log

This file tracks what is done, what is in progress, and what is next, with enough context to pick up where we left off.

## Done

### Project setup

- `uv init` with Python 3.12.
- Dependencies in `pyproject.toml`: `trafilatura`, `datasketch`, `pytest` (dev).
- `.gitignore` for `.venv/`, `__pycache__/`, build artifacts, `.egg-info/`.
- `LICENSE` (MIT, from GitHub default).
- Project layout: `src/`, `scripts/`, `tests/`, `samples/`.

### Architecture decision

- `src/` package for library code (reusable, importable, testable).
- `scripts/` for thin CLI wrappers (orchestration only).
- `tests/` for pytest tests.
- `samples/` for local data artifacts at each pipeline stage.

### Stage 1: Fetch HTML

- `src/fetcher.py` with `fetch_and_save(url, output_path)`.
- `src/config.py` with `SAMPLES_DIR` and `SOURCES` (3 Wikipedia articles: biodiversity, agriculture, permaculture).
- `scripts/fetch_samples.py` loops over `SOURCES`, calls `fetcher.fetch_and_save`.

### Stage 2: Extract text

- `src/extractor.py` with `extract_text(html)` using trafilatura (`favor_recall=True`, `include_comments=False`, `include_tables=False`).
- `scripts/extract_text.py` loops over HTML files, saves to `.txt`.
- Handles `None` from `extract_text`: prints a warning and skips the file (no crash).

### Stage 3: Filter sentences

- `src/sentence_filtering.py` exports:
  - `split_sentences(text)` (regex-based, simple).
  - `is_valid_sentence(sentence)` (applies 4 rules).
  - `filter_sentences(sentences)` (keeps valid ones).
  - Constants: `MIN_WORDS = 8`, `MAX_WORDS = 80`, `MAX_SYMBOL_RATIO = 0.20`.
- `scripts/filter_sentences.py` loops over `.txt` files, saves to `.filtered.txt` (one sentence per line).
- `tests/test_sentence_filtering.py` with 10 tests, all green:
  - Word count boundaries (4 tests, including the 8 vs 9 off-by-one fix and the `is True` assertion fix).
  - Symbol ratio (1 test using the `"@word"` construction).
  - Terminal punctuation (2 tests: `?` accepted, no-punct rejected).
  - Ellipsis (1 test using `MAX_WORDS`-long sentence so 3 periods is 0.04 ratio, isolating the ellipsis check).
  - Edge cases: empty string, whitespace only (2 tests).
  - All tests reference the module constants, not hardcoded values.

### Stage 4: Deduplicate

- `src/dedup.py` exports:
  - `split_sentence_to_words(sentence) -> list[str]` (uses `WORD_RE` from `sentence_filtering`).
  - `shingles(sentence, n=3) -> set[str]` (word n-grams).
  - `make_minhash(shingle_set, num_perm=128) -> MinHash`.
  - `jaccard(a, b) -> float` (true Jaccard).
  - `find_duplicates(sentences, threshold=0.7, num_perm=128, n=3) -> list[str]` (LSH + true Jaccard verification, first-seen wins).
- Tunable constants at the top: `DEFAULT_NUM_PERM = 128`, `DEFAULT_THRESHOLD = 0.7`, `DEFAULT_N = 3`.
- `scripts/deduplicate.py` loops over `samples/*.filtered.txt`, runs `find_duplicates`, writes `samples/*.filtered.deduped.txt`.
- `tests/test_dedup.py` with 11 tests, all green:
  - Shingling: case insensitivity, short input, custom `n` count.
  - MinHash: perfect duplicates ≥ 0.9, unrelated < 0.2, near-duplicates ≥ 0.6.
  - `find_duplicates`: empty input, identical triples collapse to one, unique list preserved, first-seen-wins ordering, threshold out of range raises `ValueError`.
- Per-file dedup verified on the 3 samples: it correctly drops repeated boilerplate like "Archived from the original on..." lines that appear many times in Wikipedia articles. Permaculture: 74 → 73 sentences.

### MinHash conceptual understanding

- 11-part deep dive covering: problem, Jaccard, scaling, the magic property, 3 worked numerical examples, why one hash function is not enough, signatures, LSH, parameters, takeaways.
- See `docs/minhash.md`.

## In progress

### Stage 0: OSM polygon selection

- Status: not started in this repo.
- The labeled base-key list from the `osm-stats` side project is the starting whitelist: 326 union base keys marked "yes" across the TF-IDF and embedding pipelines.
- Need to: load that list into this repo, design the Overpass query, filter by area bins, dedup by `(osm_type, osm_id)`, stratify by continent.

## Not started

### Stage 0 (upstream): OSM polygon selection

- Use the Overpass API to fetch polygons with tags from the remote-sensing-relevant whitelist (326 union base keys from the osm-stats side project: `building`, `highway`, `landuse`, `natural`, `water`, `wetland`, `railway`, `amenity`, `parking`, `leisure`, `power`, etc).
- Filter by: non-empty name, area in one of the bins (tiny <0.1, small 0.1-1, medium 1-10, large >=10 km²).
- Deduplicate by `(osm_type, osm_id)`.
- Stratify across world regions (continents).

### Brave API queries (upstream)

- For each polygon, build a query: `"{name} {location} {theme}"`.
- 20 results per query.
- 1.2 second delay between queries (rate limit).
- Resumable and logged (per the README).

### Stage 5 (downstream): LLM labeling

- Send each deduped sentence to an LLM.
- Binary label: relevant / not relevant to anything a satellite could see (land cover, land use, infrastructure, environment, agriculture).
- Provider TBD. Options discussed: OpenAI, Anthropic, local via Ollama. User decided to defer the choice.

### Stage 6 (downstream): Human review

- Manually label a held-out set (~100-500 sentences).
- Compute inter-rater agreement (Cohen's kappa) between LLM and human.
- Iterate on the prompt or rules if agreement is low.

## Design decisions and rationale

### Why `uv`

- Fast, modern Python package manager.
- Replaces `pip` + `venv` + `pyenv` in one tool.
- Reads `.python-version` automatically.
- Lockfile (`uv.lock`) for reproducibility.

### Why `src/` layout

- Forces explicit imports, prevents accidental reliance on working directory.
- Makes it clear what is library code vs scripts.
- Industry standard for new Python projects.

### Why `favor_recall=True` in trafilatura

- We are going to filter sentences anyway.
- Better to keep too much text than lose signal.
- Can switch to `favor_precision=True` once we know what we are keeping.

### Why `MIN_WORDS=8`, `MAX_WORDS=80`, `MAX_SYMBOL_RATIO=0.20`

- Word count bounds come directly from the README spec.
- `MAX_SYMBOL_RATIO = 0.20` is a starting point; the README says "small enough" without specifying. Tune based on what we see.

### Why tests reference constants, not hardcoded values

- Hardcoded values in tests become lies when the constant changes.
- Constant-based tests adapt to threshold tuning.
- Test names describe the rule, not the specific value.

### Why `datasketch`

- Standard Python library for MinHash and LSH.
- Well-documented, actively maintained.
- Implements both `MinHash` and `MinHashLSH`.

### Why one-per-line output for filtered and deduped sentences

- Easy to inspect with `head`, `wc -l`, `grep`.
- Easy to re-read with simple `for line in file: ...`.
- Each line is one sentence.

## Known issues and trade-offs

### Sentence splitting is naive

- Current: `re.split(r"(?<=[.?!])\s+", text)`.
- Misses abbreviations like "Dr.", "U.S.A.".
- Misses decimals like "3.14".
- Upgrade to NLTK `sent_tokenize` or `pysbd` if it causes problems on real data.

### Pipeline is not resumable

- README requires resumability.
- Currently, re-running a stage overwrites the output.
- Will need a "state file" tracking what has been done.
- This is a stage 0.5 task (between Brave and HTML) when we get to real data.

### No `logging` module

- Currently using `print()` for visibility.
- Should switch to the `logging` module for proper log levels and file output.
- Especially important when we have rate limits and resumability.

### Filter rules may need tuning

- TBD after inspecting the `.filtered.txt` files.
- May need to tune thresholds based on what we see.
- Some article types may need different parameters (e.g. scientific vs. news).

### No `conftest.py` and no `__init__.py` in `tests/`

- Pytest auto-discovers tests without them in simple projects.
- If we hit an import issue (e.g. `ModuleNotFoundError: No module named 'src'`), the fix is to add a `conftest.py` at the project root with the right path setup, or configure `pyproject.toml` for pytest.

## Conventions summary (also in `AGENTS.md`)

- No emoji in code, comments, or docs.
- No em-dashes in prose. Use periods, commas, or parentheses.
- Type hints on all public functions.
- Tunable constants at the top of each module.
- Tests reference the constants, not hardcoded values.
- Thin scripts in `scripts/`, real logic in `src/`.
- Display helpers (e.g. `preview_text`) stay in scripts, not in `src/`.
- Use `uv add` for dependencies. Never `uv pip install`.
- Boolean assertions in tests use `is True` or `is False`, never bare `assert is_valid(x)`.
