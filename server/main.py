"""
Gobston — Leaderboard backend (FastAPI + SQLite).

Endpoints:
  GET  /health                      -> {"ok": true}
  POST /score                       -> upsert điểm của 1 device
  GET  /leaderboard?scope=world&limit=100  -> top người chơi

Chạy local:
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = Path(__file__).with_name("gobston.db")

app = FastAPI(title="Gobston Leaderboard", version="1.0.0")

# Game client là WebView/Browser ở origin khác -> cần mở CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                device_id   TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                status_full TEXT NOT NULL DEFAULT '',
                status_rev  INTEGER NOT NULL DEFAULT 0,
                wins        INTEGER NOT NULL DEFAULT 0,
                best_round  INTEGER NOT NULL DEFAULT 1,
                plays       INTEGER NOT NULL DEFAULT 0,
                region      TEXT NOT NULL DEFAULT 'VN',
                updated_at  REAL NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_rank ON players (best_round DESC, wins DESC)"
        )


init_db()


class Score(BaseModel):
    device_id: str = Field(min_length=4, max_length=64)
    name: str = Field(min_length=1, max_length=16)
    status_full: str = Field(default="", max_length=20)
    status_rev: int = Field(default=0, ge=0, le=20)
    wins: int = Field(default=0, ge=0, le=1_000_000)
    best_round: int = Field(default=1, ge=1, le=99)
    plays: int = Field(default=0, ge=0, le=1_000_000)
    region: str = Field(default="VN", max_length=8)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/score")
def submit_score(s: Score) -> dict:
    # Chống "tụt hạng do client gửi nhầm": chỉ nhận điểm nếu >= điểm cũ
    # (best_round / wins không bao giờ giảm). Danh hiệu/tên thì luôn cập nhật.
    name = s.name.strip()[:16]
    with db() as conn:
        row = conn.execute(
            "SELECT wins, best_round, plays FROM players WHERE device_id = ?",
            (s.device_id,),
        ).fetchone()
        wins = max(s.wins, row["wins"]) if row else s.wins
        best = max(s.best_round, row["best_round"]) if row else s.best_round
        plays = max(s.plays, row["plays"]) if row else s.plays
        conn.execute(
            """
            INSERT INTO players (device_id, name, status_full, status_rev,
                                 wins, best_round, plays, region, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(device_id) DO UPDATE SET
                name=excluded.name, status_full=excluded.status_full,
                status_rev=excluded.status_rev, wins=excluded.wins,
                best_round=excluded.best_round, plays=excluded.plays,
                region=excluded.region, updated_at=excluded.updated_at
            """,
            (s.device_id, name, s.status_full, s.status_rev,
             wins, best, plays, s.region, time.time()),
        )
    return {"ok": True}


@app.get("/leaderboard")
def leaderboard(scope: str = "world", limit: int = 100, region: str = "VN") -> dict:
    limit = max(1, min(limit, 200))
    sql = "SELECT name, status_full, status_rev, wins, best_round FROM players"
    params: tuple = ()
    if scope == "region":
        sql += " WHERE region = ?"
        params = (region,)
        limit = min(limit, 10)
    sql += " ORDER BY best_round DESC, wins DESC, updated_at ASC LIMIT ?"
    params = params + (limit,)
    with db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return {
        "scope": scope,
        "entries": [
            {
                "nm": r["name"],
                "full": r["status_full"],
                "rev": r["status_rev"],
                "wins": r["wins"],
                "best": r["best_round"],
            }
            for r in rows
        ],
    }
