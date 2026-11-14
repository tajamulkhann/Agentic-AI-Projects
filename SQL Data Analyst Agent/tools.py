import sqlite3

def schema(db):
    with sqlite3.connect(f"file:{db}?mode=ro",uri=True) as con:
        return {r[0]:[x[1] for x in con.execute(f"PRAGMA table_info({r[0]})")] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}

def allowed_sql(statement):
    # App produces SQL only from its own vetted templates. Never execute user-generated freeform SQL.
    norm=statement.strip().upper()
    if not norm.startswith("SELECT ") or ";" in norm or "--" in norm or "/*" in norm:
        raise ValueError("Only a single allowlisted SELECT query is permitted")
    return statement

def query(db, statement, params=()):
    with sqlite3.connect(f"file:{db}?mode=ro",uri=True) as con:
        con.set_authorizer(lambda action,*args: sqlite3.SQLITE_OK if action in (sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION) else sqlite3.SQLITE_DENY)
        cur=con.execute(allowed_sql(statement),params)
        names=[d[0] for d in cur.description]
        return [dict(zip(names,row)) for row in cur.fetchmany(100)]
