import os, json, datetime
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://propad:propad@localhost:5432/propad")

BASELINE = {
    "PKB.potensi_awal":      100_000_000_000,
    "PKB.kend_baru_rp":       25_000_000_000,
    "PKB.pencairan_tunggakan":5_000_000_000,
    "PKB.mutasi_masuk":        1_000_000_000,
    "PKB.tidak_DU":            3_000_000_000,
    "PKB.mutasi_keluar":       1_000_000_000,
    "BBNKB.total":            50_000_000_000,
    "PBBKB.total":            20_000_000_000,
    "PAP.total":               5_000_000_000,
    "ROKOK.alloc_DJPK":        3_000_000_000,
}

def ensure_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""        create table if not exists param_registry (
          param_key text primary key,
          value_num numeric,
          value_text text,
          unit text,
          min_val numeric,
          max_val numeric,
          source text,
          owner text,
          effective_from date,
          effective_to date,
          version int default 1,
          updated_by text,
          updated_at timestamp
        );""")
        cur.execute("""        create table if not exists forecast_run (
          run_id text primary key,
          created_at timestamp not null,
          scenario_id text not null,
          horizon_months int not null
        );""")
        cur.execute("""        create table if not exists forecast_result (
          run_id text not null,
          periode date not null,
          jenis_pajak text not null,
          nilai numeric not null,
          model_name text not null,
          version int not null,
          primary key (run_id, periode, jenis_pajak)
        );""")
        cur.execute("""        create table if not exists scenario (
          scenario_id text primary key,
          name text not null,
          description text,
          overrides_json text not null,
          created_by text not null,
          created_at timestamp not null,
          active boolean default true
        );""")
    conn.commit()

def upsert_params(conn, params: dict):
    with conn.cursor() as cur:
        for k,v in params.items():
            cur.execute("""                insert into param_registry (param_key, value_num, unit, source, owner, updated_at)
                values (%s, %s, %s, %s, %s, %s)
                on conflict (param_key) do update set value_num=excluded.value_num, updated_at=excluded.updated_at
            """, (k, float(v), 'Rp', 'seed', 'seed', datetime.datetime.utcnow()))
    conn.commit()

def create_scenario(conn, scenario_id: str, name: str, overrides: dict, desc: str):
    with conn.cursor() as cur:
        cur.execute("select 1 from scenario where scenario_id=%s", (scenario_id,))
        if cur.fetchone():
            cur.execute("update scenario set overrides_json=%s, name=%s, description=%s where scenario_id=%s",
                        (json.dumps(overrides), name, desc, scenario_id))
        else:
            cur.execute("""                insert into scenario (scenario_id, name, description, overrides_json, created_by, created_at, active)
                values (%s,%s,%s,%s,%s,%s,true)
            """, (scenario_id, name, desc, json.dumps(overrides), 'seed', datetime.datetime.utcnow()))
    conn.commit()

def main():
    conn = psycopg.connect(DATABASE_URL)
    ensure_tables(conn)
    upsert_params(conn, BASELINE)

    # Build overrides based on baseline
    opt = BASELINE.copy()
    opt["PKB.kend_baru_rp"] = round(opt["PKB.kend_baru_rp"] * 1.05)
    opt["BBNKB.total"]      = round(opt["BBNKB.total"] * 1.05)
    opt["PBBKB.total"]      = round(opt["PBBKB.total"] * 1.03)
    opt["PKB.tidak_DU"]     = round(opt["PKB.tidak_DU"] * 0.95)
    opt["PKB.mutasi_keluar"]= round(opt["PKB.mutasi_keluar"] * 0.95)

    pes = BASELINE.copy()
    pes["PKB.kend_baru_rp"] = round(pes["PKB.kend_baru_rp"] * 0.90)
    pes["BBNKB.total"]      = round(pes["BBNKB.total"] * 0.92)
    pes["PBBKB.total"]      = round(pes["PBBKB.total"] * 0.97)
    pes["PKB.tidak_DU"]     = round(pes["PKB.tidak_DU"] * 1.10)
    pes["PKB.mutasi_keluar"]= round(pes["PKB.mutasi_keluar"] * 1.10)

    create_scenario(conn, "baseline", "Baseline", {}, "Tanpa override (pakai Parameter Registry aktif)")
    create_scenario(conn, "optimis", "Optimis (+permintaan)", opt, "Unit kendaraan & BBM naik; loss menurun")
    create_scenario(conn, "pesimis", "Pesimis (perlambatan)", pes, "Unit kendaraan & BBM turun; loss naik")

    print("Seed selesai: baseline params + 3 skenario")
    conn.close()

if __name__ == "__main__":
    main()
