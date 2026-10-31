import { useState } from 'react';
import { CalendarCheck, Check, X, Filter } from 'lucide-react';
import { recentBookings } from '../data/mockData';

const statusTabs = ['All', 'Pending', 'Approved', 'Rejected'] as const;

const statusStyles: Record<string, string> = {
  pending: 'bg-amber-50 text-amber-700 ring-1 ring-amber-600/20',
  approved: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20',
  rejected: 'bg-rose-50 text-rose-700 ring-1 ring-rose-600/20',
};

const categoryStyles: Record<string, string> = {
  guest_lecture: 'bg-indigo-50 text-indigo-700',
  club_event: 'bg-violet-50 text-violet-700',
  workshop: 'bg-cyan-50 text-cyan-700',
  seminar: 'bg-emerald-50 text-emerald-700',
  meeting: 'bg-slate-100 text-slate-700',
  cultural: 'bg-pink-50 text-pink-700',
  sports: 'bg-orange-50 text-orange-700',
  exam: 'bg-amber-50 text-amber-700',
};

function formatCategory(category: string): string {
  return category
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export default function BookingsPage() {
  const [activeTab, setActiveTab] = useState<string>('All');

  const filteredBookings = recentBookings.filter((booking) => {
    if (activeTab === 'All') return true;
    return booking.status.toLowerCase() === activeTab.toLowerCase();
  });

  const pendingCount = recentBookings.filter(
    (b) => b.status.toLowerCase() === 'pending'
  ).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Venue Booking Requests</h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage and review venue booking requests
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400" />
          <span className="text-sm text-slate-500">Filter by status</span>
        </div>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex items-center gap-2 flex-wrap">
        {statusTabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Count Summary */}
      <div className="text-sm text-slate-500">
        Showing {filteredBookings.length} requests
        {activeTab === 'All' && ` (${pendingCount} pending)`}
      </div>

      {/* Booking Cards */}
      <div className="space-y-4">
        {filteredBookings.map((booking) => {
          const isPending = booking.status.toLowerCase() === 'pending';
          const catStyle =
            categoryStyles[booking.category] || 'bg-slate-100 text-slate-700';

          return (
            <div
              key={booking.id}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                {/* Left Content */}
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold text-slate-900">{booking.title}</h3>
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        statusStyles[booking.status.toLowerCase()] || ''
                      }`}
                    >
                      {booking.status}
                    </span>
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${catStyle}`}
                    >
                      {formatCategory(booking.category)}
                    </span>
                  </div>

                  <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-4 text-sm text-slate-500">
                    <span>
                      Requested by{' '}
                      <span className="font-medium text-slate-700">
                        {booking.requestedBy}
                      </span>
                    </span>
                    <span className="hidden sm:inline text-slate-300">•</span>
                    <span className="flex items-center gap-1.5">
                      <CalendarCheck className="h-3.5 w-3.5" />
                      {booking.date} · {booking.timeSlot}
                    </span>
                  </div>

                  <div className="text-sm text-slate-500">
                    Venue:{' '}
                    <span className="font-medium text-slate-700">{booking.venue}</span>
                  </div>
                </div>

                {/* Action Buttons */}
                {isPending && (
                  <div className="flex items-center gap-2 shrink-0">
                    <button className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-50 px-3.5 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-100 transition-colors ring-1 ring-emerald-600/20">
                      <Check className="h-4 w-4" />
                      Approve
                    </button>
                    <button className="inline-flex items-center gap-1.5 rounded-lg bg-rose-50 px-3.5 py-2 text-sm font-medium text-rose-700 hover:bg-rose-100 transition-colors ring-1 ring-rose-600/20">
                      <X className="h-4 w-4" />
                      Reject
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {filteredBookings.length === 0 && (
          <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
            <CalendarCheck className="h-12 w-12 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-500">
              No booking requests found for the selected filter.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
