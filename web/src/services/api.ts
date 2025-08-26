import axios from "axios";

// pakai .env: VITE_API_BASE=http://127.0.0.1:8000  (fallback ke /api)
const API_BASE = ((import.meta as any).env?.VITE_API_BASE ?? "/api").replace(/\/$/, "");
const api = axios.create({ baseURL: API_BASE });

export interface Scenario {
  scenario_id: string;
  name: string;
  description?: string;
  overrides_json?: string;
}

export interface ForecastPoint {
  periode: string; // ISO date
  jenis_pajak: "PKB" | "BBNKB" | "PBBKB" | "PAP" | "ROKOK" | string;
  nilai: number;
}

export interface ExplainItem {
  jenis_pajak: string;
  formula: string;
  components: Record<string, number>; // base, macro_effect, policy_effect, final
}

export interface ForecastResponse {
  run_id: string;
  scenario_id?: string;
  points: ForecastPoint[];
  monthly: ForecastPoint[];
  explain: ExplainItem[];
  params_snapshot: Record<string, any>;
  overrides_applied: Record<string, any>;
}

export interface ParameterItem {
  param_key: string;
  value_num?: number;
  value_text?: string;
  unit?: string;
  source?: string;
  owner?: string;
  min_val?: number;
  max_val?: number;
}

export const Api = {
  listParameters: async () => {
    const r = await api.get("/parameters/");
    return Array.isArray(r.data) ? r.data : [];   // guard
  },
  listScenarios: async () => {
    const r = await api.get("/scenarios/");
    return Array.isArray(r.data) ? r.data : [];   // guard
  },
  runForecast: async (year: number, scenario_id?: string) => {
    const r = await api.post("/forecast/run", { year, scenario_id });
    return r.data;
  },
  reportUrl: (year: number, scenario_id?: string, fmt: "pdf"|"xlsx"|"csv"="pdf") => {
    const params = new URLSearchParams({ year: String(year), format: fmt });
    if (scenario_id) params.append("scenario_id", scenario_id);
    return `${API_BASE}/reports/apbd?${params.toString()}`;
  }
};

export default api;
