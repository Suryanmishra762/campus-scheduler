import { BookOpen } from 'lucide-react';

interface ExamEntry {
  subject: string;
  branch: string;
  semester: string;
  date: string;
  session: string;
  time: string;
  venues: string;
}

const exams: ExamEntry[] = [
  {
    subject: 'Data Structures & Algorithms',
    branch: 'CSE',
    semester: '3rd Semester',
    date: 'Nov 10, 2027',
    session: 'AM Session',
    time: '09:30 – 11:30',
    venues: 'Lecture Hall 1, 2',
  },
  {
    subject: 'Digital Electronics',
    branch: 'ECE',
    semester: '5th Semester',
    date: 'Nov 11, 2027',
    session: 'PM Session',
    time: '14:00 – 16:00',
    venues: 'Lecture Hall 3',
  },
  {
    subject: 'Engineering Mathematics III',
    branch: 'All Branches',
    semester: '3rd Semester',
    date: 'Nov 12, 2027',
    session: 'AM Session',
    time: '09:30 – 11:30',
    venues: 'Lecture Hall 1, 2, 3, 4',
  },
];

export default function UpcomingExams() {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900 mb-4">Upcoming Exams</h2>
      <div className="space-y-0 divide-y divide-slate-200">
        {exams.map((exam) => (
          <div
            key={exam.subject}
            className="border-l-4 border-indigo-500 pl-3 py-3 first:pt-0 last:pb-0"
          >
            <div className="flex items-start gap-2">
              <BookOpen className="w-4 h-4 text-indigo-500 mt-0.5 shrink-0" />
              <div className="min-w-0">
                <p className="font-medium text-slate-900">{exam.subject}</p>
                <p className="text-sm text-slate-500 mt-0.5">
                  {exam.branch}, {exam.semester}
                </p>
                <p className="text-sm text-slate-500">
                  {exam.date} &middot; {exam.session} ({exam.time})
                </p>
                <p className="text-sm text-slate-500">{exam.venues}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
