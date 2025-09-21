import os
from flask import Flask, request, jsonify
import pymysql
from pymysql.cursors import DictCursor
from datetime import datetime

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')  # IP/hostname of MariaDB (container name if using docker network)
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_NAME = os.getenv('DB_NAME', 'stationmeteo')
DB_USER = os.getenv('DB_USER', 'pico')
DB_PASS = os.getenv('DB_PASS', 'motdepassepico')

app = Flask(__name__)

TABLE_DDL = """
CREATE TABLE IF NOT EXISTS mesures (
  id INT AUTO_INCREMENT PRIMARY KEY,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  temperature DOUBLE,
  humidite DOUBLE,
  pression DOUBLE,
  co2 DOUBLE,
  humidite_surface DOUBLE,
  pluie_detectee TINYINT(1),
  indice_uv DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

# Expected columns (for lightweight forward-compatible migrations)
EXPECTED_COLUMNS = {
    'created_at': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
    'temperature': 'DOUBLE',
    'humidite': 'DOUBLE',
    'pression': 'DOUBLE',
    'co2': 'DOUBLE',
    'humidite_surface': 'DOUBLE',
    'pluie_detectee': 'TINYINT(1)',
    'indice_uv': 'DOUBLE'
}

def get_conn():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=DictCursor,
        autocommit=True,
    )

# Lazy DB initialization so that /health never fails
DB_INIT_DONE = False
DB_INIT_ERROR = None

def ensure_db():
    global DB_INIT_DONE, DB_INIT_ERROR
    if DB_INIT_DONE:
        return
    try:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(TABLE_DDL)
                # Lightweight schema migration: add any missing expected columns
                try:
                    cur.execute("SHOW COLUMNS FROM mesures")
                    existing = {row['Field'] for row in cur.fetchall()}
                    missing = [col for col in EXPECTED_COLUMNS if col not in existing]
                    for col in missing:
                        ddl = f"ALTER TABLE mesures ADD COLUMN {col} {EXPECTED_COLUMNS[col]}"
                        cur.execute(ddl)
                except Exception as mig_e:
                    # Non critical; record but continue
                    DB_INIT_ERROR = f"migration: {mig_e}" if not DB_INIT_ERROR else DB_INIT_ERROR
            DB_INIT_DONE = True
            if DB_INIT_ERROR is None:
                DB_INIT_ERROR = None
        finally:
            conn.close()
    except Exception as e:
        DB_INIT_ERROR = str(e)

@app.route('/health', methods=['GET'])
def health():
    # Do not touch DB here to keep health robust
    status = 'ok'
    db_status = 'ready' if DB_INIT_DONE else ('error' if DB_INIT_ERROR else 'not-initialized')
    return jsonify(status=status, db=db_status, db_error=DB_INIT_ERROR, time=datetime.utcnow().isoformat()+'Z')

@app.route('/add', methods=['POST'])
def add():
    if not request.is_json:
        return jsonify(error='Expected application/json'), 400
    data = request.get_json(silent=True) or {}

    # Ensure DB/table exists (retry each call until success)
    ensure_db()

    # Extract and basic type validation
    def as_float(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None
    def as_bool(x):
        if isinstance(x, bool):
            return x
        if isinstance(x, (int, float)):
            return bool(int(x))
        if isinstance(x, str):
            return x.strip().lower() in ('1','true','yes','on')
        return None

    row = {
        'temperature': as_float(data.get('temperature')),
        'humidite': as_float(data.get('humidite')),
        'pression': as_float(data.get('pression')),
        'co2': as_float(data.get('co2')),
        'humidite_surface': as_float(data.get('humidite_surface')),
        'pluie_detectee': 1 if as_bool(data.get('pluie_detectee')) else 0,
        'indice_uv': as_float(data.get('indice_uv')),
    }

    # Optional: basic sanity clamp
    if row['humidite'] is not None:
        row['humidite'] = max(0.0, min(100.0, row['humidite']))
    if row['humidite_surface'] is not None:
        row['humidite_surface'] = max(0.0, min(100.0, row['humidite_surface']))

    # Insert into DB
    sql = (
        "INSERT INTO mesures (temperature, humidite, pression, co2, humidite_surface, pluie_detectee, indice_uv) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (
                row['temperature'], row['humidite'], row['pression'], row['co2'],
                row['humidite_surface'], row['pluie_detectee'], row['indice_uv']
            ))
        return jsonify(status='ok'), 201
    except Exception as e:
        # For local LAN, return error message for debugging
        return jsonify(status='error', message=str(e)), 500
    finally:
        conn.close()


@app.route('/measures', methods=['GET'])
@app.route('/mesures', methods=['GET'])  # alias FR
def list_measures():
    # Ensure table exists
    ensure_db()

    # Parse query params
    try:
        limit = int(request.args.get('limit', '100'))
        limit = max(1, min(limit, 1000))
    except Exception:
        limit = 100
    try:
        offset = int(request.args.get('offset', '0'))
        offset = max(0, offset)
    except Exception:
        offset = 0

    sql = (
        "SELECT id, created_at, temperature, humidite, pression, co2, humidite_surface, pluie_detectee, indice_uv "
        "FROM mesures ORDER BY id DESC LIMIT %s OFFSET %s"
    )

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (limit, offset))
            rows = cur.fetchall()
        return jsonify(rows), 200
    except Exception as e:
        # Provide more debug info (exception type)
        return jsonify(status='error', message=str(e), type=type(e).__name__), 500
    finally:
        conn.close()

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', port=port)
