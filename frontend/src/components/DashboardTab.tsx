import React from 'react';
import { BookOpen, Award, CheckCircle2, TrendingUp, AlertTriangle, ArrowRight, Eye, MousePointer } from 'lucide-react';
import { StudentProfile, CourseSummary, PerformanceSummary, StudyRecommendation } from '../lib/api';

interface DashboardTabProps {
  profile: StudentProfile | null;
  courses: CourseSummary[];
  performance: PerformanceSummary | null;
  recommendation: StudyRecommendation | null;
  onNavigateTab: (tab: string) => void;
}

export const DashboardTab: React.FC<DashboardTabProps> = ({
  profile,
  courses,
  performance,
  recommendation,
  onNavigateTab,
}) => {
  const efficiency = performance?.learning_efficiency?.score || 0;
  const efficiencyGrade = performance?.learning_efficiency?.grade || 'Calculating...';

  return (
    <div className="space-y-6">
      {/* Welcome & Top Metric Cards */}
      <div className="bg-gradient-to-r from-sky-900 to-indigo-950 rounded-2xl p-6 text-white shadow-md relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-sky-500/20 text-sky-300 border border-sky-400/30">
            Student Academic Dashboard
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold mt-2">Welcome back!</h1>
          <p className="text-sm text-slate-300 mt-1">
            Track your course syllabus progress, assessment accuracy, and personalized AI recommendations derived strictly from your real learning data.
          </p>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2 text-slate-500">
            <BookOpen className="h-4 w-4 text-sky-600" />
            <span className="text-xs font-medium">Enrolled Courses</span>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{profile?.enrolled_courses_count || 0}</p>
          <span className="text-xs text-slate-400">Registered curricula</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2 text-slate-500">
            <Award className="h-4 w-4 text-amber-600" />
            <span className="text-xs font-medium">Assessments Taken</span>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{profile?.assessments_taken_count || 0}</p>
          <span className="text-xs text-slate-400">Recorded hackathons</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2 text-slate-500">
            <TrendingUp className="h-4 w-4 text-emerald-600" />
            <span className="text-xs font-medium">Overall Accuracy</span>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {performance?.overall_accuracy_percentage ? `${performance.overall_accuracy_percentage}%` : '0%'}
          </p>
          <span className="text-xs text-slate-400">Across all questions</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2 text-slate-500">
            <Eye className="h-4 w-4 text-indigo-600" />
            <span className="text-xs font-medium">Course Views</span>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{profile?.total_views || 0}</p>
          <span className="text-xs text-slate-400">LMS interactions</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm col-span-2 sm:col-span-1">
          <div className="flex items-center space-x-2 text-slate-500">
            <CheckCircle2 className="h-4 w-4 text-purple-600" />
            <span className="text-xs font-medium">Learning Efficiency</span>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{efficiency}/100</p>
          <span className="text-xs text-purple-600 font-medium">{efficiencyGrade}</span>
        </div>
      </div>

      {/* Recommended Next Action (Study Coach Card) */}
      {recommendation && (
        <div className="bg-white border-l-4 border-sky-600 rounded-xl p-5 shadow-sm border border-slate-200">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-sky-700 bg-sky-50 px-2 py-0.5 rounded">
                AI Study Coach Priority
              </span>
              <h3 className="text-lg font-bold text-slate-900 mt-1">
                Priority: {recommendation.priority_topic}
              </h3>
              <p className="text-sm text-slate-600">
                {recommendation.reason}
              </p>
              <p className="text-xs text-slate-500 mt-2 font-medium">
                🎯 {recommendation.practice_recommendation}
              </p>
            </div>
            <button
              onClick={() => onNavigateTab('study-coach')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-sky-600 text-white text-xs font-semibold rounded-lg hover:bg-sky-700 transition"
            >
              Action Plan <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Grid: Courses & Weak Topics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Enrolled Courses */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-slate-900">Enrolled Courses & Progress</h2>
            <button
              onClick={() => onNavigateTab('performance')}
              className="text-xs font-medium text-sky-600 hover:text-sky-700"
            >
              View All Analytics
            </button>
          </div>

          <div className="space-y-4 max-h-[380px] overflow-y-auto pr-2">
            {courses.map((c) => (
              <div key={c.course_id} className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-800 text-sm">{c.course_title}</span>
                  <span className="font-bold text-sky-700">{c.progress_percentage}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-sky-600 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(100, Math.max(5, c.progress_percentage))}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2">
                  <span>Domain: {c.course_domain}</span>
                  <span>{c.course_hours} hrs • {c.course_level}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Weak Topics */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              <h2 className="text-base font-bold text-slate-900">Topics Needing Revision</h2>
            </div>
            <span className="text-xs text-slate-400 font-medium">Accuracy &lt; 60%</span>
          </div>

          <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
            {(performance?.weak_topics || []).slice(0, 7).map((t) => (
              <div key={t.topic} className="p-3 rounded-lg border border-amber-100 bg-amber-50/40 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-800">{t.topic}</p>
                  <p className="text-[11px] text-slate-500">{t.skill} • {t.failed_count} failed</p>
                </div>
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-red-100 text-red-700">
                  {t.accuracy_percentage}%
                </span>
              </div>
            ))}
            {(!performance?.weak_topics || performance.weak_topics.length === 0) && (
              <p className="text-xs text-slate-500 py-6 text-center">No weak topics recorded! All topics are above 60%.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
