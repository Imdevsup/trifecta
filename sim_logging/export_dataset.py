"""
Dataset Exporter — Reads the simulation SQLite DB and emits fine-tuning datasets.

Produces:
  - sft.jsonl:              supervised fine-tuning data in OpenAI chat format
  - dpo.jsonl:              preference data (prompt / chosen / rejected)
  - dataset_manifest.json:  counts, filters, and provenance

Sources (all stored untruncated in the DB):
  - test_results:  final-exam Q&A with grader scores — highest quality SFT + DPO.
  - interactions:  oracle answers AND full lectures (richest long-form SFT content).
  - conversations: multi-turn peer dialogue — optional, lower quality.

Across an 8-domain, 365-day run, the interactions table is the largest source:
roughly one lecture per subtopic per day (~6/day) plus 15 oracle Q&A turns/day —
so a full run produces thousands of high-quality SFT records spanning all
eight domains.

Usage:
  python -m sim_logging.export_dataset
  python -m sim_logging.export_dataset --out training_data/ --min-score 8
  python -m sim_logging.export_dataset --include-conversations --include-interactions
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import config

logger = logging.getLogger(__name__)


# --- Filters ---------------------------------------------------------------

# Placeholder / error strings emitted by failing LLM calls — never train on these.
_ERROR_PATTERNS = [
    re.compile(r'^\s*\[LLM unavailable'),
    re.compile(r'^\s*\[Dry-run'),
    re.compile(r'^\s*\[Evaluator unavailable'),
    re.compile(r'^\s*\[Oracle unavailable'),
    re.compile(r'^\s*\[Gamma unavailable'),
]

_MIN_CONTENT_CHARS = 20


def _is_clean(text: str | None) -> bool:
    """True if the text looks like a valid training target (not empty, not a placeholder)."""
    if not text:
        return False
    stripped = text.strip()
    if len(stripped) < _MIN_CONTENT_CHARS:
        return False
    for pat in _ERROR_PATTERNS:
        if pat.search(stripped):
            return False
    return True


# --- Defaults --------------------------------------------------------------

DEFAULT_SFT_SYSTEM_PROMPT = (
    "You are an expert tutor. Answer questions accurately and thoroughly, "
    "providing reasoning where appropriate."
)


@dataclass
class ExportStats:
    sft_from_tests: int = 0
    sft_from_conversations: int = 0
    sft_from_interactions: int = 0
    sft_from_lectures: int = 0
    sft_total: int = 0
    dpo_pairs: int = 0
    dropped_error: int = 0
    dropped_short: int = 0


# --- SFT from test_results -------------------------------------------------

def _iter_test_sft(
    conn: sqlite3.Connection,
    min_score: float,
    system_prompt: str,
    stats: ExportStats,
) -> Iterator[dict]:
    """Yield SFT records from test_results where score >= min_score and content is clean."""
    rows = conn.execute(
        """
        SELECT agent, question_number, question_type, question, answer, score
        FROM test_results
        WHERE score >= ?
        ORDER BY question_number, agent
        """,
        (min_score,),
    ).fetchall()

    for _agent, _qnum, _qtype, question, answer, _score in rows:
        if not _is_clean(question):
            stats.dropped_short += 1
            continue
        if not _is_clean(answer):
            stats.dropped_error += 1
            continue

        yield {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question.strip()},
                {"role": "assistant", "content": answer.strip()},
            ]
        }
        stats.sft_from_tests += 1


# --- DPO from test_results -------------------------------------------------

def _iter_test_dpo(
    conn: sqlite3.Connection,
    min_gap: float,
    stats: ExportStats,
) -> Iterator[dict]:
    """Yield DPO pairs by grouping test_results per question (best vs worst agent answer).
    Only pairs where the score gap is >= min_gap and the answers differ."""
    rows = conn.execute(
        """
        SELECT question_number, question, agent, answer, score
        FROM test_results
        ORDER BY question_number, score DESC
        """
    ).fetchall()

    groups: dict[int, list[tuple]] = {}
    questions: dict[int, str] = {}
    for qnum, question, agent, answer, score in rows:
        if not _is_clean(question) or not _is_clean(answer):
            continue
        groups.setdefault(qnum, []).append((agent, answer.strip(), score))
        questions.setdefault(qnum, question.strip())

    for qnum, candidates in groups.items():
        if len(candidates) < 2:
            continue
        candidates.sort(key=lambda c: c[2], reverse=True)
        best_agent, best_answer, best_score = candidates[0]
        worst_agent, worst_answer, worst_score = candidates[-1]

        if best_score - worst_score < min_gap:
            continue
        if best_answer == worst_answer:
            continue

        yield {
            "prompt": questions[qnum],
            "chosen": best_answer,
            "rejected": worst_answer,
            "chosen_score": best_score,
            "rejected_score": worst_score,
            "chosen_agent": best_agent,
            "rejected_agent": worst_agent,
        }
        stats.dpo_pairs += 1


# --- SFT from peer conversations (opt-in) ----------------------------------

def _iter_conversation_sft(
    conn: sqlite3.Connection,
    system_prompt: str,
    stats: ExportStats,
) -> Iterator[dict]:
    """Yield multi-turn SFT examples from peer conversations.
    Transcripts are truncated at the first unclean turn so we still keep
    any valid early dialogue from a partially-broken conversation."""
    rows = conn.execute(
        """
        SELECT day, agent_a, agent_b, topic, transcript_json
        FROM conversations
        ORDER BY day, id
        """
    ).fetchall()

    for _day, agent_a, _agent_b, _topic, transcript_json in rows:
        try:
            transcript = json.loads(transcript_json)
        except json.JSONDecodeError:
            stats.dropped_error += 1
            continue

        if not transcript or len(transcript) < 2:
            continue

        first_sender = transcript[0].get("sender", agent_a)
        messages: list[dict] = [{"role": "system", "content": system_prompt}]

        for turn in transcript:
            content = (turn.get("content") or "").strip()
            if not _is_clean(content):
                break
            role = "user" if turn.get("sender") == first_sender else "assistant"
            messages.append({"role": role, "content": content})

        # Need at least one full user+assistant pair after the system message.
        if len(messages) < 3:
            continue

        # Trainers expect the last message to be assistant — trim trailing user turn.
        if messages[-1]["role"] != "assistant":
            messages = messages[:-1]
        if len(messages) < 3:
            continue

        yield {"messages": messages}
        stats.sft_from_conversations += 1


# --- SFT from oracle interactions: answers + lectures (opt-in) ------------

def _iter_interaction_sft(
    conn: sqlite3.Connection,
    system_prompt: str,
    stats: ExportStats,
) -> Iterator[dict]:
    """Yield SFT examples from oracle interactions — both Q&A answers and lectures.

    The DB logger stores full untruncated content, so we can train directly on:
      - answer_for_<agent>: oracle answering an agent's follow-up question
      - lecture_<subtopic>: oracle generating a comprehensive teaching lecture
    Lectures are the richest long-form source — multi-paragraph expert content
    on every topic in the curriculum."""
    rows = conn.execute(
        """
        SELECT prompt_preview, response_preview, action
        FROM interactions
        WHERE agent = 'oracle'
          AND (action LIKE 'answer_for_%' OR action LIKE 'lecture_%')
        ORDER BY id
        """
    ).fetchall()

    for prompt, response, action in rows:
        if not _is_clean(prompt):
            stats.dropped_short += 1
            continue
        if not _is_clean(response):
            stats.dropped_error += 1
            continue
        yield {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt.strip()},
                {"role": "assistant", "content": response.strip()},
            ]
        }
        if action.startswith("lecture_"):
            stats.sft_from_lectures += 1
        else:
            stats.sft_from_interactions += 1


# --- Writers ---------------------------------------------------------------

def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _write_manifest(path: Path, stats: ExportStats, params: dict, db_path: Path) -> None:
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_db": str(db_path),
        "params": params,
        "stats": {
            "sft_from_tests": stats.sft_from_tests,
            "sft_from_conversations": stats.sft_from_conversations,
            "sft_from_interactions": stats.sft_from_interactions,
            "sft_from_lectures": stats.sft_from_lectures,
            "sft_total": stats.sft_total,
            "dpo_pairs": stats.dpo_pairs,
            "dropped_error_or_placeholder": stats.dropped_error,
            "dropped_too_short": stats.dropped_short,
        },
        "format": {
            "sft": 'OpenAI chat format: {"messages": [{"role": "system|user|assistant", "content": "..."}]}',
            "dpo": 'TRL/axolotl format: {"prompt": "...", "chosen": "...", "rejected": "..."}',
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


# --- Orchestration ---------------------------------------------------------

def export_dataset(
    db_path: Path,
    out_dir: Path,
    min_score: float = 7.0,
    dpo_gap: float = 3.0,
    include_conversations: bool = False,
    include_interactions: bool = False,
    system_prompt: str = DEFAULT_SFT_SYSTEM_PROMPT,
    dry_run: bool = False,
) -> ExportStats:
    """Export SFT and DPO datasets from the simulation DB. Returns stats."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    stats = ExportStats()

    try:
        sft_records: list[dict] = []
        sft_records.extend(_iter_test_sft(conn, min_score, system_prompt, stats))
        if include_conversations:
            sft_records.extend(_iter_conversation_sft(conn, system_prompt, stats))
        if include_interactions:
            sft_records.extend(_iter_interaction_sft(conn, system_prompt, stats))
        stats.sft_total = len(sft_records)

        dpo_records = list(_iter_test_dpo(conn, dpo_gap, stats))
    finally:
        conn.close()

    if dry_run:
        return stats

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(out_dir / "sft.jsonl", sft_records)
    _write_jsonl(out_dir / "dpo.jsonl", dpo_records)
    _write_manifest(
        out_dir / "dataset_manifest.json",
        stats,
        params={
            "min_score": min_score,
            "dpo_gap": dpo_gap,
            "include_conversations": include_conversations,
            "include_interactions": include_interactions,
            "system_prompt": system_prompt,
        },
        db_path=db_path,
    )
    return stats


