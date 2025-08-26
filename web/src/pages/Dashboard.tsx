import { useEffect, useMemo, useState } from "react";
import { Api, ForecastPoint, ForecastResponse } from "../services/api";
import KPI from "../components/KPI";
import ScenarioSelect from "../components/ScenarioSelect";
import CompositionDonut from "../components/CompositionDonut";
import CompareBars from "../components/CompareBars";
import DownloadReport from "../components/DownloadReport";
import JatimMap from "../components/JatimMap";
import VarianceWaterfall from "../components/VarianceWaterfall";
import AssumptionCard from "../components/AssumptionCard";

function sum(points: ForecastPoint[]) { return points.reduce((a,b)=>a+b.nilai,0); }

export default function Dashboard(){
  const [year, setYear] = useState<number>(new Date().getFullYear()+1);
  const [scenario, setScenario] = useState<string|undefined>("baseline");
  const [baseline, setBaseline] = useState<ForecastPoint[]>([]);
  const [resp, setResp] = useState<ForecastResponse | null>(null);

  const totalBaseline = useMemo(()=> sum(baseline), [baseline]);
  const totalScenario = useMemo(()=> sum(resp?.points || []), [resp]);

  const runAll = async (y:number, sc?:string)=>{
    const [b, s] = await Promise.all([
      Api.runForecast(y, "baseline"),
      Api.runForecast(y, sc)
    ]);
    setBaseline(b.points);
    setResp(s);
  };

  useEffect(()=>{ runAll(year, scenario); }, [year, scenario]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-3">
        <div>
          <label className="block text-xs text-gray-500">Tahun</label>
          <input className="border rounded p-2" type="number" value={year} onChange={e=>setYear(parseInt(e.target.value))}/>
        </div>
        <ScenarioSelect value={scenario} onChange={setScenario} />
        <div className="ml-auto"><DownloadReport year={year} scenario={scenario}/></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KPI title="Total Baseline" value={totalBaseline} subtitle={`Forecast ${year}`}/>
        <KPI title={"Total " + (scenario || "Skenario")} value={totalScenario} subtitle={`Forecast ${year}`}/>
        <KPI title="Delta vs Baseline" value={totalScenario - totalBaseline} subtitle="(Skenario - Baseline)"/>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CompositionDonut points={resp?.points?.length ? resp.points : baseline} />
        <CompareBars baseline={baseline} scenario={resp?.points?.length ? resp.points : baseline} />
      </div>

      {/* Waterfall delta terhadap baseline */}
      <VarianceWaterfall
        baseline={baseline}
        scenario={resp?.points?.length ? resp.points : baseline}
      />

      <AssumptionCard meta={resp?.meta} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <JatimMap seed={year} />
        {/* Placeholder for another chart if needed */}
      </div>
    </div>
  );
}
