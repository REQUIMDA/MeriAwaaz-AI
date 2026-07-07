"use client";

import { useState } from "react";

import CitizenIssuesHeader from "@/components/mp/citizen-issues/CitizenIssuesHeader";
import SearchFilters from "@/components/mp/citizen-issues/SearchFilters";
import IssuesTable from "@/components/mp/citizen-issues/IssuesTable";
import IssueDrawer from "@/components/mp/citizen-issues/IssueDrawer";
import AIInsights from "@/components/mp/citizen-issues/AIInsights";
import RecentActivity from "@/components/mp/citizen-issues/RecentActivity";

import {
  aiInsight,
  categoryOptions,
  issueStats,
  issues,
  priorityOptions,
  recentActivity,
  sortOptions,
  statusOptions,
  wardOptions,
} from "@/components/mp/citizen-issues/mockData";

import type { CitizenIssue } from "@/components/mp/citizen-issues/types";

export default function CitizenIssuesPage() {
  const [search, setSearch] = useState("");

  const [category, setCategory] = useState(categoryOptions[0]);

  const [ward, setWard] = useState(wardOptions[0]);

  const [status, setStatus] = useState(statusOptions[0]);

  const [priority, setPriority] = useState(priorityOptions[0]);

  const [sort, setSort] = useState(sortOptions[0]);

  const [selectedIssue, setSelectedIssue] =
    useState<CitizenIssue | null>(null);

  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleView = (issue: CitizenIssue) => {
    setSelectedIssue(issue);
    setDrawerOpen(true);
  };

  const handleAssign = (issue: CitizenIssue) => {
    console.log("Assign", issue.id);
  };

  const handleResolve = (issue: CitizenIssue) => {
    console.log("Resolve", issue.id);
  };

  return (
    <>
      <CitizenIssuesHeader stats={issueStats} />

      <SearchFilters
        search={search}
        category={category}
        ward={ward}
        status={status}
        priority={priority}
        sort={sort}
        categoryOptions={categoryOptions}
        wardOptions={wardOptions}
        statusOptions={statusOptions}
        priorityOptions={priorityOptions}
        sortOptions={sortOptions}
        onSearchChange={setSearch}
        onCategoryChange={setCategory}
        onWardChange={setWard}
        onStatusChange={setStatus}
        onPriorityChange={setPriority}
        onSortChange={setSort}
      />

      <div className="grid grid-cols-1 gap-8 md:grid-cols-12">

        <div className="col-span-12">

          <IssuesTable
            issues={issues}
            onView={handleView}
            onAssign={handleAssign}
            onResolve={handleResolve}
          />

        </div>

        <div className="col-span-12 md:col-span-7">

          <AIInsights
            title={aiInsight.title}
            description={aiInsight.description}
          />

        </div>

        <div className="col-span-12 md:col-span-5">

          <RecentActivity
            activities={recentActivity}
          />

        </div>

      </div>

      <IssueDrawer
        issue={selectedIssue}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </>
  );
}