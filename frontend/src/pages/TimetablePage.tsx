import { useState } from 'react';
import { Filter, ChevronLeft, ChevronRight } from 'lucide-react';

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
const timeSlots = [
  '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
  '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM',
];

interface SessionBlock {
  id: string;
  code: string;
  name: string;
  venue: string;
  day: number;       // 0 = Monday
  startSlot: number; // 0 = 8AM
  span: number;      // number of hour slots
  color: 'indigo' | 'emerald' | 'violet' | 'amber';
}

const sessions: SessionBlock[] = [
  {
    id: '1',
    code: 'CS301',
    name: 'DSA',
    venue: 'LH-1',
    day: 0,
    startSlot: 1,
    span: 1,
    color: 'indigo',
  },
  {
    id: '2',
    code: 'EC501',
    name: 'Digital Electronics',
    venue: 'LH-3',
    day: 1,
    startSlot: 2,
    span: 1,
    color: 'emerald',
  },
  {
    id: '3',
    code: 'CS302',
    name: 'DBMS Lab',
    venue: 'CS-LAB-1',
    day: 2,
    startSlot: 6,
    span: 2,
    color: 'violet',
  },
  {
    id: '4',
    code: 'MA301',
    name: 'Engg. Math III',
    venue: 'CR-101',
    day: 3,
    startSlot: 0,
    span: 1,
    color: 'amber',
  },
];

const colorMap = {
  indigo: {
    bg: 'bg-indigo-50',
    border: 'border-l-indigo-500',
    text: 'text-indigo-700',
    sub: 'text-indigo-500',
  },
  emerald: {
    bg: 'bg-emerald-50',
    border: 'border-l-emerald-500',
    text: 'text-emerald-700',
    sub: 'text-emerald-500',
  },
  violet: {
    bg: 'bg-violet-50',
    border: 'border-l-violet-500',
    text: 'text-violet-700',
    sub: 'text-violet-500',
  },
  amber: {
    bg: 'bg-amber-50',
    border: 'border-l-amber-500',
    text: 'text-amber-700',
    sub: 'text-amber-500',
  },
};

export default function TimetablePage() {
  const [department, setDepartment] = useState('CSE');
  const [semester, setSemester] = useState('3rd');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Weekly Timetable</h1>
          <p className="text-sm text-slate-500 mt-1">View and manage class schedules</p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {/* Department Filter */}
          <div className="relative">
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="appearance-none rounded-lg border border-slate-200 bg-white px-3 py-2 pr-8 text-sm text-slate-700 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            >
              <option value="CSE">CSE</option>
              <option value="ECE">ECE</option>
              <option value="EEE">EEE</option>
              <option value="ME">ME</option>
              <option value="CE">CE</option>
            </select>
            <Filter className="absolute right-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
          </div>

          {/* Semester Filter */}
          <div className="relative">
            <select
              value={semester}
              onChange={(e) => setSemester(e.target.value)}
              className="appearance-none rounded-lg border border-slate-200 bg-white px-3 py-2 pr-8 text-sm text-slate-700 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            >
              <option value="1st">1st Semester</option>
              <option value="2nd">2nd Semester</option>
              <option value="3rd">3rd Semester</option>
              <option value="4th">4th Semester</option>
              <option value="5th">5th Semester</option>
              <option value="6th">6th Semester</option>
              <option value="7th">7th Semester</option>
              <option value="8th">8th Semester</option>
            </select>
            <Filter className="absolute right-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
          </div>

          {/* Week Navigation */}
          <div className="flex items-center gap-1">
            <button className="rounded-lg border border-slate-200 bg-white p-2 text-slate-600 hover:bg-slate-50 transition-colors">
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="rounded-lg bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-700">
              This Week
            </span>
            <button className="rounded-lg border border-slate-200 bg-white p-2 text-slate-600 hover:bg-slate-50 transition-colors">
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Timetable Grid */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-auto">
        <div className="min-w-[800px]">
          {/* Days Header */}
          <div className="grid grid-cols-[100px_repeat(5,1fr)] border-b border-slate-200">
            <div className="sticky left-0 z-10 bg-slate-50 p-3 text-xs font-semibold text-slate-500 uppercase tracking-wider border-r border-slate-200">
              Time
            </div>
            {days.map((day) => (
              <div
                key={day}
                className="p-3 text-center text-sm font-semibold text-slate-700 bg-slate-50 border-r border-slate-200 last:border-r-0"
              >
                {day}
              </div>
            ))}
          </div>

          {/* Time Rows */}
          {timeSlots.map((time, rowIndex) => (
            <div
              key={time}
              className="grid grid-cols-[100px_repeat(5,1fr)] border-b border-slate-100 last:border-b-0"
            >
              {/* Time Label */}
              <div className="sticky left-0 z-10 bg-white p-3 text-xs font-medium text-slate-500 border-r border-slate-200 flex items-start">
                {time}
              </div>

              {/* Day Cells */}
              {days.map((_, dayIndex) => {
                const session = sessions.find(
                  (s) => s.day === dayIndex && s.startSlot === rowIndex
                );
                const isOccupiedBySpan = sessions.some(
                  (s) =>
                    s.day === dayIndex &&
                    s.startSlot < rowIndex &&
                    s.startSlot + s.span > rowIndex
                );

                if (isOccupiedBySpan) {
                  return null;
                }

                if (session) {
                  const colors = colorMap[session.color];
                  return (
                    <div
                      key={`${dayIndex}-${rowIndex}`}
                      className="p-1.5 border-r border-slate-100 last:border-r-0"
                      style={
                        session.span > 1
                          ? { gridRow: `span ${session.span}` }
                          : undefined
                      }
                    >
                      <div
                        className={`h-full rounded-lg border-l-4 ${colors.border} ${colors.bg} p-2.5 cursor-pointer hover:shadow-sm transition-shadow`}
                      >
                        <p className={`text-xs font-semibold ${colors.text}`}>
                          {session.code} - {session.name}
                        </p>
                        <p className={`text-xs mt-1 ${colors.sub}`}>
                          {session.venue}
                        </p>
                      </div>
                    </div>
                  );
                }

                return (
                  <div
                    key={`${dayIndex}-${rowIndex}`}
                    className="p-1.5 border-r border-slate-100 last:border-r-0 min-h-[60px]"
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
