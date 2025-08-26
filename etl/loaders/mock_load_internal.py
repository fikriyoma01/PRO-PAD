import os, csv, pathlib
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://propad:propad@localhost:5432/propad")
BASE = pathlib.Path(__file__).parent.parent / "data"

def ensure_raw_tables(conn):
    with conn.cursor() as cur:
        cur.execute("create schema if not exists raw;")
        cur.execute("""        create table if not exists raw.realisasi_pajak (
          tanggal date,
          jenis_pajak text,
          nilai numeric
        );""")
        cur.execute("""        create table if not exists raw.pjk05 (
          periode date,
          segmen text,
          nilai numeric
        );""")
        cur.execute("""        create table if not exists raw.unit_kendaraan (
          periode date,
          segmen text,
          unit int,
          avg_ticket numeric
        );""")
    conn.commit()

def load_csv(conn, table, filename, cols):
    path = BASE / filename
    assert path.exists(), f"{path} not found"
    with conn.cursor() as cur, open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [tuple(r[c] for c in cols) for r in reader]
        # truncate then insert for simple mock
        cur.execute(f"truncate table {table};")
        args = ','.join(['%s'] * len(cols))
        cur.executemany(f"insert into {table} ({','.join(cols)}) values ({args})", rows)
    conn.commit()
    print(f"Loaded {len(rows)} rows into {table}")

def main():
    conn = psycopg.connect(DATABASE_URL)
    ensure_raw_tables(conn)
    load_csv(conn, "raw.realisasi_pajak", "mock_realisasi_pajak.csv", ["tanggal","jenis_pajak","nilai"])
    load_csv(conn, "raw.pjk05", "mock_pjk05.csv", ["periode","segmen","nilai"])
    load_csv(conn, "raw.unit_kendaraan", "mock_unit_kendaraan.csv", ["periode","segmen","unit","avg_ticket"])
    conn.close()
    print("Mock internal data loaded.")
if __name__ == "__main__":
    main()
