from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    enrollments = relationship("StudentCourse", back_populates="student", cascade="all, delete-orphan")
    engagements = relationship("CourseEngagement", back_populates="student", cascade="all, delete-orphan")
    attempts = relationship("AssessmentAttempt", back_populates="student", cascade="all, delete-orphan")
    question_results = relationship("AssessmentQuestionResult", back_populates="student", cascade="all, delete-orphan")
    practice_sessions = relationship("PracticeHistory", back_populates="student", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_title = Column(String(255), nullable=False, index=True)
    course_domain = Column(String(100), nullable=False, index=True)
    course_sub_domain = Column(String(100), nullable=False, index=True)
    course_level = Column(String(50), nullable=False)
    course_hours = Column(Integer, default=0)
    total_chapters = Column(Integer, default=0)
    total_activities = Column(Integer, default=0)

    # Relationships
    enrollments = relationship("StudentCourse", back_populates="course")
    engagements = relationship("CourseEngagement", back_populates="course")


class StudentCourse(Base):
    __tablename__ = "student_courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False, index=True)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    is_legacy_completion = Column(Boolean, default=False)
    certificate_issued = Column(Boolean, default=False)
    certificate_issued_at = Column(DateTime, nullable=True)
    certificate_link = Column(Text, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    __table_args__ = (
        Index("idx_student_course_unique", "student_id", "course_id", unique=True),
    )


class CourseEngagement(Base):
    __tablename__ = "course_engagement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False, index=True)
    total_views = Column(Integer, default=0)
    first_viewed_at = Column(DateTime, nullable=True)
    last_viewed_at = Column(DateTime, nullable=True)
    mcq_attempted_count = Column(Integer, default=0)
    mcq_total_score_obtained = Column(Integer, default=0)
    resource_clicks_downloads = Column(Integer, default=0)
    
    # Store parsed JSON for deep analytics
    views_json = Column(JSON, nullable=True)
    mcq_submissions_json = Column(JSON, nullable=True)
    resource_clicks_json = Column(JSON, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="engagements")
    course = relationship("Course", back_populates="engagements")

    __table_args__ = (
        Index("idx_engagement_student_course", "student_id", "course_id", unique=True),
    )


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=True)
    sub_domain = Column(String(100), nullable=True)
    num_questions = Column(Integer, default=0)
    passing_score = Column(Float, default=60.0) # percentage
    max_attempts = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    
    # Prerequisites for business rule engine
    prerequisite_course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="SET NULL"), nullable=True)
    prerequisite_assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    attempts = relationship("AssessmentAttempt", back_populates="assessment")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    attempt_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(64), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False, index=True)
    round_id = Column(Integer, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True)
    total_questions_attempted = Column(Integer, default=0)
    total_score_obtained = Column(Float, default=0.0)
    total_possible_score = Column(Float, default=0.0)
    accuracy_rate = Column(Float, default=0.0) # 0.0 to 1.0
    status = Column(String(50), default="completed") # pass, fail, completed

    # Relationships
    student = relationship("Student", back_populates="attempts")
    assessment = relationship("Assessment", back_populates="attempts")
    question_results = relationship("AssessmentQuestionResult", back_populates="attempt", cascade="all, delete-orphan")


class AssessmentQuestionResult(Base):
    __tablename__ = "assessment_question_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    attempt_id = Column(Integer, ForeignKey("assessment_attempts.attempt_id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(64), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, nullable=False, index=True)
    skill = Column(String(100), nullable=True, index=True)
    topic = Column(String(100), nullable=False, index=True) # mapped from question_sub_domain
    difficulty = Column(String(50), default="medium", index=True)
    question_type = Column(String(50), default="mcq")
    status = Column(String(50), default="unAttempted", index=True) # pass, fail, unAttempted, partiallyCorrect
    obtained_score = Column(Float, default=0.0)
    question_score = Column(Float, default=0.0)
    submission_time = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="question_results")
    attempt = relationship("AssessmentAttempt", back_populates="question_results")

    __table_args__ = (
        Index("idx_student_topic_status", "student_id", "topic", "status"),
        Index("idx_student_difficulty", "student_id", "difficulty"),
    )


class PracticeHistory(Base):
    __tablename__ = "practice_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    course_name = Column(String(100), nullable=True)
    topic = Column(String(100), nullable=False, index=True)
    difficulty = Column(String(50), default="medium")
    num_questions = Column(Integer, default=5)
    score_obtained = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.0)
    completed_at = Column(DateTime, default=datetime.utcnow)
    details_json = Column(JSON, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="practice_sessions")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False) # user or assistant
    content = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)
    tools_used_json = Column(JSON, nullable=True)
    sources_used_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
