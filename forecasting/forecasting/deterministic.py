from datetime import date
from typing import List, Dict

def _pkb(params: Dict, year: int) -> float:
    potensi = float(params.get("PKB.potensi_awal", 0))
    pkb_baru = float(params.get("PKB.kend_baru_rp", 0))
    pencairan = float(params.get("PKB.pencairan_tunggakan", 0))
    mut_masuk = float(params.get("PKB.mutasi_masuk", 0))
    tdk_du = float(params.get("PKB.tidak_DU", 0))
    mut_keluar = float(params.get("PKB.mutasi_keluar", 0))
    return potensi + pkb_baru + pencairan + mut_masuk - tdk_du - mut_keluar

def _bbnkb(params: Dict, year: int) -> float:
    return float(params.get("BBNKB.total", 0))

def _pbbkb(params: Dict, year: int) -> float:
    return float(params.get("PBBKB.total", 0))

def _pap(params: Dict, year: int) -> float:
    return float(params.get("PAP.total", 0))

def _rokok(params: Dict, year: int) -> float:
    return float(params.get("ROKOK.alloc_DJPK", 0))

JENIS = ["PKB", "BBNKB", "PBBKB", "PAP", "ROKOK"]

def forecast_next_year_deterministic(year: int, params: Dict) -> List[Dict]:
    values = {
        "PKB": _pkb(params, year),
        "BBNKB": _bbnkb(params, year),
        "PBBKB": _pbbkb(params, year),
        "PAP": _pap(params, year),
        "ROKOK": _rokok(params, year),
    }
    out = []
    for j in JENIS:
        out.append({"periode": date(year, 12, 31), "jenis_pajak": j, "nilai": values[j], "model": "Konsep1"})
    return out
