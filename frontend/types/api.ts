// Types mirroring the MeriAwaaz AI backend (FastAPI) responses.
// Keep in sync with backend/app/schemas/*.py and backend/app/api/*.py.

export interface ScoreBreakdown {
  citizen_demand: number;    // 0-40
  severity: number;          // 0-30
  population_impact: number; // 0-20
  cost_feasibility: number;  // 0-10
}

export interface Explanation {
  evidence: string[];
  summary: string;
  confidence_score: number;
}

export interface Recommendation {
  project_id: string;
  title: string;
  priority_score: number; // 0-100
  breakdown: ScoreBreakdown;
  is_existing_plan_project: boolean;
  reason?: string | null;
  explanation?: Explanation | null;
}

export interface ProjectCard {
  id: string;
  title: string;
  category: string;
  priority_score: number;
  breakdown: ScoreBreakdown;
  is_existing_plan_project: boolean;
}

export interface DashboardData {
  projects: ProjectCard[];
  heatmap: unknown[];
  total_submissions: number;
  last_updated: string;
}

export interface RecommendationsResponse {
  items: Recommendation[];
}

// POST /api/submissions and /api/submissions/video response
export interface SubmissionResponse {
  status: "processed" | "degraded" | "stored" | string;
  submission_id: string;
  photo_url?: string | null;
  audio_url?: string | null;
  video_url?: string | null;
  error?: string | null;
  topics?: number;
  recommendation?: Recommendation | null;
  recommendations?: Recommendation[];
}

// GET /api/submissions (list) row
export interface SubmissionListItem {
  id: string;
  created_at: string;
  input_type: string;
  category?: string | null;
  location?: string | null;
  summary?: string | null;
  raw_text?: string | null;
  cluster_id?: string | null;
  priority_score?: number | null;
  photo_url?: string | null;
  audio_url?: string | null;
  video_url?: string | null;
  lat?: number | null;
  lng?: number | null;
  resolved?: boolean;
}

export interface SubmissionListResponse {
  items: SubmissionListItem[];
  total: number;
}

// GET /api/heatmap
export interface HeatmapProject {
  id: string;
  title: string;
  category: string;
  description?: string | null;
  explanation?: string | null;
  submission_count: number;
  population_affected: number;
  priority_score: number;
  breakdown: ScoreBreakdown;
  is_existing_plan_project: boolean;
}

export interface HeatmapTown {
  name: string;
  state: string;
  lat?: number | null;
  lng?: number | null;
  projects: HeatmapProject[];
}

export interface HeatmapData {
  towns: HeatmapTown[];
}

export interface SubmitIssueInput {
  text: string;
  category?: string;
  location?: string;
  lat?: number | null;
  lng?: number | null;
  photo?: File | null;
  audio?: File | null;
}
