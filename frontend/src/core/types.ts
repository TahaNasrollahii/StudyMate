export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export enum StudyMode {
  SUMMARY = "summary",
  QUIZ = "quiz",
  PLAN = "plan",
}

export interface StudyRequestPayload {
  topic: string;
  mode: StudyMode;
}

export interface StudyResponseData {
  id: number;
  topic: string;
  mode: StudyMode;
  result: string;
  created_at: string;
}

export interface StudyHistoryResponse {
  results: StudyResponseData[];
}

export interface ErrorResponse {
  detail: string;
}
