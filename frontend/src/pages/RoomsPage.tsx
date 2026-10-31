import { useState } from 'react';
import { Search, MapPin, Users, Monitor, Wifi, Wind, Accessibility } from 'lucide-react';

type RoomStatus = 'Available' | 'Occupied' | 'Under Maintenance';

interface Room {
  id: string;
  name: string;
  building: string;
  capacity: number;
  type: string;
  status: RoomStatus;
  accessible: boolean;
  features: string[];
}

const rooms: Room[] = [
  {
    id: '1',
    name: 'Main Auditorium',
    building: 'Admin Block',
    capacity: 500,
    type: 'auditorium',
    status: 'Available',
    accessible: true,
    features: ['Projector', 'Sound System', 'AC', 'Wi-Fi'],
  },
  {
    id: '2',
    name: 'Lecture Hall 1',
    building: 'Lecture Hall Complex',
    capacity: 200,
    type: 'lecture_hall',
    status: 'Occupied',
    accessible: true,
    features: ['Projector', 'AC', 'Wi-Fi'],
  },
  {
    id: '3',
    name: 'Computing Lab 1',
    building: 'CSE Building',
    capacity: 90,
    type: 'lab_cs',
    status: 'Available',
    accessible: false,
    features: ['Computers', 'Projector', 'AC', 'Wi-Fi'],
  },
  {
    id: '4',
    name: 'Seminar Hall 1',
    building: 'Library Building',
    capacity: 150,
    type: 'seminar_hall',
    status: 'Available',
    accessible: true,
    features: ['Projector', 'AC', 'Wi-Fi', 'Video Conferencing'],
  },
  {
    id: '5',
    name: 'Classroom A-101',
    building: 'Academic Block A',
    capacity: 90,
    type: 'classroom',
    status: 'Occupied',
    accessible: false,
    features: ['Projector', 'Wi-Fi'],
  },
  {
    id: '6',
    name: 'Electronics Lab 1',
    building: 'EE-ECE Building',
    capacity: 80,
    type: 'lab_elec',
    status: 'Under Maintenance',
    accessible: false,
    features: ['Lab Equipment', 'AC', 'Wi-Fi'],
  },
];

const statusStyles: Record<RoomStatus, string> = {
  Available: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20',
  Occupied: 'bg-amber-50 text-amber-700 ring-1 ring-amber-600/20',
  'Under Maintenance': 'bg-rose-50 text-rose-700 ring-1 ring-rose-600/20',
};

const filterOptions = ['All', 'Lecture Halls', 'Labs', 'Seminar Halls'] as const;

export default function RoomsPage() {
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState<string>('All');

  const filteredRooms = rooms.filter((room) => {
    const matchesSearch =
      room.name.toLowerCase().includes(search.toLowerCase()) ||
      room.building.toLowerCase().includes(search.toLowerCase());

    let matchesFilter = true;
    if (activeFilter === 'Lecture Halls') {
      matchesFilter = room.type === 'lecture_hall' || room.type === 'auditorium';
    } else if (activeFilter === 'Labs') {
      matchesFilter = room.type === 'lab_cs' || room.type === 'lab_elec';
    } else if (activeFilter === 'Seminar Halls') {
      matchesFilter = room.type === 'seminar_hall';
    }

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Rooms & Venues</h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage campus rooms, labs, and auditoriums
          </p>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search rooms..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full sm:w-64 rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 flex-wrap">
        {filterOptions.map((filter) => (
          <button
            key={filter}
            onClick={() => setActiveFilter(filter)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              activeFilter === filter
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {filter}
          </button>
        ))}
      </div>

      {/* Room Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredRooms.map((room) => (
          <div
            key={room.id}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
          >
            {/* Top Row: Name & Status */}
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold text-slate-900">{room.name}</h3>
                <div className="flex items-center gap-1.5 mt-1">
                  <MapPin className="h-3.5 w-3.5 text-slate-400" />
                  <span className="text-sm text-slate-500">{room.building}</span>
                </div>
              </div>
              <span
                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium whitespace-nowrap ${statusStyles[room.status]}`}
              >
                {room.status}
              </span>
            </div>

            {/* Capacity */}
            <div className="mt-4 flex items-center gap-2">
              <Users className="h-4 w-4 text-slate-400" />
              <span className="text-sm text-slate-600">{room.capacity} seats</span>
              {room.accessible && (
                <span className="ml-auto flex items-center gap-1 text-xs text-emerald-600 font-medium">
                  <Accessibility className="h-3.5 w-3.5" />
                  Accessible
                </span>
              )}
            </div>

            {/* Features */}
            <div className="mt-3 flex flex-wrap gap-1.5">
              {room.features.map((feature) => (
                <span
                  key={feature}
                  className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
                >
                  {feature === 'Wi-Fi' && <Wifi className="h-3 w-3" />}
                  {feature === 'AC' && <Wind className="h-3 w-3" />}
                  {(feature === 'Projector' ||
                    feature === 'Computers' ||
                    feature === 'Video Conferencing') && (
                    <Monitor className="h-3 w-3" />
                  )}
                  {feature}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
