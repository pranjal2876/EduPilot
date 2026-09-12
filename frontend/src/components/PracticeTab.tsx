import React, { useState } from 'react';
import { Target, CheckCircle2, XCircle, FileText, ArrowRight, RefreshCw, Trophy } from 'lucide-react';
import { fetchApi, PracticeQuizResponse, PracticeSubmissionResult } from '../lib/api';

interface PracticeTabProps {
  studentId: string;
}

export const PracticeTab: React.FC<PracticeTabProps> = ({ studentId }) => {
  const [topic, setTopic] = useState('Profit and Loss');
  const [difficulty, setDifficulty] = useState('medium');
  const [numQuestions, setNumQuestions] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [activeQuiz, setActiveQuiz] = useState<PracticeQuizResponse | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [submissionResult, setSubmissionResult] = useState<PracticeSubmissionResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const topicsList = [
    'Profit and Loss',
    'Database Normalization',
    'Python',
    'Alligation and Mixture',
    'Percentages',
    'Time and Work',
  ];

  const handleGenerateQuiz = async () => {
    setLoading(true);
    setError(null);
    setSubmissionResult(null);
    setSelectedAnswers({});

    try {
      const res = await fetchApi<PracticeQuizResponse>(
        '/practice/generate',
        studentId,
        {
          method: 'POST',
          body: JSON.stringify({
            topic,
            course_name: 'General',
            difficulty,
            num_questions: numQuestions,
          }),
        }
      );
      setActiveQuiz(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate quiz');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (qid: number, opt: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [qid]: opt,
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!activeQuiz) return;
    setSubmitting(true);
    setError(null);

    try {
      const res = await fetchApi<PracticeSubmissionResult>(
        '/practice/submit',
        studentId,
        {
          method: 'POST',
          body: JSON.stringify({
            quiz_id: activeQuiz.quiz_id,
            topic: activeQuiz.topic,
            difficulty: activeQuiz.difficulty,
            answers: selectedAnswers,
          }),
        }
      );
      setSubmissionResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Quiz Config Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-center space-x-3 mb-4">
          <div className="h-10 w-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-sm">
            <Target className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">Personalized Practice Lab</h2>
            <p className="text-xs text-slate-500">
              Questions synthesized strictly from retrieved course notes • Graded deterministically
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Target Topic</label>
            <select
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              {topicsList.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Difficulty Level</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="easy">Easy (Foundational)</option>
              <option value="medium">Medium (Standard)</option>
              <option value="hard">Hard (Advanced)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Question Count</label>
            <select
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value={3}>3 Questions</option>
              <option value={5}>5 Questions</option>
            </select>
          </div>

          <button
            onClick={handleGenerateQuiz}
            disabled={loading}
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs py-2.5 px-4 rounded-lg shadow-sm transition disabled:opacity-50 flex items-center justify-center gap-1.5"
          >
            {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Target className="h-4 w-4" />}
            Generate Quiz
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-xs border border-red-200">
            {error}
          </div>
        )}
      </div>

      {/* Active Quiz Form */}
      {activeQuiz && !submissionResult && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-base font-bold text-slate-900">{activeQuiz.topic} Quiz</h3>
              <p className="text-xs text-slate-500">
                Difficulty: <span className="capitalize font-semibold">{activeQuiz.difficulty}</span> •{' '}
                {activeQuiz.questions.length} questions
              </p>
            </div>
            <span className="text-xs font-mono bg-slate-100 px-2.5 py-1 rounded text-slate-600">
              Session ID: {activeQuiz.quiz_id.slice(0, 8)}
            </span>
          </div>

          <div className="space-y-6">
            {activeQuiz.questions.map((q, idx) => (
              <div key={q.question_id} className="p-4 rounded-xl bg-slate-50/70 border border-slate-200/80">
                <p className="text-xs font-semibold text-slate-500 mb-1">Question {idx + 1}</p>
                <p className="text-sm font-semibold text-slate-900 mb-3">{q.question}</p>

                <div className="space-y-2">
                  {q.options.map((opt) => {
                    const isSelected = selectedAnswers[q.question_id] === opt;
                    return (
                      <label
                        key={opt}
                        onClick={() => handleSelectOption(q.question_id, opt)}
                        className={`flex items-center space-x-3 p-3 rounded-lg border text-xs cursor-pointer transition ${
                          isSelected
                            ? 'bg-emerald-50 border-emerald-500 text-emerald-900 font-medium'
                            : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        <input
                          type="radio"
                          name={`q-${q.question_id}`}
                          checked={isSelected}
                          onChange={() => {}}
                          className="text-emerald-600 focus:ring-emerald-500 h-3.5 w-3.5"
                        />
                        <span>{opt}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-end">
            <button
              onClick={handleSubmitQuiz}
              disabled={submitting || Object.keys(selectedAnswers).length === 0}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm transition disabled:opacity-50 flex items-center gap-1.5"
            >
              {submitting ? 'Scoring Answers...' : 'Submit Quiz & Grade'}
            </button>
          </div>
        </div>
      )}

      {/* Graded Quiz Results Card */}
      {submissionResult && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="bg-gradient-to-r from-emerald-900 to-teal-950 text-white p-6 rounded-xl flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-300">
                Evaluation Complete
              </span>
              <h3 className="text-2xl font-bold mt-1">
                Score: {submissionResult.score_obtained} / {submissionResult.total_possible_score}
              </h3>
              <p className="text-sm text-emerald-100 mt-0.5">
                Accuracy: {submissionResult.accuracy_percentage}%
              </p>
            </div>
            <Trophy className="h-12 w-12 text-amber-400" />
          </div>

          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
            <span className="text-xs font-bold text-emerald-800 uppercase tracking-wide">Next Step Recommendation:</span>
            <p className="text-xs text-emerald-900 mt-1 font-medium leading-relaxed">
              {submissionResult.next_study_recommendation}
            </p>
          </div>

          <div className="space-y-4">
            <h4 className="text-sm font-bold text-slate-900">Question-by-Question Review</h4>
            {submissionResult.results.map((r, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl border text-xs ${
                  r.is_correct ? 'bg-emerald-50/40 border-emerald-200' : 'bg-red-50/40 border-red-200'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-slate-800 text-sm">Question {idx + 1}</span>
                  {r.is_correct ? (
                    <span className="flex items-center gap-1 text-emerald-700 font-bold">
                      <CheckCircle2 className="h-4 w-4" /> Correct (+1.0)
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-red-700 font-bold">
                      <XCircle className="h-4 w-4" /> Incorrect (0.0)
                    </span>
                  )}
                </div>
                <p className="text-slate-800 font-medium mb-2">{r.question}</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 p-2.5 bg-white/80 rounded-lg border border-slate-200">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Your Answer</span>
                    <span className={`font-semibold ${r.is_correct ? 'text-emerald-700' : 'text-red-700'}`}>
                      {r.your_answer || 'No answer selected'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Correct Answer</span>
                    <span className="font-semibold text-emerald-700">{r.correct_answer}</span>
                  </div>
                </div>

                <div className="mt-2.5 text-slate-600 leading-relaxed">
                  <span className="font-semibold text-slate-800">Explanation: </span>
                  {r.explanation}
                </div>

                <div className="mt-2 text-[11px] text-slate-500 flex items-center gap-1">
                  <FileText className="h-3 w-3" /> Source: <span className="font-mono">{r.source}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-2 flex justify-end">
            <button
              onClick={() => {
                setActiveQuiz(null);
                setSubmissionResult(null);
              }}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg shadow-sm"
            >
              Start New Practice Quiz
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
