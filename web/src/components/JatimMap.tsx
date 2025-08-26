import { useMemo } from "react";

type City = { name: string; lat: number; lon: number; value: number };

const CITIES: Omit<City, "value">[] = [
  { name: "Surabaya", lat: -7.2575, lon: 112.7521 },
  { name: "Sidoarjo", lat: -7.453, lon: 112.717 },
  { name: "Gresik", lat: -7.155, lon: 112.655 },
  { name: "Mojokerto", lat: -7.472, lon: 112.435 },
  { name: "Jombang", lat: -7.546, lon: 112.233 },
  { name: "Lamongan", lat: -7.119, lon: 112.416 },
  { name: "Bojonegoro", lat: -7.15, lon: 111.889 },
  { name: "Tuban", lat: -6.894, lon: 112.05 },
  { name: "Malang", lat: -7.983, lon: 112.621 },
  { name: "Batu", lat: -7.871, lon: 112.523 },
  { name: "Pasuruan", lat: -7.645, lon: 112.907 },
  { name: "Probolinggo", lat: -7.754, lon: 113.214 },
  { name: "Situbondo", lat: -7.706, lon: 113.951 },
  { name: "Bondowoso", lat: -7.913, lon: 113.82 },
  { name: "Jember", lat: -8.172, lon: 113.7 },
  { name: "Lumajang", lat: -8.133, lon: 113.226 },
  { name: "Banyuwangi", lat: -8.218, lon: 114.369 },
  { name: "Madiun", lat: -7.63, lon: 111.523 },
  { name: "Magetan", lat: -7.644, lon: 111.344 },
  { name: "Ngawi", lat: -7.401, lon: 111.446 },
  { name: "Ponorogo", lat: -7.866, lon: 111.466 },
  { name: "Trenggalek", lat: -8.089, lon: 111.717 },
  { name: "Tulungagung", lat: -8.065, lon: 111.901 },
  { name: "Kediri", lat: -7.816, lon: 112.011 },
  { name: "Blitar", lat: -8.098, lon: 112.167 },
  { name: "Sampang", lat: -7.19, lon: 113.241 },
  { name: "Pamekasan", lat: -7.156, lon: 113.474 },
  { name: "Sumenep", lat: -7.004, lon: 113.862 },
  { name: "Bangkalan", lat: -7.031, lon: 112.745 },
];

function project(lon: number, lat: number, width: number, height: number) {
  const minLon = 111.0, maxLon = 114.5;
  const minLat = -8.9,  maxLat = -6.7;
  const x = ((lon - minLon) / (maxLon - minLon)) * width;
  const y = (1 - ((lat - minLat) / (maxLat - minLat))) * height;
  return { x, y };
}

export default function JatimMap({ seed = 1 }: { seed?: number }) {
  const data: City[] = useMemo(() => {
    const rng = (i: number) => Math.abs(Math.sin(seed * 999 + i * 37.7));
    return CITIES.map((c, i) => ({ ...c, value: Math.round(5_000 + rng(i) * 95_000) }));
  }, [seed]);

  const width = 680, height = 420;
  const maxVal = Math.max(...data.map(d => d.value));
  const minVal = Math.min(...data.map(d => d.value));
  const denom = Math.max(maxVal - minVal, 1);

  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="text-sm font-semibold mb-2">Peta (Dummy) — Distribusi Per Kab/Kota</div>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-[420px] bg-blue-50 rounded">
        <polyline
          points="10,280 60,260 120,250 200,260 260,250 330,255 380,260 440,270 500,290 560,310 600,320 640,330"
          fill="none" stroke="#93c5fd" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round"
        />
        <polyline
          points="420,200 480,205 540,210 580,215"
          fill="none" stroke="#93c5fd" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round"
        />
        {data.map((d, i) => {
          const { x, y } = project(d.lon, d.lat, width, height);
          const r = 4 + 18 * ((d.value - minVal) / denom);
          return (
            <g key={i}>
              <circle cx={x} cy={y} r={r} fill="rgba(30,64,175,0.75)" />
              <text x={x + 6} y={y - 6} fontSize="10" fill="#111827">{d.name}</text>
            </g>
          );
        })}
        <g>
          <circle cx="40" cy="360" r="6" fill="rgba(30,64,175,0.75)" />
          <text x="55" y="364" fontSize="11" fill="#111827">Semakin besar lingkaran → nilai dummy lebih tinggi</text>
        </g>
      </svg>
    </div>
  );
}
