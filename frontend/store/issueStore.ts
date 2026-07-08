import { create } from "zustand";

export interface SubmissionResponse {
  status: string;
  submission_id: string;
  photo_url?: string | null;
  audio_url?: string | null;
  recommendation?: unknown;
}

interface IssueState {
  // Complaint Details
  category: string;
  description: string;
  location: string;

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

  photo: null,
  audio: null,

  submissionId: "",
  status: "",
  response: null,

  setCategory: (category: string) => set({ category }),

  setDescription: (description: string) =>
    set({ description }),

  setLocation: (location: string) =>
    set({ location }),

  setPhoto: (photo: File | null) =>
    set({ photo }),

  setAudio: (audio: File | null) =>
    set({ audio }),

  setSubmissionId: (submissionId: string) =>
    set({ submissionId }),

  setStatus: (status: string) =>
    set({ status }),

  setResponse: (response: SubmissionResponse | null) =>
    set({ response }),

  reset: () =>
    set({
      category: "",
      description: "",
      location: "",

      photo: null,
      audio: null,

      submissionId: "",
      status: "",
      response: null,
    }),
}));