# backend/scripts/seed_simulation.py
from __future__ import annotations
import os, json, math, random
from datetime import date
from typing import Dict, List, Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://propad:propad@localhost:5432/propad")
engine = create_engine(DATABASE_URL, future=True)

YEARS = list(range(2019, 2027))  # 2019–2026

# ---------- Helper UPSERT ----------
def upsert_parameter(conn, key: str, value_num=None, value_text=None, unit=None, source=None, owner="seed", min_val=None, max_val=None):
    conn.execute(
        text("""
        INSERT INTO parameters (param_key, value_num, value_text, unit, source, owner, min_val, max_val)
        VALUES (:k, :vn, :vt, :u, :s, :o, :minv, :maxv)
        ON CONFLICT (param_key) DO UPDATE SET
          value_num = EXCLUDED.value_num,
          value_text = EXCLUDED.value_text,
          unit = COALESCE(EXCLUDED.unit, parameters.unit),
          source = COALESCE(EXCLUDED.source, parameters.source),
          owner = COALESCE(EXCLUDED.owner, parameters.owner),
          min_val = COALESCE(EXCLUDED.min_val, parameters.min_val),
          max_val = COALESCE(EXCLUDED.max_val, parameters.max_val)
        """),
        {"k": key, "vn": value_num, "vt": value_text, "u": unit, "s": source, "o": owner, "minv": min_val, "maxv": max_val}
    )

def upsert_scenario(conn, scenario_id: str, name: str, description: str, overrides: dict):
    conn.execute(
        text("""
        INSERT INTO scenarios (scenario_id, name, description, overrides_json)
        VALUES (:id, :name, :desc, :ov)
        ON CONFLICT (scenario_id) DO UPDATE SET
          name = EXCLUDED.name,
          description = EXCLUDED.description,
          overrides_json = EXCLUDED.overrides_json
        """),
        {"id": scenario_id, "name": name, "desc": description, "ov": json.dumps(overrides, ensure_ascii=False)}
    )

def ensure_table(conn, ddl: str):
    conn.execute(text(ddl))

# ---------- Seed values ----------
def seed_scenarios(conn):
    # Parameter override keys dipakai oleh engine forecasting Anda
    baseline = {}
    optimis = {
        "gaikindo_multiplier": 1.05,
        "aisi_multiplier": 1.03,
        "pdrb_growth_bias_pp": +0.3,    # +0.3 p.p
        "inflasi_bias_pp": -0.2,        # -0.2 p.p
        "bi_rate_bias_pp": -0.25,       # -25 bps
        "tunggakan_collection_boost": 1.1,  # +10%
        "gdp_growth": 0.06, 
        "policy.PKB": 1.03, 
        "policy.BBNKB": 1.02
    }
    pesimis = {
        "gaikindo_multiplier": 0.90,
        "aisi_multiplier": 0.92,
        "pdrb_growth_bias_pp": -0.5,
        "inflasi_bias_pp": +0.4,
        "bi_rate_bias_pp": +0.5,
        "tunggakan_collection_boost": 0.9,
        "gdp_growth": 0.03, 
        "policy.PKB": 0.98, 
        "policy.BBNKB": 0.97
    }
    upsert_scenario(conn, "baseline", "Baseline", "Asumsi resmi & netral", baseline)
    upsert_scenario(conn, "optimis", "Optimis", "Permintaan kuat; kredit longgar; pertumbuhan di atas tren", optimis)
    upsert_scenario(conn, "pesimis", "Pesimis", "Permintaan melemah; kredit ketat; pertumbuhan di bawah tren", pesimis)

