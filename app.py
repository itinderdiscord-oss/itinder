import os
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Libere aqui o(s) domínio(s) do seu site quando for pra produção,
# em vez de "*". Ex: CORS(app, origins=["https://seusite.com"])
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não encontrada. Configure a variável de ambiente "
        "no seu Web Service do Render apontando para o Postgres."
    )

# Render às vezes fornece a URL como "postgres://", mas psycopg2 exige "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clicks (
            id SERIAL PRIMARY KEY,
            source TEXT,
            created_at TIMESTAMPTZ NOT NULL
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()


init_db()


@app.route("/api/click", methods=["POST"])
def register_click():
    data = request.get_json(silent=True) or {}
    source = data.get("source", "unknown")[:100]  # limita tamanho, evita abuso

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clicks (source, created_at) VALUES (%s, %s)",
        (source, datetime.now(timezone.utc)),
    )
    conn.commit()

    cur.execute("SELECT COUNT(*) AS c FROM clicks")
    total = cur.fetchone()["c"]

    cur.close()
    conn.close()

    return jsonify({"ok": True, "total": total}), 201


@app.route("/api/stats", methods=["GET"])
def stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS c FROM clicks")
    total = cur.fetchone()["c"]

    cur.execute(
        "SELECT source, COUNT(*) AS c FROM clicks GROUP BY source ORDER BY c DESC"
    )
    by_source = cur.fetchall()

    cur.execute(
        "SELECT COUNT(*) AS c FROM clicks WHERE created_at >= now() - interval '1 day'"
    )
    last_24h = cur.fetchone()["c"]

    cur.close()
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
