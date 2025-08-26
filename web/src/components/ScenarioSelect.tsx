import { useEffect, useState } from "react";
import { Api, Scenario } from "../services/api";

export default function ScenarioSelect({value, onChange}:{value:string|undefined; onChange:(v:string|undefined)=>void}){
  const [list, setList] = useState<Scenario[]>([]);
  useEffect(()=>{
    Api.listScenarios().then(setList).catch(()=>setList([]));
  },[]);
  return (
    <div className="flex items-center gap-2">
      <label className="text-xs text-gray-500">Skenario</label>
      <select className="border rounded p-2" value={value ?? ""} onChange={e=>onChange(e.target.value||undefined)}>
        <option value="">baseline</option>
        {list.map(s=> <option key={s.scenario_id} value={s.scenario_id}>{s.name}</option>)}
      </select>
    </div>
  )
}
