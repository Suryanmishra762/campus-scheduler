import { DoorOpen, Users, CalendarClock, Clock, CheckCircle2 } from 'lucide-react';
import StatCard from '../components/dashboard/StatCard';
import RecentBookings from '../components/dashboard/RecentBookings';
import QuickActions from '../components/dashboard/QuickActions';
import UpcomingExams from '../components/dashboard/UpcomingExams';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorAlert from '../components/ui/ErrorAlert';
import { useApi } from '../hooks/useApi';
import { fetchDatasetSummary, fetchRecentBookings } from '../services/api';
import type { DashboardStats, DatasetSummaryResponse, BookingRequest } from '../types';

interface DashboardPageProps {
  onNavigate?: (page: string) => void;
}

/** Map the backend summary response to the UI stat shape. */
function toStats(summary: DatasetSummaryResponse): DashboardStats {
  return {
    totalRooms: summary.counts.rooms,
    totalFaculty: summary.counts.faculty,
    activeSessions: summary.counts.sessions,
    pendingBookings: summary.counts.booking_requests,
  };
}

export default function DashboardPage({ onNavigate }: DashboardPageProps) {
  const {
    data: summary,
    loading: statsLoading,
    error: statsError,
    refetch: refetchStats,
  } = useApi(fetchDatasetSummary);

  const {
    data: liveBookings,
    loading: bookingsLoading,
    error: bookingsError,
    refetch: refetchBookings,
  } = useApi(fetchRecentBookings);

  const stats: DashboardStats | null = summary ? toStats(summary) : null;
  const bookings: BookingRequest[] = liveBookings ?? [];

  return (
    <div className="space-y-6">
      {/* Editorial Overview Header Banner */}
      <div className="bg-[#FFFDF8] rounded-[24px] border border-[#E8E1D5] p-5 sm:p-6 shadow-xs flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-[#B9D9C2]/35 border border-[#B9D9C2]/60 px-3 py-0.5 text-xs font-bold text-[#1B4D2E]">
              <CheckCircle2 size={13} />
              System Operational
            </span>
            <span className="text-xs text-[#75716B] font-medium hidden sm:inline">
              • Academic Calendar 2027
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-[#1E1E1E] mt-2 tracking-tight">
            Campus Operations Overview
          </h2>
          <p className="text-xs sm:text-sm text-[#75716B] mt-1 font-medium max-w-2xl">
            Live metrics from the official CIT dataset. Review room utilization, faculty schedules, and manage campus booking requests.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto shrink-0">
          <button
            type="button"
            onClick={() => onNavigate?.('timetable')}
            className="rounded-full bg-[#1E1E1E] hover:bg-black text-white px-4 py-2 text-xs font-semibold shadow-2xs transition-colors cursor-pointer"
          >
            Open Timetable
          </button>
        </div>
      </div>

      {/* Stats Error state */}
      {!statsLoading && statsError && (
        <ErrorAlert
          message={`Failed to load dashboard statistics: ${statsError}`}
          onRetry={refetchStats}
        />
      )}

      {/* Stats Grid */}
      {statsLoading ? (
        <div className="bg-[#FFFDF8] rounded-[24px] border border-[#E8E1D5] p-8 shadow-xs">
          <LoadingSpinner message="Loading dashboard statistics from backend…" />
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard
            title="Total Rooms"
            value={stats.totalRooms}
            icon={DoorOpen}
            trend={`${stats.totalRooms} campus facilities & labs`}
            color="blue"
          />
          <StatCard
            title="Faculty Members"
            value={stats.totalFaculty}
            icon={Users}
            trend={`${stats.totalFaculty} teaching professors & leads`}
            color="green"
          />
          <StatCard
            title="Active Sessions"
            value={stats.activeSessions}
            icon={CalendarClock}
            trend={`${stats.activeSessions} weekly curriculum slots`}
            color="yellow"
          />
          <StatCard
            title="Pending Bookings"
            value={stats.pendingBookings}
            icon={Clock}
            trend={`${stats.pendingBookings} venue reservation requests`}
            color="pink"
          />
        </div>
      ) : null}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Bookings — spans 2 columns */}
        <div className="lg:col-span-2">
          <RecentBookings
            bookings={bookings}
            loading={bookingsLoading}
            error={bookingsError}
            onRetry={refetchBookings}
            onNavigate={onNavigate}
          />
        </div>

        {/* Right Sidebar: Quick Actions & Upcoming Exams */}
        <div className="space-y-6">
          <QuickActions onNavigate={onNavigate} />
          <UpcomingExams onNavigate={onNavigate} />
        </div>
      </div>
    </div>
  );
}