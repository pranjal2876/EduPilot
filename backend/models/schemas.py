from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class StudentProfile(BaseModel):
    student_id: str
    enrolled_courses_count: int
    assessments_taken_count: int
    total_views: int
    total_resource_clicks: int
    certificates_earned: int

class CourseSummary(BaseModel):
    course_id: int
    course_title: str
    course_domain: str
    course_sub_domain: str
    course_level: str
    course_hours: int
    enrolled_at: Optional[str]
    progress_percentage: float
    certificate_issued: bool
    certificate_link: Optional[str]

class CourseEngagementDetail(BaseModel):
    course_id: int
    course_title: str
    total_views: int
    first_viewed_at: Optional[str]
    last_viewed_at: Optional[str]
    mcq_attempted_count: int
    mcq_total_score_obtained: int
    resource_clicks_downloads: int
    progress_percentage: float

class TopicPerformance(BaseModel):
    topic: str
    skill: str
    total_questions: int
    passed_count: int
    failed_count: int
    obtained_score: float
    max_score: float
    accuracy_percentage: float
    is_weak: bool

class DifficultyPerformance(BaseModel):
    difficulty: str # easy, medium, hard
    total_questions: int
    accuracy_percentage: float

class LearningEfficiencyDetail(BaseModel):
    score: int # 0 to 100
    grade: str # High, Moderate, Needs Improvement
    formula_summary: str
    factors: Dict[str, float] # accuracy_weight, progress_weight, etc.
    explanation: str

class EngagementPerformanceInsight(BaseModel):
    quadrant: str # e.g. "High Engagement, Low Assessment Performance"
    summary: str
    detailed_reasoning: str
    recommended_strategy: str

class StudentPerformanceSummary(BaseModel):
    student_id: str
    overall_accuracy_percentage: float
    total_questions_attempted: int
    total_assessments_completed: int
    weak_topics: List[TopicPerformance]
    all_topics: List[TopicPerformance]
    difficulty_breakdown: List[DifficultyPerformance]
    learning_efficiency: LearningEfficiencyDetail
    engagement_vs_performance: EngagementPerformanceInsight

class AssessmentRequirement(BaseModel):
    name: str
    satisfied: bool
    detail: str

class AssessmentEligibilityResponse(BaseModel):
    assessment_id: int
    title: str
    eligible: bool
    requirements: List[AssessmentRequirement]
    failed_requirements: List[str]
    reasons: List[str]

class PracticeQuestion(BaseModel):
    question_id: int
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    source: str
    topic: str
    difficulty: str

class PracticeQuizRequest(BaseModel):
    topic: str
    course_name: Optional[str] = "General"
    difficulty: str = "medium" # easy, medium, hard
    num_questions: int = Field(default=5, ge=1, le=10)

class PracticeQuizResponse(BaseModel):
    quiz_id: str
    topic: str
    difficulty: str
    num_questions: int
    questions: List[Dict[str, Any]] # question prompt & options (answer hidden until submission)

class PracticeSubmissionRequest(BaseModel):
    quiz_id: str
    topic: str
    difficulty: str
    answers: Dict[int, str] # question_id -> chosen option string

class PracticeSubmissionResult(BaseModel):
    quiz_id: str
    topic: str
    score_obtained: float
    total_possible_score: float
    accuracy_percentage: float
    results: List[Dict[str, Any]] # question, your_answer, correct_answer, is_correct, explanation, source
    next_study_recommendation: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    intent: str
    tools_used: List[str]
    sources: List[str]
    data_trace: Optional[Dict[str, Any]] = None
