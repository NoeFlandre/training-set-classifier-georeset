# MinHash: a deep dive

This is a self-contained writeup of the MinHash algorithm, covering the problem, the math, and a worked example. Read this before touching `src/dedup.py`.

## 1. The problem

After sentence filtering, we have thousands of sentences. Many are near-duplicates:

- "Pollinators are essential for crop production."
- "Crop production depends heavily on pollinators."

These say the same thing but have zero string overlap. Exact string matching misses the duplicate. We need a fuzzy duplicate detector that asks: "how similar are these two pieces of text?"

This is the "document similarity" problem. The standard solution for set-like data is Jaccard similarity, and MinHash is the trick that makes it scale.

## 2. Jaccard similarity (the natural measure)

For two sets A and B:

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

Range: 0 (no overlap) to 1 (identical).

For text, we represent each sentence as a set of shingles (n-grams of consecutive words). The standard is n=3 (word trigrams), which captures local word order without exploding the set size.

Worked example by hand:

```
Sentence A: "the cat sat on the mat"
Sentence B: "the cat sat on a mat"
```

A's trigrams (window of 3 words, slide by 1):
1. the cat sat
2. cat sat on
3. sat on the
4. on the mat

B's trigrams:
1. the cat sat
2. cat sat on
3. sat on a
4. on a mat

Set math:

```
A ∩ B = {the cat sat, cat sat on}                  # 2 elements
A ∪ B = {the cat sat, cat sat on, sat on the,      # 6 elements
          on the mat, sat on a, on a mat}

J(A, B) = 2 / 6 ≈ 0.33
```

A second example for contrast:

```
A: "the cat sat on the mat"
C: "the dog ran through the park"
A ∩ C = {}
J(A, C) = 0
```

Unrelated sentences get Jaccard 0.

A third example: one word changed in the middle. Changing "the" to "a" in "over the lazy" affects 3 of 7 trigrams. The Jaccard drops noticeably. This is a feature: the metric is sensitive to local word order changes, not just bag-of-words.

## 3. Why naive does not scale

To dedup N sentences, the naive approach is pairwise: for each new sentence, compute Jaccard against all N existing ones.

- Per comparison: O(|A| + |B|) set operations. For ~20-word sentences, ~17 trigrams per set, ~34 operations.
- For one query against N=10,000: 10,000 × 34 = 340,000 operations. OK.
- For 10,000 queries: 10,000² × 34 = 3.4 × 10^9. Hours.

The deeper problem is storage: storing 10,000 sentences as full shingle sets is 170,000 trigrams. For 1M sentences: 17M trigrams in memory.

We need a compact fingerprint that preserves similarity information.

## 4. The MinHash insight (the magic)

A hash function `h` maps any string to an integer. For a set S, the min-hash of S is:

```
min-hash(S) = min over all x in S of h(x)
```

Hash every element, take the smallest hash value.

The key property:

```
P(min-hash(A) == min-hash(B)) = J(A, B)
```

This is the magic. Proof by cases:

Consider the universe `U = A ∪ B`. Hash everything in U. The smallest hash value in U is some element `u*`. Where is `u*`?

- If `u*` is in `A ∩ B` (shared): then `min(h(A)) = h(u*)` and `min(h(B)) = h(u*)`. They agree.
- If `u*` is in A only: then `min(h(A)) = h(u*)` but `min(h(B)) > h(u*)`. They disagree.
- If `u*` is in B only: symmetric. They disagree.

So they agree if and only if the global minimum of `h(U)` is in the intersection. Assuming `h` is "random" (treats all elements equally), the probability that the global minimum is in the intersection is:

```
P(u* in A ∩ B) = |A ∩ B| / |A ∪ B| = J(A, B)
```

QED.

## 5. A worked numerical example

Setup: universe `U = {a, b, c, d, e}`. Hash function:

```
h(a) = 5
h(b) = 2
h(c) = 8
h(d) = 1
h(e) = 6
```

Case 1, high overlap, expect agreement:

```
A = {a, b, c}        h(A) = {5, 2, 8}    min = 2
F = {a, b}           h(F) = {5, 2}       min = 2

A ∩ F = {a, b}        |A ∩ F| = 2
A ∪ F = {a, b, c}     |A ∪ F| = 3
J(A, F) = 2/3 ≈ 0.67

min-hashes: 2 vs 2 -> AGREE
```

Verify: global min of `h(A ∪ F)` is `h(b) = 2`. `b` is in `A ∩ F`. Correct.

Case 2, low overlap, expect disagreement:

```
A = {a, b, c}        h(A) = {5, 2, 8}    min = 2
G = {b, d, e}        h(G) = {2, 1, 6}    min = 1

A ∩ G = {b}           |A ∩ G| = 1
A ∪ G = {a, b, c, d, e}   |A ∪ G| = 5
J(A, G) = 1/5 = 0.20

min-hashes: 2 vs 1 -> DISAGREE
```

Verify: global min of `h(A ∪ G)` is `h(d) = 1`. `d` is in `G` only. So they disagree. Correct.

Case 3, same Jaccard, different outcome (the noise):

```
A = {a, b, c, d, e}    h(A) = {5, 2, 8, 1, 6}    min = 1
H = {a, b, c, d, f}    h(H) = {5, 2, 8, 1, 3}    min = 1

A ∩ H = {a, b, c, d}   |A ∩ H| = 4
A ∪ H = {a, b, c, d, e, f}   |A ∪ H| = 6
J(A, H) = 4/6 ≈ 0.67

min-hashes: 1 vs 1 -> AGREE
```

Same Jaccard (0.67) as case 1, but the global min happens to be `d`, which is in both. So they agree.

