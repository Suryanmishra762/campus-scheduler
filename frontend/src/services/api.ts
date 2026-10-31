/* ──────────────────────────────────────────────
 *  API client — CIT Campus Scheduler
 *
 *  Thin wrapper around fetch(). Base URL is read
 *  from the VITE_API_BASE_URL env variable so it
 *  is never hardcoded in component code.
 * ────────────────────────────────────────────── */

import type {
  HealthResponse,
  DatasetSummaryResponse,
  DatasetInfoResponse,
  ScheduleGenerateResponse,
} from '../types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '';

/** Represents a structured error from the API layer. */
export class ApiError extends Error {
  status: number;
  detail?: string;

  constructor(message: string, status: number, detail?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

// ── Internal helpers ──────────────────────────

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let detail: string | undefined;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      detail = res.statusText;
    }
    throw new ApiError(
      `API request failed: ${res.status}`,
      res.status,
      detail,
    );
  }

  return res.json() as Promise<T>;
}

// ── Public API surface ────────────────────────

/** GET /api/health */
export function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health');
}

/**
 * GET /api/dataset/summary
 *
 * Returns counts for rooms, faculty, sessions,
 * booking_requests, exams, etc. — perfect for
 * populating the dashboard stat cards.
 */
export function fetchDatasetSummary(): Promise<DatasetSummaryResponse> {
  return request<DatasetSummaryResponse>('/api/dataset/summary');
}

/** GET /api/dataset */
export function fetchDatasetInfo(): Promise<DatasetInfoResponse> {
  return request<DatasetInfoResponse>('/api/dataset');
}

/**
 * POST /api/schedule/generate
 *
 * Triggers the CP-SAT solver. Can take up to
 * `timeLimitSeconds` to complete (default 120).
 */
export function generateSchedule(
  timeLimitSeconds: number = 120,
): Promise<ScheduleGenerateResponse> {
  return request<ScheduleGenerateResponse>(
    `/api/schedule/generate?time_limit_seconds=${timeLimitSeconds}`,
    { method: 'POST' },
  );
}
