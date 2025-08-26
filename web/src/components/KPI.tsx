export default function KPI({title, value, subtitle}:{title:string;value:string|number;subtitle?:string}){
  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-2xl font-semibold">{typeof value === 'number' ? value.toLocaleString() : value}</div>
      {subtitle && <div className="text-xs text-gray-400">{subtitle}</div>}
    </div>
  );
}
