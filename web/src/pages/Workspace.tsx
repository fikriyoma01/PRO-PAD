import { useEffect, useState } from "react";
import { Api, ForecastPoint } from "../services/api";
import ScenarioSelect from "../components/ScenarioSelect";
import ParameterInspector from "../components/ParameterInspector";
import DownloadReport from "../components/DownloadReport";

export default function Workspace(){
  const [year, setYear] = useState<number>(new Date().getFullYear()+1);
  const [scenario, setScenario] = useState<string|undefined>(undefined);
  const [points, setPoints] = useState<ForecastPoint[]>([]);
  const [creating, setCreating] = useState(false);
  const [newScenario, setNewScenario] = useState({ id: "", name: "", desc: "", overrides: "{}" });

  const runForecast = async ()=>{
    const res = await Api.runForecast(year, scenario);
    setPoints(res.points);
  };

  const createScenario = async ()=>{
    try{
      const overrides = JSON.parse(newScenario.overrides || "{}");
      await fetch("/api/scenarios/", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ scenario_id: newScenario.id, name: newScenario.name, description: newScenario.desc, overrides })
      });
      setCreating(false);
      alert("Skenario dibuat.");
    }catch(e:any){
      alert("Gagal membuat skenario: " + e.message);
    }
  };

  useEffect(()=>{ /* optional preload */ },[]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-3">
        <div>
          <label className="block text-xs text-gray-500">Tahun</label>
          <input className="border rounded p-2" type="number" value={year} onChange={e=>setYear(parseInt(e.target.value))}/>
        </div>
        <ScenarioSelect value={scenario} onChange={setScenario} />
        <button className="px-4 py-2 rounded bg-blue-600 text-white" onClick={runForecast}>Jalankan Proyeksi</button>
        <div className="ml-auto"><DownloadReport year={year} scenario={scenario}/></div>
      </div>

      <div className="bg-white rounded-2xl p-4 shadow">
        <div className="flex items-center justify-between mb-2">
          <div>
            <div className="text-sm font-semibold">Hasil Proyeksi</div>
            <div className="text-xs text-gray-500">Periode {year}-12-31</div>
          </div>
          <button className="px-3 py-2 rounded bg-gray-800 text-white" onClick={()=>setCreating(true)}>+ Buat Skenario</button>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead><tr><th className="text-left p-2">Jenis Pajak</th><th className="text-right p-2">Nilai</th></tr></thead>
            <tbody>
              {points.map((p,i)=> (
                <tr key={i} className="border-t">
                  <td className="p-2">{p.jenis_pajak}</td>
                  <td className="p-2 text-right">{p.nilai.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <ParameterInspector/>

      {creating && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white rounded-2xl p-4 shadow max-w-xl w-full space-y-3">
            <div className="text-lg font-semibold">Buat Skenario</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-gray-500">Scenario ID</label>
                <input className="border rounded p-2 w-full" value={newScenario.id} onChange={e=>setNewScenario({...newScenario, id:e.target.value})}/>
              </div>
              <div>
                <label className="text-xs text-gray-500">Nama</label>
                <input className="border rounded p-2 w-full" value={newScenario.name} onChange={e=>setNewScenario({...newScenario, name:e.target.value})}/>
              </div>
              <div className="md:col-span-2">
                <label className="text-xs text-gray-500">Deskripsi</label>
                <input className="border rounded p-2 w-full" value={newScenario.desc} onChange={e=>setNewScenario({...newScenario, desc:e.target.value})}/>
              </div>
              <div className="md:col-span-2">
                <label className="text-xs text-gray-500">Overrides (JSON)</label>
                <textarea className="border rounded p-2 w-full h-32" value={newScenario.overrides} onChange={e=>setNewScenario({...newScenario, overrides:e.target.value})}></textarea>
                <div className="text-xs text-gray-500 mt-1">Contoh: {"{"}"PKB.kend_baru_rp": 28000000000{"}"}</div>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <button className="px-3 py-2 rounded bg-gray-200" onClick={()=>setCreating(false)}>Batal</button>
              <button className="px-3 py-2 rounded bg-blue-600 text-white" onClick={createScenario}>Simpan</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
