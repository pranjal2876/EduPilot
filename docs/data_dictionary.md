# Data Dictionary — AI College Learning Assistant

This document provides a comprehensive specification of the structured datasets provided for the **AI College Learning Assistant**, their fields, data types, nested JSON schemas, inferred relationships, derived metrics, and known dataset limitations.

---

## 1. Dataset Overview

The system ingests two primary datasets:
1. **Student Course Engagement** (`student_course_engagement.xlsx`): 9,157 records covering 1,480 unique students and 245 unique courses across 5 academic domains.
2. **Hackathon Submissions** (`Untitled spreadsheet.xlsx`): 18,299 records covering 1,830 unique students and 2,081 unique hackathon assessments across skills such as Aptitude, Coding, and English.
3. **Student Overlap**: Exactly **72 students** have recorded activity in **both** datasets, providing full multi-modal profiles (rich course learning engagement combined with extensive assessment question attempts).

---

## 2. Dataset 1: `student_course_engagement.xlsx`

### 2.1 Table Structure & Columns

| Column Name | Data Type (Source) | Nullable | Example Value | Description |
| :--- | :--- | :---: | :--- | :--- |
| `user_id` | String (UUID v4) | No | `0836214b-4f04-40aa-b6fd-1de3abfc8f3b` | Unique identifier of the student. |
| `course_id` | Integer (int64) | No | `229` | Unique numerical identifier for the course. |
| `course_title` | String | No | `Microprocessor & Microcontroller` | Full human-readable name of the course. |
| `course_domain` | String (Category) | No | `Skills Wise`, `Technologies`, `Customized Lesson Plan` | Broad academic category/stream. |
| `course_sub_domain`| String | No | `Microprocessor & Microcontroller`, `Python` | Granular academic topic or discipline. |
| `course_level` | String (Enum) | No | `beginner`, `intermediate`, `advanced` | Difficulty level assigned to the course. |
| `course_hours` | Integer (int64) | No | `60` | Estimated credit hours / curriculum duration. |
| `enrolled_at` | Timestamp (ISO) | No | `2026-01-02 09:04:52` | Timestamp when the student enrolled. |
| `is_legacy_completion` | Boolean | No | `False` | Flag indicating completion in a legacy LMS. |
| `certificate_issued` | Boolean | No | `False` / `True` | Whether a certificate was issued to the student. |
| `certificate_issued_at`| Timestamp | Yes (9,035 nulls) | `2026-02-15 14:22:10` | Issuance timestamp (null if not certified). |
| `certificate_link` | String (URL) | Yes (9,035 nulls) | `https://certificates.example.com/...` | Public verification URL for the certificate. |
| `total_views` | Integer (int64) | No | `1` | Cumulative number of times student viewed course. |
| `first_viewed_at` | Timestamp (ISO) | No | `2026-01-02 09:04:50` | Timestamp of student's initial course visit. |
| `last_viewed_at` | Timestamp (ISO) | No | `2026-01-02 09:04:50` | Timestamp of student's most recent visit. |
| `total_chapters_in_course` | Integer (int64) | No | `10` | Total syllabus chapters configured in course. |
| `total_activities_in_course` | Integer (int64) | No | `75` | Total learning activities (videos, pages, links). |
| `mcq_attempted_count` | Integer (int64) | No | `0` | In-course formative MCQ questions attempted. |
| `mcq_total_score_obtained` | Integer (int64) | No | `0` | Cumulative score obtained on in-course MCQs. |
| `resource_clicks_downloads`| Integer (int64) | No | `2` | Count of interaction events on course assets. |
| `engagement_json` | Serialized JSON | No | `{"views": [...], "mcq_submissions": [...], ...}` | Granular event-level interaction logs. |

### 2.2 `engagement_json` Internal Schema

The `engagement_json` field stores a JSON object with three root keys:
- `views`: List of view objects with timestamp `viewed_at`.
- `mcq_submissions`: List of in-course MCQ attempts with `mcq_id`, `chapter_activity_id`, `score`, `answer`, `submitted_at`.
- `resource_clicks_downloads`: List of asset interaction events with `type` (link/page/pdf), `clicked_at`, `course_chapter_id`, `chapter_activity_id`.

---