def seed_parameters_core(conn):
    # Market share Jatim (statis namun editable)
    upsert_parameter(conn, "market_share_r4_jatim", 0.085, unit="share", source="historical avg")
    upsert_parameter(conn, "market_share_r2_jatim", 0.1045, unit="share", source="historical avg")

    # Rasio operasional
    upsert_parameter(conn, "rasio_tidak_daftar_ulang", 0.12, unit="share/yr", source="historical")
    upsert_parameter(conn, "rasio_mutasi_keluar", 0.02, unit="share/yr", source="historical")
    upsert_parameter(conn, "rasio_mutasi_masuk", 0.018, unit="share/yr", source="historical")
    upsert_parameter(conn, "tunggakan_collection_rate", 0.35, unit="share/yr", source="historical")

    # Tarif & nilai rata-rata
    upsert_parameter(conn, "pbbkb_tarif", 0.05, unit="rate", source="regulatory")
    upsert_parameter(conn, "pkb_avg_per_unit_r2", 350_000, unit="IDR/unit", source="realisasi 2024 Q1")
    upsert_parameter(conn, "pkb_avg_per_unit_r4", 2_800_000, unit="IDR/unit", source="realisasi 2024 Q1")
    upsert_parameter(conn, "bbnkb_avg_per_unit_r2", 1_500_000, unit="IDR/unit", source="realisasi 2024 Q1")
    upsert_parameter(conn, "bbnkb_avg_per_unit_r4", 22_000_000, unit="IDR/unit", source="realisasi 2024 Q1")

    # Asumsi makro & target industri per tahun
    # Angka dibuat wajar untuk simulasi (bisa Anda ubah di Parameter Editor)
    # Format key: <prefix>_<tahun>
    gaikindo = {
        2019: 1000000, 2020: 530000, 2021: 850000, 2022: 1050000,
        2023: 1010000, 2024: 900000, 2025: 820000, 2026: 900000
    }
    aisi = {
        2019: 6500000, 2020: 3950000, 2021: 5200000, 2022: 5400000,
        2023: 5600000, 2024: 5200000, 2025: 5300000, 2026: 5450000
    }
    pdrb = {
        2019: 5.5, 2020: -2.5, 2021: 3.5, 2022: 5.2,
        2023: 5.1, 2024: 5.0, 2025: 5.1, 2026: 5.2
    }
    inflasi = {
        2019: 2.7, 2020: 1.7, 2021: 1.9, 2022: 5.5,
        2023: 3.0, 2024: 2.9, 2025: 3.0, 2026: 3.0
    }
    bi_rate = {
        2019: 5.00, 2020: 3.75, 2021: 3.50, 2022: 5.50,
        2023: 6.00, 2024: 6.25, 2025: 5.75, 2026: 5.50
    }
    for y in YEARS:
        upsert_parameter(conn, f"gaikindo_target_{y}", gaikindo[y], unit="unit/yr", source="simulasi")
        upsert_parameter(conn, f"aisi_target_{y}", aisi[y], unit="unit/yr", source="simulasi")
        upsert_parameter(conn, f"pdrb_growth_{y}", pdrb[y], unit="percent", source="simulasi")
        upsert_parameter(conn, f"inflasi_{y}", inflasi[y], unit="percent", source="simulasi")
        upsert_parameter(conn, f"bi_rate_{y}", bi_rate[y], unit="percent", source="simulasi")
        
        # === Tambahan: parameter transparan untuk engine ===
    bulk_params = []

    # total dasar & growth satu tahun ke depan
    bulk_params.extend([
        {"param_key": "base_total", "value_num": 3_200_000_000_000, "unit": "IDR", "source": "seed"},
        {"param_key": "gdp_growth", "value_num": 0.05, "unit": "ratio", "source": "seed"},
    ])

    # pangsa (harus kira-kira menjumlah 1.0, nanti engine akan normalisasi)
    for k, v in {"PKB": 0.34, "BBNKB": 0.27, "PBBKB": 0.22, "PAP": 0.07, "ROKOK": 0.10}.items():
        bulk_params.append({"param_key": f"share.{k}", "value_num": v, "unit": "share", "source": "seed"})

    # elastisitas terhadap pertumbuhan (nilai >1 responsif, <1 kurang responsif)
    for k, v in {"PKB": 1.10, "BBNKB": 0.95, "PBBKB": 0.85, "PAP": 0.70, "ROKOK": 0.60}.items():
        bulk_params.append({"param_key": f"elas.{k}", "value_num": v, "unit": "elas", "source": "seed"})

    # multiplier kebijakan (1.00 = netral; >1 dorong; <1 tekan)
    for k in ["PKB", "BBNKB", "PBBKB", "PAP", "ROKOK"]:
        bulk_params.append({"param_key": f"policy.{k}", "value_num": 1.00, "unit": "mult", "source": "seed"})

    # musiman bulanan (proporsi, jumlah ~1.0)
    seasonal = [0.077,0.078,0.082,0.083,0.086,0.090,0.092,0.090,0.087,0.081,0.078,0.076]
    for i, v in enumerate(seasonal, start=1):
        bulk_params.append({"param_key": f"seasonal.m{i:02d}", "value_num": v, "unit": "share", "source": "seed"})

    # simpan/UPSERT semuanya
    for p in bulk_params:
        upsert_parameter(conn,
            key=p["param_key"],
            value_num=p.get("value_num"),
            unit=p.get("unit"),
            source=p.get("source"),
            owner="seed"
        )

