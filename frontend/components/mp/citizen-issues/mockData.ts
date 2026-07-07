import type {
  ActivityItem,
  CitizenIssue,
  IssueStats,
} from "./types";

export const issueStats: IssueStats = {
  total: 248,
  open: 82,
  inProgress: 109,
  resolved: 57,
};

export const issues: CitizenIssue[] = [
  {
    id: "ISS-8291",
    title: "Low Water Pressure in Ward 12",
    description:
      "Residents have reported consistently low water pressure over the past three days, making daily household activities difficult.",
    citizen: {
      name: "Ramesh Kumar",
    },
    ward: "Ward 12",
    category: "Water Supply",
    priority: "High",
    status: "In Progress",
    submittedAt: "24 Oct 2023",
    image: "",
    aiSummary:
      "Multiple complaints indicate an infrastructure issue affecting a large section of Ward 12.",
    aiSuggestedAction:
      "Inspect pumping station and nearby distribution pipeline within 24 hours.",
  },
  {
    id: "ISS-8288",
    title: "Highway Potholes",
    description:
      "Large potholes near the main highway junction are causing traffic congestion and vehicle damage.",
    citizen: {
      name: "Anjali Sharma",
    },
    ward: "Ward 14",
    category: "Roads",
    priority: "Critical",
    status: "Open",
    submittedAt: "23 Oct 2023",
    image: "",
    aiSummary:
      "Road quality complaints in Ward 14 have increased significantly during the past week.",
    aiSuggestedAction:
      "Deploy emergency road repair team before further road deterioration.",
  },
  {
    id: "ISS-8275",
    title: "Garbage Collection Delay",
    description:
      "Waste collection vehicles have not visited the locality for four consecutive days.",
    citizen: {
      name: "Priya Nair",
    },
    ward: "Ward 8",
    category: "Sanitation",
    priority: "Medium",
    status: "Resolved",
    submittedAt: "22 Oct 2023",
    image: "",
    aiSummary:
      "Temporary staffing shortage caused missed collection schedules.",
    aiSuggestedAction:
      "Increase collection frequency for the next week to clear backlog.",
  },
  {
    id: "ISS-8270",
    title: "Frequent Power Outages",
    description:
      "Power interruptions occur almost every evening between 6 PM and 8 PM.",
    citizen: {
      name: "Vikas Singh",
    },
    ward: "Ward 18",
    category: "Electricity",
    priority: "High",
    status: "In Progress",
    submittedAt: "21 Oct 2023",
    image: "",
    aiSummary:
      "Transformer load exceeds expected evening demand.",
    aiSuggestedAction:
      "Inspect transformer health and rebalance feeder loads.",
  },
  {
    id: "ISS-8265",
    title: "Medicine Shortage",
    description:
      "Essential medicines are unavailable at the district hospital pharmacy.",
    citizen: {
      name: "Sneha Patel",
    },
    ward: "Ward 3",
    category: "Healthcare",
    priority: "Critical",
    status: "Open",
    submittedAt: "20 Oct 2023",
    image: "",
    aiSummary:
      "Inventory depletion detected across multiple essential medicines.",
    aiSuggestedAction:
      "Trigger emergency procurement and redistribute stock from nearby facilities.",
  },
  {
    id: "ISS-8258",
    title: "School Drainage Overflow",
    description:
      "Drainage overflow outside the government school creates unsafe conditions during rain.",
    citizen: {
      name: "Amit Joshi",
    },
    ward: "Ward 6",
    category: "Drainage",
    priority: "Medium",
    status: "Open",
    submittedAt: "18 Oct 2023",
    image: "",
    aiSummary:
      "Blocked drainage line identified from historical maintenance records.",
    aiSuggestedAction:
      "Schedule desilting operation before the next rainfall.",
  },
];

export const recentActivity: ActivityItem[] = [
  {
    id: "1",
    issueId: "ISS-8291",
    title: "Issue Created",
    description: "Water pressure complaint submitted by citizen.",
    timestamp: "2 mins ago",
  },
  {
    id: "2",
    issueId: "ISS-8288",
    title: "Assigned",
    description: "Assigned to Roads Department.",
    timestamp: "24 mins ago",
  },
  {
    id: "3",
    issueId: "ISS-8270",
    title: "Status Updated",
    description: "Marked as In Progress.",
    timestamp: "1 hour ago",
  },
  {
    id: "4",
    issueId: "ISS-8275",
    title: "Issue Resolved",
    description: "Sanitation department closed the request.",
    timestamp: "Yesterday",
  },
];

export const categoryOptions = [
  "All Categories",
  "Water Supply",
  "Roads",
  "Drainage",
  "Electricity",
  "Healthcare",
  "Education",
  "Public Transport",
  "Sanitation",
];

export const wardOptions = [
  "All Wards",
  "Ward 1",
  "Ward 3",
  "Ward 6",
  "Ward 8",
  "Ward 12",
  "Ward 14",
  "Ward 18",
  "Ward 21",
];

export const priorityOptions = [
  "All Priorities",
  "Critical",
  "High",
  "Medium",
  "Low",
];

export const statusOptions = [
  "All Status",
  "Open",
  "In Progress",
  "Resolved",
];

export const sortOptions = [
  "Newest First",
  "Oldest First",
  "Priority",
  "Ward",
  "Category",
];

export const aiInsight = {
  title: "Road Complaint Spike Detected",
  description:
    "MeriAwaaz AI detected a 34% increase in road quality complaints from Ward 14 during the past seven days. Similar complaint descriptions indicate a likely common infrastructure issue. Prioritizing repair work in this ward could reduce recurring complaints.",
};