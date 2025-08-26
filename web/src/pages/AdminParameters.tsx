import { useEffect, useMemo, useState } from "react";
import api, { Api, ParameterItem } from "../services/api";

type EditRow = ParameterItem & { _isNew?: boolean };

export default function AdminParameters(){
  const [rows, setRows] = useState<EditRow[]>([]);
  const [q, setQ] = useState("");

  const load = async ()=> {
    const data = await Api.listParameters();
    setRows(data);
  };
  useEffect(()=>{ load(); }, []);

  const filtered = useMemo(()=> rows.filter(r => (r.param_key + (r.source||'') + (r.owner||'')).toLowerCase().includes(q.toLowerCase())), [rows, q]);

  const updateRow = (idx: number, field: keyof EditRow, val: any)=> {
    setRows(prev => prev.map((r,i)=> i===idx ? { ...r, [field]: val } : r));
  };

  const saveRow = async (r: EditRow)=> {
    const payload = { ...r };
    await api.post("/parameters/", payload);
    await load();
    alert("Tersimpan");
  };

  const deleteRow = async (key: string)=> {
    if (!confirm("Hapus parameter ini?")) return;
    await api.delete(`/parameters/${encodeURIComponent(key)}`);
    await load();
  };

  const addNew = ()=> {
    setRows(prev => [{ param_key: "", value_num: undefined, value_text: "", unit: "Rp", source: "admin", owner: "admin", _isNew: true }, ...prev]);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between">
        <div>
          <div className="text-xl font-semibold">Parameter Editor (Admin)</div>
          <div className="text-xs text-gray-500">Tambah/Ubah/Hapus Parameter Registry</div>
        </div>
        <div className="flex items-center gap-2">
          <input className="border rounded p-2" placeholder="Cari..." value={q} onChange={e=>setQ(e.target.value)}/>
          <button className="px-3 py-2 rounded bg-blue-600 text-white" onClick={addNew}>+ Parameter</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl p-4 shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="text-left p-2">Key</th>
              <th className="text-right p-2">Value Num</th>
              <th className="text-left p-2">Value Text</th>
              <th className="text-left p-2">Unit</th>
              <th className="text-left p-2">Source</th>
              <th className="text-left p-2">Owner</th>
              <th className="text-right p-2">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r, idx)=> (
              <tr key={idx} className="border-t">
                <td className="p-2">
                  <input className="border rounded p-1 w-64" value={r.param_key} onChange={e=>updateRow(idx, "param_key", e.target.value)}/>
                </td>
                <td className="p-2 text-right">
                  <input className="border rounded p-1 w-40 text-right" value={r.value_num ?? ""} onChange={e=>updateRow(idx, "value_num", e.target.value === "" ? undefined : Number(e.target.value))}/>
                </td>
                <td className="p-2">
                  <input className="border rounded p-1 w-56" value={r.value_text ?? ""} onChange={e=>updateRow(idx, "value_text", e.target.value)}/>
                </td>
                <td className="p-2"><input className="border rounded p-1 w-20" value={r.unit ?? ""} onChange={e=>updateRow(idx, "unit", e.target.value)}/></td>
                <td className="p-2"><input className="border rounded p-1 w-24" value={r.source ?? ""} onChange={e=>updateRow(idx, "source", e.target.value)}/></td>
                <td className="p-2"><input className="border rounded p-1 w-24" value={r.owner ?? ""} onChange={e=>updateRow(idx, "owner", e.target.value)}/></td>
                <td className="p-2 text-right space-x-2">
                  <button className="px-2 py-1 bg-emerald-600 text-white rounded" onClick={()=>saveRow(r)}>Simpan</button>
                  <button className="px-2 py-1 bg-red-600 text-white rounded" onClick={()=>deleteRow(r.param_key)}>Hapus</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
