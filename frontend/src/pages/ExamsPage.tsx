import { Calendar, Download } from 'lucide-react';

interface ExamEntry {
  id: string;
  code: string;
  subject: string;
  date: string;
  session: 'AM' | 'PM';
  venues: string;
  branchSem: string;
}

const exams: ExamEntry[] = [
  {
    id: '1',
    code: 'CS301',
    subject: 'Data Structures & Algorithms',
    date: 'Nov 10, 2027',
    session: 'AM',
    venues: 'LH-1, LH-2',
    branchSem: 'CSE 3rd Sem',
  },
  {
    id: '2',
    code: 'EC501',
    subject: 'Digital Electronics',
    date: 'Nov 11, 2027',
    session: 'PM',
    venues: 'LH-3',
    branchSem: 'ECE 5th Sem',
  },
  {
    id: '3',
    code: 'MA301',
    subject: 'Engg. Mathematics III',
    date: 'Nov 12, 2027',
    session: 'AM',
    venues: 'LH-1 to LH-4',
    branchSem: 'All 3rd Sem',
  },
  {
    id: '4',
    code: 'CS302',
    subject: 'Database Management Systems',
    date: 'Nov 13, 2027',
    session: 'PM',
    venues: 'CS-LAB-1, CS-LAB-2',
    branchSem: 'CSE 3rd Sem',
  },
  {
    id: '5',
    code: 'PH201',
    subject: 'Engineering Physics',
    date: 'Nov 14, 2027',
    session: 'AM',
    venues: 'LH-5, LH-6',
    branchSem: 'All 1st Sem',
  },
];

export default function ExamsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Examination Schedule</h1>
            <p className="text-sm text-slate-500 mt-1">
              View and manage upcoming examination schedules
            </p>
          </div>
          <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700 ring-1 ring-indigo-600/20">
            <Calendar className="h-3.5 w-3.5" />
            End Semester 2027
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Semester Selector */}
          <select className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none">
            <option>End Semester - Nov 2027</option>
            <option>Mid Semester - Sep 2027</option>
            <option>End Semester - May 2027</option>
          </select>

          <button className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 transition-colors">
            <Download className="h-4 w-4" />
            Export
          </button>
        </div>
      </div>

      {/* Exam Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        {/* Table Header */}
        <div className="hidden md:grid grid-cols-[80px_2fr_120px_80px_1fr_1fr] gap-4 border-b border-slate-200 bg-slate-50 px-6 py-3">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Code
          </span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Subject
          </span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Date
          </span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Session
          </span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Venue(s)
          </span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Branch & Sem
          </span>
        </div>

        {/* Table Rows */}
        {exams.map((exam, index) => (
          <div
            key={exam.id}
            className={`grid grid-cols-1 md:grid-cols-[80px_2fr_120px_80px_1fr_1fr] gap-2 md:gap-4 items-center px-6 py-4 border-b border-slate-100 last:border-b-0 hover:bg-slate-50/50 transition-colors ${
              index % 2 === 0 ? 'bg-white' : 'bg-slate-50/30'
            }`}
          >
            {/* Code */}
            <div>
              <span className="inline-flex items-center rounded-md bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-700">
                {exam.code}
              </span>
            </div>

            {/* Subject */}
            <div>
              <span className="text-sm font-medium text-slate-900">{exam.subject}</span>
            </div>

            {/* Date */}
            <div className="flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5 text-slate-400 hidden md:block" />
              <span className="text-sm text-slate-600">{exam.date}</span>
            </div>

            {/* Session */}
            <div>
              <span
                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  exam.session === 'AM'
                    ? 'bg-amber-50 text-amber-700 ring-1 ring-amber-600/20'
                    : 'bg-indigo-50 text-indigo-700 ring-1 ring-indigo-600/20'
                }`}
              >
                {exam.session === 'AM' ? '🌅 AM' : '🌇 PM'}
              </span>
            </div>

            {/* Venue */}
            <div>
              <span className="text-sm text-slate-600">{exam.venues}</span>
            </div>

            {/* Branch & Sem */}
            <div>
              <span className="inline-flex items-center rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700 ring-1 ring-emerald-600/20">
                {exam.branchSem}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Summary */}
      <div className="flex items-center justify-between rounded-lg bg-slate-50 border border-slate-200 px-4 py-3">
        <span className="text-sm text-slate-500">
          Showing {exams.length} examinations scheduled
        </span>
        <span className="text-xs text-slate-400">
          Last updated: Oct 31, 2027
        </span>
      </div>
    </div>
  );
}
