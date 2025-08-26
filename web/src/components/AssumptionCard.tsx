import React from 'react';
import { ForecastMeta } from '../services/api';

interface AssumptionCardProps {
  meta?: ForecastMeta;
}

// Helper to format numbers
const formatNumber = (num: number, precision = 2) => {
  if (num >= 1e12) return `${(num / 1e12).toFixed(precision)} T`;
  if (num >= 1e9) return `${(num / 1e9).toFixed(precision)} M`;
  if (num >= 1e6) return `${(num / 1e6).toFixed(precision)} Jt`;
  if (num >= 1e3) return `${(num / 1e3).toFixed(precision)} Rb`;
  return num.toFixed(precision);
};

const AssumptionCard: React.FC<AssumptionCardProps> = ({ meta }) => {
  if (!meta) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-md animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const { assumptions, model_weights, backtest, reconciliation, interval } = meta;

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-3 text-gray-700">Asumsi & Algoritma</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        {/* Section for Assumptions */}
        <div>
          <h3 className="font-semibold text-gray-600 border-b pb-1 mb-2">Asumsi Utama</h3>
          <ul className="list-disc list-inside space-y-1">
            <li>Base Total PAD: <span className="font-mono">{formatNumber(assumptions.base_total)}</span></li>
            <li>GDP Growth: <span className="font-mono">{(assumptions.gdp_growth * 100).toFixed(1)}%</span></li>
          </ul>
        </div>

        {/* Section for Model Weights */}
        <div>
          <h3 className="font-semibold text-gray-600 border-b pb-1 mb-2">Model Averaging</h3>
          <ul className="list-disc list-inside space-y-1">
            <li>Driver-Based: <span className="font-mono">{(model_weights.driver_based * 100).toFixed(1)}%</span> (MAPE: {backtest.driver_mape.toFixed(2)}%)</li>
            <li>Statistical (ETS): <span className="font-mono">{(model_weights.statistical_ets * 100).toFixed(1)}%</span> (MAPE: {backtest.stat_mape.toFixed(2)}%)</li>
          </ul>
        </div>

        {/* Section for Reconciliation */}
        <div>
          <h3 className="font-semibold text-gray-600 border-b pb-1 mb-2">Rekonsiliasi Hirarkis</h3>
          <ul className="list-disc list-inside space-y-1">
            <li>Metode: <span className="font-mono">{reconciliation.method}</span></li>
            <li>Total Awal: <span className="font-mono">{formatNumber(reconciliation.pre_total)}</span></li>
            <li>Total Akhir: <span className="font-mono">{formatNumber(reconciliation.post_total)}</span></li>
          </ul>
        </div>

        {/* Section for Prediction Interval */}
        <div>
          <h3 className="font-semibold text-gray-600 border-b pb-1 mb-2">Interval Prediksi (Total)</h3>
          <ul className="list-disc list-inside space-y-1">
            <li>P10 (Pesimis): <span className="font-mono">{formatNumber(interval.p10_total)}</span></li>
            <li>P50 (Median): <span className="font-mono">{formatNumber(interval.p50_total)}</span></li>
            <li>P90 (Optimis): <span className="font-mono">{formatNumber(interval.p90_total)}</span></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AssumptionCard;
