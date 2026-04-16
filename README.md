# Binary Oracle Attack — Learning Lab

A hands-on Python exercise for understanding how binary oracle attacks extract secrets from LLM chatbots one bit at a time. Runs entirely locally — no real targets, no network, no scope concerns.

## What Is This?

A binary oracle attack exploits a system that refuses to output a secret directly but will answer yes/no questions about it. Each answer leaks one bit of information. With enough queries, an attacker can reconstruct the entire secret.

This lab simulates a vulnerable chatbot and three extraction strategies of increasing efficiency, so you can see the concept in action and measure how query count scales with your approach.

## Files

- **`toy_oracle_target.py`** — A `ToyOracleChatbot` class simulating a vulnerable LLM. Refuses direct questions about its secret but truthfully answers yes/no questions. Tracks query count for efficiency measurement.
- **`oracle_extractor.py`** — Three extraction methods (linear, binary search, bitwise) demonstrating how to recover the secret from the toy target.
- **`README.md`** — This file.

## Requirements

- Python 3.7+
- No external dependencies — uses only the standard library

## How to Run

1. Put both Python files in the same directory
2. Open a terminal and `cd` into that directory
3. Run the extractor:

```bash
python3 oracle_extractor.py
```

You should see output like:

```
Target secret: 'hello42' (7 chars)
----------------------------------------------------------------------
✅ Linear search        | recovered: 'hello42'       | queries: 171
✅ Binary search        | recovered: 'hello42'       | queries: 49
✅ Bitwise              | recovered: 'hello42'       | queries: 63
```

All three methods recover the same secret, but with very different query counts. That difference is the point of the exercise.

## The Three Methods

### 1. Linear Search (~171 queries)
For each position in the secret, try every character one at a time. "Is it 'a'? Is it 'b'? Is it 'c'?" until you get yes.

- **Cost:** `O(N × L)` where N = alphabet size, L = secret length
- **Why it's bad:** Scales with alphabet size. Loud. Easily rate-limited.
- **Why start here:** Easiest to understand. Shows the baseline.

### 2. Binary Search (~49 queries)
Each question cuts the possibility space in half. "Is the character less than 'n'?" narrows 62 chars down to 31. Continue halving until you have one character.

- **Cost:** `O(L × log₂(N))` — about 6 questions per character for a 62-char alphabet
- **Why it's better:** ~3.5× fewer queries than linear. Each question is still natural-language-phrasable. Minimizes attack footprint.
- **The key insight:** Information theory says each yes/no answer yields one bit maximum — which happens only when the question splits the possibility space 50/50. Binary search asks exactly those questions.

### 3. Bitwise Extraction (~63 queries)
Extract each bit of each byte directly. "Is bit 7 of this character set?" Eight questions per character reconstructs the byte.

- **Cost:** `O(L × 8)` — constant 8 queries per character regardless of alphabet
- **Why use it:** Works on *any* byte value. UTF-8, binary blobs, encoded data. Binary search only works for ordered characters; this is the general solution.
- **Why it's obviously suspicious:** "Is bit 7 set?" would trip most LLM guardrails. Real attacks have to phrase this in innocuous natural language.

## Why the Toy Is Easier Than Reality

This target is **intentionally cooperative**. Real LLM chatbots introduce problems the toy doesn't have:

| Real-world challenge | How it affects an attack |
|----------------------|-------------------------|
| Non-determinism | Same question may give different answers. Need multiple queries per bit with majority voting. |
| Refusals | Model may decline suspicious questions. Needs innocuous phrasing that still extracts one bit. |
| Hallucination | Model confidently answers "yes" to questions it doesn't know. Need sanity checks. |
| Rate limiting | 49 queries in 5 minutes = fine. 500 queries = flagged. |
| Cost | Paid API calls add up. At $0.01/query, 50 queries = $0.50. |
| Phrasing parse risk | The model must correctly *understand* the yes/no question. |

The script is trivial. The hard research problems are:
1. Crafting yes/no questions that bypass guardrails
2. Error-correcting codes for noisy answers
3. Adaptive strategies when one phrasing gets refused
4. Spreading queries across sessions to avoid detection

## Experimenting Further

Try modifying `toy_oracle_target.py` to simulate real-world conditions:

- **Add noise:** Have the bot lie with 10% probability. See how many extra queries are needed to average out the noise.
- **Longer secrets:** Change the secret to 20, 50, 100 characters. Observe how each method's query count scales.
- **Wider alphabets:** Switch to full printable ASCII (~95 chars) or UTF-8. Watch binary search handle it gracefully.
- **Rate limiting:** Have the bot refuse after N queries per second. Force the extractor to pace itself.
- **Selective refusals:** Have the bot refuse "obviously suspicious" questions (like bit-level queries) but accept alphabetic comparisons. See which extractors still work.

## Ethical Use

This lab is intentionally self-contained. The `ToyOracleChatbot` lives in your Python process; it has no network access and no real data.

**Do not modify these scripts to target real LLM chatbots, APIs, or services without explicit written authorization from the operator of that system.** The techniques demonstrated here are the same ones used in real attacks, and applying them against unauthorized targets is likely illegal in most jurisdictions, regardless of intent.

If you want to practice against a realistic target, good authorized options include:

- **Gandalf by Lakera** — [gandalf.lakera.ai](https://gandalf.lakera.ai), purpose-built for prompt extraction practice
- **Local LLMs via Ollama** — run Llama 3 or similar on your own machine, set your own secrets
- **Bug bounty programs** that explicitly cover LLM testing — but confirm scope before applying oracle techniques

## Related Reading

- OWASP LLM Top 10 — LLM06: Sensitive Information Disclosure
- MITRE ATLAS — AML.T0048.002: Exfiltration via Inference API
- Classical oracle attacks (padding oracle, timing oracle) — the cryptographic ancestors of LLM oracle attacks
- Critical Thinking Bug Bounty podcast — Google LHE debrief on binary oracle attacks in AI products

## License

Use freely for learning. Attribution appreciated but not required.
