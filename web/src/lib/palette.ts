export const PALETTE = {
  PKB: "#2563eb",
  BBNKB: "#10b981",
  PBBKB: "#f59e0b",
  PAP: "#ef4444",
  ROKOK: "#8b5cf6",
  baseline: "#1f2937",
  scenario: "#111827",
  gray: "#9ca3af"
};

export const ORDER = ["PKB","BBNKB","PBBKB","PAP","ROKOK"];
export const colorFor = (jenis: string) => (PALETTE as any)[jenis] || "#0ea5e9";
