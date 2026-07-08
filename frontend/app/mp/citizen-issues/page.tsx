"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import CitizenIssuesHeader from "@/components/mp/citizen-issues/CitizenIssuesHeader";
import SearchFilters from "@/components/mp/citizen-issues/SearchFilters";
import IssuesTable from "@/components/mp/citizen-issues/IssuesTable";
import IssueDrawer from "@/components/mp/citizen-issues/IssueDrawer";
import AIInsights from "@/components/mp/citizen-issues/AIInsights";
import RecentActivity from "@/components/mp/citizen-issues/RecentActivity";

import type {
  ActivityItem,
  CitizenIssue,
  IssueCategory,
  IssuePriority,
  IssueStatus,
} from "@/components/mp/citizen-issues/types";

import { API_BASE, listSubmissions, resolveSubmissions } from "@/services/api";
import type { SubmissionListItem } from "@/types/api";

// ── ward canonicalisation (merge typos / case / Hindi → one ward) ────────
const HINDI_WARD: Record<string, string> = {
  "केसरपुर": "kesarpur",
  "रामपुर": "rampur",
  "सुल्तानपुर": "sultanpur",
  "सुलतानपुर": "sultanpur",
  "भेलूपुर": "bhelupur",
  "भेलुपुर": "bhelupur",
  "नागपुर": "nagpur",
  "खंडवा": "khandwa",
  "महाराष्ट्र": "maharashtra",
};
const KNOWN_WARDS = ["kesarpur", "rampur", "sultanpur", "bhelupur", "nagpur", "khandwa", "maharashtra"];

function levenshtein(a: string, b: string): number {
  const m = a.length;
  const n = b.length;
  const d: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) d[i][0] = i;
  for (let j = 0; j <= n; j++) d[0][j] = j;
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost);
    }
  return d[m][n];
}
function titleCase(s: string): string {
  return s.split(/\s+/).map((w) => (w ? w[0].toUpperCase() + w.slice(1) : w)).join(" ");
}
function canonicalWard(loc?: string | null): string {
  const rawTrim = (loc || "").trim();
  if (!rawTrim || rawTrim.toLowerCase() === "unspecified") return "Unspecified";
  let key = HINDI_WARD[rawTrim] || rawTrim.toLowerCase();
  key = key.replace(/[^\p{L}\s]/gu, " ").replace(/\s+/g, " ").trim();
  if (!key) return "Unspecified";
  for (const token of key.split(" ")) {
    for (const known of KNOWN_WARDS) {
      const tol = Math.max(1, Math.floor(known.length / 3));
      if (levenshtein(token, known) <= tol) return titleCase(known);
    }
  }
  return titleCase(key);
}

