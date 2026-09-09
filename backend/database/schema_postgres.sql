-- PostgreSQL Normalized Application Schema for AI College Learning Assistant
-- Generates all tables, primary keys, foreign keys, and analytical indexes

-- 1. Students
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Courses
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    course_title VARCHAR(255) NOT NULL,
    course_domain VARCHAR(100) NOT NULL,
    course_sub_domain VARCHAR(100) NOT NULL,
    course_level VARCHAR(50) NOT NULL,
    course_hours INTEGER DEFAULT 0,
    total_chapters INTEGER DEFAULT 0,
    total_activities INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_courses_domain ON courses(course_domain);
CREATE INDEX IF NOT EXISTS idx_courses_sub_domain ON courses(course_sub_domain);

-- 3. Student Courses (Enrollments & Certificates)
CREATE TABLE IF NOT EXISTS student_courses (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_legacy_completion BOOLEAN DEFAULT FALSE,
    certificate_issued BOOLEAN DEFAULT FALSE,
    certificate_issued_at TIMESTAMP WITHOUT TIME ZONE,
    certificate_link TEXT,
    CONSTRAINT uq_student_course UNIQUE (student_id, course_id)
);
CREATE INDEX IF NOT EXISTS idx_student_courses_student ON student_courses(student_id);
CREATE INDEX IF NOT EXISTS idx_student_courses_course ON student_courses(course_id);

-- 4. Course Engagement
CREATE TABLE IF NOT EXISTS course_engagement (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    total_views INTEGER DEFAULT 0,
    first_viewed_at TIMESTAMP WITHOUT TIME ZONE,
    last_viewed_at TIMESTAMP WITHOUT TIME ZONE,
    mcq_attempted_count INTEGER DEFAULT 0,
    mcq_total_score_obtained INTEGER DEFAULT 0,
    resource_clicks_downloads INTEGER DEFAULT 0,
    views_json JSONB,
    mcq_submissions_json JSONB,
    resource_clicks_json JSONB,
    CONSTRAINT uq_course_engagement UNIQUE (student_id, course_id)
);
CREATE INDEX IF NOT EXISTS idx_course_engagement_student ON course_engagement(student_id);
CREATE INDEX IF NOT EXISTS idx_course_engagement_course ON course_engagement(course_id);

-- 5. Assessments
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    domain VARCHAR(100),
    sub_domain VARCHAR(100),
    num_questions INTEGER DEFAULT 0,
    passing_score DOUBLE PRECISION DEFAULT 60.0,
    max_attempts INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    prerequisite_course_id INTEGER REFERENCES courses(course_id) ON DELETE SET NULL,
    prerequisite_assessment_id INTEGER REFERENCES assessments(assessment_id) ON DELETE SET NULL
);

-- 6. Assessment Attempts
CREATE TABLE IF NOT EXISTS assessment_attempts (
    attempt_id INTEGER PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    assessment_id INTEGER NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    round_id INTEGER,
    submitted_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_questions_attempted INTEGER DEFAULT 0,
    total_score_obtained DOUBLE PRECISION DEFAULT 0.0,
    total_possible_score DOUBLE PRECISION DEFAULT 0.0,
    accuracy_rate DOUBLE PRECISION DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'completed'
);
CREATE INDEX IF NOT EXISTS idx_attempts_student ON assessment_attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_attempts_assessment ON assessment_attempts(assessment_id);
CREATE INDEX IF NOT EXISTS idx_attempts_submitted_at ON assessment_attempts(submitted_at);

-- 7. Assessment Question Results
CREATE TABLE IF NOT EXISTS assessment_question_results (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER NOT NULL REFERENCES assessment_attempts(attempt_id) ON DELETE CASCADE,
    student_id VARCHAR(64) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    assessment_id INTEGER NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL,
    skill VARCHAR(100),
    topic VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50) DEFAULT 'medium',
    question_type VARCHAR(50) DEFAULT 'mcq',
    status VARCHAR(50) DEFAULT 'unAttempted',
    obtained_score DOUBLE PRECISION DEFAULT 0.0,
    question_score DOUBLE PRECISION DEFAULT 0.0,
    submission_time TIMESTAMP WITHOUT TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_qr_student ON assessment_question_results(student_id);
CREATE INDEX IF NOT EXISTS idx_qr_topic ON assessment_question_results(topic);
CREATE INDEX IF NOT EXISTS idx_qr_student_topic ON assessment_question_results(student_id, topic);
CREATE INDEX IF NOT EXISTS idx_qr_difficulty ON assessment_question_results(student_id, difficulty);
CREATE INDEX IF NOT EXISTS idx_qr_status ON assessment_question_results(student_id, status);

-- 8. Practice History
CREATE TABLE IF NOT EXISTS practice_history (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_name VARCHAR(100),
    topic VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50) DEFAULT 'medium',
    num_questions INTEGER DEFAULT 5,
    score_obtained DOUBLE PRECISION DEFAULT 0.0,
    total_score DOUBLE PRECISION DEFAULT 0.0,
    accuracy DOUBLE PRECISION DEFAULT 0.0,
    completed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    details_json JSONB
);
CREATE INDEX IF NOT EXISTS idx_practice_student ON practice_history(student_id);

-- 9. Conversation History (Chat context)
CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    intent VARCHAR(50),
    tools_used_json JSONB,
    sources_used_json JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_chat_student ON conversation_messages(student_id);