## 3. Dataset 2: `Untitled spreadsheet.xlsx` (Hackathon Submissions)

### 3.1 Table Structure & Columns

| Column Name | Data Type (Source) | Nullable | Example Value | Description |
| :--- | :--- | :---: | :--- | :--- |
| `user_id` | String (UUID v4) | No | `0001e847-507d-44d9-8683-7a879fc9689c` | Unique identifier of the student. |
| `hackathon_id` | Integer (int64) | No | `341` | Unique numerical identifier for the assessment. |
| `num_questions` | Integer (int64) | No | `57` | Total number of questions configured in test. |
| `submission_json`| Serialized JSON | Yes (1,146 nulls) | `[{"skill": "English", ...}]` | Array of question-level attempt objects. |

### 3.2 `submission_json` Question-Level Schema

When present, `submission_json` is an array of objects where each element records a student's attempt on a single question:
- `attempt_id`: Unique numeric identifier for the submission attempt.
- `round_id`: Assessment round identifier.
- `question_id`: Unique numeric question identifier.
- `skill`: Core domain (e.g. `Aptitude`, `Coding`, `English`).
- `question_sub_domain`: Specific topic list (e.g. `["Paragraph question"]`, `["Percentages"]`, `["Time and Work"]`, `["Profit and Loss"]`, `["Python"]`, `["Array"]`).
- `difficulty`: `easy`, `medium`, or `hard`.
- `question_type`: `mcq`, `coding`, `subjective`, etc.
- `obtained_score`: Score earned by student.
- `question_score`: Maximum possible score for the question.
- `status`: `pass`, `fail`, `unAttempted`, or `partiallyCorrect`.
- `submission_time`: ISO timestamp when question was submitted.
- `submission`: Object containing `questionId`, `questionType`, and `mcqAnswer` UUID list.

---

## 4. Inferred Relationships

1. **Student Entity**: Both datasets share `user_id` as the primary student identifier.
2. **Course Entity**: `course_id`, `course_title`, `course_domain`, `course_sub_domain`, `course_level`, `course_hours`, `total_chapters_in_course`, and `total_activities_in_course` define static course entities.
3. **Assessment Entity**: `hackathon_id` represents an assessment entity, with `num_questions` representing total question count.
4. **Topic Alignment**: The `question_sub_domain` values in assessments (e.g., *Percentages*, *Time and Work*, *Python*, *Profit and Loss*, *Number Systems*) directly align with `course_title` and `course_sub_domain` from the engagement dataset.

---

## 5. Derived Metrics Specification

| Metric Name | Derivation Formula | Interpretation & Usage |
| :--- | :--- | :--- |
| **Topic Accuracy** | (sum(obtained_score) / sum(question_score)) * 100% | Quantifies student mastery in a specific sub-domain. |
| **Weak Topic Flag** | Topic Accuracy < 60.0% (or Fail Count >= 2) | Identifies areas needing remediation and study coach priority. |
| **Course Progress** | min(100%, ((total_views + resource_clicks) / total_activities) * 100%) (or 100% if certificate_issued) | Approximates syllabus completion percentage. |
| **Learning Efficiency** | 0.40 * Accuracy + 0.30 * Progress + 0.20 * ResourceRatio + 0.10 * Consistency | Normalized 0–100 score reflecting learning pace and quality. |
| **Engagement vs Performance Quadrant** | Bivariate classification comparing Engagement Index vs Assessment Accuracy | Pinpoints students with high effort/low yield or high talent/low effort. |

---

## 6. Dataset Limitations

1. **Absence of Question Stems**: The assessment dataset stores question IDs, scores, and UUID answer choices, but not the textual question prompts or option strings. RAG-grounded practice question generation synthesizes questions from curriculum notes rather than replaying raw question IDs.
2. **Null Submissions**: 1,146 rows in `Untitled spreadsheet.xlsx` have `submission_json = NULL`, representing registrations where the student never launched or submitted the hackathon.
3. **Partial Student Overlap**: 72 students exist in both datasets, while others only exist in one. The application handles single-dataset students gracefully without crashing, while prioritizing overlapping students for full end-to-end multi-modal demonstrations.
4. **Certificate Rarity**: Only 122 out of 9,157 course enrollments (~1.33%) have certificates issued, making resource clicks and views vital indicators of active progress.