This is the lesson: the property is probabilistic, not deterministic. With one hash function, you get a coin flip weighted by Jaccard.

## 6. Why one hash function is not enough

With one hash function, the answer is binary: match or do not match. You can only conclude "0% similar" or "100% similar" from a single trial, useless as a similarity estimate.

Solution: use k hash functions and average. For k hash functions, the fraction that match estimates Jaccard:

```
estimated_J(A, B) = (count of i where sig_A[i] == sig_B[i]) / k
```

Worked example with k=3, using the Case 1 sets (A = {a,b,c}, F = {a,b}, true J = 0.67). Add 2 more hash functions:

```
h1(x) = 5, 2, 8, 1, 6   (as before)
h2(x) = 3, 7, 1, 9, 4   (new mapping)
h3(x) = 1, 4, 2, 7, 5   (new mapping)
```

Compute min-hashes:

```
A = {a, b, c}  ->  h2(A) = {3, 7, 1}  ->  min = 1 (c)
F = {a, b}     ->  h2(F) = {3, 7}     ->  min = 3 (a)
                 h2: 1 vs 3 -> DISAGREE

A = {a, b, c}  ->  h3(A) = {1, 4, 2}  ->  min = 1 (a)
F = {a, b}     ->  h3(F) = {1, 4}     ->  min = 1 (a)
                 h3: 1 vs 1 -> AGREE
```

Combining with h1 (which agreed):

```
h1: AGREE
h2: DISAGREE
h3: AGREE
Matches: 2/3 ≈ 0.67
True J:   0.67
```

Estimate matches true Jaccard exactly. With more hash functions, the estimate gets closer (law of large numbers).

The variance of the estimator: if the true Jaccard is J and we use k hash functions, the match count is binomial with mean `k·J` and variance `k·J·(1-J)`. The standard error of the estimated J is:

```
std = sqrt(J · (1-J) / k)
```

For J=0.5 and k=128: std ≈ sqrt(0.25/128) ≈ 0.044. 95% confidence interval roughly ±0.09.
For J=0.5 and k=512: std ≈ 0.022. 95% CI ±0.04. Better but 4x the storage.

The tradeoff: more hash functions = lower noise, more storage, more compute. k=128 is a common default, around 1 KB per sentence, ~5% error.

## 7. The MinHash signature (the data structure)

For a sentence S, the MinHash signature is a vector of k integers:

```
sig(S) = [m1, m2, ..., mk]
where mi = min over all x in shingles(S) of h_i(x)
```

Storage: k integers. For k=128, 8-byte ints: 1024 bytes = 1 KB per sentence.

For 50,000 sentences: 50 MB total. Compared to storing full shingle sets: probably 5-10x reduction. And the comparison is now O(k) per pair: just count how many positions match.

## 8. LSH: making lookup fast at scale

Even with signatures, comparing N sentences pairwise is O(N² · k). For N=50,000: 3.2 × 10^11 operations. Hours.

Key observation: most pairs of sentences are NOT similar. We do not need to check all pairs, we need to find the few that ARE similar.

Locality-Sensitive Hashing (LSH) splits the signature into b bands of r rows each (so k = b · r). For each band, compute a "band hash" by hashing the r values together. Two signatures are candidates for similarity if they have the same band hash for at least one band.

Probability analysis: the probability that two signatures with Jaccard J become candidates is:

```
P(candidate) = 1 - (1 - J^r)^b
```

For k=128, b=32, r=4:

| Jaccard J | P(candidate)               |
|-----------|------------------------------|
| 0.1       | ~0.003 (essentially never)   |
| 0.3       | ~0.30 (sometimes)            |
| 0.5       | ~0.87 (very likely)          |
| 0.7       | ~0.997 (almost certain)      |
| 0.9       | ~1.0 (certain)               |

This is the sigmoid-like curve we want: high-J pairs are candidates, low-J pairs are not. We only verify candidates with full signature comparison.

For 50,000 sentences with mostly low-J pairs: instead of 1.25 × 10^9 pair checks, only a few thousand candidates. About 100,000x speedup.

## 9. Putting it all together

The algorithm in one paragraph: for each sentence, shingle into 3-grams, compute a 128-int MinHash signature (the smallest hash value per hash function over all shingles), insert into an LSH index (split signature into 32 bands of 4 rows, hash each band). To find duplicates of a query sentence, compute its signature, query the LSH to get candidates, verify candidates with full signature comparison, mark as duplicate if similarity above threshold (e.g. 0.7).

For our small dataset (a few thousand sentences per file), we can skip the LSH step entirely and do brute-force pairwise comparison. The library (`datasketch`) handles the details for us.

## 10. Parameters we will use

| Parameter        | Value | Why                                           |
|------------------|-------|------------------------------------------------|
| `n` (shingle size) | 3   | Standard for word-level shingling.             |
| `num_perm` (signature length) | 128 | Standard. ~5% standard error on similarity estimates. |
| `threshold` (LSH and dedup) | 0.7 | Reasonable default for "near-duplicate". Tune on real data. |

## 11. What you should walk away with

1. The min-hash property is the magic. `min(h(A)) = min(h(B))` iff the global minimum is in `A ∩ B`. `P(this) = J(A, B)`.
2. Multiple hash functions average out the noise. Fraction matching = Jaccard estimator. Noise shrinks as `1/sqrt(k)`.
3. Storage is fixed-size. 128 integers per sentence, regardless of length. ~1 KB.
4. LSH is about avoiding comparisons. The band trick makes high-J pairs likely candidates and low-J pairs very unlikely.
5. It is probabilistic. You will see noisy estimates, not exact values. That is the deal: speed and storage in exchange for some error.
