import React, { useState } from 'react';
import { Award, Zap, Compass, BarChart3, AlertTriangle, CheckCircle2, History, Search } from 'lucide-react';
import { PerformanceSummary } from '../lib/api';

interface PerformanceTabProps {
  performance: PerformanceSummary | null;
  assessmentHistory: any[];
}

export const PerformanceTab: React.FC<PerformanceTabProps> = ({
  performance,
  assessmentHistory,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMode, setFilterMode] = useState<'all' | 'weak'>('all');

  if (!performance) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-slate-200">
        <p className="text-sm text-slate-500">Loading student performance analytics...</p>
      </div>
    );
  }

  const eff = performance.learning_efficiency;
  const ins = performance.engagement_vs_performance;

  const filteredTopics = (performance.all_topics || []).filter((t) => {
    const matchesSearch =
      t.topic.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.skill.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterMode === 'all' || t.is_weak;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Top Derived Analytics Cards: Learning Efficiency + Engagement vs Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Phase 6: Learning Efficiency Score Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm relative overflow-hidden">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-purple-700 bg-purple-50 px-2.5 py-1 rounded-md border border-purple-200">
                Derived Metric • Phase 6
              </span>
              <h2 className="text-lg font-bold text-slate-900 mt-2 flex items-center gap-2">
                <Zap className="h-5 w-5 text-purple-600" />
                Learning Efficiency Score
              </h2>
            </div>
            <div className="text-right">
              <span className="text-3xl font-extrabold text-purple-700">{eff.score}</span>
              <span className="text-slate-400 font-bold text-lg">/100</span>
              <p className="text-xs font-semibold text-purple-600">{eff.grade}</p>
            </div>
          </div>

          <p className="text-xs text-slate-600 mt-3 leading-relaxed">
            {eff.explanation}
          </p>

          <div className="mt-4 pt-4 border-t border-slate-100">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Formula Breakdown: <code className="text-purple-600 bg-purple-50 px-1 py-0.5 rounded">{eff.formula_summary}</code>
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
              <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
                <span className="text-slate-500 block text-[10px]">Accuracy (40%)</span>
                <span className="font-bold text-slate-800">+{eff.factors.accuracy_contribution} pts</span>
              </div>
              <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
                <span className="text-slate-500 block text-[10px]">Progress (30%)</span>
                <span className="font-bold text-slate-800">+{eff.factors.progress_contribution} pts</span>
              </div>
              <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
                <span className="text-slate-500 block text-[10px]">Resources (20%)</span>
                <span className="font-bold text-slate-800">+{eff.factors.resource_contribution} pts</span>
              </div>
              <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
                <span className="text-slate-500 block text-[10px]">Consistency (10%)</span>
                <span className="font-bold text-slate-800">+{eff.factors.consistency_contribution} pts</span>
              </div>
            </div>
          </div>
        </div>

        {/* Phase 5: Engagement vs Performance Diagnostic Quadrant Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-sky-700 bg-sky-50 px-2.5 py-1 rounded-md border border-sky-200">
              Diagnostic Insights • Phase 5
            </span>
            <h2 className="text-lg font-bold text-slate-900 mt-2 flex items-center gap-2">
              <Compass className="h-5 w-5 text-sky-600" />
              Engagement vs Performance Analysis
            </h2>
          </div>

          <div className="mt-3 p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-xs font-bold text-sky-800 uppercase tracking-wide">Quadrant Classification</span>
            <p className="text-sm font-bold text-slate-900 mt-0.5">{ins.quadrant}</p>
            <p className="text-xs text-slate-600 mt-1">{ins.summary}</p>
          </div>

          <div className="mt-3 text-xs text-slate-600 space-y-1.5">
            <p><span className="font-semibold text-slate-800">Reasoning:</span> {ins.detailed_reasoning}</p>
            <p><span className="font-semibold text-slate-800">Strategic Focus:</span> {ins.recommended_strategy}</p>
          </div>
        </div>
      </div>

      {/* Difficulty Breakdown */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-slate-600" />
          Accuracy by Question Difficulty Tier
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {performance.difficulty_breakdown.map((d) => (
            <div key={d.difficulty} className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
              <div className="flex items-center justify-between">
                <span className="capitalize font-bold text-sm text-slate-800">{d.difficulty}</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                  {d.total_questions} questions
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 mt-3">
                <div
                  className={`h-2 rounded-full ${
                    d.accuracy_percentage >= 60 ? 'bg-emerald-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.max(5, d.accuracy_percentage)}%` }}
                />
              </div>
              <div className="flex justify-between items-center mt-2 text-xs">
                <span className="text-slate-500">Accuracy Rate:</span>
                <span className="font-bold text-slate-900">{d.accuracy_percentage}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Topic Accuracy Breakdown Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Topic-Level Accuracy & Weakness Engine</h3>
            <p className="text-xs text-slate-500">Derived deterministically: Accuracy = Obtained Score / Possible Score</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="h-3.5 w-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search topics or skills..."
                className="pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 w-44 sm:w-52"
              />
            </div>
            <div className="flex bg-slate-100 p-0.5 rounded-lg text-xs">
              <button
                onClick={() => setFilterMode('all')}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  filterMode === 'all'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                All ({performance.all_topics.length})
              </button>
              <button
                onClick={() => setFilterMode('weak')}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  filterMode === 'weak'
                    ? 'bg-red-600 text-white shadow-sm'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Weak ({performance.weak_topics.length})
              </button>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Topic</th>
                <th className="px-4 py-3">Skill / Domain</th>
                <th className="px-4 py-3">Questions</th>
                <th className="px-4 py-3">Passed / Failed</th>
                <th className="px-4 py-3">Accuracy</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredTopics.map((t) => (
                <tr key={t.topic} className="hover:bg-slate-50/80 transition">
                  <td className="px-4 py-3 font-semibold text-slate-800">{t.topic}</td>
                  <td className="px-4 py-3 text-slate-600">{t.skill}</td>
                  <td className="px-4 py-3 text-slate-600">{t.total_questions}</td>
                  <td className="px-4 py-3 text-slate-600">
                    <span className="text-emerald-600 font-medium">{t.passed_count}</span> /{' '}
                    <span className="text-red-600 font-medium">{t.failed_count}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-200 rounded-full h-1.5">
                        <div
                          className={`h-1.5 rounded-full ${t.is_weak ? 'bg-red-500' : 'bg-emerald-500'}`}
                          style={{ width: `${Math.max(5, t.accuracy_percentage)}%` }}
                        />
                      </div>
                      <span className="font-bold text-slate-800">{t.accuracy_percentage}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {t.is_weak ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-red-700 bg-red-50 px-2 py-0.5 rounded-full border border-red-200">
                        <AlertTriangle className="h-3 w-3" /> Needs Revision
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                        <CheckCircle2 className="h-3 w-3" /> Proficient
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {filteredTopics.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                    No matching topics found for &quot;{searchQuery}&quot;.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Assessment History Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
          <History className="h-4 w-4 text-slate-600" />
          Recorded Assessment History
        </h3>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Attempt ID</th>
                <th className="px-4 py-3">Assessment ID</th>
                <th className="px-4 py-3">Date Submitted</th>
                <th className="px-4 py-3">Questions</th>
                <th className="px-4 py-3">Score</th>
                <th className="px-4 py-3">Accuracy</th>
                <th className="px-4 py-3">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {assessmentHistory.map((h, i) => (
                <tr key={i} className="hover:bg-slate-50/80 transition">
                  <td className="px-4 py-3 font-mono text-slate-600">#{h.attempt_id}</td>
                  <td className="px-4 py-3 font-semibold text-slate-800">Assessment #{h.assessment_id}</td>
                  <td className="px-4 py-3 text-slate-500">{h.submitted_at}</td>
                  <td className="px-4 py-3 text-slate-600">{h.questions_attempted}</td>
                  <td className="px-4 py-3 text-slate-600">{h.score_obtained} / {h.possible_score}</td>
                  <td className="px-4 py-3 font-bold text-slate-800">{h.accuracy_percentage}%</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        h.status === 'pass'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {h.status.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
              {assessmentHistory.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-center text-slate-400">
                    No assessment history recorded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