# --- CLI -------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export fine-tuning datasets (SFT + DPO) from the CTS simulation database.",
    )
    parser.add_argument("--db", type=Path, default=config.LOG_DB_PATH,
                        help=f"Path to simulation DB (default: {config.LOG_DB_PATH})")
    parser.add_argument("--out", type=Path, default=Path("training_data"),
                        help="Output directory for JSONL files (default: training_data/)")
    parser.add_argument("--min-score", type=float, default=7.0,
                        help="Minimum grader score (0-10) for SFT inclusion from test_results (default: 7.0)")
    parser.add_argument("--dpo-gap", type=float, default=3.0,
                        help="Minimum score gap between chosen and rejected for DPO pairs (default: 3.0)")
    parser.add_argument("--include-conversations", action="store_true",
                        help="Also export peer conversations as multi-turn SFT (lower quality)")
    parser.add_argument("--include-interactions", action="store_true",
                        help="Also export oracle Q&A AND full lectures from the interactions table")
    parser.add_argument("--system-prompt", type=str, default=DEFAULT_SFT_SYSTEM_PROMPT,
                        help="System prompt prepended to every SFT example")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute counts without writing files")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        stats = export_dataset(
            db_path=args.db,
            out_dir=args.out,
            min_score=args.min_score,
            dpo_gap=args.dpo_gap,
            include_conversations=args.include_conversations,
            include_interactions=args.include_interactions,
            system_prompt=args.system_prompt,
            dry_run=args.dry_run,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    verb = "Would export" if args.dry_run else "Exported"
    print(f"\n{verb}:")
    print(f"  SFT total:              {stats.sft_total}")
    print(f"    from test_results:    {stats.sft_from_tests}")
    if args.include_conversations:
        print(f"    from conversations:   {stats.sft_from_conversations}")
    if args.include_interactions:
        print(f"    from oracle Q&A:      {stats.sft_from_interactions}")
        print(f"    from lectures:        {stats.sft_from_lectures}")
    print(f"  DPO pairs:              {stats.dpo_pairs}")
    if stats.dropped_error or stats.dropped_short:
        print(f"  Dropped — error/placeholder: {stats.dropped_error}")
        print(f"  Dropped — too short:         {stats.dropped_short}")

    if not args.dry_run:
        print(f"\n  Output: {args.out.resolve()}/")
        print(f"    sft.jsonl              ({stats.sft_total} records)")
        print(f"    dpo.jsonl              ({stats.dpo_pairs} records)")
        print(f"    dataset_manifest.json")

    if stats.sft_total == 0 and stats.dpo_pairs == 0:
        print(
            "\nWarning: no records exported. Is the simulation DB populated, "
            "and has the final test been run? Try a lower --min-score.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
