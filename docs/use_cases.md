# Core Use Cases & User Journeys — AI College Learning Assistant

This document details the primary use cases supported by the prototype, highlighting the distinct roles played by the Database, RAG, Business Rules, and AI Orchestration.

---

## Use Case 1: Diagnostic Weak-Topic Identification
- **User Query**: *"What topics am I weak in?"* or *"What are my weak topics?"*
- **Primary Source**: Structured Assessment Submissions Database (`assessment_question_results` table).
- **Processing Flow**:
  1. Orchestrator classifies intent as `weak_topics`.
  2. Calls controlled backend function `get_weak_topics(student_id)`.
  3. Analytics engine evaluates accuracy for each topic: $\text{Accuracy} = \frac{\sum \text{obtained\_score}}{\sum \text{question\_score}}$.
  4. Filters topics with accuracy $< 60\%$ or failed questions $\ge 2$, sorted in ascending order of proficiency.
  5. LLM responds with exact factual accuracy figures and failure counts (e.g. Alligation and Mixture, 0.0%, 2 failures).
  6. Conversational memory records the identified weak topics for subsequent follow-up queries.

---

## Use Case 2: Grounded Course Concept Explanation (RAG)
- **User Query**: *"Explain normalization from my DBMS course."*
- **Primary Source**: Unstructured Course Curriculum Knowledge Base (`dbms_normalization.md`).
- **Processing Flow**:
  1. Orchestrator classifies intent as `course_concept`.
  2. Calls RAG service `search_course_content(query, course_filter="DBMS")`.
  3. Vector store computes cosine similarity using `all-MiniLM-L6-v2` embeddings over chunked markdown documents.
  4. Retrieves high-scoring chunks explaining 1NF, 2NF, 3NF, and BCNF.
  5. LLM synthesizes a clear pedagogical explanation referencing exact syllabus sections (`Database Management Systems (DBMS) → 4. Normal Forms (Source: dbms_normalization.md)`).
  6. UI renders source citation pill badges.

---

## Use Case 3: Contextual Multi-Turn Follow-Up (Flow 1)
- **Turn 1**: *"What are my weak topics?"*
  - Assistant responds with weak topics (e.g., *Alligation and Mixture*, *Percentages*).
- **Turn 2**: *"Explain the first one."*
  - **Memory Resolution**: Orchestrator resolves "the first one" to *Alligation and Mixture*.
  - Calls RAG service for *Alligation and Mixture*.
  - Explains the Rule of Alligation and dilution formulas with source attribution.
- **Turn 3**: *"Give me 5 questions on it."*
  - **Memory Resolution**: Resolves "it" to *Alligation and Mixture*.
  - Invokes `generate_practice_quiz(topic="Alligation and Mixture", num_questions=5)`.
  - Generates 5 multiple-choice questions with 4 options each, grounded in the curriculum.

---

## Use Case 4: Assessment Eligibility Verification (Flow 2)
- **User Query**: *"Can I take assessment 341?"* or *"Why am I not eligible for this assessment?"*
- **Primary Source**: Deterministic Business Rule Engine (`rule_engine.py`) + Database.
- **Processing Flow**:
  1. Orchestrator extracts assessment ID and invokes `check_assessment_eligibility(student_id, assessment_id)`.
  2. Rule engine evaluates all four formal requirements:
     - `Assessment Active Status`: `True`
     - `Prerequisite Course Completion`: Checks student progress in prerequisite course (Python, ID 103). Progress = 8.7%, required = 80%. `False`.
     - `Prerequisite Assessment Passed`: `True` (No prerequisite required).
     - `Maximum Attempt Limit`: 0 attempts used out of 3. `True`.
  3. Determines `eligible: False`.
  4. Assistant formats structured checklist:
     ```
     Status: NOT ELIGIBLE
     [✓] Assessment Active Status: Open for submissions
     [✗] Prerequisite Course Completion: Course 'Python' progress is 8.7% (Required: 80% or certificate)
     [✓] Prerequisite Assessment Passed: None required
     [✓] Maximum Attempt Limit: Used 0 of 3 permitted attempts

     Reasons for Failure:
     - Required course 'Python' progress is 8.7%, which is below the 80% completion requirement.
     ```
  5. The LLM explains the result deterministically without altering the outcome.

---

## Use Case 5: AI Study Coach Priority Roadmap
- **User Action / Query**: *"What should I study next?"* or visiting the **Study Coach** tab.
- **Primary Source**: Performance Engine + Course Engagement Data.
- **Processing Flow**:
  1. Analyzes student's weakest topic with lowest accuracy and highest error count.
  2. Locates matching enrolled courses in student's catalog.
  3. Outputs:
     - **Priority Topic**: e.g., *Alligation and Mixture*.
     - **Factual Reason**: Recorded accuracy is 0.0% with 2 failed questions.
     - **Recommended Action**: Study the Rule of Alligation and review worked dilution examples.
     - **Relevant Course Material**: Module mapping in Quantitative Aptitude & Analytical Problem Solving.
     - **Practice Recommendation**: Complete 5 medium practice questions.

---

## Use Case 6: Interactive Personalized Practice Lab
- **User Action**: Selecting topic, difficulty, and question count on the Practice tab.
- **Processing Flow**:
  1. Backend generates grounded questions via RAG.
  2. Displays options to student without revealing correct answers.
  3. Student selects answers and clicks "Submit Quiz & Grade".
  4. Backend grades each question deterministically, computes accuracy, records score into `practice_history` table, and displays itemized feedback with explanations and citations.

---

## Use Case 7: Hallucination Refusal for Missing Knowledge
- **User Query**: *"What is the internal college policy for hostel curfew and canteen discount?"*
- **Processing Flow**:
  1. Query intent classified as `unsupported_policy`.
  2. System detects query requests administrative policies not contained in the academic catalog or student database.
  3. Refuses safely: *"I don't have enough information in the available college records or course materials to answer that. I can only assist with your enrolled courses, academic performance, assessment eligibility, and curriculum concepts."*
