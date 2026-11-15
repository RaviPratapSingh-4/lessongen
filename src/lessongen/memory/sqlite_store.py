import sqlite3
import time
from pathlib import Path

from .base import MemoryStore

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, ts TEXT, topic TEXT, status TEXT, attempts INT, tokens INT);
CREATE TABLE IF NOT EXISTS check_failures(check_id TEXT PRIMARY KEY, count INT, last_seen TEXT, last_reason TEXT);
CREATE TABLE IF NOT EXISTS lessons(id INTEGER PRIMARY KEY AUTOINCREMENT, check_id TEXT UNIQUE, text TEXT, status TEXT DEFAULT 'active', source_run TEXT, hits INT DEFAULT 0);
CREATE TABLE IF NOT EXISTS rubric_proposals(id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT UNIQUE, fix_hint TEXT, status TEXT DEFAULT 'pending', source_run TEXT);
"""


class SQLiteStore(MemoryStore):
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def _rows(self, sql, *a):
        return [dict(r) for r in self.db.execute(sql, a).fetchall()]

    def record_run(self, run_id, topic, status, attempts, tokens):
        self.db.execute("INSERT OR REPLACE INTO runs VALUES(?,?,?,?,?,?)", (run_id, time.strftime("%Y-%m-%d %H:%M:%S"), topic, status, attempts, tokens))
        self.db.commit()

    def record_failures(self, counts, last_reason):
        for cid, n in counts.items():
            self.db.execute(
                "INSERT INTO check_failures VALUES(?,?,?,?) ON CONFLICT(check_id) DO UPDATE SET count=count+excluded.count,last_seen=excluded.last_seen,last_reason=excluded.last_reason",
                (cid, n, time.strftime("%Y-%m-%d %H:%M:%S"), last_reason.get(cid, "")),
            )
        self.db.commit()

    def failure_counts(self):
        return {r["check_id"]: r["count"] for r in self._rows("SELECT check_id,count FROM check_failures")}

    def has_lesson(self, check_id):
        return bool(self._rows("SELECT 1 FROM lessons WHERE check_id=?", check_id))

    def add_lesson(self, check_id, text, source_run):
        self.db.execute("INSERT OR IGNORE INTO lessons(check_id,text,source_run) VALUES(?,?,?)", (check_id, text, source_run))
        self.db.commit()

    def active_lessons(self, limit=8):
        return self._rows("SELECT * FROM lessons WHERE status='active' ORDER BY id DESC LIMIT ?", limit)

    def bump_hits(self, ids):
        for i in ids:
            self.db.execute("UPDATE lessons SET hits=hits+1 WHERE id=?", (i,))
        self.db.commit()

    def add_proposal(self, description, fix_hint, source_run):
        cur = self.db.execute("INSERT OR IGNORE INTO rubric_proposals(description,fix_hint,source_run) VALUES(?,?,?)", (description, fix_hint, source_run))
        self.db.commit()
        return cur.lastrowid if cur.rowcount else None

    def proposals(self, status="pending"):
        return self._rows("SELECT * FROM rubric_proposals WHERE status=?", status)

    def set_proposal(self, pid, status):
        cur = self.db.execute("UPDATE rubric_proposals SET status=? WHERE id=?", (status, pid))
        self.db.commit()
        return cur.rowcount > 0

    def approved_checks(self):
        return [{"check_id": f"X{r['id']}", **r} for r in self._rows("SELECT * FROM rubric_proposals WHERE status='approved'")]

    def runs(self, limit=10):
        return self._rows("SELECT * FROM runs ORDER BY ts DESC LIMIT ?", limit)
