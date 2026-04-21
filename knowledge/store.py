"""
Knowledge Store — Manages impulse, deep_thinking, and axiom memory per agent.
v6: Deduplication on add, clean entry validation, improved retrieval with
both n-gram TF-IDF and DB interaction history as retrieval sources.
"""

import json
import math
import uuid
import copy
import re
import sqlite3
from pathlib import Path
from typing import Optional

import config


# --- Text utilities ---

def tokenize(text: str) -> list[str]:
    """Lowercase, tokenize preserving internal hyphens and apostrophes,
    then filter stopwords and short tokens. Keeps 'einstein's' and
    'first-order' as single tokens."""
    words = re.findall(r"[a-z0-9]+(?:['-][a-z0-9]+)*", text.lower())
    return [w for w in words if len(w) > 1 and w not in config.STOPWORDS]


def bigrams(tokens: list[str]) -> list[str]:
    """Generate bigrams from token list for better phrase matching."""
    return [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]


def word_count_tokens(text: str) -> int:
    return len(text.split())


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    words = text.split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[:max_tokens])


def clean_content(text: str) -> str:
    """Strip chain-of-thought dumps, internal reasoning artifacts, and meta-noise."""
    # Remove lines that are clearly internal model reasoning
    lines = text.split("\n")
    clean_lines = []
    skip = False
    for line in lines:
        lower = line.strip().lower()
        # Skip chain-of-thought markers
        if any(marker in lower for marker in [
            "the user wants me to",
            "i need to analyze",
            "let me choose",
            "key constraints:",
            "looking at the topics",
            "good candidates:",
            "option:",
            "or:",
            "i need to identify",
        ]):
            skip = True
            continue
        if skip and line.strip().startswith("-"):
            continue  # skip bullet lists in reasoning blocks
        if skip and not line.strip():
            skip = False
            continue
        skip = False
        clean_lines.append(line)

    result = "\n".join(clean_lines).strip()
    # If cleaning removed everything, return original
    return result if result else text.strip()


def content_fingerprint(text: str) -> str:
    """Generate a normalized fingerprint for dedup — lowercase, stripped, key words only."""
    tokens = sorted(set(tokenize(text)))
    return " ".join(tokens[:30])


def similarity_score(fp1: str, fp2: str) -> float:
    """Jaccard similarity between two fingerprints."""
    s1 = set(fp1.split())
    s2 = set(fp2.split())
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


