import { DoorOpen, Users, CalendarClock, Clock } from 'lucide-react';
import StatCard from '../components/dashboard/StatCard';
import RecentBookings from '../components/dashboard/RecentBookings';
import QuickActions from '../components/dashboard/QuickActions';
import UpcomingExams from '../components/dashboard/UpcomingExams';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorAlert from '../components/ui/ErrorAlert';
import { useApi } from '../hooks/useApi';
import { fetchDatasetSummary } from '../services/api';
import { dashboardStats as fallbackStats, recentBookings } from '../data/mockData';
import type { DashboardStats, DatasetSummaryResponse } from '../types';

/** Map the backend summary response to the UI stat shape. */
function toStats(summary: DatasetSummaryResponse): DashboardStats {
  return {
    totalRooms: summary.counts.rooms,
    totalFaculty: summary.counts.faculty,
    activeSessions: summary.counts.sessions,
    pendingBookings: summary.counts.booking_requests,
  };
}

export default function DashboardPage() {
  const {
    data: summary,
    loading,
    error,
    refetch,
  } = useApi(fetchDatasetSummary);

  // Use API data when available, otherwise fall back to mock data
  const stats: DashboardStats = summary ? toStats(summary) : fallbackStats;
  const isLive = !!summary;

  return (
    <div className="space-y-6">
      {/* API connection banner */}
      {!loading && error && (
        <ErrorAlert
          message={`${error}. Showing offline data.`}
          onRetry={refetch}
        />
      )}

      {/* Stats Grid */}
      {loading ? (
        <LoadingSpinner message="Loading dashboard statistics…" />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard
            title="Total Rooms"
            value={stats.totalRooms}
            icon={DoorOpen}
            trend={isLive ? `${stats.totalRooms} in dataset` : '3 under maintenance'}
            color="indigo"
          />
          <StatCard
            title="Faculty Members"
            value={stats.totalFaculty}
            icon={Users}
            trend={isLive ? `${stats.totalFaculty} registered` : '2 on leave today'}
            color="emerald"
          />
          <StatCard
            title="Active Sessions"
            value={stats.activeSessions}
            icon={CalendarClock}
            trend={isLive ? 'From dataset' : 'Week 5 of semester'}
            color="amber"
          />
          <StatCard
            title="Pending Bookings"
            value={stats.pendingBookings}
            icon={Clock}
            trend={isLive ? 'Booking requests' : '3 new today'}
            color="rose"
          />
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Bookings — spans 2 columns */}
        <div className="lg:col-span-2">
          <RecentBookings bookings={recentBookings} />
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          <QuickActions />
          <UpcomingExams />
        </div>
      </div>
    </div>
  );
}
