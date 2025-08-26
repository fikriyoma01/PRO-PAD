export default function ParamSnapshot({ snapshot }:{snapshot: Record<string, any>}) {
  const entries = Object.entries(snapshot || {});
  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="text-sm font-semibold mb-2">Parameter yang Dipakai</div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
        {entries.map(([k,v])=>(
          <div key={k} className="flex justify-between gap-4 border rounded px-2 py-1">
            <span className="text-gray-500">{k}</span>
            <span className="font-mono">{typeof v === 'number' ? new Intl.NumberFormat('id-ID').format(v) : String(v)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
