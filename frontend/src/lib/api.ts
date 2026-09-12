// Frontend API Client for AI College Learning Assistant

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export interface StudentProfile {
  student_id: string;
  enrolled_courses_count: number;
  assessments_taken_count: number;
  total_views: number;
  total_resource_clicks: number;
  certificates_earned: number;
}

export interface DemoStudent {
  student_id: string;
  name: string;
  profile_description: string;
  courses_count: number;
  assessments_count: number;
  views: number;
}

export interface CourseSummary {
  course_id: number;
  course_title: string;
  course_domain: string;
  course_sub_domain: string;
  course_level: string;
  course_hours: number;
  enrolled_at: string;
  progress_percentage: number;
  certificate_issued: boolean;
  certificate_link?: string;
}

export interface TopicPerformance {
  topic: string;
  skill: string;
  total_questions: number;
  passed_count: number;
  failed_count: number;
  obtained_score: number;
  max_score: number;
  accuracy_percentage: number;
  is_weak: boolean;
}

export interface DifficultyPerformance {
  difficulty: string;
  total_questions: number;
  accuracy_percentage: number;
}

export interface LearningEfficiencyDetail {
  score: number;
  grade: string;
  formula_summary: string;
  factors: Record<string, number>;
  explanation: string;
}

export interface EngagementPerformanceInsight {
  quadrant: string;
  summary: string;
  detailed_reasoning: string;
  recommended_strategy: string;
}

export interface PerformanceSummary {
  student_id: string;
  overall_accuracy_percentage: number;
  total_questions_attempted: number;
  total_assessments_completed: number;
  weak_topics: TopicPerformance[];
  all_topics: TopicPerformance[];
  difficulty_breakdown: DifficultyPerformance[];
  learning_efficiency: LearningEfficiencyDetail;
  engagement_vs_performance: EngagementPerformanceInsight;
}

export interface AssessmentItem {
  assessment_id: number;
  title: string;
  domain: string;
  sub_domain: string;
  num_questions: number;
  passing_score: number;
  max_attempts: number;
  is_active: boolean;
  prerequisite_course_id?: number;
  prerequisite_course_name?: string;
}

export interface AssessmentRequirement {
  name: string;
  satisfied: boolean;
  detail: string;
}

export interface AssessmentEligibility {
  assessment_id: number;
  title: string;
  eligible: boolean;
  requirements: AssessmentRequirement[];
  failed_requirements: string[];
  reasons: string[];
}

export interface StudyRecommendation {
  priority_topic: string;
  skill?: string;
  accuracy_percentage?: number;
  total_questions?: number;
  failed_count?: number;
  reason: string;
  recommended_action: string;
  relevant_course_material: string;
  practice_recommendation: string;
  coach_summary?: string;
}

export interface ChatResponse {
  reply: string;
  intent: string;
  tools_used: string[];
  sources: string[];
  data_trace?: any;
}

export interface PracticeQuestion {
  question_id: number;
  question: string;
  options: string[];
  topic: string;
  difficulty: string;
  source: string;
}

export interface PracticeQuizResponse {
  quiz_id: string;
  topic: string;
  difficulty: string;
  num_questions: number;
  questions: PracticeQuestion[];
}

export interface PracticeSubmissionResult {
  quiz_id: string;
  topic: string;
  score_obtained: number;
  total_possible_score: number;
  accuracy_percentage: number;
  results: Array<{
    question_id: number;
    question: string;
    options: string[];
    your_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
    source: string;
  }>;
  next_study_recommendation: string;
}

export async function fetchApi<T>(endpoint: string, studentId: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    'X-Student-Id': studentId,
    ...(options.headers || {}),
  };

  const url = `${API_BASE}/api/v1${endpoint}`;
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}
