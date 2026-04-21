"""
SQLite Database Logger — Academic-grade logging of all simulation events.
Tables: interactions, knowledge_mutations, conversations, snapshots, test_results, overflow_events

Thread-safe: all writes are serialized through a reentrant lock so the
connection (opened with check_same_thread=False) cannot be torn across threads.

Batching: wrap a block of writes in `with db_logger.batch():` to defer commits
until the block exits — turns a chain of per-row fsyncs into one.

Note on column names: columns named `*_preview` (prompt_preview, response_preview,
content_preview, deleted_content_preview) are historical — they now store the
FULL untruncated content. Truncation was removed so the DB is a faithful record
of every oracle lecture, agent answer, and knowledge mutation. Downstream tools
(fine-tuning exporter, analysis scripts) rely on this.
"""

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class DatabaseLogger:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._write_lock = threading.RLock()
        self._batch_depth = 0
        self._create_tables()

    def _create_tables(self):
        with self._write_lock:
            c = self.conn.cursor()

            c.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day INTEGER,
                    phase TEXT,
                    agent TEXT,
                    action TEXT,
                    prompt_preview TEXT,
                    response_preview TEXT,
                    tokens_in INTEGER DEFAULT 0,
                    tokens_out INTEGER DEFAULT 0,
                    latency_ms INTEGER DEFAULT 0,
                    model TEXT,
                    timestamp TEXT
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_mutations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day INTEGER,
                    agent TEXT,
                    store_type TEXT,
                    mutation_type TEXT,
                    entry_id TEXT,
                    content_preview TEXT,
                    timestamp TEXT
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day INTEGER,
                    phase TEXT,
                    agent_a TEXT,
                    agent_b TEXT,
                    topic TEXT,
                    transcript_json TEXT,
                    num_exchanges INTEGER,
                    timestamp TEXT
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day INTEGER,
                    agent TEXT,
                    store_type TEXT,
                    entry_count INTEGER,
                    entries_json TEXT,
                    timestamp TEXT
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent TEXT,
                    question_number INTEGER,
                    question_type TEXT,
                    question TEXT,
                    answer TEXT,
                    score REAL,
                    score_reasoning TEXT,
                    timestamp TEXT
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS overflow_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day INTEGER,
                    agent TEXT,
                    store_type TEXT,
                    deleted_entry_id TEXT,
                    deleted_content_preview TEXT,
                    reason TEXT DEFAULT 'capacity_overflow',
                    timestamp TEXT
                )
            """)

            # --- Indices for faster queries (used by retrieve_from_db and analysis) ---
            c.execute("CREATE INDEX IF NOT EXISTS idx_interactions_agent_day ON interactions(agent, day)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_interactions_day ON interactions(day)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_interactions_phase ON interactions(phase)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_conversations_day ON conversations(day)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_conversations_agents ON conversations(agent_a, agent_b)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_mutations_agent ON knowledge_mutations(agent, day)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_agent_day ON snapshots(agent, day)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_test_results_agent ON test_results(agent)")

            self.conn.commit()

    @contextmanager
    def batch(self):
        """Defer commits within this block; one commit is issued on exit.
        Nestable — only the outermost batch commits."""
        with self._write_lock:
            self._batch_depth += 1
        try:
            yield
        finally:
            with self._write_lock:
                self._batch_depth -= 1
                if self._batch_depth == 0:
                    self.conn.commit()

    def _write(self, sql: str, params: tuple):
        """Execute a write under the shared lock. Commits immediately unless inside a batch."""
        with self._write_lock:
            self.conn.execute(sql, params)
            if self._batch_depth == 0:
                self.conn.commit()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def log_interaction(
        self,
        day: int,
        phase: str,
        agent: str,
        action: str,
        prompt_preview: str = "",
        response_preview: str = "",
        tokens_in: int = 0,
        tokens_out: int = 0,
        latency_ms: int = 0,
        model: str = "",
    ):
        self._write(
            """INSERT INTO interactions
               (day, phase, agent, action, prompt_preview, response_preview,
                tokens_in, tokens_out, latency_ms, model, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (day, phase, agent, action, prompt_preview, response_preview,
             tokens_in, tokens_out, latency_ms, model, self._now()),
        )

    def log_mutation(
        self,
        day: int,
        agent: str,
        store_type: str,
        mutation_type: str,
        entry_id: str,
        content_preview: str = "",
    ):
        self._write(
            """INSERT INTO knowledge_mutations
               (day, agent, store_type, mutation_type, entry_id, content_preview, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (day, agent, store_type, mutation_type, entry_id, content_preview, self._now()),
        )

    def log_conversation(
        self,
        day: int,
        phase: str,
        agent_a: str,
        agent_b: str,
        topic: str,
        transcript: list[dict],
        num_exchanges: int,
    ):
        self._write(
            """INSERT INTO conversations
               (day, phase, agent_a, agent_b, topic, transcript_json, num_exchanges, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (day, phase, agent_a, agent_b, topic,
             json.dumps(transcript, ensure_ascii=False), num_exchanges, self._now()),
        )

    def log_snapshot(
        self,
        day: int,
        agent: str,
        store_type: str,
        entry_count: int,
        entries: list[dict],
    ):
        self._write(
            """INSERT INTO snapshots
               (day, agent, store_type, entry_count, entries_json, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (day, agent, store_type, entry_count,
             json.dumps(entries, ensure_ascii=False), self._now()),
        )

    def log_test_result(
        self,
        agent: str,
        question_number: int,
        question_type: str,
        question: str,
        answer: str,
        score: float,
        score_reasoning: str = "",
    ):
        self._write(
            """INSERT INTO test_results
               (agent, question_number, question_type, question, answer, score, score_reasoning, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (agent, question_number, question_type, question, answer, score,
             score_reasoning, self._now()),
        )

    def log_overflow(
        self,
        day: int,
        agent: str,
        store_type: str,
        deleted_entry_id: str,
        deleted_content_preview: str = "",
    ):
        self._write(
            """INSERT INTO overflow_events
               (day, agent, store_type, deleted_entry_id, deleted_content_preview, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (day, agent, store_type, deleted_entry_id, deleted_content_preview, self._now()),
        )

    def get_all_interactions(self, agent: str = None) -> list[dict]:
        with self._write_lock:
            if agent:
                rows = self.conn.execute(
                    "SELECT * FROM interactions WHERE agent = ? ORDER BY id", (agent,)
                ).fetchall()
            else:
                rows = self.conn.execute("SELECT * FROM interactions ORDER BY id").fetchall()
            cols = [d[0] for d in self.conn.execute("SELECT * FROM interactions LIMIT 0").description]
        return [dict(zip(cols, r)) for r in rows]

    def get_test_results(self) -> list[dict]:
        with self._write_lock:
            rows = self.conn.execute("SELECT * FROM test_results ORDER BY id").fetchall()
            cols = [d[0] for d in self.conn.execute("SELECT * FROM test_results LIMIT 0").description]
        return [dict(zip(cols, r)) for r in rows]

    def get_overflow_events(self) -> list[dict]:
        with self._write_lock:
            rows = self.conn.execute("SELECT * FROM overflow_events ORDER BY id").fetchall()
            cols = [d[0] for d in self.conn.execute("SELECT * FROM overflow_events LIMIT 0").description]
        return [dict(zip(cols, r)) for r in rows]

    def get_snapshots(self, day: int = None) -> list[dict]:
        with self._write_lock:
            if day:
                rows = self.conn.execute(
                    "SELECT * FROM snapshots WHERE day = ? ORDER BY id", (day,)
                ).fetchall()
            else:
                rows = self.conn.execute("SELECT * FROM snapshots ORDER BY id").fetchall()
            cols = [d[0] for d in self.conn.execute("SELECT * FROM snapshots LIMIT 0").description]
        return [dict(zip(cols, r)) for r in rows]

    def get_knowledge_mutations(self) -> list[dict]:
        with self._write_lock:
            rows = self.conn.execute("SELECT * FROM knowledge_mutations ORDER BY id").fetchall()
            cols = [d[0] for d in self.conn.execute("SELECT * FROM knowledge_mutations LIMIT 0").description]
        return [dict(zip(cols, r)) for r in rows]

    def close(self):
        with self._write_lock:
            self.conn.commit()
            self.conn.close()
