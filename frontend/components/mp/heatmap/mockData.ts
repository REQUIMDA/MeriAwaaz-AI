import { Hotspot } from "./types";

export const hotspots: Hotspot[] = [
  {
    id: "1",
    title: "Sector 12 Hotspot",
    ward: "Ward 14",
    x: 35,
    y: 40,
    severity: "high",
    complaints: 142,
    averageResolutionDays: 8.4,
    dominantCategory: "Water Supply",
    priorityScore: 92,
    recommendation:
      "Deploy smart sensors in the main feeder line. Predictive analysis indicates an 82% probability of valve failure within the next 14 days.",
    issues: [
      {
        id: "1",
        title: "Water Contamination",
        severity: "high",
        percentage: 80,
      },
      {
        id: "2",
        title: "Power Fluctuations",
        severity: "medium",
        percentage: 40,
      },
    ],
  },

  {
    id: "2",
    title: "Old Town Market",
    ward: "Ward 18",
    x: 45,
    y: 70,
    severity: "high",
    complaints: 116,
    averageResolutionDays: 6.9,
    dominantCategory: "Road Quality",
    priorityScore: 88,
    recommendation:
      "Prioritize resurfacing of the primary access road and improve drainage before the monsoon season.",
    issues: [
      {
        id: "3",
        title: "Road Damage",
        severity: "high",
        percentage: 78,
      },
      {
        id: "4",
        title: "Traffic Congestion",
        severity: "medium",
        percentage: 46,
      },
    ],
  },

  {
    id: "3",
    title: "Gokuldham Colony",
    ward: "Ward 9",
    x: 60,
    y: 55,
    severity: "medium",
    complaints: 67,
    averageResolutionDays: 4.3,
    dominantCategory: "Waste Management",
    priorityScore: 61,
    recommendation:
      "Increase waste collection frequency and deploy an additional sanitation vehicle during weekends.",
    issues: [
      {
        id: "5",
        title: "Overflowing Bins",
        severity: "medium",
        percentage: 58,
      },
      {
        id: "6",
        title: "Illegal Dumping",
        severity: "low",
        percentage: 22,
      },
    ],
  },

  {
    id: "4",
    title: "North Junction",
    ward: "Ward 6",
    x: 75,
    y: 30,
    severity: "medium",
    complaints: 53,
    averageResolutionDays: 5.1,
    dominantCategory: "Public Lighting",
    priorityScore: 55,
    recommendation:
      "Replace faulty street lights and install smart lighting sensors for preventive maintenance.",
    issues: [
      {
        id: "7",
        title: "Street Light Failure",
        severity: "medium",
        percentage: 64,
      },
      {
        id: "8",
        title: "Unsafe Crossings",
        severity: "low",
        percentage: 29,
      },
    ],
  },
];