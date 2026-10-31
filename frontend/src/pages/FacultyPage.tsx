import { useState } from 'react';
import { Search, Mail, Clock } from 'lucide-react';

type FacultyStatus = 'Available' | 'On Leave' | 'Visiting';

interface Faculty {
  id: string;
  name: string;
  department: string;
  maxHours: string;
  status: FacultyStatus;
  schedule?: string;
  email: string;
  initials: string;
  avatarColor: string;
}

const facultyMembers: Faculty[] = [
  {
    id: '1',
    name: 'Dr. Ananya Mishra',
    department: 'CSE',
    maxHours: '4 hrs/day',
    status: 'Available',
    email: 'ananya.mishra@cit.edu',
    initials: 'AM',
    avatarColor: 'bg-indigo-100 text-indigo-700',
  },
  {
    id: '2',
    name: 'Dr. Rohit Sahoo',
    department: 'CSE',
    maxHours: '4 hrs/day',
    status: 'Available',
    email: 'rohit.sahoo@cit.edu',
    initials: 'RS',
    avatarColor: 'bg-emerald-100 text-emerald-700',
  },
  {
    id: '3',
    name: 'Dr. Kavya Iyer',
    department: 'CSE',
    maxHours: '4 hrs/day',
    status: 'Available',
    email: 'kavya.iyer@cit.edu',
    initials: 'KI',
    avatarColor: 'bg-violet-100 text-violet-700',
  },
  {
    id: '4',
    name: 'Dr. Sandeep Patnaik',
    department: 'CSE',
    maxHours: '4 hrs/day',
    status: 'Available',
    email: 'sandeep.patnaik@cit.edu',
    initials: 'SP',
    avatarColor: 'bg-amber-100 text-amber-700',
  },
  {
    id: '5',
    name: 'Dr. Meera Nair',
    department: 'CSE',
    maxHours: '4 hrs/day',
    status: 'On Leave',
    email: 'meera.nair@cit.edu',
    initials: 'MN',
    avatarColor: 'bg-rose-100 text-rose-700',
  },
  {
    id: '6',
    name: 'Prof. Vikram Rao',
    department: 'CSE',
    maxHours: '4 hrs/day',
    status: 'Visiting',
    schedule: 'Tue/Thu',
    email: 'vikram.rao@cit.edu',
    initials: 'VR',
    avatarColor: 'bg-cyan-100 text-cyan-700',
  },
];

const statusStyles: Record<FacultyStatus, string> = {
  Available: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20',
  'On Leave': 'bg-rose-50 text-rose-700 ring-1 ring-rose-600/20',
  Visiting: 'bg-sky-50 text-sky-700 ring-1 ring-sky-600/20',
};

export default function FacultyPage() {
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('All');

  const filtered = facultyMembers.filter((f) => {
    const matchesSearch = f.name.toLowerCase().includes(search.toLowerCase());
    const matchesDept = deptFilter === 'All' || f.department === deptFilter;
    return matchesSearch && matchesDept;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Faculty Directory</h1>
          <p className="text-sm text-slate-500 mt-1">
            View and manage faculty members and their schedules
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Department Filter */}
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
          >
            <option value="All">All Departments</option>
            <option value="CSE">CSE</option>
            <option value="ECE">ECE</option>
            <option value="EEE">EEE</option>
            <option value="ME">ME</option>
          </select>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search faculty..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full sm:w-56 rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* Faculty Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        {/* Table Header */}
        <div className="hidden sm:grid grid-cols-[2fr_1fr_1fr_1fr_1fr] gap-4 border-b border-slate-200 bg-slate-50 px-6 py-3">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Name
          </span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Department
          </span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Max Hours
          </span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Status
          </span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">
            Action
          </span>
        </div>

        {/* Table Rows */}
        {filtered.map((faculty) => (
          <div
            key={faculty.id}
            className="grid grid-cols-1 sm:grid-cols-[2fr_1fr_1fr_1fr_1fr] gap-3 sm:gap-4 items-center px-6 py-4 border-b border-slate-100 last:border-b-0 hover:bg-slate-50/50 transition-colors"
          >
            {/* Name & Avatar */}
            <div className="flex items-center gap-3">
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold shrink-0 ${faculty.avatarColor}`}
              >
                {faculty.initials}
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">
                  {faculty.name}
                  {faculty.status === 'Visiting' && (
                    <span className="ml-1.5 text-xs font-normal text-slate-400">
                      (Visiting)
                    </span>
                  )}
                </p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <Mail className="h-3 w-3 text-slate-400" />
                  <span className="text-xs text-slate-400">{faculty.email}</span>
                </div>
              </div>
            </div>

            {/* Department */}
            <div className="flex items-center gap-2 sm:block">
              <span className="text-xs text-slate-400 sm:hidden">Dept:</span>
              <span className="text-sm text-slate-600">{faculty.department}</span>
            </div>

            {/* Max Hours */}
            <div className="flex items-center gap-2">
              <Clock className="h-3.5 w-3.5 text-slate-400 hidden sm:block" />
              <span className="text-xs text-slate-400 sm:hidden">Hours:</span>
              <span className="text-sm text-slate-600">{faculty.maxHours}</span>
            </div>

            {/* Status */}
            <div>
              <span
                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[faculty.status]}`}
              >
                {faculty.status}
                {faculty.schedule && ` (${faculty.schedule})`}
              </span>
            </div>

            {/* Action */}
            <div className="text-right">
              <button className="rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-700 hover:bg-indigo-100 transition-colors">
                View Schedule
              </button>
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="px-6 py-12 text-center text-sm text-slate-400">
            No faculty members found matching your search.
          </div>
        )}
      </div>
    </div>
  );
}
