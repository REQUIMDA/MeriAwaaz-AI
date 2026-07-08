export type IssueCategory =
  | "Water Supply"
  | "Roads"
  | "Electricity"
  | "Healthcare"
  | "Sanitation"
  | "Education"
  | "Drainage"
  | "Public Transport";

export type IssuePriority =
  | "Low"
  | "Medium"
  | "High"
  | "Critical";

export type IssueStatus =
  | "Open"
  | "Assigned"
  | "In Progress"
  | "Resolved";

export interface CitizenIssue {
  id: string;

  // Stable backend id (full uuid) — used for assign/resolve tracking.
  rawId?: string;

  title: string;

  description: string;

  citizen: {
    name: string;
  };

  ward: string;

  category: IssueCategory;

  priority: IssuePriority;

  status: IssueStatus;

  assigned?: boolean;

  submittedAt: string;

  image?: string;

  audioUrl?: string;

  lat?: number | null;

  lng?: number | null;

  aiSummary: string;

  aiSuggestedAction: string;
}

export interface ActivityItem {
  id: string;

  issueId: string;

  title: string;

  description: string;

  timestamp: string;
}

export interface IssueStats {
  total: number;

  open: number;

  inProgress: number;

  resolved: number;
}

export interface IssueFilters {
  search: string;

  category: string;

  ward: string;

  status: string;

  priority: string;

  sort: string;
}