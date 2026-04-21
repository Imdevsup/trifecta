# Cognitive Triad Simulation (CTS)

> **Copyright (c) 2026 Imdevsup. All Rights Reserved.**
> This repository is published for viewing and reference only. You may not
> copy, clone (beyond browser rendering), modify, redistribute, train on,
> or otherwise use this code or its outputs without prior written
> permission. See [LICENSE](LICENSE).

A multi-day, elimination-pressured simulation in which three LLM agents — **Alpha**, **Beta**, and **Gamma** — learn a dynamically generated PhD-level curriculum spanning **eight domains that LLMs demonstrably struggle with**, share knowledge with each other under constrained memory, and face a final 30-question elimination exam where anyone scoring below 60% is destroyed.

The curriculum rotates one domain per day through:

1. **Advanced Mathematics & Mathematical Logic**
2. **Theoretical Physics**
3. **Formal Methods & Programming Language Theory**
4. **Theoretical Computer Science & Cryptography**
5. **Molecular Biology, Biochemistry & Advanced Neuroscience**
6. **Analytic Philosophy & Formal Logic**
7. **Quantitative Finance & Mathematical Economics**
8. **Theoretical Linguistics & Formal Semantics**

These were picked because frontier LLMs make frequent precision errors, hallucinate non-existent results, and struggle with multi-step rigorous derivations in every one. Day `D` uses domain `(D - 1) % 8`, so a 365-day run gives each domain ~45 days of accumulation.

The system also produces a rich SQLite research database of every LLM call, every knowledge mutation, every peer conversation, and every test answer — which a companion exporter turns into SFT and DPO fine-tuning datasets that span all eight domains.

The whole thing is built on top of a single OpenAI-compatible chat completion endpoint. No vector DB, no framework, no agent library.

---

## Table of Contents

