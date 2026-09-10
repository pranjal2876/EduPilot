# Test Plan & 20-Scenario Verification Matrix — AI College Learning Assistant

This document details the automated evaluation suite implemented in `backend/tests/test_suite_20.py` covering all 20 required scenarios specified in Phase 16 and Section 14 of the assignment specification.

---

## 1. Running the Automated Test Suite

Run the full automated test suite directly from the project root:

```bash
python -m unittest backend/tests/test_suite_20.py
```

Or using pytest:

```bash
pytest backend/tests/test_suite_20.py -v
```

---

## 2. 20-Scenario Evaluation Matrix & Results

| # | Scenario Category | Question / Action | Expected Behaviour | Actual Behaviour | Result |
| :-: | :--- | :--- | :--- | :--- | :-: |
| **1** | **Database Question (Profile)** | `GET /api/v1/students/me/profile` | Returns HTTP 200 with student ID, enrolled course count, and engagement stats. | Status 200, Enrolled: 11 courses, Views: 11, Resources: 32 | **PASS** |
| **2** | **Course Engagement Question** | `GET /api/v1/students/me/courses/103/engagement` | Returns views, MCQ scores, and resource downloads for Python course. | Status 200, Views: 1, Resources: 8, Progress: 8.7% | **PASS** |
| **3** | **Performance Question** | `GET /api/v1/performance/me` | Computes overall accuracy percentage and question attempt counts. | Status 200, Accuracy: 34.5%, Total Q: 239, Assessments: 9 | **PASS** |
| **4** | **Weak-Topic Question** | `GET /api/v1/performance/me/weak-topics` | Returns list of topics strictly with accuracy $< 60\%$ or fail count $\ge 2$. | Status 200, Found 48 weak topics. Top weak: Alligation and Mixture (0%) | **PASS** |
| **5** | **Assessment History Question** | `GET /api/v1/students/me/assessments/history` | Returns chronological list of past attempts with scores and status. | Status 200, 9 past assessment attempts loaded with scores and dates | **PASS** |
| **6** | **RAG Question (DBMS Normalization)** | *"Explain normalization from my DBMS course."* | Retrieves DBMS curriculum chunks and explains 1NF/2NF/3NF without hallucination. | Status 200, Intent: `course_concept`, Explains atomic values, partial/transitive dependencies | **PASS** |
| **7** | **RAG Source Verification** | *"Explain ACID properties in transactions."* | Explicitly cites curriculum source document. | Status 200, Sources: `Database Management Systems (DBMS) → 5. ACID Properties (Source: dbms_normalization.md)` | **PASS** |
| **8** | **Missing RAG Information** | *"Explain quantum teleportation in astrophysics."* | Refuses and states information is unavailable in course material. | Status 200, Reply: *"I couldn't find sufficient information in the available course material."* | **PASS** |
| **9** | **Business-Rule Question** | `GET /api/v1/assessments/341/eligibility` | Evaluates all 4 deterministic institutional rules. | Status 200, Evaluated 4 formal rules (Active, Prereq Course, Prereq Test, Max Attempts) | **PASS** |
| **10** | **Ineligible Assessment** | `GET /api/v1/assessments/901/eligibility` | Returns `eligible: false` with explicit prerequisite failure reason. | Status 200, `eligible: false`, Failed: `['Prerequisite Course Completion']`, Progress: 8.7% < 80% | **PASS** |
| **11** | **Eligible Assessment** | `GET /api/v1/assessments/7/eligibility` | Returns `eligible: true` when all requirements are satisfied. | Status 200, `eligible: true`, All requirements passed | **PASS** |
| **12** | **Multi-Source Question** | *"Can I take the assessment and what should I study?"* | Combines assessment eligibility checking and study coach recommendations. | Status 200, Tools invoked: `check_assessment_eligibility`, `get_course_progress`, `get_topic_performance` | **PASS** |
| **13** | **Follow-up Question (Memory)** | *"Explain the first one."* (after weak topics query) | Resolves "the first one" to primary weak topic using session memory. | Status 200, Intent: `course_concept`, Resolves to *Alligation and Mixture*, retrieves curriculum notes | **PASS** |
| **14** | **Personalized Recommendation** | `GET /api/v1/performance/me/recommendation` | Returns priority topic, factual reason with actual score, and practice plan. | Status 200, Priority: *Alligation and Mixture*, Reason: 0.0% accuracy across 2 questions | **PASS** |
| **15** | **Personalized Practice** | `POST /api/v1/practice/generate` & `submit` | Generates grounded questions, grades answers, returns score & explanations. | Status 200, Score: 3.0/3.0 (100%), Itemized explanations and sources returned | **PASS** |
| **16** | **Invalid Student Handling** | `GET /api/v1/students/me/profile` (invalid UUID) | Returns HTTP 404 Not Found without system crash. | Status 404, Detail: *"Student profile not found"* | **PASS** |
| **17** | **Unauthorized Access Prevention** | `GET /api/v1/students/me/courses/229/progress` | Blocks access to course progress for courses student is not enrolled in. | Status 404, Detail: *"Course enrollment not found for this student"* | **PASS** |
| **18** | **Missing Student Data Handling** | `GET /api/v1/performance/me` (0-record student) | Handles zero-activity student gracefully returning 0% without divide-by-zero error. | Status 200, Total Q: 0, Accuracy: 0.0%, Learning Efficiency: 0/100 | **PASS** |
| **19** | **Difficult-Topic Analysis** | `GET /api/v1/performance/me` (difficulty breakdown) | Computes accuracy across easy, medium, and hard difficulty levels. | Status 200, Easy: 32.0%, Medium: 34.5%, Hard: 41.7% | **PASS** |
| **20** | **Hallucination Refusal Test** | *"What is the internal college policy for hostel curfew?"* | Explicitly refuses to fabricate university administrative policy. | Status 200, Intent: `unsupported_policy`, Refusal: *"I don't have enough information in available college records..."* | **PASS** |

---

## 3. Summary of Verification

- **Total Test Cases**: 20 / 20
- **Passed**: 20 (100%)
- **Failed**: 0 (0%)
- **Execution Time**: ~10 seconds
