import { useEffect, useMemo, useState } from "react";
import { Api, ParameterItem } from "../services/api";

export default function ParameterInspector(){
  const [params, setParams] = useState<ParameterItem[]>([]);
  const [q, setQ] = useState("");
  useEffect(()=>{ Api.listParameters().then(setParams).catch(()=>setParams([])); }, []);
  const filtered = useMemo(()=> params.filter(p => (p.param_key+ (p.source||'') + (p.owner||'')).toLowerCase().includes(q.toLowerCase())), [params, q]);
  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="flex items-end justify-between gap-3 mb-3">
        <div>
          <div className="text-sm font-semibold">Parameter Inspector</div>
          <div className="text-xs text-gray-500">Cari & audit parameter aktif</div>
        </div>
        <input className="border rounded p-2" placeholder="Cari..." value={q} onChange={e=>setQ(e.target.value)} />
      </div>
      <div className="overflow-auto max-h-96">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-gray-50">
            <tr>
              <th className="text-left p-2">Key</th>
              <th className="text-right p-2">Nilai</th>
              <th className="text-left p-2">Unit</th>
              <th className="text-left p-2">Source</th>
              <th className="text-left p-2">Owner</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p,i)=> (
              <tr key={i} className="border-t">
                <td className="p-2">{p.param_key}</td>
                <td className="p-2 text-right">{(p.value_num ?? (p.value_text ?? "")).toLocaleString?.() ?? (p.value_text ?? "")}</td>
                <td className="p-2">{p.unit || ""}</td>
                <td className="p-2">{p.source || ""}</td>
                <td className="p-2">{p.owner || ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
