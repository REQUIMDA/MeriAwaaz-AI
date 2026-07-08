import { create } from "zustand";
import type { SubmissionResponse } from "@/types/api";

export type { SubmissionResponse };

interface IssueState {
  // Complaint Details
  category: string;
  description: string;
  location: string;

  // Marked location (from the interactive map). Null when no pin is placed.
  locationLat: number | null;
  locationLng: number | null;

  // Attachments
  photo: File | null;
  audio: File | null;

  // Backend Response
  submissionId: string;
  status: string;
  response: SubmissionResponse | null;

  // Setters
  setCategory: (category: string) => void;
  setDescription: (description: string) => void;
  setLocation: (location: string) => void;
  setLocationCoords: (lat: number | null, lng: number | null) => void;

  setPhoto: (photo: File | null) => void;
  setAudio: (audio: File | null) => void;

  setSubmissionId: (submissionId: string) => void;
  setStatus: (status: string) => void;

  setResponse: (response: SubmissionResponse | null) => void;

  reset: () => void;
}

export const useIssueStore = create<IssueState>((set) => ({
  category: "",
  description: "",
  location: "",

  locationLat: null,
  locationLng: null,

  photo: null,
  audio: null,

  submissionId: "",
  status: "",
  response: null,

  setCategory: (category: string) => set({ category }),

  setDescription: (description: string) => set({ description }),

  setLocation: (location: string) => set({ location }),

  setLocationCoords: (locationLat: number | null, locationLng: number | null) =>
    set({ locationLat, locationLng }),

  setPhoto: (photo: File | null) => set({ photo }),

  setAudio: (audio: File | null) => set({ audio }),

  setSubmissionId: (submissionId: string) => set({ submissionId }),

  setStatus: (status: string) => set({ status }),

  setResponse: (response: SubmissionResponse | null) => set({ response }),

  reset: () =>
    set({
      category: "",
      description: "",
      location: "",
      locationLat: null,
      locationLng: null,

      photo: null,
      audio: null,

      submissionId: "",
      status: "",
      response: null,
    }),
}));
