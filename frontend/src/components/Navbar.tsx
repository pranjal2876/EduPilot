import React from 'react';
import { GraduationCap, User, Sparkles } from 'lucide-react';
import { DemoStudent } from '../lib/api';

interface NavbarProps {
  demoStudents: DemoStudent[];
  activeStudentId: string;
  onSelectStudent: (id: string) => void;
  activeTab: string;
  onSelectTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  demoStudents,
  activeStudentId,
  onSelectStudent,
  activeTab,
  onSelectTab,
}) => {
  const activeStudent = demoStudents.find((s) => s.student_id === activeStudentId) || demoStudents[0];

  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'assistant', label: 'AI Assistant' },
    { id: 'performance', label: 'Performance' },
    { id: 'practice', label: 'Practice' },
    { id: 'assessments', label: 'Assessments' },
    { id: 'study-coach', label: 'Study Coach' },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectTab('dashboard')}>
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <GraduationCap className="h-6 w-6" />
            </div>
            <div>
              <span className="font-bold text-lg text-slate-900 tracking-tight flex items-center gap-1.5">
                AI College Learning Assistant
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-sky-100 text-sky-700 border border-sky-200">
                  Prototype
                </span>
              </span>
              <p className="text-xs text-slate-500 hidden sm:block">Structured Data + RAG + Deterministic Rules + Analytics</p>
            </div>
          </div>

          {/* Student Switcher & Profile */}
          <div className="flex items-center space-x-3">
            <div className="text-right hidden md:block">
              <p className="text-xs font-medium text-slate-500">Active Student Persona</p>
              <p className="text-sm font-semibold text-slate-800">{activeStudent?.name || 'Aarav Sharma'}</p>
            </div>
            <div className="relative">
              <select
                value={activeStudentId}
                onChange={(e) => onSelectStudent(e.target.value)}
                className="bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium text-xs rounded-lg px-3 py-2 border border-slate-300 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all cursor-pointer"
              >
                {demoStudents.map((s) => (
                  <option key={s.student_id} value={s.student_id}>
                    {s.name} ({s.courses_count} courses, {s.assessments_count} tests)
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 sm:space-x-4 border-t border-slate-100 py-2 overflow-x-auto">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-sky-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
