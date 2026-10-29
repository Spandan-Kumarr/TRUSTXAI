"""Local-only persistence; never writes patient/case content into the Git checkout."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import sqlite3
import uuid
from .config import APP_DATA, DB_PATH


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connection():
    APP_DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    try:
        yield con
        con.commit()
    finally:
        con.close()


def initialize():
    with connection() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS cases (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, input_json TEXT NOT NULL,
          status TEXT NOT NULL, progress_json TEXT NOT NULL, result_json TEXT,
          error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted_at TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
          id TEXT PRIMARY KEY, case_id TEXT REFERENCES cases(id), role TEXT NOT NULL,
          kind TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS nli_cache (key TEXT PRIMARY KEY, scores_json TEXT NOT NULL);
        ''')


def decode(row):
    if row is None:
        return None
    data = dict(row)
    for key in ('input_json', 'progress_json', 'result_json'):
        value = data.pop(key)
        data[key.removesuffix('_json')] = json.loads(value) if value else None
    data.pop('deleted_at', None)
    return data


def create_case(payload):
    identifier, stamp = str(uuid.uuid4()), now()
    title = payload.get('title') or ' '.join(payload['case_text'].split()[:8]).rstrip('.!?')
    with connection() as con:
        con.execute('INSERT INTO cases VALUES (?,?,?,?,?,?,?,?,?,NULL)',
                    (identifier, title[:100], json.dumps(payload), 'queued',
                     json.dumps({'stage': 'queued', 'detail': 'Waiting for the local model', 'percent': 0}),
                     None, None, stamp, stamp))
    return get_case(identifier)


def get_case(identifier):
    with connection() as con:
        return decode(con.execute('SELECT * FROM cases WHERE id=? AND deleted_at IS NULL', (identifier,)).fetchone())


def list_cases():
    with connection() as con:
        return [dict(row) for row in con.execute('SELECT id,title,status,created_at,updated_at FROM cases WHERE deleted_at IS NULL ORDER BY created_at DESC')]


def update_case(identifier, *, status=None, progress=None, result=None, error=None):
    values = {'updated_at': now()}
    if status is not None: values['status'] = status
    if progress is not None: values['progress_json'] = json.dumps(progress)
    if result is not None: values['result_json'] = json.dumps(result, ensure_ascii=False)
    if error is not None: values['error'] = error
    with connection() as con:
        keys = list(values)
        con.execute('UPDATE cases SET '+','.join(key+'=?' for key in keys)+' WHERE id=? AND deleted_at IS NULL',
                    [values[key] for key in keys]+[identifier])


def delete_case(identifier):
    with connection() as con:
        con.execute('UPDATE cases SET deleted_at=?,updated_at=? WHERE id=?', (now(), now(), identifier))


def add_message(case_id, role, kind, payload):
    identifier = str(uuid.uuid4())
    with connection() as con:
        con.execute('INSERT INTO messages VALUES (?,?,?,?,?,?)',
                    (identifier, case_id, role, kind, json.dumps(payload, ensure_ascii=False), now()))
    return identifier


def messages(case_id):
    with connection() as con:
        result = []
        for row in con.execute('SELECT * FROM messages WHERE case_id=? ORDER BY created_at,rowid', (case_id,)):
            data = dict(row); data['payload'] = json.loads(data.pop('payload_json')); result.append(data)
        return result


def cached_score(key):
    with connection() as con:
        row = con.execute('SELECT scores_json FROM nli_cache WHERE key=?', (key,)).fetchone()
        return json.loads(row[0]) if row else None


def save_scores(values):
    with connection() as con:
        con.executemany('INSERT OR REPLACE INTO nli_cache VALUES (?,?)',
                        [(key, json.dumps(score)) for key, score in values])


def discard_case(identifier):
    """Rollback a newly created request that was not admitted to the worker queue."""
    with connection() as con:
        con.execute('DELETE FROM messages WHERE case_id=?', (identifier,))
        con.execute('DELETE FROM cases WHERE id=?', (identifier,))


def discard_message(identifier):
    with connection() as con:
        con.execute('DELETE FROM messages WHERE id=?', (identifier,))