class KnowledgeStore:
    """A single knowledge store (impulse, deep_thinking, or axiom) for one agent."""

    DEDUP_THRESHOLD = 0.7  # Entries with Jaccard >= this are considered duplicates
    CLUSTER_SIMILARITY = 0.35  # Entries with TF-IDF cosine >= this are clustered together

    def __init__(
        self,
        agent_name: str,
        store_type: str,
        max_entries: int,
        max_tokens: int,
        rng,
        db_logger=None,
    ):
        self.agent_name = agent_name
        self.store_type = store_type
        self.max_entries = max_entries
        self.max_tokens = max_tokens
        self.rng = rng
        self.db_logger = db_logger
        self.entries: list[dict] = []
        self._tfidf_cache = None
        self._fingerprints: dict[str, str] = {}  # entry_id -> fingerprint

    def _invalidate_cache(self):
        self._tfidf_cache = None

    def _is_duplicate(self, content: str) -> bool:
        """Check if content is substantially similar to an existing entry."""
        return self.has_similar(content, threshold=self.DEDUP_THRESHOLD)

    def has_similar(self, content: str, threshold: float = 0.5) -> bool:
        """Public helper: does the store already contain an entry whose
        fingerprint Jaccard-similarity to content meets the threshold?
        Used by peer knowledge sharing to skip transfers of already-known facts."""
        new_fp = content_fingerprint(content)
        for existing_fp in self._fingerprints.values():
            if similarity_score(new_fp, existing_fp) >= threshold:
                return True
        return False

    def add(
        self,
        content: str,
        day: int,
        source: str = "self",
        topic: str = "",
        reasoning_chain: str = "",
        confidence: float = 0.5,
        proposed_by: str = "",
        validated_by: str = "",
        tags: list[str] | None = None,
    ) -> tuple[str, Optional[dict]]:
        """Add an entry with deduplication and content cleaning."""
        # Clean the content
        content = clean_content(content)
        truncated = truncate_to_tokens(content, self.max_tokens)

        # Skip if too short or empty
        if len(truncated.strip()) < 20:
            return "", None

        # Skip if duplicate
        if self._is_duplicate(truncated):
            return "", None

        keywords = tokenize(truncated)

        deleted_entry = None
        if len(self.entries) >= self.max_entries:
            deleted_entry = self._evict(day)

        entry = {
            "id": str(uuid.uuid4()),
            "content": truncated,
            "tokens": word_count_tokens(truncated),
            "created_day": day,
            "access_count": 0,
            "source": source,
            "topic": topic,
            "keywords": keywords,
        }

        if self.store_type == "deep_thinking":
            entry["reasoning_chain"] = reasoning_chain
            entry["confidence"] = confidence
        elif self.store_type == "axiom":
            entry["proposed_by"] = proposed_by or source
            entry["validated_by"] = validated_by
            entry["tags"] = tags or keywords[:10]
            entry["challenges_survived"] = 0

        self.entries.append(entry)
        self._fingerprints[entry["id"]] = content_fingerprint(truncated)
        self._invalidate_cache()

        if self.db_logger:
            self.db_logger.log_mutation(
                day=day, agent=self.agent_name, store_type=self.store_type,
                mutation_type="add", entry_id=entry["id"],
                content_preview=truncated,
            )

        return entry["id"], deleted_entry

    def _utility_score(self, entry: dict, day: int) -> float:
        """Calculate utility score for eviction. Lower = more likely to evict.
        Combines: access frequency, confidence, and recency."""
        access = entry.get("access_count", 0)
        confidence = entry.get("confidence", 0.5)
        age = max(1, day - entry.get("created_day", 0))
        recency = 1.0 / age  # More recent = higher score

        # Weighted combination
        return (access * 0.4) + (confidence * 0.3) + (recency * 0.3)

    def _evict(self, day: int) -> dict:
        """Evict the entry with the lowest utility score (least accessed, oldest, lowest confidence)."""
        victim = min(self.entries, key=lambda e: self._utility_score(e, day))

        self.entries.remove(victim)
        self._fingerprints.pop(victim["id"], None)
        self._invalidate_cache()

        if self.db_logger:
            self.db_logger.log_overflow(
                day=day, agent=self.agent_name, store_type=self.store_type,
                deleted_entry_id=victim["id"],
                deleted_content_preview=victim["content"],
            )
        return victim

    def prepare_for_retrieval(self):
        """Pre-compute TF-IDF cache for fast batch retrieval."""
        self._build_tfidf_cache()
        # Rebuild fingerprints if needed (e.g. after load from disk)
        if not self._fingerprints:
            for entry in self.entries:
                self._fingerprints[entry["id"]] = content_fingerprint(entry["content"])

    def _build_tfidf_cache(self):
        """Pre-compute sparse TF-IDF vectors with unigrams + bigrams for better phrase matching."""
        n = len(self.entries)
        if n == 0:
            self._tfidf_cache = None
            return

        # Use unigrams + bigrams for richer matching
        doc_tokens = []
        for entry in self.entries:
            unigrams = entry["keywords"]
            bgs = bigrams(unigrams)
            doc_tokens.append(unigrams + bgs)

        # Document frequency
        df = {}
        for dt in doc_tokens:
            for t in set(dt):
                df[t] = df.get(t, 0) + 1

        # IDF (smoothed)
        idf = {}
        for t, freq in df.items():
            idf[t] = math.log((n + 1) / (1 + freq)) + 1

        # Sparse document vectors
        doc_vecs = []
        for dt in doc_tokens:
            if not dt:
                doc_vecs.append(({}, 0.0))
                continue
            doc_tf = {}
            for t in dt:
                doc_tf[t] = doc_tf.get(t, 0) + 1
            d_len = len(dt)
            sparse = {}
            for t, count in doc_tf.items():
                w = (count / d_len) * idf.get(t, 0)
                if w > 0:
                    sparse[t] = w
            mag = math.sqrt(sum(v * v for v in sparse.values())) if sparse else 0.0
            doc_vecs.append((sparse, mag))

        self._tfidf_cache = (n, idf, doc_vecs)

    def retrieve_by_topic(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve entries by TF-IDF cosine similarity (unigrams + bigrams)."""
        if not self.entries:
            return []

        query_unigrams = tokenize(query)
        if not query_unigrams:
            return self.entries[:top_k]

        query_tokens = query_unigrams + bigrams(query_unigrams)

        if self._tfidf_cache is None or self._tfidf_cache[0] != len(self.entries):
            self._build_tfidf_cache()

        n, idf, doc_vecs = self._tfidf_cache

        # Sparse query vector
        query_tf = {}
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0) + 1
        q_len = len(query_tokens)

        query_sparse = {}
        for t, count in query_tf.items():
            w = (count / q_len) * idf.get(t, 0)
            if w and w > 0:
                query_sparse[t] = w

        mag_q = math.sqrt(sum(v * v for v in query_sparse.values())) if query_sparse else 0.0
        if mag_q == 0:
            return self.entries[:top_k]

        # Cosine similarity
        scores = []
        for sparse_doc, mag_d in doc_vecs:
            if mag_d == 0:
                scores.append(0.0)
            else:
                dot = sum(w * sparse_doc.get(t, 0) for t, w in query_sparse.items())
                scores.append(dot / (mag_q * mag_d))

        # Rank and return top-k with minimum relevance threshold
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results = []
        for i in ranked[:top_k]:
            if scores[i] > 0.05:
                self.entries[i]["access_count"] = self.entries[i].get("access_count", 0) + 1
                results.append(self.entries[i])
        return results

    def retrieve_by_keywords(self, keywords: list[str], top_k: int = 5) -> list[dict]:
        """Retrieve entries by keyword intersection."""
        if not self.entries:
            return []

        kw_set = set(w.lower() for w in keywords)
        scored = []
        for entry in self.entries:
            entry_kw = set(entry.get("tags", entry.get("keywords", [])))
            overlap = len(kw_set & entry_kw)
            if overlap > 0:
                scored.append((entry, overlap))

        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for entry, _ in scored[:top_k]:
            entry["access_count"] = entry.get("access_count", 0) + 1
            results.append(entry)
        return results

    def get_all(self) -> list[dict]:
        return list(self.entries)

    def get_entry_by_id(self, entry_id: str) -> Optional[dict]:
        for entry in self.entries:
            if entry["id"] == entry_id:
                return entry
        return None

    def remove_by_id(self, entry_id: str, day: int = 0) -> Optional[dict]:
        for i, entry in enumerate(self.entries):
            if entry["id"] == entry_id:
                removed = self.entries.pop(i)
                self._fingerprints.pop(entry_id, None)
                self._invalidate_cache()
                if self.db_logger:
                    self.db_logger.log_mutation(
                        day=day, agent=self.agent_name, store_type=self.store_type,
                        mutation_type="discard", entry_id=entry_id,
                        content_preview=removed["content"],
                    )
                return removed
        return None

    def transfer_entry(self, entry: dict, day: int, source_agent: str) -> tuple[str, Optional[dict]]:
        """Accept a knowledge entry from another store or agent."""
        content = truncate_to_tokens(entry["content"], self.max_tokens)
        new_source = f"transferred_from_{source_agent}" if source_agent else entry.get("source", "transfer")

        kwargs = dict(content=content, day=day, source=new_source, topic=entry.get("topic", ""))
        if self.store_type == "deep_thinking":
            kwargs["reasoning_chain"] = entry.get("reasoning_chain", "")
            kwargs["confidence"] = entry.get("confidence", 0.5)
        elif self.store_type == "axiom":
            kwargs["proposed_by"] = entry.get("proposed_by", source_agent)
            kwargs["validated_by"] = entry.get("validated_by", "")
            kwargs["tags"] = entry.get("tags", entry.get("keywords", []))[:10]

        return self.add(**kwargs)

    def count(self) -> int:
        return len(self.entries)

    def is_full(self) -> bool:
        return len(self.entries) >= self.max_entries

    def persist(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)

    def load(self, filepath: Path):
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
            self._invalidate_cache()
            # Rebuild fingerprints
            self._fingerprints = {}
            for entry in self.entries:
                self._fingerprints[entry["id"]] = content_fingerprint(entry["content"])

    def cluster_entries(self) -> list[list[dict]]:
        """Group related entries into clusters by TF-IDF cosine similarity.
        Returns list of clusters (each cluster is a list of entries)."""
        if len(self.entries) < 3:
            return [list(self.entries)] if self.entries else []

        # Build TF-IDF if needed
        if self._tfidf_cache is None or self._tfidf_cache[0] != len(self.entries):
            self._build_tfidf_cache()

        n, idf, doc_vecs = self._tfidf_cache

        # Simple greedy clustering: assign each entry to first cluster with similarity >= threshold
        clusters: list[list[int]] = []
        assigned = set()

        for i in range(n):
            if i in assigned:
                continue
            cluster = [i]
            assigned.add(i)
            sparse_i, mag_i = doc_vecs[i]
            if mag_i == 0:
                clusters.append(cluster)
                continue

            for j in range(i + 1, n):
                if j in assigned:
                    continue
                sparse_j, mag_j = doc_vecs[j]
                if mag_j == 0:
                    continue
                dot = sum(w * sparse_j.get(t, 0) for t, w in sparse_i.items())
                sim = dot / (mag_i * mag_j) if (mag_i * mag_j) > 0 else 0
                if sim >= self.CLUSTER_SIMILARITY:
                    cluster.append(j)
                    assigned.add(j)

            clusters.append(cluster)

        return [[self.entries[i] for i in c] for c in clusters]

    def consolidate(self, day: int) -> int:
        """Consolidate clusters of 3+ similar entries into single summary entries
        by merging unique sentences across the cluster.
        Returns number of entries consolidated (removed)."""
        clusters = self.cluster_entries()
        consolidated = 0

        for cluster in clusters:
            if len(cluster) < 3:
                continue

            # Build merged content from cluster entries
            contents = [e["content"] for e in cluster]
            topic = cluster[0].get("topic", "")

            # Take unique sentences across all entries
            seen_sents = set()
            unique_parts = []
            for c in contents:
                for sent in c.replace("\n", ". ").split(". "):
                    sent = sent.strip()
                    if sent and sent.lower() not in seen_sents and len(sent) > 10:
                        seen_sents.add(sent.lower())
                        unique_parts.append(sent)
            summary = ". ".join(unique_parts[:15])  # Cap at 15 unique sentences

            if not summary or len(summary) < 20:
                continue

            # Remove old entries
            for entry in cluster:
                self.remove_by_id(entry["id"], day=day)
                consolidated += 1

            # Add consolidated entry
            max_confidence = max(e.get("confidence", 0.5) for e in cluster)
            total_access = sum(e.get("access_count", 0) for e in cluster)

            kwargs = dict(
                content=f"[CONSOLIDATED] {summary}",
                day=day,
                source="consolidation",
                topic=topic,
            )
            if self.store_type == "deep_thinking":
                kwargs["reasoning_chain"] = f"Consolidated from {len(cluster)} related entries"
                kwargs["confidence"] = min(max_confidence + 0.1, 1.0)
            elif self.store_type == "axiom":
                kwargs["proposed_by"] = "consolidation"
                kwargs["validated_by"] = "system"

            entry_id, _ = self.add(**kwargs)
            if entry_id:
                # Carry over access count
                for e in self.entries:
                    if e["id"] == entry_id:
                        e["access_count"] = total_access
                        break
                consolidated -= 1  # We added one back

        return consolidated

    def get_concept_bundles(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve entries as concept bundles — groups of related entries returned together.
        Better than flat retrieval because related facts stay together."""
        # First get top entries by relevance
        top_entries = self.retrieve_by_topic(query, top_k=top_k * 2)
        if not top_entries:
            return []

        # Group the top entries by topic similarity
        bundles = []
        used = set()
        for entry in top_entries:
            if entry["id"] in used:
                continue
            bundle = {"primary": entry, "related": []}
            used.add(entry["id"])

            # Find related entries in the top results
            primary_fp = content_fingerprint(entry["content"])
            for other in top_entries:
                if other["id"] in used:
                    continue
                other_fp = content_fingerprint(other["content"])
                if similarity_score(primary_fp, other_fp) >= 0.2:
                    bundle["related"].append(other)
                    used.add(other["id"])

            bundles.append(bundle)
            if len(bundles) >= top_k:
                break

        return bundles

    def snapshot(self) -> list[dict]:
        return copy.deepcopy(self.entries)


# --- DB Retrieval: pull relevant knowledge from simulation DB ---

def retrieve_from_db(db_path: Path, query: str, agent_name: str = None, top_k: int = 10) -> list[dict]:
    """
    Retrieve relevant knowledge from the simulation DB.
    Searches interactions (oracle answers, lecture content, peer conversations)
    and returns the most relevant response_preview entries by keyword overlap.
    """
    if not db_path.exists():
        return []

    query_tokens = set(tokenize(query))
    if not query_tokens:
        return []

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # Pull oracle answers and lecture content (richest knowledge)
    if agent_name:
        cur.execute("""
            SELECT response_preview, action, day, phase FROM interactions
            WHERE (agent = ? OR agent = 'oracle')
              AND response_preview IS NOT NULL AND length(response_preview) > 50
            ORDER BY day DESC LIMIT 500
        """, (agent_name,))
    else:
        cur.execute("""
            SELECT response_preview, action, day, phase FROM interactions
            WHERE response_preview IS NOT NULL AND length(response_preview) > 50
            ORDER BY day DESC LIMIT 500
        """)

    rows = cur.fetchall()

    # Also pull conversation transcripts
    if agent_name:
        cur.execute("""
            SELECT transcript_json, topic, day FROM conversations
            WHERE agent_a = ? OR agent_b = ?
            ORDER BY day DESC LIMIT 100
        """, (agent_name, agent_name))
    else:
        cur.execute("""
            SELECT transcript_json, topic, day FROM conversations
            ORDER BY day DESC LIMIT 100
        """)
    conv_rows = cur.fetchall()
    conn.close()

    # Score interactions by keyword overlap
    scored = []
    seen = set()
    for response, action, day, phase in rows:
        if not response or response in seen:
            continue
        seen.add(response)
        resp_tokens = set(tokenize(response))
        overlap = len(query_tokens & resp_tokens)
        if overlap >= 2:  # At least 2 keyword matches
            scored.append({
                "content": response,
                "source": f"db:{action}",
                "day": day,
                "phase": phase,
                "relevance": overlap,
            })

    # Score conversation excerpts
    for transcript_json, topic, day in conv_rows:
        try:
            transcript = json.loads(transcript_json)
            for turn in transcript:
                msg = turn.get("message", "")
                if len(msg) < 50 or msg in seen:
                    continue
                seen.add(msg)
                msg_tokens = set(tokenize(msg))
                overlap = len(query_tokens & msg_tokens)
                if overlap >= 2:
                    scored.append({
                        "content": msg[:500],
                        "source": f"db:conversation",
                        "day": day,
                        "phase": "PEER_CONVERSATION",
                        "relevance": overlap,
                    })
        except (json.JSONDecodeError, TypeError):
            continue

    # Sort by relevance and return top-k
    scored.sort(key=lambda x: x["relevance"], reverse=True)
    return scored[:top_k]


def create_stores_for_agent(agent_name: str, rng, db_logger=None) -> dict[str, KnowledgeStore]:
    """Create the three knowledge stores for an agent."""
    return {
        "impulse": KnowledgeStore(
            agent_name=agent_name, store_type="impulse",
            max_entries=config.IMPULSE_MAX_ENTRIES, max_tokens=config.IMPULSE_MAX_TOKENS,
            rng=rng, db_logger=db_logger,
        ),
        "deep_thinking": KnowledgeStore(
            agent_name=agent_name, store_type="deep_thinking",
            max_entries=config.DEEP_MAX_ENTRIES, max_tokens=config.DEEP_MAX_TOKENS,
            rng=rng, db_logger=db_logger,
        ),
        "axiom": KnowledgeStore(
            agent_name=agent_name, store_type="axiom",
            max_entries=config.AXIOM_MAX_ENTRIES, max_tokens=config.AXIOM_MAX_TOKENS,
            rng=rng, db_logger=db_logger,
        ),
    }
