import React, { useState, useEffect } from 'react';
import { ShieldCheck, CheckCircle2, XCircle, AlertCircle, RefreshCw, BookOpen, Layers } from 'lucide-react';
import { fetchApi, AssessmentItem, AssessmentEligibility } from '../lib/api';

interface AssessmentsTabProps {
  studentId: string;
}

export const AssessmentsTab: React.FC<AssessmentsTabProps> = ({ studentId }) => {
  const [assessments, setAssessments] = useState<AssessmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkingId, setCheckingId] = useState<number | null>(null);
  const [selectedEligibility, setSelectedEligibility] = useState<AssessmentEligibility | null>(null);

  useEffect(() => {
    loadAssessments();
  }, []);

  const loadAssessments = async () => {
    setLoading(true);
    try {
      const data = await fetchApi<AssessmentItem[]>('/assessments/list', studentId);
      setAssessments(data);
    } catch (err) {
      console.error('Failed to load assessments:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckEligibility = async (assessmentId: number) => {
    setCheckingId(assessmentId);
    setSelectedEligibility(null);
    try {
      const res = await fetchApi<AssessmentEligibility>(
        `/assessments/${assessmentId}/eligibility`,
        studentId
      );
      setSelectedEligibility(res);
    } catch (err) {
      console.error('Eligibility check error:', err);
    } finally {
      setCheckingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex items-start justify-between">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-200">
            Phase 9 • Business Rule Engine
          </span>
          <h2 className="text-lg font-bold text-slate-900 mt-2 flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-indigo-600" />
            Institutional Assessment Eligibility Catalog
          </h2>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl">
            Assessment access is strictly determined by deterministic application business rules: active test window,
            prerequisite course syllabus completion (80% / certified), prerequisite exam clearance, and maximum attempt limits.
          </p>
        </div>
        <button
          onClick={loadAssessments}
          className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition"
          title="Refresh Catalog"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {/* Eligibility Modal / Alert Drawer */}
      {selectedEligibility && (
        <div className="bg-white rounded-2xl border-2 border-indigo-500/50 p-6 shadow-lg space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <span className="text-xs font-semibold text-slate-500">Evaluation Result</span>
              <h3 className="text-base font-bold text-slate-900">{selectedEligibility.title}</h3>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-extrabold tracking-wide uppercase ${
                selectedEligibility.eligible
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                  : 'bg-red-100 text-red-800 border border-red-300'
              }`}
            >
              {selectedEligibility.eligible ? 'ELIGIBLE TO ATTEMPT' : 'NOT ELIGIBLE'}
            </span>
          </div>

          {/* 4-Rule Verification Checklist */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              Deterministic Business Rules Verification:
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {selectedEligibility.requirements.map((req, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-xl border text-xs flex items-start gap-2.5 ${
                    req.satisfied
                      ? 'bg-emerald-50/50 border-emerald-200 text-emerald-900'
                      : 'bg-red-50/50 border-red-200 text-red-900'
                  }`}
                >
                  {req.satisfied ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
                  )}
                  <div>
                    <span className="font-bold block">{req.name}</span>
                    <span className="text-[11px] opacity-90">{req.detail}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Reasons for Failure */}
          {!selectedEligibility.eligible && selectedEligibility.reasons.length > 0 && (
            <div className="p-3.5 bg-red-50 rounded-xl border border-red-200 text-xs text-red-800 space-y-1">
              <span className="font-bold block flex items-center gap-1.5">
                <AlertCircle className="h-4 w-4 text-red-600" />
                Deterministic Reasons for Failure:
              </span>
              <ul className="list-disc list-inside space-y-0.5 pl-1">
                {selectedEligibility.reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="pt-2 flex justify-end">
            <button
              onClick={() => setSelectedEligibility(null)}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50"
            >
              Close Evaluation
            </button>
          </div>
        </div>
      )}

      {/* Assessments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {assessments.map((a) => (
          <div key={a.assessment_id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400">ID #{a.assessment_id}</span>
                {a.is_active ? (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-700">
                    ACTIVE
                  </span>
                ) : (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-200 text-slate-600">
                    ARCHIVED
                  </span>
                )}
              </div>
              <h3 className="text-sm font-bold text-slate-900 mt-1">{a.title}</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {a.domain} • {a.sub_domain} • {a.num_questions} Questions
              </p>

              {/* Prerequisites Info */}
              <div className="mt-3 pt-3 border-t border-slate-100 text-[11px] space-y-1 text-slate-600">
                <div className="flex items-center gap-1.5">
                  <BookOpen className="h-3.5 w-3.5 text-slate-400" />
                  <span>Prerequisite: </span>
                  <span className="font-semibold text-slate-800">
                    {a.prerequisite_course_name || 'None'}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Layers className="h-3.5 w-3.5 text-slate-400" />
                  <span>Max Attempts: </span>
                  <span className="font-semibold text-slate-800">{a.max_attempts}</span>
                  <span className="text-slate-400 ml-2">Passing Score: {a.passing_score}%</span>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <button
                onClick={() => handleCheckEligibility(a.assessment_id)}
                disabled={checkingId === a.assessment_id}
                className="w-full bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold py-2 px-3 rounded-lg transition disabled:opacity-50 flex items-center justify-center gap-1.5"
              >
                {checkingId === a.assessment_id ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <ShieldCheck className="h-3.5 w-3.5 text-sky-400" />
                )}
                Check Eligibility
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
