export type Severity = "high" | "medium" | "low";

export type IssueCategory =
  | "Water Supply"
  | "Road Quality"
  | "Public Lighting"
  | "Waste Management";

export interface IssueCluster {
  id: string;
  title: string;
  severity: Severity;
  percentage: number;
}

export interface Hotspot {
  id: string;

  title: string;

  ward: string;

  latitude?: number;
  longitude?: number;

  x: number;
  y: number;

  severity: Severity;

  complaints: number;

  averageResolutionDays: number;

  dominantCategory: IssueCategory;

  priorityScore: number;

  recommendation: string;

  issues: IssueCluster[];
}

export interface HeatmapFilterState {
  categories: IssueCategory[];

  ward: string;

  timeRange: "30days" | "quarter";

  severity: Severity | "all";
}