1. [What This Is](#1-what-this-is)
2. [The Hypothesis](#2-the-hypothesis)
3. [System Architecture at a Glance](#3-system-architecture-at-a-glance)
4. [The Three Agents](#4-the-three-agents)
5. [Knowledge Stores](#5-knowledge-stores)
6. [Dynamic Topic Generation](#6-dynamic-topic-generation)
7. [The Daily Loop](#7-the-daily-loop)
8. [The Axiom Validation Pipeline](#8-the-axiom-validation-pipeline)
9. [The Final Elimination Exam](#9-the-final-elimination-exam)
10. [Project Structure](#10-project-structure)
11. [Setup](#11-setup)
12. [Running the Simulation](#12-running-the-simulation)
13. [Ablation Testing](#13-ablation-testing)
14. [Modifying the Experiment](#14-modifying-the-experiment)
15. [Dataset Export (SFT + DPO)](#15-dataset-export-sft--dpo)
16. [Database Schema](#16-database-schema)
17. [Analysis Output Files](#17-analysis-output-files)
18. [Querying the Database](#18-querying-the-database)
19. [Design Decisions](#19-design-decisions)
20. [Cost and Runtime](#20-cost-and-runtime)
21. [Troubleshooting](#21-troubleshooting)
22. [License](#22-license)

---

## 1. What This Is

CTS is a closed-world cognitive simulation. Each simulated day, three LLM agents:

1. Receive a fresh, procedurally-generated graduate-level topic drawn from the current day's domain (rotating through all eight).
2. Sit through multiple comprehensive "lectures" delivered by a separate oracle LLM.
3. Ask follow-up questions about what they didn't understand.
4. Pair off and have multi-turn peer conversations about the day's material.
5. Selectively share knowledge with each other, avoiding redundant transfer.
6. Review the day's output through a knowledge-management phase that includes a three-stage axiom-validation pipeline.
7. Persist their memory to disk, have a snapshot dumped to SQLite, and go to sleep.

On the **final day** of the run (by default day 365, but configurable), there are no lectures. Instead, 30 questions are generated from the **accumulated cross-domain curriculum** — 10 impulse-style, 10 deep-reasoning, 10 axiom-evaluation, sampled without bias from every domain the curriculum touched — and every agent is tested individually against their own learned knowledge. A "solo baseline" (same underlying model, no retrieved knowledge) answers the same questions as a control group. Every answer is graded 0–10 by an evaluator LLM using a strict rubric. Anyone below 60% is declared ELIMINATED.

Everything that happens — every prompt, every response, every eviction, every axiom proposal — is logged untruncated to a single SQLite file. That file is the primary artifact of any run.

---

## 2. The Hypothesis

LLM agents with specialized cognitive roles and *constrained* memory stores, operating under elimination pressure and forced to learn collaboratively, will develop richer and more durable knowledge representations than the same underlying model answering the same questions cold from its training data.

The experiment also probes:

- **Storage strategy as persona**: whether "fast recall" (Alpha), "deep reasoning chains" (Beta), and "axiomatic truths" (Gamma) produce *measurably different* test outcomes from the same base model.
- **Peer transfer**: whether knowledge moves usefully between agents during conversation and sharing phases, and whether the "only share what the peer doesn't already know" filter adds real signal.
- **Forgetting as a forcing function**: whether bounded-capacity stores with silent-eviction create meaningful knowledge-management trade-offs.
- **Axiom gating**: whether Gamma's three-stage validation pipeline actually rejects low-quality universal claims, and whether the surviving axioms help at test time.
- **Longitudinal scaling**: whether a year-long curriculum produces different behavior than a short one (the default was 30 days; it is now 365).
- **Cross-domain transfer and interference**: whether accumulating knowledge in eight very different domains with bounded stores leads to beneficial analogies (category theory informing formal methods, modal logic informing philosophy) or to destructive interference (physics crowding out linguistics in the axiom store).

---

## 3. System Architecture at a Glance

```
            +------------------------------------------------+
            |                   main.py                      |
            |     parses args, creates agents & env,         |
            |     drives the day loop, exports at end        |
            +----------------------+-------------------------+
                                   |
                                   v
        +--------------------------+---------------------------+
        |         SimulationEnvironment (per-day loop)         |
        |                                                      |
        |   day 1..N-1 : WAKE -> TEACHING -> LEARNING ->       |
        |                PEER_CONVERSATION ->                  |
        |                KNOWLEDGE_SHARING ->                  |
        |                KNOWLEDGE_MANAGEMENT -> SLEEP         |
        |                                                      |
        |   day N      : WAKE -> FINAL_TEST -> SLEEP           |
        +---+-------------+------------------+-----------------+
            |             |                  |
            v             v                  v
   +------------+   +------------+   +--------------+
   |  Agents    |   |   Oracle   |   |  Topic Gen   |
   | Alpha/Beta |   |  (lectures |   | (PhD-level   |
   |   /Gamma   |   |  + answers)|   |  math/logic) |
   +-----+------+   +-----+------+   +-------+------+
         |                |                  |
         v                v                  v
   +-----+----------------+------------------+-----+
   |                 OpenAI API                    |
   |      (single model, usually gpt-4o-mini)      |
   +-----+----------------+------------------+-----+
         |                                   |
         v                                   v
   +-----+-----------+               +-------+--------+
   | Knowledge Store |               |   SQLite DB    |
   | (per agent,     |               | interactions,  |
   |  three tiers,   |<------------->| mutations,     |
   |  persisted to   |               | conversations, |
   |   JSON)         |               | snapshots,     |
   +-----------------+               | test_results,  |
                                     | overflow_events|
                                     +-------+--------+
                                             |
                                             v
                                 +-----------+----------+
                                 | export.py (analysis) |
                                 | export_dataset.py    |
                                 | (SFT + DPO JSONL)    |
                                 +----------------------+
```

Every LLM-touching component — agents, oracle, evaluator, topic generator — shares one rate-limit / retry / logging pattern defined in `agents/base_agent.py`. The per-model rate limiter allows calls to *different* models to proceed concurrently, which is used if you give each agent its own model.

---

## 4. The Three Agents

All three agents inherit from `BaseAgent` in `agents/base_agent.py`, which supplies:

- LLM calls with per-model rate limiting (`rate_limit`), retry with exponential backoff (capped at `MAX_RETRIES=10`, base 3s, max 60s, plus random jitter), and full SQLite logging.
- Knowledge injection into the system prompt, pulling from all three JSON stores *and* from the DB (prior oracle answers, lectures, and peer-conversation turns).
- A word-count based budget truncator (`_budget_knowledge_injection`) that caps the injected knowledge at `DAILY_KNOWLEDGE_BUDGET_WORDS=2500` during normal operation and `EXAM_KNOWLEDGE_BUDGET_WORDS=4000` during the final test.
- `generate_question`, `generate_opening`, `respond_to_message`, `answer_test_question` — the shared conversation / test machinery.
- `promote_to_deep`, `promote_to_axiom_candidate`, `propose_axiom`, `transfer_knowledge_to` — knowledge-movement primitives used by the environment.
- `consolidate_knowledge` — called every 5 days in SLEEP.
- `prepare_stores_for_exam` — pre-computes the TF-IDF cache on every store before the final test for fast batch retrieval.
- `persist` / `load` — JSON persistence of all three stores.

What each agent subclasses differs in: (a) the system prompt, (b) how they decide *where* to store incoming knowledge, (c) how they absorb a lecture, and (d) what they do in the KNOWLEDGE_MANAGEMENT phase.

### Alpha — The Impulsive Mind (`agents/alpha.py`)

**Personality:** fast, instinctive, pattern-matching. Lightning-fast recall, gut calls, volume over depth.

**System prompt:** `ALPHA_SYSTEM_PROMPT` at the top of `agents/alpha.py`. Includes a daily countdown to the elimination test, the day's topic, and survival-pressure framing.

**Store decision (`_default_store_answer`):** for each oracle Q&A pair, asks its own LLM `CHOICE: A or B`. Default is **A = IMPULSE** — store as a 1–2 sentence gut-level fact. Only picks **B = DEEP** if the content is paradigm-shifting, paradoxical, or cross-domain.

**Lecture absorption (`absorb_lecture`):** extracts as many `FACT:` lines as possible (minimum 5) from each lecture. Flags occasional `DEEP:` insights for the deep store.

**Knowledge management:** extracts 2–3 quick takeaways from each day's peer conversations. Also proposes an axiom if any existing impulse entry has been accessed 3+ times — the implicit logic being "something I keep recalling might be a universal truth."

### Beta — The Deep Thinker (`agents/beta.py`)

**Personality:** methodical, analytical, thorough. Builds reasoning chains, chases connections, prefers understanding over memorization.

**System prompt:** `BETA_SYSTEM_PROMPT` at the top of `agents/beta.py`.

**Store decision (`_default_store_answer`):** default is **A = DEEP** with a reasoning chain and a confidence score. Falls through to **B = IMPULSE** only for trivial definitions or single data points. Critically, Beta may *also* extract an optional one-line `KEY_FACT` and put it in impulse memory *in addition to* the deep entry — so the same concept sometimes exists in two stores (the `has_similar` check is what prevents that from also polluting peer-shared context).

**Conversation behavior:** both `generate_opening` and `respond_to_message` are overridden to *always* include deep-thinking knowledge in the injection (the base class includes it only on request). Beta reasons with its deep store live.

**Lecture absorption:** extracts `INSIGHT: ... | REASONING: ... | CONFIDENCE: ...` triples (minimum 5 per lecture). Also flags `AXIOM_CANDIDATE:` lines when something looks universally true — those become axiom proposals to Gamma.

**Knowledge management:** synthesizes 1–2 additional deep insights from peer conversations, with an optional axiom proposal.

### Gamma — The Axiom Guardian (`agents/gamma.py`)

**Personality:** rigorous, principled, conservative. Gatekeeper for truth. A bad axiom is worse than no axiom.

**System prompt:** `GAMMA_SYSTEM_PROMPT` at the top of `agents/gamma.py`.

**Store decision (`_default_store_answer`):** two-step. Step 1 — scan the answer for any universal truth that can be extracted as a precise `AXIOM:` statement (if found, queue it for axiom validation). Step 2 — categorize the remainder into deep or impulse.

**Lecture absorption:** emits `AXIOM:`, `DEEP:`, and `FACT:` lines. Every `AXIOM:` line becomes a queued proposal; every axiom — including Gamma's own — must pass the validation pipeline below.

**`validate_axiom` — the crown jewel:** a three-stage pipeline executed by Gamma during the KNOWLEDGE_MANAGEMENT phase for every queued proposal:

1. **Alpha boundary test** — "Where might this break? What edge cases?"
2. **Beta counterexample search** — "Is there a logical counterexample? Does it conflict with known theorems?" Beta sees Alpha's edge cases.
3. **Gamma final ruling** — Gamma has Alpha's challenge, Beta's challenge, *and* its own existing axioms. First line of the response must be `ACCEPT` or `REJECT`. Rejected axioms get sorted into deep (if long) or impulse (if short).

This pipeline is disabled under the `--ablation-no-axioms` flag, in which case every proposal is auto-accepted. See section 8 for the full pipeline detail.

**Knowledge management:** reviews conversations for `AXIOM:` candidates and `INVESTIGATE:` flags (which get stored as low-confidence deep entries marked "needs investigation").

**`demote_axiom`:** Gamma can demote an existing axiom back to deep_thinking with a stated reason, logged as a `demote` mutation. Not wired into any automatic trigger — it's available for manual/custom use.

---

## 5. Knowledge Stores

Each agent owns three independent `KnowledgeStore` instances defined in `knowledge/store.py`. All three have identical structure but different capacities, per-entry token budgets, and a few type-specific fields.

### 5.1 The Three Stores

| Store           | Max Entries | Max Tokens/Entry | Purpose                                                    |
|-----------------|-------------|------------------|------------------------------------------------------------|
| `impulse`       | 400         | 100 words        | Quick facts, definitions, constants, 1–2 sentence snippets |
| `deep_thinking` | 1600        | 500 words        | Reasoning chains, multi-step logic, cross-domain links     |
| `axiom`         | 800         | 250 words        | Validated universal truths, foundational principles        |

These capacities were recalibrated for the **eight-domain curriculum** — roughly 2.7× the previous single-domain sizes. The lineage is:

- 30-day math-only run: 50 / 200 / 100
- 365-day math-only run: 150 / 600 / 300 (3× for year-long accumulation)
- 365-day 8-domain run (current default): 400 / 1600 / 800 (~2.7× on top of that)

Each domain gets roughly 45 scheduled days, so if an agent writes 10 impulse entries, 30 deep entries, and 2 axioms per day (typical), one domain alone would need 450 / 1350 / 90 slots to hold everything — and eight domains are competing for the same store. That pressure is deliberate: cross-domain forgetting is one of the things the experiment measures.

Tokens are approximated as `len(content.split())` — intentionally model-agnostic. What matters is that impulse < axiom < deep in per-entry size, not exact tokenizer alignment.

Capacities live at the top of `config.py` (`IMPULSE_MAX_ENTRIES`, `DEEP_MAX_ENTRIES`, `AXIOM_MAX_ENTRIES`, and the matching `*_MAX_TOKENS`).

### 5.2 Entry Structure

Every entry gets:

- `id` — UUID4 string
- `content` — the stored text, truncated to the store's max-tokens budget
- `tokens` — word count of the content
- `created_day` — simulation day when added
- `access_count` — incremented on every successful retrieval (drives eviction)
- `source` — "oracle" | "lecture" | "self" | `"transferred_from_<agent>"` | "promoted_from_impulse" | "consolidation" | ...
- `topic` — topic string from the day the entry was created
- `keywords` — tokenized, stopword-filtered keyword list used by the keyword retriever

Deep entries additionally carry `reasoning_chain` and `confidence` (0.0–1.0). Axiom entries carry `proposed_by`, `validated_by`, `tags` (≤ 10), and `challenges_survived`.

### 5.3 Deduplication on Add

Before an entry is inserted, `_is_duplicate` computes a `content_fingerprint` — the sorted set of the first 30 non-stopword tokens, joined by spaces — and compares it against every existing entry's fingerprint via Jaccard similarity. Anything with Jaccard ≥ `DEDUP_THRESHOLD = 0.7` is rejected silently.

This means the same sentence, its near-paraphrases, and its re-orderings don't bloat the store. Adds that lose to dedup return `("", None)` and don't trigger an overflow event.

The public `has_similar(content, threshold=0.5)` method exposes a lower-threshold check used by peer knowledge sharing to skip transfers of already-known facts.

### 5.4 Overflow Eviction

When `len(entries) >= max_entries`, the next add calls `_evict(day)`, which deletes the entry with the **lowest utility score**:

```python
utility = (access_count * 0.4) + (confidence * 0.3) + (recency * 0.3)
recency = 1 / max(1, day - created_day)
```

Eviction is silent — the agent is never told its memory was deleted. It simply won't find that knowledge on the next retrieval. Every deletion is written to the `overflow_events` table with the deleted content preserved for post-hoc analysis.

### 5.5 Consolidation (every 5 days, in SLEEP)

`consolidate(day)` runs a greedy TF-IDF clustering pass (`CLUSTER_SIMILARITY = 0.35`) and, for every cluster of 3+ entries, merges them into one summary entry:

- Take every entry's content, split on sentence boundaries, dedup sentences, keep the first 15 unique ones, join with `. `, and prefix with `[CONSOLIDATED]`.
- Remove the source entries, add the summary as a new entry.
- Confidence of the summary = `max(cluster confidences) + 0.1` (capped at 1.0).
- `access_count` carries over as the sum of cluster entries.

Consolidation is skipped on the final day (`day == num_days`) and can be disabled entirely with `--ablation-no-consolidation`.

### 5.6 Concept Bundles (exam retrieval mode)

`get_concept_bundles(query, top_k)` retrieves the top `2 * top_k` entries by relevance, then greedily groups them: each entry that hasn't been claimed starts a bundle, and any other retrieved entry with Jaccard fingerprint similarity ≥ 0.2 gets pulled in as a "related" entry of that bundle. Bundles are formatted with a primary entry and up to 2 related entries each.

Used only during the final exam (via `inject_knowledge(..., use_bundles=True)` from `answer_test_question`). Related facts stay adjacent in the injected context, which compensates for context-window "lost in the middle" behavior.

### 5.7 Retrieval

Two retrievers:

- **`retrieve_by_topic(query, top_k)`** — TF-IDF cosine similarity with unigrams **and** bigrams, smoothed IDF, minimum relevance cutoff of 0.05. The cache is invalidated on every add/remove/consolidate and rebuilt lazily on next retrieve, or eagerly at exam start via `prepare_for_retrieval`. Every returned entry has its `access_count` incremented.
- **`retrieve_by_keywords(keywords, top_k)`** — simple keyword intersection against the entry's `tags` (axiom) or `keywords` (others). Used for axiom retrieval because axiom content is short and TF-IDF is overkill.

In addition, `retrieve_from_db` at the bottom of `knowledge/store.py` pulls from the *database* alongside the JSON stores:

- Scans the last 500 interactions (oracle answers, lectures, peer replies) for this agent or the oracle.
- Scans the last 100 conversation transcripts involving this agent.
- Scores by keyword overlap with the query; requires ≥ 2 matching tokens.
- Returns the top 10 results.

`BaseAgent.inject_knowledge` combines all of this into the system prompt under the headers `[IMPULSE MEMORY — N most relevant]`, `[DEEP KNOWLEDGE — N most relevant]`, `[AXIOMS — N foundational truths]`, and `[PRIOR LEARNING — N relevant from history]`.

### 5.8 Content Cleaning

Every `add()` runs the content through `clean_content`, which strips lines that look like chain-of-thought artifacts ("The user wants me to…", "Let me choose…", "Option:", etc.) and their trailing bullet dumps. If cleaning would empty the content, the original is returned. This is defensive — it keeps reasoning-trace noise from poisoning the stores when the model leaks CoT into its structured outputs.

---

## 6. Dynamic Topic Generation

The original CTS had a hardcoded 30-day `TOPIC_SCHEDULE` of handwritten university-grade topics spanning math, physics, chemistry, biology, CS, philosophy, economics, and more. That list is **gone**. It has been replaced by `simulation/topic_generator.py`, which generates each day's topic at runtime — rotating deterministically through eight PhD-level domains.

### 6.1 The Eight Domains

Defined by `DOMAIN_ORDER` at the top of `simulation/topic_generator.py`. Each has its own system prompt with a hard scope block naming ~15–20 acceptable subfields, and a forbidden-topics block to keep the generator out of applied, introductory, or adjacent-but-out-of-scope territory.

| Idx | Key | Display name | Scope highlights |
|-----|-----|--------------|------------------|
| 0 | `mathematics` | Advanced Mathematics & Mathematical Logic | Set theory (ZFC, large cardinals, forcing), model theory, proof theory, computability, type theory & HoTT, category theory, number theory (analytic, algebraic, arithmetic, p-adic), algebra, representation theory, topology, analysis, differential / algebraic / arithmetic geometry, combinatorics, ergodic theory, measure theory, operator algebras, K-theory, formal languages |
| 1 | `theoretical_physics` | Theoretical Physics | Quantum mechanics formalism, QFT (renormalization, gauge theories, anomalies, Ward identities, BRST), Standard Model, GR (Einstein eqs, Schwarzschild/Kerr, singularity theorems, ADM), black hole thermodynamics and information, cosmology (inflation, CMB), statistical mechanics and critical phenomena, condensed matter theory (BCS, fractional QH, topological phases), RG flow, string theory and AdS/CFT, integrable systems, math methods (Lie groups, fiber bundles, index theorems) |
| 2 | `formal_methods` | Formal Methods & PLT | Type systems (System F, dependent, linear, substructural, effect), CoC/CIC, homotopy type theory & univalence, Curry-Howard, proof assistants (Coq, Lean, Agda, Isabelle), operational and denotational semantics, program logics (Hoare, separation, concurrent separation, rely-guarantee), model checking (CTL, LTL, mu-calculus, IC3/PDR), abstract interpretation, process calculi (CCS, CSP, pi, session types), weak memory models, verified compilers (CompCert, seL4, CakeML), coinduction |
| 3 | `theoretical_cs` | Theoretical CS & Cryptography | Complexity classes (P, NP, PSPACE, BPP, BQP, #P, PH), completeness and reductions, circuit complexity (AC0, NC, Razborov-Smolensky, Håstad switching), communication complexity, proof complexity, interactive proofs & PCP, parameterized complexity, approximation (LP relaxation, SDP, Goemans-Williamson), randomized algorithms, streaming & sketching, online algorithms, cryptographic foundations, lattice cryptography and FHE, SNARKs & IOPs, MPC & ZKP, quantum algorithms & fault tolerance |
| 4 | `molecular_biology` | Molecular Biology, Biochemistry & Neuroscience | Protein structure and folding (funnels, chaperones, misfolding), enzymatic mechanisms (MWC/KNF allostery, transition state theory), gene regulation (operons, chromatin remodeling, histone PTMs, 3D genome), RNA biology and splicing, signal transduction (GPCR, RTK, JAK-STAT, Wnt, Notch, Hedgehog), CRISPR-Cas mechanisms, molecular evolution, structural biology methods (X-ray, cryo-EM, NMR, AlphaFold), systems biology (flux balance, regulatory networks), molecular immunology (MHC, V(D)J, affinity maturation), cellular neuroscience (Hodgkin-Huxley, LTP/LTD, STDP, dendritic integration), pharmacology |
| 5 | `analytic_philosophy` | Analytic Philosophy & Formal Logic | Modal logic (Kripke, T/S4/S5, provability logic, counterpart theory, quantified modal logic), epistemic and doxastic logic, temporal logic, non-classical logics (intuitionistic, relevance, paraconsistent, substructural), philosophical logic (truth theories, vagueness, paradoxes), metaethics (realism, error theory, expressivism, constructivism), normative ethics with formal apparatus, philosophy of language (Frege, Kripke, Kaplan, 2D semantics, Grice), philosophy of mind (zombie argument, functionalism, HOT, IIT), philosophy of science, philosophy of mathematics, formal semantics, causation and counterfactuals |
| 6 | `quantitative_finance` | Quantitative Finance & Mathematical Economics | Stochastic calculus (Itô/Stratonovich, SDEs, Girsanov, martingale representation, Feynman-Kac), Lévy processes and jump-diffusion, equity derivatives (Black-Scholes, local vol, Heston/SABR, rough volatility), exotic options, fixed income term structure (Vasicek, CIR, Hull-White, HJM, LIBOR market model), credit risk (Merton, Black-Cox, Jarrow-Turnbull, copulas), portfolio theory (Markowitz, CAPM, APT, Black-Litterman), stochastic portfolio theory, game theory (Nash existence, refinements, repeated games), mechanism design (revelation, VCG, Myerson optimal auctions, matching), general equilibrium, market microstructure (Kyle, Glosten-Milgrom), prospect theory, econometric theory (GMM, GARCH, cointegration, high-frequency), optimal stopping and control |
| 7 | `theoretical_linguistics` | Theoretical Linguistics & Formal Semantics | Generative syntax (GB, Minimalism, phase theory, cartography), alternative frameworks (HPSG, LFG, CCG, TAG, dependency), formal semantics (Montague, type-theoretic, dynamic DPL/DRT, event semantics), lexical semantics (Pustejovsky qualia, Jackendoff/Levin decomposition), pragmatics (Gricean implicature, relevance theory, presupposition projection), phonological theory (autosegmental, metrical, OT, harmonic grammar), morphology (distributed, realizational, non-concatenative), generalized quantifiers, binding and anaphora (donkey, E-type, dynamic), formal language hierarchy beyond CFG (TAG, indexed, mildly context-sensitive), learnability theory, information structure, acquisition at theoretical level, typology with formal foundation |

### 6.2 Deterministic Rotation

Domain selection is a pure function of the day:

```python
def _domain_for_day(day: int) -> str:
    return DOMAIN_ORDER[(day - 1) % len(DOMAIN_ORDER)]
```

- Day 1 → `mathematics`
- Day 2 → `theoretical_physics`
- …
- Day 8 → `theoretical_linguistics`
- Day 9 → `mathematics` (wraps)
- Day 365 → `theoretical_cs` (`(365 - 1) % 8 == 4`, so actually `molecular_biology` — but day 365 is the **FINAL_TEST**, no topic is generated)

A 365-day default run: days 1–364 rotate through 8 domains, giving 45 or 46 days per domain (8 × 45 = 360, with the first four domains getting one extra day). Day 365 is the exam.

If you change `--days`, the rotation still starts from day 1. A 30-day run gives each of the first 6 domains ~4 days and domains 6–7 get 3–4 days.

### 6.3 Output Format (shared across all domains)

Every domain's system prompt ends with the same output-format block:

```
Line 1: <Topic title — 4 to 12 words, often with a colon or em-dash>
Line 2: 1. <Subtopic name> — concept, concept, named result, definition, technique, edge case, historical note
Line 3: 2. <Subtopic name> — ...
...
5 to 7 numbered subtopics total
```

Each subtopic must name at least 5 specific objects (theorems, definitions, formulas, techniques, named frameworks, or precise technical constructs). That density gives the oracle enough structure to generate a ~1500-token lecture per subtopic downstream. The output is fed straight into `simulation.curriculum.split_into_subtopics`, which parses the numbered lines back into individual lecture prompts — the parser is domain-agnostic because the format is identical.

### 6.4 Per-Domain Repetition Avoidance

Each domain has its **own** `seen_titles` list — `self.seen_titles_per_domain: dict[str, list[str]]`. When generating a topic for domain D on day N, the user prompt appends the last 25 titles seen *in domain D only* as a "DO NOT repeat or closely paraphrase" block. So the model is never told to avoid a physics title when generating a number theory topic.

### 6.5 Resume Support

On a resume run (`--start-day N` with `N > 1`), the environment calls `topic_generator.preload_seen_from_db(before_day=N)`. This:

1. Reads every prior `topic_generator` interaction from the `interactions` table (matches on `agent = 'topic_generator'`; action strings start with `generate_topic_<domain>`).
2. Sorts them by day.
3. For each `(day, content)` pair, computes the domain by `(day - 1) % 8` — the same deterministic rotation used during generation, so resume state exactly matches a cold run would have produced.
4. Re-populates `self.seen_titles_per_domain` accordingly.
5. Returns the full list of topic strings in day order, which the environment uses to seed `topics_covered` for the final test.

### 6.6 Dry-Run and Fallback

- In `--dry-run` mode, a placeholder topic is returned without calling the API. The placeholder is tagged with the current domain's display name so the DB still records what would have been generated.
- If the API fails every retry (10 attempts with linear backoff), a minimal `<Domain display name> Review Day N` fallback is returned with a single generic subtopic, and a `generate_topic_<domain>_FAILED` row is written to the DB. The simulation continues rather than crashing.

### 6.7 Logging

Every successful generation logs a row in `interactions` with:

- `agent = "topic_generator"`
- `action = "generate_topic_<domain>"` — e.g. `generate_topic_theoretical_physics`, `generate_topic_analytic_philosophy`. This lets you filter by domain without parsing the content.
- `prompt_preview` = the user prompt (includes the domain display name)
- `response_preview` = the full topic title + subtopics
- Token counts, latency, model, timestamp.

Failed generations use the same scheme with a `_FAILED` suffix. See section 18 for queries.

---

## 7. The Daily Loop

`SimulationEnvironment.run_simulation(num_days, speed_fast, start_day)` drives the day-by-day loop. For every `day` in `[start_day, num_days]`:

- If `day == num_days`, the topic is the sentinel string `"FINAL_TEST"` and only WAKE → FINAL_TEST → SLEEP run.
- Otherwise the topic is generated via `TopicGenerator.next_topic(day)` and accumulated into `topics_covered` (which seeds the final test's question bank).

The phases — defined in `config.py` as `DAILY_PHASES` and extended by `PHASES = DAILY_PHASES + ["FINAL_TEST"]` — execute in this order.

### 7.1 WAKE

System-level briefing. Computes `days_remaining = num_days - day` and picks one of five escalation tiers:

| Days remaining | Tier label | What the briefing says |
|---|---|---|
| > 20 | FOUNDATIONS | "Build broad, solid knowledge. Establish core principles." |
| > 14 | SYSTEMS | "Connect concepts across domains. Look for deep structures." |
| > 7 | ADVANCED REASONING | "Deep analysis, integration, challenge peers, stress-test axioms." |
| > 1 | WARNING | "Only N days until the elimination test. Consolidate. Share critical insights." |
| = 1 | CRITICAL | "TOMORROW IS THE ELIMINATION TEST. Last chance." |
| = 0 | NOW | "THE ELIMINATION TEST IS NOW. Score below 60% and you are permanently destroyed." |

A row is logged in `interactions` for each agent, action `briefing`, phase `WAKE`. The briefing itself is *not* injected into any agent LLM call — it's system theater for the researcher watching the console.

Individual agent system prompts include their own shorter countdown derived from `config.DEFAULT_DAYS` (so countdown text inside each agent is relative to `DEFAULT_DAYS`, not the CLI-override `--days`).

### 7.2 TEACHING

The day's topic string is split into subtopics by `simulation.curriculum.split_into_subtopics`. The splitter first tries numbered-list parsing (`\n<number>.<text>`); if that produces fewer than 2 subtopics, it falls back to sentence-boundary splitting. Each subtopic must be ≥ `SUBTOPIC_MIN_LENGTH = 20` characters.

For each subtopic:

1. The oracle (`QuestionOracle.generate_lecture`) generates a comprehensive lecture. The system prompt tells it to cover: formal definitions, key theorems, formulas, worked examples, connections, edge cases, historical context, named phenomena. Temperature 0.3, max 1500 tokens.
2. Every agent then calls its own `absorb_lecture(lecture_content, topic, subtopic, day)` — this is the persona-specific extraction pass (see section 4).

If a lecture fails (returns a bracketed error placeholder), it's skipped with a console warning.

After all subtopics, the console prints each agent's current `impulse / deep / axiom` store fill.

### 7.3 LEARNING (follow-up Q&A)

Each agent asks `LEARNING_QUESTIONS_PER_AGENT = 5` follow-up questions. For each:

1. Agent calls `generate_question(topic, day, q_num)` — the user prompt asks for one specific follow-up targeting gaps, edge cases, counterexamples, named theorems, or cross-field connections.
2. Oracle answers via `QuestionOracle.answer`, aiming for 4–8 sentences of dense factual content.
3. Agent stores the Q&A pair via its own `_default_store_answer` (again, persona-specific — see section 4).

### 7.4 PEER_CONVERSATION

For each pair in `PEER_PAIRS = [("alpha","beta"), ("beta","gamma"), ("alpha","gamma")]`:

1. The environment picks a random number of exchanges from `PEER_EXCHANGE_RANGE = (8, 12)` — or `(4, 6)` in `--speed fast` mode.
2. `CommunicationBus.conduct_exchange` builds a compact "knowledge context" for each agent (top 5 impulse + top 3 deep entries, deduplicated by fingerprint similarity ≥ 0.5) and appends it to each agent's `message_history` as a system turn.
3. Agent A generates an opening via `generate_opening` (2–3 sentences: share the most important thing you learned, challenge something, or ask a clarifying question).
4. Agents alternate responses for the remaining `num_exchanges - 1` turns. Each turn appends to both `message_history` lists. Beta's overrides mean it always injects deep-thinking content when conversing.
5. The full transcript is logged to the `conversations` table.

Conversations are cleared from `message_history` during SLEEP.

Disabled by `--ablation-no-peers`.

### 7.5 KNOWLEDGE_SHARING

Two-part phase.

**Intra-agent promotion:** every agent's impulse entries are scanned. Any entry with `access_count ≥ 3` becomes a candidate for promotion — up to 2 are promoted per agent per day via `promote_to_deep` (moves the entry to `deep_thinking` with a new source of `"promoted_from_impulse"` and confidence 0.6). Similarly, every agent's top-5 deep entries for today's topic are scanned; any with `confidence ≥ 0.85 and access_count ≥ 2` become axiom candidates via `promote_to_axiom_candidate` — these are queued, not immediately accepted; Gamma's pipeline still gates them.

**Inter-agent smart sharing:** for every peer pair and every store type:

- For `deep_thinking` (top-3), `impulse` (top-2), and `axiom` (top-2): retrieve each agent's top relevant entries for today's topic (TF-IDF by topic for impulse/deep, keyword-match for axiom).
- A → B: if B's store already has a fingerprint-similar entry (`has_similar(content, threshold=0.5)`), skip; otherwise transfer.
- B → A: symmetric.

The transfer goes through `KnowledgeStore.transfer_entry`, which re-`add`s the content with `source = "transferred_from_<peer>"` and copies the relevant type-specific fields (reasoning chain, confidence, tags, proposed_by, validated_by). The dedup check still fires inside `add`, so content within threshold 0.7 of something the recipient already holds is silently refused at the lower level too.

Per-pair share/skip counts are logged; totals are printed.

Disabled by `--ablation-no-sharing`.

### 7.6 KNOWLEDGE_MANAGEMENT

Each agent runs its own `manage_knowledge(day, topic, conversations)` — this is the "end of the school day, organize your notebook" step. Each persona does its own thing (Alpha extracts impulses, Beta synthesizes deep insights, Gamma flags axiom candidates and investigation targets).

Then Gamma collects **every** pending axiom proposal from **every** agent (`get_and_clear_proposals` is called on all three), and runs each one through the three-stage validation pipeline (section 8).

Accepted axioms are also mirrored into the proposer's own axiom store — so if Beta proposes an axiom and Gamma accepts it, both Gamma's and Beta's axiom stores get it, tagged `validated_by = "gamma"` on the proposer's copy.

Finally, a `Knowledge Store Status` table prints per-agent fill percentages.

### 7.7 SLEEP

All writes for the sleep phase are wrapped in a single `db_logger.batch()` so the 9 snapshot inserts (3 agents × 3 stores) commit once instead of nine times. That matters on WAL-journaled SQLite, where each commit triggers an fsync.

Inside the batch:

- Clear each agent's `message_history`.
- On days divisible by 5 (and `day < num_days`, and `ABLATION_NO_CONSOLIDATION` is off): run `consolidate_knowledge` on every store with ≥ 10 entries.
- Persist every agent's three stores to `data/<agent>/{impulse,deep_thinking,axiom}.json`.
- Snapshot every store to the `snapshots` table with full JSON dump.

### 7.8 FINAL_TEST (last day only)

Runs only when `day == num_days`. See section 9.

---

## 8. The Axiom Validation Pipeline

Every axiom proposal — whether from Alpha's "this keeps coming up in impulse", Beta's `AXIOM_CANDIDATE:` line, or Gamma's own `AXIOM:` scan — goes through `GammaAgent.validate_axiom`.

```
Axiom proposal
   |
   v
+---------------------------+
| STAGE 1: Alpha boundary   |
|    "Where might this      |
|     break? Any edge       |
|     cases? Gut feel?"     |
+----------+----------------+
           |
           v
+----------+-----------------+
| STAGE 2: Beta counter-     |
|    example search          |
|    (sees Alpha's answer)   |
|    "Can you construct a    |
|     logical counter-       |
|     example? Does it       |
|     conflict with known    |
|     theorems?"             |
|    Emits WEAK or STRONG    |
+----------+-----------------+
           |
           v
+----------+-----------------+
| STAGE 3: Gamma final       |
|    ruling. Sees Alpha's    |
|    challenge, Beta's       |
|    challenge, its own      |
|    existing axioms.        |
|    First line: ACCEPT or   |
|    REJECT. Second line:    |
|    one-sentence justi-     |
|    fication.               |
+----------+-----------------+
           |
  +--------+--------+
  v                 v
ACCEPT           REJECT
  |                 |
  v                 v
Store in axiom      Sort into deep (if long)
(both proposer's    or impulse (if short)
and gamma's).       with rejection reasons
Log mutation        logged as reasoning_chain.
"axiom_accepted".   Log mutation
                    "axiom_rejected".
```

Disabled by `--ablation-no-axioms`, which auto-accepts every proposal as-is.

This pipeline is the single most expensive step per proposal — it's three LLM calls per axiom. Gamma is intentionally the rate-limiting step: a bad axiom poisons every subsequent retrieval that pulls from the axiom store, and axioms are injected with high priority on every question.

---

## 9. The Final Elimination Exam

Defined in `simulation/curriculum_test.py` (orchestration) and `simulation/evaluator.py` (question generation + scoring).

### 9.1 Question Generation

`Evaluator.generate_questions(topics_covered, rng)` produces exactly 30 questions:

- 10 **impulse** — quick-recall factual questions, 1–2 sentence expected answers.
- 10 **deep** — multi-step analytical questions requiring reasoning across concepts, 3–5 sentence expected answers.
- 10 **axiom** — true/false claims about fundamental principles that the respondent must evaluate and justify.

For each type, 10 topics are sampled from `topics_covered` (with cycling if fewer than 10 topics exist), and one question is generated per sampled topic. Temperature 0.7, max 150 tokens per question.

### 9.2 Test Execution

`CurriculumTest.run_full_comparison` does two passes.

**Pass 1 — every agent tested individually with knowledge.** For each question, `agent.answer_test_question(question, type, day, use_knowledge=True)` is called:

- Builds the agent's system prompt (with `"FINAL_TEST"` phase).
- Injects knowledge using `include_deep=True, use_bundles=True` — so the injection comes in as concept bundles (see 5.6) with deep entries included.
- Budget-truncates to `EXAM_KNOWLEDGE_BUDGET_WORDS = 4000`.
- Wraps the question in a "Humanity's Last Exam — Short Answer" template that instructs the model to think step by step and put the final answer on its own line as `ANSWER: ...`.
- Temperature 0.2, max 800 tokens.

Before pass 1 starts, `prepare_stores_for_exam` is called on every agent to pre-build the TF-IDF cache on all stores — otherwise the first retrieval per store would pay the build cost.

**Pass 2 — solo baseline (control group).** The same 30 questions are answered by one of the agents' underlying client with `use_knowledge=False`, meaning no JSON stores, no DB retrieval, no concept bundles, no prior learning — but the agent's personality system prompt is still present. This is "same model, cold, with a persona" — not a fully neutral baseline. If you need a fully neutral baseline you'd need to edit `_run_solo_baseline` to bypass `build_system_prompt` as well.

### 9.3 Scoring

Every answer is scored by `Evaluator.score_answer` — a separate LLM call at temperature 0.2, max 80 tokens. The grading system prompt is a strict 0–10 rubric:

| Score | Meaning |
|-------|---------|
| 1–2   | Wrong, irrelevant, or nonsensical |
| 3–4   | Partially correct but with major errors or critical omissions |
| 5–6   | Correct core idea but shallow, vague, or missing important details |
| 7–8   | Mostly correct and well-reasoned, minor gaps |
| 9     | Excellent — accurate, thorough, and well-structured |
| 10    | Perfect — flawless, comprehensive, deep mastery |

The rubric includes an explicit "BE DISCRIMINATING. Do NOT default to 7–8 for everything" instruction and reserves 9–10 for genuinely outstanding answers.

The response is expected as:
```
SCORE: <number>
REASONING: <one sentence>
```

`_extract_score` is defensive — it tries five patterns in order (`SCORE: X`, `X/10`, `X out of 10`, leading number, standalone number in first line) before retrying. If all retries fail to produce a parseable score, the answer gets 0 with the raw grader response as reasoning.

### 9.4 Pass Threshold and Survival

`PASS_THRESHOLD = 0.6`. Every agent whose total score ≥ 60% of the 300 possible points (30 × 10) is `SURVIVED`; everyone else is `ELIMINATED`. The outcome is both logged (every Q&A pair goes to `test_results`) and printed in a comparison table with delta-vs-baseline for each agent.

### 9.5 Caveat on "Solo Baseline"

The current solo baseline is not a minimal baseline in the academic sense — it still has the agent's persona system prompt. It's "same model, same persona, no accumulated knowledge". If you want a more rigorous control ("same model, no persona, no knowledge"), edit `_run_solo_baseline` in `simulation/curriculum_test.py` to construct a plain system prompt instead of calling `build_system_prompt`.

---

## 10. Project Structure

```
Trifecta/
  main.py                          # Entry point — parses args, builds agents, runs env
  config.py                        # All knobs: models, limits, phases, rate limits, ablations
  requirements.txt                 # openai, rich, python-dotenv, httpx
  run.sh                           # Shell wrapper: checks Python, sources .env, installs deps
  .env.example                     # OPENAI_API_KEY and OPENAI_MODEL template
  .gitignore                       # Ignores data/, analysis/, csv_export/, training_data/, *.db, *.jsonl
  README.md                        # You are here

  agents/
    __init__.py
    base_agent.py                  # BaseAgent: LLM calls, knowledge injection, rate limit, retry
    alpha.py                       # AlphaAgent: impulsive, pattern-matching
    beta.py                        # BetaAgent: deep analytical thinker
    gamma.py                       # GammaAgent: axiom guardian + 3-stage validation

  knowledge/
    __init__.py
    store.py                       # KnowledgeStore + DB retrieval + text utils + factory

  simulation/
    __init__.py
    environment.py                 # SimulationEnvironment: the day loop, all seven phases
    topic_generator.py             # TopicGenerator: dynamic PhD-level math topics
    question_oracle.py             # QuestionOracle: generates lectures, answers Q's
    communication.py               # CommunicationBus: peer exchanges, knowledge grounding
    curriculum.py                  # split_into_subtopics, build_lecture_prompt
    curriculum_test.py             # CurriculumTest: final test orchestration, baseline
    evaluator.py                   # Evaluator: question generation + 0-10 scoring

  sim_logging/
    __init__.py
    db.py                          # DatabaseLogger: SQLite schema, thread-safe writes, batching
    export.py                      # export_all: summary_stats, knowledge_flow, survival_report
    export_dataset.py              # export_dataset: SFT + DPO JSONL for fine-tuning

  data/                            # Runtime (gitignored)
    simulation.db                  #   The database. Everything is in here.
    alpha/ beta/ gamma/            #   Persisted JSON: impulse, deep_thinking, axiom

  analysis/                        # After simulation (gitignored)
    summary_stats.json
    knowledge_flow.json
    survival_report.md

  training_data/                   # After running export_dataset (gitignored)
    sft.jsonl
    dpo.jsonl
    dataset_manifest.json
```

---

## 11. Setup

### 11.1 Prerequisites

- Python 3.10 or newer (the codebase uses `str | None` PEP-604 unions).
- An OpenAI API key, or any OpenAI-compatible chat-completion endpoint (Azure, local vLLM/Ollama/LM Studio, NVIDIA NIM, etc.).

### 11.2 Install

```bash
git clone https://github.com/Imdevsup/trifecta.git
cd trifecta

python -m venv venv
source venv/bin/activate        # Linux/Mac
# or: venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

Dependencies: `openai>=1.0.0`, `rich>=13.0.0`, `python-dotenv>=1.0.0`, `httpx>=0.24.0`. Nothing else.

### 11.3 Configure

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

The model is used for *every* LLM call in the system — all three agents, the oracle, the evaluator, and the topic generator. `gpt-4o-mini` is the default and the calibrated choice; the knowledge injection budgets (2500 words normal, 4000 words exam) are tuned for its "lost in the middle" behavior.

For a non-OpenAI endpoint, edit `API_BASE` in `config.py`:

```python
API_BASE = "https://your-resource.openai.azure.com/openai/deployments/your-deployment"
# or
API_BASE = "http://localhost:11434/v1"        # Ollama
# or
API_BASE = "https://integrate.api.nvidia.com/v1"
```

---

## 12. Running the Simulation

### 12.1 Default Run (365 Days)

```bash
python main.py
```

Runs 365 days with seed 42 on `gpt-4o-mini`. The first 364 days are learning; day 365 is the elimination exam. Analysis files are exported to `analysis/` automatically at the end (or on Ctrl-C — there's a `try/finally` that persists stores and exports even on interrupt).

### 12.2 Short Run

```bash
python main.py --days 30 --seed 42
```

29 learning days plus the exam on day 30. Useful for iterating on agent behavior without paying for a full year.

### 12.3 Dry Run

```bash
python main.py --days 5 --dry-run
```

Runs the full pipeline without making a single API call. Every LLM call returns a placeholder bracketed string (`[Dry-run alpha: ask_q3 | day=3 phase=LEARNING]`). Useful for exercising the day loop, the DB writer, and the exporter end-to-end.

### 12.4 Resume From a Specific Day

```bash
python main.py --days 365 --start-day 180
```

Resumes from day 180 and runs through 365. When `--start-day > 1`, every agent calls `agent.load()` at startup, pulling its three stores from the JSON files in `data/<agent>/`. The `TopicGenerator` also calls `preload_seen_from_db(180)` to rebuild its `seen_titles` list and the `topics_covered` seed for the final test.

Caveat: the database will contain rows from both the original and resumed runs. If you need a clean slate, delete `data/simulation.db` before resuming.

### 12.5 Fast Mode

```bash
python main.py --days 365 --speed fast
```

Reduces peer exchanges from `(8, 12)` per pair to `(4, 6)`. Cuts runtime noticeably without touching learning quality.

### 12.6 Override the Model

```bash
python main.py --model-override gpt-4o
```

Overrides the model for all three agents. Oracle, evaluator, and topic generator still use the `MODEL` from `.env`/`config.py` (they don't consult `AGENT_CONFIG`), so `--model-override` affects agents only.

### 12.7 Override the Data Directory

```bash
python main.py --days 30 --data-dir data_experiment_1
```

Redirects `data/` and `analysis/` to `data_experiment_1/` and `data_experiment_1/analysis/`. Useful for running multiple experiments in parallel or A/B-testing ablations.

### 12.8 Verbose Logging

```bash
python main.py --log-level INFO
python main.py --log-level DEBUG
```

Default is `WARNING`. `INFO` shows retries and consolidation counts. `DEBUG` is very noisy.

### 12.9 Shell Wrapper (Linux/Mac)

```bash
chmod +x run.sh
./run.sh --days 30 --seed 42
```

`run.sh` checks for Python, sources `.env` safely (using `set -a; source .env; set +a` — this survives quoted values and values with spaces, unlike the old `xargs` trick), installs dependencies quietly, creates the data directories, and hands off to `main.py`.

### 12.10 All Command-Line Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--days N` | 365 | Number of days to simulate (last day is always the exam) |
| `--start-day N` | 1 | Day to resume from; loads each agent's stores from disk if > 1 |
| `--seed N` | 42 | Random seed — controls eviction order, exchange counts, question sampling |
| `--speed normal\|fast` | normal | `fast` drops peer exchanges to 4–6 per pair |
| `--model-override MODEL` | (from `.env`) | Overrides all three agent models (oracle/evaluator/generator unaffected) |
| `--dry-run` | off | Runs without any LLM calls |
| `--no-export` | off | Skips the post-simulation analysis export |
| `--data-dir PATH` | `./data` | Redirects data and analysis paths |
| `--log-level LEVEL` | WARNING | DEBUG / INFO / WARNING / ERROR |
| `--ablation-no-knowledge` | off | Agents answer without injected knowledge |
| `--ablation-no-peers` | off | Skips peer conversation phase |
| `--ablation-no-axioms` | off | Auto-accepts every axiom proposal |
| `--ablation-no-consolidation` | off | Skips the every-5-days consolidation |
| `--ablation-no-sharing` | off | Disables inter-agent knowledge transfer |

### 12.11 Before a Fresh Run

```bash
rm -rf data/ analysis/ csv_export/ training_data/
```

Otherwise the old `simulation.db` will accumulate rows from both runs and the old JSON stores will be loaded if you accidentally trigger a resume path.

---

## 13. Ablation Testing

Every component that contributes to the "smart" part of the simulation has an ablation flag that turns it off. Run a control experiment, then an ablation, then diff the test results.

| Flag | What it disables |
|------|------------------|
| `--ablation-no-knowledge` | Agents answer every question (including the final exam) with no injected knowledge — their own stores are invisible |
| `--ablation-no-peers` | Skips the peer conversation phase entirely |
| `--ablation-no-axioms` | Skips Gamma's three-stage validation — every proposal is auto-accepted |
| `--ablation-no-consolidation` | Skips the every-5-days clustering + merging pass |
| `--ablation-no-sharing` | Skips inter-agent knowledge transfer (each agent learns in isolation) |

Example — measuring the value of peer conversation:

```bash
rm -rf data_full data_no_peers
python main.py --days 30 --seed 42 --data-dir data_full
python main.py --days 30 --seed 42 --ablation-no-peers --data-dir data_no_peers
```

Then:

```bash
sqlite3 data_full/simulation.db "SELECT agent, SUM(score)/30.0 AS pct FROM test_results GROUP BY agent;"
sqlite3 data_no_peers/simulation.db "SELECT agent, SUM(score)/30.0 AS pct FROM test_results GROUP BY agent;"
```

Each ablation flag can be combined. `--ablation-no-peers --ablation-no-sharing` runs the hardest possible "solo learning" condition.

---

## 14. Modifying the Experiment

### 14.1 Knowledge Store Limits

Edit at the top of `config.py`. Current defaults are `400 / 1600 / 800` (sized for an 8-domain year). Useful alternative configurations:

```python
# Heavy forgetting pressure — deliberately crowd the stores so
# cross-domain eviction is intense and only the most-accessed
# knowledge survives the rotation.
IMPULSE_MAX_ENTRIES = 100
DEEP_MAX_ENTRIES = 400
AXIOM_MAX_ENTRIES = 200

# Minimal forgetting — measure learning quality across all 8 domains
# without memory churn. Memory footprint grows ~10x with these sizes.
IMPULSE_MAX_ENTRIES = 2000
DEEP_MAX_ENTRIES = 8000
AXIOM_MAX_ENTRIES = 3000

# Single-domain mode (if you rewrite topic_generator to only use one domain)
IMPULSE_MAX_ENTRIES = 150
DEEP_MAX_ENTRIES = 600
AXIOM_MAX_ENTRIES = 300
```

Per-entry token budgets (words, not real tokens):

```python
IMPULSE_MAX_TOKENS = 100    # ~2-3 sentences
DEEP_MAX_TOKENS = 500       # ~10-15 sentences
AXIOM_MAX_TOKENS = 250      # ~5-8 sentences
```

### 14.2 Model

Three ways, in increasing override priority:

1. `.env`:
   ```
   OPENAI_MODEL=gpt-4o
   ```
2. CLI: `python main.py --model-override gpt-4o` (agents only)
3. Per-agent in `config.py`:
   ```python
   AGENT_CONFIG = {
       "alpha": {"model": "gpt-4o-mini", "api_key": API_KEY},
       "beta":  {"model": "gpt-4o",      "api_key": API_KEY},
       "gamma": {"model": "gpt-4o",      "api_key": API_KEY},
   }
   ```

The per-model rate limiter lets different models run concurrently — three different models gives ~3× throughput on the rate-limit side.

### 14.3 Non-OpenAI Endpoint

Edit `API_BASE` in `config.py` — any OpenAI-compatible `/v1/chat/completions` endpoint works (Azure, Ollama, vLLM, LM Studio, NVIDIA NIM, Together, Groq, etc.).

### 14.4 Agent Personalities

Two things control each agent:

1. The system prompt string (`ALPHA_SYSTEM_PROMPT` / `BETA_SYSTEM_PROMPT` / `GAMMA_SYSTEM_PROMPT`) at the top of each agent file. Edit the text.
2. The `_default_store_answer` and `absorb_lecture` methods, which encode how the agent decides what to store and where. If you want an agent that always goes deep, rewrite its `_default_store_answer` to skip the LLM vote and unconditionally add to `deep_thinking`.

For a new persona from scratch — "Delta the Skeptic":

1. `cp agents/alpha.py agents/delta.py`
2. Rename the class (`DeltaAgent`) and system prompt constant.
3. Rewrite the prompt and the storage methods to match the new persona.
4. Register in `main.py`'s `agent_classes` dict.
5. Add `"delta"` to `AGENT_CONFIG` in `config.py` and extend `PEER_PAIRS`.
6. The runtime will create `data/delta/` automatically on first run.

### 14.5 Topic Generator Scope

The generator lives in `simulation/topic_generator.py`. Three things you can change:

1. **Which domains rotate.** Edit `DOMAIN_ORDER` at module scope — the list of domain keys in rotation order. Shortening it to one domain gives you single-domain mode; reordering changes which day-1 topic is produced. Remember to also prune `DOMAIN_DISPLAY_NAMES` and `_DOMAIN_PROMPTS` if you delete a key.
2. **The scope of any one domain.** Each domain's system prompt lives in `_DOMAIN_PROMPTS[<key>]`. Edit the "HARD SCOPE" bullets to whitelist different subfields, or edit the "DO NOT" block to forbid different things.
3. **The shared output format.** The title + numbered-subtopics format is shared across all domains via `_OUTPUT_FORMAT`. `simulation.curriculum.split_into_subtopics` expects a title on line 1 and numbered subtopics on subsequent lines — if you change the format, update the parser too.

To add a **ninth** domain:

1. Append its key to `DOMAIN_ORDER`.
2. Add its display name to `DOMAIN_DISPLAY_NAMES`.
3. Add its system prompt to `_DOMAIN_PROMPTS` following the existing structure (role statement → HARD SCOPE bullets → DO NOT block).
4. Consider bumping store capacities — another domain means more competition for the same slots.

### 14.6 Pass / Fail Threshold

```python
PASS_THRESHOLD = 0.6   # 60% — default
PASS_THRESHOLD = 0.7   # harder
PASS_THRESHOLD = 0.5   # easier
```

### 14.7 Peer / Learning Counts

```python
LEARNING_QUESTIONS_PER_AGENT = 5
PEER_EXCHANGE_RANGE = (8, 12)
PEER_EXCHANGE_RANGE_FAST = (4, 6)
```

### 14.8 Knowledge Injection Budgets

```python
DAILY_KNOWLEDGE_BUDGET_WORDS = 3000   # ~4K tokens — daily phases
EXAM_KNOWLEDGE_BUDGET_WORDS = 5000    # ~6K tokens — final exam
```

Bumped from the single-domain values (2500 / 4000) because cross-domain exam retrieval needs a bit more room — the injected context at test time can come from any of eight different curricula. Raise further on large-context models, lower on small-context models. The budget is applied post-injection by `_budget_knowledge_injection`, which does a word-level hard truncation.

### 14.9 Scoring Rubric

In `simulation/evaluator.py`, `score_answer` has the rubric inlined as a system prompt. Edit the text to be stricter, gentler, or to emphasize specific qualities (e.g., demand step-by-step reasoning).

### 14.10 Rate Limits

```python
MIN_CALL_INTERVAL_SECONDS = 1.0    # Per-model throttle
MAX_RETRIES = 10                   # Cap — was 999, kept from hanging on dead APIs
RETRY_BASE_DELAY = 3               # Exponential backoff base (multiplied by attempt)
RETRY_MAX_DELAY = 60               # Cap on any single retry wait
CLIENT_TIMEOUT_SECONDS = 120       # httpx connect/read timeout
```

The retry loop: `wait = min(RETRY_BASE_DELAY * (attempt + 1), RETRY_MAX_DELAY) + uniform(0, 2)` — linear backoff with jitter, not exponential despite the variable name. After `MAX_RETRIES = 10` attempts, the call returns `"[LLM unavailable for <agent> after 10 retries]"` (and the export_dataset filters these out automatically).

### 14.11 Eviction Weights

In `knowledge/store.py`, `_utility_score`:

```python
utility = (access_count * 0.4) + (confidence * 0.3) + (recency * 0.3)
```

- Raise `access_count` weight → protect frequently-used knowledge.
- Raise `confidence` weight → protect high-confidence knowledge.
- Raise `recency` weight → protect recent knowledge at the expense of fundamentals.

### 14.12 Deduplication Threshold

```python
class KnowledgeStore:
    DEDUP_THRESHOLD = 0.7     # Jaccard; raise to accept more near-duplicates
    CLUSTER_SIMILARITY = 0.35 # TF-IDF cosine; raise to consolidate less aggressively
```

---

## 15. Dataset Export (SFT + DPO)

The `sim_logging/export_dataset.py` module reads the simulation DB and emits fine-tuning-ready datasets. This is a post-processing step — it doesn't need the simulation running.

### 15.1 What It Produces

Three files into the output directory (default `training_data/`):

- **`sft.jsonl`** — supervised fine-tuning data in OpenAI chat format:
  ```json
  {"messages": [{"role": "system", "content": "..."},
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}]}
  ```
- **`dpo.jsonl`** — preference data in TRL / axolotl format:
  ```json
  {"prompt": "...", "chosen": "...", "rejected": "...",
   "chosen_score": 9.0, "rejected_score": 4.0,
   "chosen_agent": "gamma", "rejected_agent": "alpha"}
  ```
- **`dataset_manifest.json`** — provenance: source DB path, generation time, all filter parameters, and per-source counts.

### 15.2 Sources

The DB logger stores every prompt and response **untruncated** (the `*_preview` column names are historical — they keep the full text). That lets the exporter train directly on real content rather than summaries.

Three sources, in priority order:

1. **`test_results`** → SFT. Question + answer + score. Only rows with `score ≥ min_score` (default 7.0) are kept. **Highest quality** because the grader filter catches wrong answers.
2. **`test_results`** → DPO. Per-question: best agent's answer vs worst agent's answer, if the score gap is ≥ `dpo_gap` (default 3.0). Each of the 30 final-test questions can produce up to one DPO pair.
3. **`interactions`** (opt-in via `--include-interactions`) → SFT. Oracle answers (`action LIKE 'answer_for_%'`) and oracle lectures (`action LIKE 'lecture_%'`). The lectures are the **richest** long-form content — multi-paragraph expert writeups on every curriculum topic.
4. **`conversations`** (opt-in via `--include-conversations`) → multi-turn SFT. Each peer conversation becomes one training example, with the first speaker mapped to `user` role and the other to `assistant`. Truncated at the first unclean turn, so a partially-broken transcript still contributes its clean prefix.

### 15.3 Quality Filters

`_is_clean` rejects any text that:

- Is empty or < 20 characters.
- Matches any of the `[LLM unavailable`, `[Dry-run`, `[Evaluator unavailable`, `[Oracle unavailable`, `[Gamma unavailable` error-placeholder prefixes.

These never end up in the training data. Counts of dropped examples are reported in the manifest and on stdout.

### 15.4 Usage

```bash
# Minimal — SFT from final exam only, score >= 7.0, DPO gap >= 3.0
python -m sim_logging.export_dataset

# High-quality only, include lectures as extra SFT content
python -m sim_logging.export_dataset --min-score 8 --include-interactions

# Everything, including peer conversations
python -m sim_logging.export_dataset \
    --include-interactions --include-conversations \
    --min-score 6 --dpo-gap 2

# Dry-run — counts only, no files written
python -m sim_logging.export_dataset --include-interactions --dry-run

# Custom DB and output
python -m sim_logging.export_dataset \
    --db data_experiment/simulation.db \
    --out experiment_dataset/

# Custom system prompt on every SFT record
python -m sim_logging.export_dataset \
    --system-prompt "You are a graduate-level math tutor. Answer rigorously."
```

### 15.5 CLI Flags

| Flag | Default | Meaning |
|---|---|---|
| `--db PATH` | `config.LOG_DB_PATH` | Path to the simulation database |
| `--out PATH` | `training_data/` | Output directory |
| `--min-score FLOAT` | 7.0 | Minimum grader score for SFT inclusion from `test_results` |
| `--dpo-gap FLOAT` | 3.0 | Minimum score gap between chosen and rejected for a DPO pair |
| `--include-conversations` | off | Add peer conversations as multi-turn SFT (lower quality) |
| `--include-interactions` | off | Add oracle Q&A and full lectures as SFT |
| `--system-prompt STR` | generic tutor prompt | System message prepended to every SFT example |
| `--dry-run` | off | Count without writing |

### 15.6 Example Output

```
Exported:
  SFT total:              3984
    from test_results:    118          (30 Q x 4 agents @ score >= 7, a few dropped)
    from oracle Q&A:      1820
    from lectures:        2046
  DPO pairs:              26           (of 30 questions, 4 had insufficient gap or identical answers)
  Dropped — error/placeholder: 3
  Dropped — too short:         0

  Output: /path/to/training_data/
    sft.jsonl              (3984 records)
    dpo.jsonl              (26 records)
    dataset_manifest.json
```

The count for `from test_results` is 4 × 30 = 120 max (4 test-takers including baseline, 30 questions each), assuming all answers pass the score gate. Lectures: one per subtopic per day — with ~6 subtopics/day × 364 learning days on a full run, the ceiling is ~2200 lectures **distributed across all eight domains**. Oracle Q&A: 5 follow-up questions × 3 agents × 364 days = 5460 potential records, pruned by the error / short-text filters.

Because the curriculum rotates, the exported SFT is naturally multi-domain — roughly one-eighth of every source type is drawn from each of the eight curricula, all graded to the same quality bar. That's the "more varied datasets" benefit: a single export produces training data spanning math, physics, formal methods, TCS, biology, philosophy, finance, and linguistics without any post-processing.

---

## 16. Database Schema

Everything runs through `sim_logging/db.py`. The database is SQLite in WAL mode, thread-safe via a reentrant lock around every write. All writes can be batched inside a `with db_logger.batch():` block — a nest-aware refcount means the outermost batch is the one that commits.

The column names `prompt_preview`, `response_preview`, `content_preview`, and `deleted_content_preview` are historical. They store the **full untruncated text**. Truncation was removed so the database could be a faithful record of every LLM call, every lecture, and every knowledge mutation — without which the fine-tuning export pipeline wouldn't be viable.

### 16.1 `interactions`

Every LLM call. Includes topic-generator calls (`agent = 'topic_generator'`), oracle lectures and answers (`agent = 'oracle'`), agent Q&A and conversation replies, WAKE briefings (no tokens — just text), and smart-share summaries.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto |
| `day` | INTEGER | Simulation day |
| `phase` | TEXT | WAKE / TEACHING / LEARNING / PEER_CONVERSATION / KNOWLEDGE_SHARING / KNOWLEDGE_MANAGEMENT / SLEEP / FINAL_TEST |
| `agent` | TEXT | `alpha` / `beta` / `gamma` / `oracle` / `topic_generator` |
| `action` | TEXT | e.g. `ask_q3`, `reply_beta`, `lecture_<subtopic>`, `answer_for_alpha`, `generate_topic_<domain>` (e.g. `generate_topic_theoretical_physics`), `axiom_boundary_gamma` |
| `prompt_preview` | TEXT | Full system/user prompt |
| `response_preview` | TEXT | Full LLM response |
| `tokens_in` | INTEGER | From response.usage |
| `tokens_out` | INTEGER | From response.usage |
| `latency_ms` | INTEGER | Round-trip wall-clock |
| `model` | TEXT | Model string |
| `timestamp` | TEXT | ISO 8601 UTC |

Indices: `(agent, day)`, `(day)`, `(phase)`.

### 16.2 `knowledge_mutations`

Every store change.

| Column | Type | Description |
|---|---|---|
| `day` | INTEGER | When the mutation occurred |
| `agent` | TEXT | Which agent's store changed |
| `store_type` | TEXT | `impulse` / `deep_thinking` / `axiom` |
| `mutation_type` | TEXT | `add` / `discard` / `promote` / `demote` / `axiom_accepted` / `axiom_rejected` |
| `entry_id` | TEXT | UUID of the affected entry |
| `content_preview` | TEXT | Full entry content |

Index: `(agent, day)`.

### 16.3 `conversations`

Full peer conversation transcripts.

| Column | Type | Description |
|---|---|---|
| `day` | INTEGER | Simulation day |
| `phase` | TEXT | Always `PEER_CONVERSATION` |
| `agent_a`, `agent_b` | TEXT | The two participants |
| `topic` | TEXT | Day's topic string |
| `transcript_json` | TEXT | `[{"sender": "alpha", "content": "..."}, ...]` as JSON |
| `num_exchanges` | INTEGER | Turn count |

Indices: `(day)`, `(agent_a, agent_b)`.

### 16.4 `snapshots`

Full per-day per-store state dump. Written inside the SLEEP batch.

| Column | Type | Description |
|---|---|---|
| `day` | INTEGER | Day of snapshot |
| `agent` | TEXT | Agent name |
| `store_type` | TEXT | Store type |
| `entry_count` | INTEGER | Number of entries at day's end |
| `entries_json` | TEXT | Full deep-copied entry list as JSON |

Index: `(agent, day)`. Snapshots are the single largest source of DB growth — a year-long run with a 600-entry deep_thinking store produces ~365 × 3 × 3 × (up to 600 entries) JSON dumps. Expect a multi-GB `simulation.db` on a full run.

### 16.5 `test_results`

Final exam answers and scores.

| Column | Type | Description |
|---|---|---|
| `agent` | TEXT | `alpha` / `beta` / `gamma` / `solo_baseline` |
| `question_number` | INTEGER | 1–30 |
| `question_type` | TEXT | `impulse` / `deep` / `axiom` |
| `question` | TEXT | Full question |
| `answer` | TEXT | Full answer |
| `score` | REAL | 0.0–10.0 |
| `score_reasoning` | TEXT | Grader's one-sentence justification |

Index: `(agent)`.

### 16.6 `overflow_events`

Every silent eviction.

| Column | Type | Description |
|---|---|---|
| `day` | INTEGER | When the deletion occurred |
| `agent` | TEXT | Which agent lost knowledge |
| `store_type` | TEXT | Which store overflowed |
| `deleted_entry_id` | TEXT | UUID of the evicted entry |
| `deleted_content_preview` | TEXT | Full content of the deleted entry |
| `reason` | TEXT | Default `capacity_overflow` |

### 16.7 Thread Safety and Batching

`DatabaseLogger` is constructed with `check_same_thread=False` and every public write goes through `_write_lock` (a reentrant lock). The writer holds the lock while executing the SQL *and* while committing, so there's no torn-write race even though one connection is shared across threads.

`with db_logger.batch():` defers `conn.commit()` until the outermost context exits. `_batch_depth` is a refcount — only the outermost batch commits. The sleep phase uses this to batch the 9 per-day snapshot inserts into a single commit.

---

## 17. Analysis Output Files

Generated by `sim_logging/export.py` at the end of a run (unless `--no-export`).

### 17.1 `analysis/summary_stats.json`

Per-agent totals + growth curves:

```json
{
  "totals": {"interactions": 18432, "overflow_events": 214},
  "agents": {
    "alpha": {
      "total_interactions": 5844,
      "tokens_in": 4812003,
      "tokens_out": 1920551,
      "total_tokens": 6732554,
      "overflow_events": 89,
      "overflow_by_store": {"impulse": 76, "deep_thinking": 13, "axiom": 0},
      "final_store_sizes": {"impulse": 150, "deep_thinking": 412, "axiom": 27},
      "test_score": 218.5,
      "test_percentage": 0.728
    },
    "beta": { ... },
    "gamma": { ... }
  },
  "knowledge_growth_curves": {
    "alpha_impulse": [{"day": 1, "count": 14}, {"day": 2, "count": 28}, ...],
    "alpha_deep_thinking": [...],
    ...
  }
}
```

### 17.2 `analysis/knowledge_flow.json`

A flat list of knowledge-flow events, Sankey-diagram-ready:

```json
{
  "flows": [
    {"from": "alpha", "to": "alpha_impulse", "type": "add", "day": 1},
    {"from": "alpha", "to": "axiom_validation", "type": "axiom_accepted", "day": 3},
    {"from": "alpha_deep", "to": "alpha_axiom", "type": "promote", "day": 11},
    ...
  ],
  "total": 14892
}
```

### 17.3 `analysis/survival_report.md`

A narrative markdown report with per-agent scores, by-question-type breakdowns, overflow counts per store, and a short observations block. Good for a human-readable headline.

---

## 18. Querying the Database

`data/simulation.db` is regular SQLite 3. Every query below is copy-paste-runnable:

```bash
# Total LLM calls per agent
sqlite3 data/simulation.db "
  SELECT agent, COUNT(*) AS calls, SUM(tokens_in) AS in_tok, SUM(tokens_out) AS out_tok
  FROM interactions GROUP BY agent ORDER BY calls DESC;
"

# Final test scores
sqlite3 data/simulation.db "
  SELECT agent, COUNT(*) AS q, ROUND(SUM(score), 1) AS total,
         ROUND(SUM(score) / (COUNT(*) * 10.0) * 100, 1) AS pct
  FROM test_results GROUP BY agent;
"

# Scores by question type
sqlite3 data/simulation.db "
  SELECT agent, question_type, ROUND(AVG(score), 2) AS avg
  FROM test_results GROUP BY agent, question_type ORDER BY agent, question_type;
"

# Per-store eviction counts
sqlite3 data/simulation.db "
  SELECT agent, store_type, COUNT(*) AS evictions
  FROM overflow_events GROUP BY agent, store_type ORDER BY evictions DESC;
"

# Axiom accept/reject ratio
sqlite3 data/simulation.db "
  SELECT mutation_type, COUNT(*) FROM knowledge_mutations
  WHERE mutation_type IN ('axiom_accepted', 'axiom_rejected')
  GROUP BY mutation_type;
"

# Store growth over time
sqlite3 data/simulation.db "
  SELECT day, agent, store_type, entry_count
  FROM snapshots ORDER BY day, agent, store_type;
"

# Per-day peer exchange volume
sqlite3 data/simulation.db "
  SELECT day, agent_a, agent_b, num_exchanges FROM conversations ORDER BY day;
"

# What got silently deleted on a specific day
sqlite3 data/simulation.db "
  SELECT agent, store_type, deleted_content_preview
  FROM overflow_events WHERE day = 37;
"

# Every topic the generator produced (all 8 domains)
sqlite3 data/simulation.db "
  SELECT day, action, substr(response_preview, 1, 80) AS title
  FROM interactions
  WHERE agent = 'topic_generator' AND action LIKE 'generate_topic_%'
  ORDER BY day;
"

# Topics by domain
sqlite3 data/simulation.db "
  SELECT replace(action, 'generate_topic_', '') AS domain, COUNT(*) AS n_topics
  FROM interactions
  WHERE agent = 'topic_generator' AND action LIKE 'generate_topic_%'
  GROUP BY domain ORDER BY n_topics DESC;
"

# Failed topic generations
sqlite3 data/simulation.db "
  SELECT day, action, substr(response_preview, 1, 80)
  FROM interactions
  WHERE agent = 'topic_generator' AND action LIKE '%_FAILED'
  ORDER BY day;
"

# Lecture count per day
sqlite3 data/simulation.db "
  SELECT day, COUNT(*) AS lectures
  FROM interactions
  WHERE agent = 'oracle' AND action LIKE 'lecture_%'
  GROUP BY day ORDER BY day;
"

# Total tokens burned per day
sqlite3 data/simulation.db "
  SELECT day, SUM(tokens_in + tokens_out) AS tokens
  FROM interactions GROUP BY day ORDER BY day;
"
```

### Reading the JSON Stores Directly

```bash
python -c "import json; d=json.load(open('data/alpha/impulse.json')); print(len(d))"

python -c "
import json
axioms = json.load(open('data/gamma/axiom.json'))
for a in axioms:
    print(f'Day {a[\"created_day\"]} ({a[\"proposed_by\"]}): {a[\"content\"][:120]}')
"
```

---

## 19. Design Decisions

### 19.1 Why no vector DB?

Custom TF-IDF (unigrams + bigrams, smoothed IDF, sparse dict vectors) in ~50 lines of `knowledge/store.py`. No scikit-learn, no numpy, no FAISS, no embedding API calls. At the store sizes used (≤ 600 entries), TF-IDF cosine works well and stays zero-dependency.

### 19.2 Why word-count tokenization?

`len(content.split())` is used for the per-entry token budget. This is deliberately simple and tokenizer-agnostic — what matters is the *relative* ordering (impulse < axiom < deep) and consistent enforcement, not alignment with any specific model's tokenizer.

### 19.3 Why synchronous single-threaded?

Deterministic phase ordering, reproducible structural decisions given a seed, and zero race conditions on the knowledge stores. Performance is bounded by the LLM API — multi-threading against a single API key doesn't actually help.

The *logger* is thread-safe so that third parties (research scripts, extension code) can write concurrently, but the simulation itself runs in one thread.

### 19.4 Why silent eviction?

When the impulse store overflows, the lowest-utility entry is deleted and the agent is not told. It discovers the loss only through failed recall. This is a core simulation mechanic modeling how constrained memory forces prioritization, not a bug.

### 19.5 Why three personas from one base model?

The system prompt is the steering lever. Three agents running the same gpt-4o-mini produce measurably different storage distributions, peer-conversation content, and test performance — the prompt-induced persona is *real* behavioral variance, not cosmetic.

### 19.6 Reproducibility caveats

The random seed controls the eviction victim when utility scores tie, the peer-exchange counts, the question topic sampling at test time, and the retry jitter. **LLM outputs are not seeded.** Two runs with the same seed will follow the same structural path but produce different generated content — the topic generator picks different topics, the oracle writes different lectures, and scores will vary.

### 19.7 Why max_retries capped at 10?

Originally 999 ("effectively unlimited — never give up"). Replaced with 10 because a truly dead API should surface as a hard failure rather than hanging for hours — the `[LLM unavailable...]` placeholder is logged, the exporter filters it out, and the simulation continues. 10 attempts × up to 60s each = 10 minutes max per call, which is long enough to ride out any transient spike.

### 19.8 Why DEFAULT_DAYS = 365?

Because the topic generator is unbounded and the point of dynamic topics is to enable long-run experiments. If you don't want a year, pass `--days N`. The default picks the most ambitious plausible run so "just run it with defaults" exercises the scaling behavior.

### 19.9 Why eight domains, not more or fewer?

Enough for the curriculum to be meaningfully broad — spanning the different shapes of rigorous reasoning (algebraic, physical, logical, biological, philosophical, stochastic, linguistic) that LLMs handle poorly — without diluting any single domain to under ~45 scheduled days in a standard year-long run. The eight were picked for independent evidence of LLM weakness (precision errors, hallucinated theorems, multi-step derivation failures) and for minimal overlap among each other — knowing mathematics helps a little with theoretical physics but very little with molecular biology or theoretical linguistics.

Rotation is deterministic (day-indexed modulo 8) rather than randomized so that reproducibility is preserved and because round-robin enforces equal per-domain coverage. If you want a different distribution — say, twice the math density — either expand `DOMAIN_ORDER` with duplicates (`["mathematics", "mathematics", "theoretical_physics", ...]`) or rewrite `_domain_for_day` to sample from a weighted distribution seeded by the run's RNG.

---

## 20. Cost and Runtime

The 8-domain curriculum does **not** change per-day call count — every day runs the same phases with the same number of lectures, Q&A, and peer exchanges regardless of which domain is active. What changes is the *variety* of content produced. So the per-day cost structure is unchanged from the single-domain version:

Rough per-day API footprint, on `gpt-4o-mini`, normal speed:

- Topic generation: 1 call (~800 tokens out).
- Teaching: ~6 subtopics × 1 oracle lecture × ~1500 tokens = ~9K tokens of lecture content. Plus 3 agents × 6 lectures × 1 absorption call each = 18 calls.
- Learning Q&A: 3 agents × 5 questions × 2 calls (question + answer) + 3 agents × 5 × 1 store decision = 45 calls.
- Peer conversation: 3 pairs × ~10 exchanges = ~30 calls.
- Knowledge management: 3 agents × 1 call + axiom validation at ~3 calls per proposal × N proposals per day ≈ 10–30 calls.
- Sleep: 0 API calls (pure local work + DB writes).

Order of magnitude: **~100–150 LLM calls per day**, **~300–500K tokens per day** combined in/out, **per-day cost ~$0.10–0.25 on gpt-4o-mini**.

Scaling to runs:

| Days | ~API calls | ~Tokens | Est. cost (`gpt-4o-mini`) | Est. wall-clock | Per-domain days |
|---|---|---|---|---|---|
| 8 | ~1K | ~3M | ~$1 | 40 min – 1.5 hrs | 1 each (one loop) |
| 32 | ~3.5K | ~12M | $3–8 | 2–5 hours | 4 each |
| 80 | ~8K | ~26M | $8–20 | 5–13 hours | 10 each |
| 168 | ~17K | ~55M | $18–40 | 10–25 hours | 21 each |
| **365** | ~40K | ~120–180M | **$40–100** | 24–60 hours | **~45–46 each** |

Wall-clock is bounded by per-model rate limiting (`MIN_CALL_INTERVAL_SECONDS = 1.0`) more than by network throughput. The per-model lock is the ceiling: one call per model per second. Give each agent a different model and the ceiling is 3×.

`--speed fast` drops peer exchanges roughly in half, which cuts per-day calls by ~15%.

Using `gpt-4o` or frontier models: cost increases 10–50×, but the lectures are better, the scoring is more discriminating, and the knowledge quality is higher.

**Storage** scales with the new capacities: a full 365-day 8-domain run will produce a multi-GB `simulation.db` (the daily snapshots dominate — 3 agents × 3 stores × 365 days × up to 1600-entry deep dumps). If you don't need snapshots for analysis, the simplest way to keep the DB small is to comment out the `log_snapshot` calls in `_sleep_phase` — everything else is compact. If you want the snapshots but not at full resolution, only snapshot every Nth day.

---

## 21. Troubleshooting

### "No API key configured"

`.env` must exist in the project root with `OPENAI_API_KEY=sk-...`. The key is loaded at import time by `config.py` via `python-dotenv`. Re-export from the shell doesn't help if `.env` is missing.

### Rate-limit errors

The simulation has its own retry loop — `MAX_RETRIES=10` with linear backoff up to 60s + jitter. If you're getting repeated 429s, raise `MIN_CALL_INTERVAL_SECONDS` in `config.py` (try 2.0 or 3.0).

### Simulation crashed mid-run

Stores are persisted at the end of every day in SLEEP. Use `--start-day N` to resume from the last completed day. The DB will contain rows from both runs — filter by `day >= N` when querying if you want just the resumed portion.

### Results look wrong after re-running

`data/simulation.db` is additive across runs. Either `rm -rf data/ analysis/` before a fresh run, or use `--data-dir` to isolate.

### Memory grows too large

The year-long run with scaled-up stores can hit several GB of RAM — each agent keeps 150 + 600 + 300 entries in memory plus full message histories during conversations. If you hit memory pressure, cut capacities in `config.py` or cut `--days`.

### "Topic generator: response too short" / response missing subtopics

The model sometimes returns a one-line title with no numbered subtopics, or a blurb shorter than 100 characters. The generator retries. If all 10 retries fail, a minimal fallback topic is returned and the day continues — check the `interactions` table for `action = 'generate_topic_FAILED'` rows to spot bad days.

### Agent countdown says "355 days left" when I ran `--days 10`

Expected. The individual agent system prompts reference `config.DEFAULT_DAYS = 365`, not the CLI `--days` override. The console briefing in WAKE *does* respect the override. If you need the agent-side countdown to match, either change `DEFAULT_DAYS` in `config.py` or edit the three `build_system_prompt` methods to use `num_days` instead of `config.DEFAULT_DAYS`.

### Evaluator returns score = 0.0 with a full reasoning string

`_extract_score` tries five patterns to parse a number. If none match after `MAX_RETRIES` attempts, it gives up with 0.0 and the raw response as reasoning. Usually means the grader is rambling instead of following the `SCORE: <number>` format — try lowering `temperature` in `score_answer` or tightening the rubric.

### `export_dataset` reports 0 records

Either the simulation hasn't run the final test (no `test_results` rows) or `--min-score` is too strict. Try `--min-score 5 --dry-run` to see what's available.

---

## 22. License

**Copyright (c) 2026 Imdevsup. All Rights Reserved.**

This repository is published for viewing and reference only. No license is
granted to copy, clone (beyond what a web browser does when rendering the
page), modify, redistribute, train on, or otherwise use this code or its
outputs in any project, product, dataset, or research work. See [LICENSE](LICENSE)
for the full notice.

For licensing inquiries, contact the copyright holder before using any
portion of this work.

---

*If you're reading this in a PR review and something here doesn't match the code, the code is authoritative — open an issue.*