def seed_optional_domain_tables(conn):
    # Tabel mock untuk sumber data eksternal/operasional (tidak mengganggu engine)
    ensure_table(conn, """
    CREATE TABLE IF NOT EXISTS vehicle_targets (
      year int PRIMARY KEY,
      target_r4 int NOT NULL,
      target_r2 int NOT NULL
    );""")
    ensure_table(conn, """
    CREATE TABLE IF NOT EXISTS bbm_volume (
      year int,
      produk text,
      volume_kl numeric,
      PRIMARY KEY (year, produk)
    );""")
    ensure_table(conn, """
    CREATE TABLE IF NOT EXISTS rokok_allocation (
      year int PRIMARY KEY,
      alokasi_idr numeric
    );""")
    ensure_table(conn, """
    CREATE TABLE IF NOT EXISTS pap_skpd (
      year int,
      month int,
      nilai_idr numeric,
      PRIMARY KEY (year, month)
    );""")
    ensure_table(conn, """
    CREATE TABLE IF NOT EXISTS realisasi_bulanan (
      year int,
      month int,
      jenis_pajak text, -- PKB/BBNKB/PBBKB/PAP/ROKOK
      nilai_idr numeric,
      PRIMARY KEY (year, month, jenis_pajak)
    );""")

    # Isi data target kendaraan (mirror parameter di atas)
    for y in YEARS:
        conn.execute(
            text("""INSERT INTO vehicle_targets (year, target_r4, target_r2)
                    VALUES (:y, :r4, :r2)
                    ON CONFLICT (year) DO UPDATE SET target_r4=EXCLUDED.target_r4, target_r2=EXCLUDED.target_r2"""),
            {"y": y, "r4": int(0.085 * (1000000 if y==2019 else (820000 if y==2025 else 900000))),  # dummy prov share
             "r2": int(0.1045 * (6500000 if y==2019 else (5300000 if y==2025 else 5450000)))}
        )

    # Volume BBM (KL) per produk – angka dummy tapi proporsional
    produk = ["Pertalite", "Pertamax", "Solar", "Dexlite"]
    for y in YEARS:
        base = 6_000_000  # KL
        for i, p in enumerate(produk):
            vol = base * (0.55 if p == "Pertalite" else 0.20 if p == "Solar" else 0.20 if p=="Pertamax" else 0.05)
            vol *= (1.00 + 0.01*(y-2019))  # tren naik tipis
            conn.execute(
                text("""INSERT INTO bbm_volume (year, produk, volume_kl)
                        VALUES (:y, :p, :v)
                        ON CONFLICT (year, produk) DO UPDATE SET volume_kl=EXCLUDED.volume_kl"""),
                {"y": y, "p": p, "v": round(vol, 3)}
            )

    # Alokasi rokok (IDR) – dummy
    for y in YEARS:
        base = 2_200_000_000_000  # 2.2T baseline 2019
        drift = 1.02 ** (y - 2019)
        conn.execute(
            text("""INSERT INTO rokok_allocation (year, alokasi_idr)
                    VALUES (:y, :v)
                    ON CONFLICT (year) DO UPDATE SET alokasi_idr=EXCLUDED.alokasi_idr"""),
            {"y": y, "v": int(base * drift)}
        )

    # PAP SKPD bulanan (IDR) – flat-ish + musiman
    for y in YEARS:
        annual = 300_000_000_000  # 300 M
        for m in range(1, 13):
            seasonal = 1.0 + 0.12*math.sin((m/12)*2*math.pi)
            val = (annual/12) * seasonal
            conn.execute(
                text("""INSERT INTO pap_skpd (year, month, nilai_idr)
                        VALUES (:y, :m, :v)
                        ON CONFLICT (year, month) DO UPDATE SET nilai_idr=EXCLUDED.nilai_idr"""),
                {"y": y, "m": m, "v": int(val)}
            )

    # Realisasi bulanan per jenis pajak (IDR) – dummy konsisten baseline
    jenis = ["PKB", "BBNKB", "PBBKB", "PAP", "ROKOK"]
    random.seed(42)
    for y in YEARS:
        # target tahunan kasar (IDR)
        totals = {
            "PKB": 4_200_000_000_000,
            "BBNKB": 3_600_000_000_000,
            "PBBKB": 2_000_000_000_000,
            "PAP": 300_000_000_000,
            "ROKOK": 2_200_000_000_000,
        }
        for j in jenis:
            # distribusi musiman
            month_weights = [1 + 0.15*math.sin((m/12)*2*math.pi) for m in range(1, 13)]
            s = sum(month_weights)
            month_weights = [w/s for w in month_weights]
            for m, w in enumerate(month_weights, start=1):
                noise = 0.95 + 0.10*random.random()
                v = int(totals[j] * w * noise)
                conn.execute(
                    text("""INSERT INTO realisasi_bulanan (year, month, jenis_pajak, nilai_idr)
                            VALUES (:y, :m, :j, :v)
                            ON CONFLICT (year, month, jenis_pajak) DO UPDATE SET nilai_idr=EXCLUDED.nilai_idr"""),
                    {"y": y, "m": m, "j": j, "v": v}
                )

def main():
    print(f"Connecting to {DATABASE_URL}")
    with engine.begin() as conn:
        # pastikan tabel inti ada (sesuai skema backend Anda)
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS parameters (
          param_key text PRIMARY KEY,
          value_num numeric NULL,
          value_text text NULL,
          unit text NULL,
          source text NULL,
          owner text NULL,
          min_val numeric NULL,
          max_val numeric NULL
        );"""))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS scenarios (
          scenario_id text PRIMARY KEY,
          name text NOT NULL,
          description text NULL,
          overrides_json text NULL
        );"""))

        print("Seeding scenarios…")
        seed_scenarios(conn)
        print("Seeding parameter registry…")
        seed_parameters_core(conn)
        print("Seeding optional domain tables (mock)…")
        seed_optional_domain_tables(conn)

    print("DONE ✅  — simulasi data terpasang.")

if __name__ == "__main__":
    main()
