import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Libere aqui o(s) domínio(s) do seu site quando for pra produção,
# em vez de "*". Ex: CORS(app, origins=["https://seusite.com"])
CORS(app)

DB_PATH = os.environ.get("DB_PATH", "clicks.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


@app.route("/api/click", methods=["POST"])
def register_click():
    data = request.get_json(silent=True) or {}
    source = data.get("source", "unknown")[:100]  # limita tamanho, evita abuso

    conn = get_db()
    conn.execute(
        "INSERT INTO clicks (source, created_at) VALUES (?, ?)",
        (source, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    total = conn.execute("SELECT COUNT(*) AS c FROM clicks").fetchone()["c"]
    conn.close()

    return jsonify({"ok": True, "total": total}), 201


@app.route("/api/stats", methods=["GET"])
def stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) AS c FROM clicks").fetchone()["c"]

    by_source = conn.execute(
        "SELECT source, COUNT(*) AS c FROM clicks GROUP BY source ORDER BY c DESC"
    ).fetchall()

    last_24h = conn.execute(
        "SELECT COUNT(*) AS c FROM clicks WHERE created_at >= datetime('now', '-1 day')"
    ).fetchone()["c"]

    conn.close()

    return jsonify(
        {
            "total": total,
            "last_24h": last_24h,
            "by_source": [{"source": r["source"], "count": r["c"]} for r in by_source],
        }
    )


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