// ── other mapping ────────────────────────────────────────────────────────
const CATEGORY_MAP: Record<string, IssueCategory> = {
  Water: "Water Supply",
  Roads: "Roads",
  Electricity: "Electricity",
  Healthcare: "Healthcare",
  Sanitation: "Sanitation",
  Education: "Education",
  Vocational: "Education",
  Other: "Public Transport",
};
function mapCategory(c?: string | null): IssueCategory {
  return (c && CATEGORY_MAP[c]) || "Roads";
}
function priorityFromScore(score?: number | null): IssuePriority {
  if (score == null) return "Medium";
  if (score >= 55) return "Critical";
  if (score >= 40) return "High";
  if (score >= 25) return "Medium";
  return "Low";
}
function fmtDate(iso: string): string {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}
function relative(iso: string): string {
  const t = new Date(iso).getTime();
  if (isNaN(t)) return "";
  const m = Math.floor((Date.now() - t) / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m} min ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

// Assignment is an MP-side UI marker with no backend field → keep in localStorage.
// (Resolution is a real backend state that affects the dashboard/map.)
const ASSIGNED_KEY = "mp_assigned_ids";
function loadIds(key: string): string[] {
  try {
    return JSON.parse(localStorage.getItem(key) || "[]");
  } catch {
    return [];
  }
}
function saveIds(key: string, ids: string[]) {
  try {
    localStorage.setItem(key, JSON.stringify(ids));
  } catch {
    /* ignore */
  }
}

const STATUS_OPTIONS = ["All Status", "Open", "Assigned", "Resolved"];
const PRIORITY_OPTIONS = ["All Priorities", "Critical", "High", "Medium", "Low"];
const SORT_OPTIONS = ["Newest First", "Oldest First", "Priority"];

export default function CitizenIssuesPage() {
  const [raw, setRaw] = useState<SubmissionListItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [assignedIds, setAssignedIds] = useState<string[]>([]);

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All Categories");
  const [ward, setWard] = useState("All Wards");
  const [status, setStatus] = useState(STATUS_OPTIONS[0]);
  const [priority, setPriority] = useState(PRIORITY_OPTIONS[0]);
  const [sort, setSort] = useState(SORT_OPTIONS[0]);

  const [selectedIssue, setSelectedIssue] = useState<CitizenIssue | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => setAssignedIds(loadIds(ASSIGNED_KEY)), []);

  const refresh = useCallback(async () => {
    try {
      const r = await listSubmissions(200);
      setRaw(r.items);
      setError(null);
    } catch (e) {
      setError(String((e as Error).message || e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const assignedSet = useMemo(() => new Set(assignedIds), [assignedIds]);

  const allIssues: CitizenIssue[] = useMemo(() => {
    return raw.map((item) => {
      const resolved = !!item.resolved;
      const assigned = !resolved && assignedSet.has(item.id);
      const issueStatus: IssueStatus = resolved ? "Resolved" : assigned ? "Assigned" : "Open";
      const title = item.summary || item.raw_text || "Citizen submission";
      return {
        id: item.id.slice(0, 8).toUpperCase(),
        rawId: item.id,
        title: title.length > 90 ? title.slice(0, 90) + "…" : title,
        description: item.raw_text || item.summary || "",
        citizen: { name: "Anonymous Citizen" },
        ward: canonicalWard(item.location),
        category: mapCategory(item.category),
        priority: priorityFromScore(item.priority_score),
        status: issueStatus,
        assigned,
        submittedAt: fmtDate(item.created_at),
        image: item.photo_url ? `${API_BASE}${item.photo_url}` : "",
        audioUrl: item.audio_url ? `${API_BASE}${item.audio_url}` : "",
        lat: item.lat ?? null,
        lng: item.lng ?? null,
        aiSummary: item.summary || "",
        aiSuggestedAction:
          item.priority_score != null
            ? `Linked to a project scoring ${Math.round(item.priority_score)}/100 — review on the heatmap.`
            : "Awaiting AI scoring.",
      };
    });
  }, [raw, assignedSet]);

  const categoryOptions = useMemo(
    () => ["All Categories", ...Array.from(new Set(allIssues.map((i) => i.category))).sort()],
    [allIssues]
  );
  const wardOptions = useMemo(
    () => ["All Wards", ...Array.from(new Set(allIssues.map((i) => i.ward))).sort()],
    [allIssues]
  );

  const issues = useMemo(() => {
    let list = allIssues;
    if (status === "All Status") list = list.filter((i) => i.status !== "Resolved");
    else list = list.filter((i) => i.status === status);

    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (i) =>
          i.id.toLowerCase().includes(q) ||
          i.title.toLowerCase().includes(q) ||
          i.description.toLowerCase().includes(q) ||
          i.ward.toLowerCase().includes(q)
      );
    }
    if (category !== "All Categories") list = list.filter((i) => i.category === category);
    if (ward !== "All Wards") list = list.filter((i) => i.ward === ward);
    if (priority !== "All Priorities") list = list.filter((i) => i.priority === priority);

    const rank: Record<IssuePriority, number> = { Critical: 3, High: 2, Medium: 1, Low: 0 };
    if (sort === "Priority") list = [...list].sort((a, b) => rank[b.priority] - rank[a.priority]);
    else if (sort === "Oldest First") list = [...list].reverse();
    return list;
  }, [allIssues, status, search, category, ward, priority, sort]);

  const stats = useMemo(() => {
    const total = allIssues.length;
    const open = allIssues.filter((i) => i.status === "Open").length;
    const inProgress = allIssues.filter((i) => i.status === "Assigned").length;
    const resolved = allIssues.filter((i) => i.status === "Resolved").length;
    return { total, open, inProgress, resolved };
  }, [allIssues]);

  const aiInsight = useMemo(() => {
    const active = allIssues.filter((i) => i.status !== "Resolved");
    if (!active.length) {
      return {
        title: "Awaiting citizen submissions",
        description:
          "Once citizens submit issues, MeriAwaaz AI surfaces the dominant demand clusters and recommended actions here.",
      };
    }
    const counts: Record<string, number> = {};
    for (const i of active) counts[i.category] = (counts[i.category] || 0) + 1;
    const [topCat, n] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
    const pct = Math.round((n / active.length) * 100);
    return {
      title: `${topCat} is the dominant demand`,
      description: `${topCat} accounts for ${pct}% of the ${active.length} active citizen submissions. Similar complaints are clustered into ranked projects — prioritising this category is likely to reduce recurring issues.`,
    };
  }, [allIssues]);

  const recentActivity: ActivityItem[] = useMemo(
    () =>
      raw.slice(0, 5).map((r) => ({
        id: r.id,
        issueId: r.id.slice(0, 8).toUpperCase(),
        title: r.resolved
          ? "Issue resolved"
          : assignedSet.has(r.id)
          ? "Issue assigned"
          : "Issue submitted",
        description: r.summary || r.raw_text || "New citizen submission",
        timestamp: relative(r.created_at),
      })),
    [raw, assignedSet]
  );

  // ── actions ──────────────────────────────────────────────────────────
  const handleView = (issue: CitizenIssue) => {
    setSelectedIssue(issue);
    setDrawerOpen(true);
  };

  const handleAssign = (issue: CitizenIssue) => {
    if (!issue.rawId) return;
    setAssignedIds((prev) => {
      if (prev.includes(issue.rawId!)) return prev;
      const next = [...prev, issue.rawId!];
      saveIds(ASSIGNED_KEY, next);
      return next;
    });
  };

  const resolveMany = useCallback(
    async (ids: string[]) => {
      const real = ids.filter(Boolean);
      if (!real.length) return;
      // Optimistic: hide immediately, then persist + reconcile.
      setRaw((prev) => prev.map((r) => (real.includes(r.id) ? { ...r, resolved: true } : r)));
      setDrawerOpen(false);
      try {
        await resolveSubmissions(real);
      } catch (e) {
        console.error(e);
      }
      refresh();
    },
    [refresh]
  );

  const handleResolve = (issue: CitizenIssue) => {
    if (issue.rawId) resolveMany([issue.rawId]);
  };

  const handleResolveAll = () => {
    const ids = issues.filter((i) => i.status !== "Resolved" && i.rawId).map((i) => i.rawId!);
    if (!ids.length) return;
    if (
      typeof window !== "undefined" &&
      !window.confirm(`Resolve all ${ids.length} shown complaint(s)? Fully-resolved clusters leave the dashboard and map.`)
    )
      return;
    resolveMany(ids);
  };

  const resolvableShown = issues.filter((i) => i.status !== "Resolved").length;

  return (
    <>
      <CitizenIssuesHeader stats={stats} />

      {error && (
        <div className="mb-6 rounded-2xl border border-[#FFDAD6] bg-[#FFF3F2] p-4 text-sm text-[#BA1A1A]">
          Could not reach the backend ({error}). Start the API at{" "}
          <code>http://localhost:8000</code> and refresh.
        </div>
      )}

      <SearchFilters
        search={search}
        category={category}
        ward={ward}
        status={status}
        priority={priority}
        sort={sort}
        categoryOptions={categoryOptions}
        wardOptions={wardOptions}
        statusOptions={STATUS_OPTIONS}
        priorityOptions={PRIORITY_OPTIONS}
        sortOptions={SORT_OPTIONS}
        onSearchChange={setSearch}
        onCategoryChange={setCategory}
        onWardChange={setWard}
        onStatusChange={setStatus}
        onPriorityChange={setPriority}
        onSortChange={setSort}
      />

      {/* Bulk action for the current filter */}
      {!loading && resolvableShown > 0 && (
        <div className="mb-6 flex items-center justify-between rounded-2xl border border-[#C3C7CC]/40 bg-white px-6 py-4">
          <p className="text-sm text-[#43474B]">
            <span className="font-bold text-black">{resolvableShown}</span> complaint(s) match the
            current filter.
          </p>
          <button
            onClick={handleResolveAll}
            className="flex items-center gap-2 rounded-xl bg-[#1C7C33] px-4 py-2 text-sm font-bold text-white transition hover:opacity-90"
          >
            <span className="material-symbols-outlined text-[18px]">done_all</span>
            Resolve all shown
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 gap-8 md:grid-cols-12">
        <div className="col-span-12">
          {loading ? (
            <div className="glass-card bento-item rounded-[24px] p-10 text-center text-[#43474B]">
              Loading citizen issues…
            </div>
          ) : (
            <IssuesTable
              issues={issues}
              onView={handleView}
              onAssign={handleAssign}
              onResolve={handleResolve}
            />
          )}
        </div>

        <div className="col-span-12 md:col-span-7">
          <AIInsights title={aiInsight.title} description={aiInsight.description} />
        </div>

        <div className="col-span-12 md:col-span-5">
          <RecentActivity activities={recentActivity} />
        </div>
      </div>

      <IssueDrawer issue={selectedIssue} open={drawerOpen} onClose={() => setDrawerOpen(false)} />
    </>
  );
}
