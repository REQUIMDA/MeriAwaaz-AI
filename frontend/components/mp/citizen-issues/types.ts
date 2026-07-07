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
  | "In Progress"
  | "Resolved";

export interface CitizenIssue {
  id: string;

  title: string;

  description: string;

  citizen: {
    name: string;
  };

  ward: string;

  category: IssueCategory;

  priority: IssuePriority;

  status: IssueStatus;

  submittedAt: string;

  image?: string;

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