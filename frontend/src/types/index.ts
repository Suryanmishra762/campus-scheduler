/* ──────────────────────────────────────────────
 *  Types — CIT Campus Scheduler Frontend
 *
 *  Includes both UI-layer types and types that
 *  mirror the actual FastAPI response shapes.
 * ────────────────────────────────────────────── */

// ── Room (matches backend dataset.rooms[]) ──

export interface Room {
  id: string;
  name: string;
  building: string;
  type:
    | 'auditorium'
    | 'lecture_hall'
    | 'classroom'
    | 'seminar_hall'
    | 'outdoor'
    | 'lab_cs'
    | 'lab_elec'
    | 'lab_phy'
    | 'workshop'
    | 'lab_civil';
  capacity: number;
  features: string[];
  accessible: boolean;
  allowed_uses: string[];
}

// ── Faculty (matches backend dataset.faculty[]) ──

export interface FacultyUnavailability {
  day: string;
  periods: number[];
  reason: string;
}

export interface FacultyPreference {
  type: string;
  days: string[];
  periods: number[];
  note: string;
}

export interface Faculty {
  id: string;
  name: string;
  department: string;
  max_hours_per_day: number;
  needs_accessible: boolean;
  unavailable: FacultyUnavailability[];
  preferences: FacultyPreference[];
}

// ── Booking request (UI-layer shape for display) ──

export interface BookingRequest {
  id: string;
  title: string;
  requestedBy: string;
  role: 'faculty' | 'department_coordinator' | 'club' | 'admin';
  venue: string;
  date: string;
  timeSlot: string;
  status: 'pending' | 'approved' | 'rejected';
  category: 'guest_lecture' | 'department_event' | 'club_event' | 'institute_event';
  createdAt: string;
}

// ── Dashboard stats (UI-layer aggregate) ──

export interface DashboardStats {
  totalRooms: number;
  totalFaculty: number;
  activeSessions: number;
  pendingBookings: number;
}

// ── Navigation ──

export type PageId = 'dashboard' | 'timetable' | 'rooms' | 'faculty' | 'exams' | 'bookings';

// ══════════════════════════════════════════════
//  Backend API response types
//  (derived from inspecting the FastAPI routes)
// ══════════════════════════════════════════════

/** GET /api/health */
export interface HealthResponse {
  status: string;
  service: string;
}

/** GET /api/dataset/summary → get_dataset_summary() */
export interface DatasetSummaryResponse {
  dataset_id: string;
  institute: string;
  sections: number;
  counts: DatasetCounts;
  status: string;
}

export interface DatasetCounts {
  rooms: number;
  room_unavailability: number;
  faculty: number;
  student_groups: number;
  courses: number;
  sessions: number;
  booking_requests: number;
  cancellations: number;
  exams: number;
}

/** GET /api/dataset */
export interface DatasetInfoResponse {
  dataset_id: string;
  institute: string;
  calendar: DatasetCalendar;
  counts: DatasetCounts;
}

export interface DatasetCalendar {
  days: string[];
  periods: CalendarPeriod[];
  lunch: { after_period: number; start: string; end: string };
  lab_start_periods: number[];
  event_only_periods: number[];
  fest_week: string;
  exam_week: {
    days: string[];
    sessions: { id: string; start: string; end: string }[];
  };
}

export interface CalendarPeriod {
  id: number;
  start: string;
  end: string;
  teaching: boolean;
}

/** POST /api/schedule/generate */
export interface ScheduleGenerateResponse {
  success: boolean;
  status: string;
  message: string;
  scheduled: ScheduledSession[];
  unscheduled: UnscheduledSession[];
  diagnostics: ScheduleDiagnostics;
  solve_time_seconds: number;
}

export interface ScheduledSession {
  session_id: string;
  course_id: string;
  kind: string;
  groups: string[];
  faculty_id: string;
  day: string;
  period: number;
  duration: number;
  room_id: string;
  size: number;
}

export interface UnscheduledSession {
  session_id: string;
  reason: string;
}

export interface ScheduleDiagnostics {
  total_sessions: number;
  modelled_sessions: number;
  pre_infeasible: number;
  scheduled_count: number;
  unscheduled_count: number;
  objective_value: number | null;
  solver_status: string;
}
