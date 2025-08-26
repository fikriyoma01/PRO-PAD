import React from "react";
import { Api } from "../services/api";

type Props = {
  year: number;
  scenario?: string; // jika undefined, backend pakai baseline
};

export default function DownloadReport({ year, scenario }: Props) {
  const urlPdf  = Api.reportUrl(year, scenario, "pdf");
  const urlXlsx = Api.reportUrl(year, scenario, "xlsx");
  const urlCsv  = Api.reportUrl(year, scenario, "csv");

  return (
    <div className="flex gap-2">
      <a href={urlPdf}  target="_blank" rel="noreferrer" className="px-3 py-2 bg-emerald-600 text-white rounded">Unduh PDF</a>
      <a href={urlXlsx} target="_blank" rel="noreferrer" className="px-3 py-2 bg-indigo-600 text-white rounded">Unduh XLSX</a>
      <a href={urlCsv}  target="_blank" rel="noreferrer" className="px-3 py-2 bg-gray-700 text-white rounded">Unduh CSV</a>
    </div>
  );
}
