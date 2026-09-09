# Business Rules Specification — AI College Learning Assistant

This document formally specifies all deterministic business rules implemented in the application layer.

> [!IMPORTANT]
> **Deterministic Execution Guarantee**:
> In accordance with Phase 9 and Section 4.C of the assignment specification, business rules are implemented exclusively as deterministic backend Python functions. They are **never** embedded solely inside LLM prompts with an expectation that the model will follow them probabilistically. The LLM explains the results but can never alter or override them.

---

## 1. Assessment Eligibility Rules

The function `check_assessment_eligibility(student_id, assessment_id)` evaluates four formal criteria:

### Rule 1.1: Assessment Active Status
- **Condition**: `assessment.is_active == True`.
- **Logic**: If `is_active` is `False`, the assessment is archived or closed.
- **Result if Failed**:
  - Requirement: `Assessment Active Status` marked failed.
  - Reason: *"Assessment '{title}' is currently closed/inactive."*

### Rule 1.2: Prerequisite Course Completion
- **Condition**: If `assessment.prerequisite_course_id` is defined:
  1. The student must be enrolled in the prerequisite course (`student_courses` record exists).
  2. The student must satisfy at least ONE of:
     - `certificate_issued == True`
     - `is_legacy_completion == True`
     - `progress_percentage >= 80.0%`
- **Result if Failed**:
  - If not enrolled: *"You must enroll in and complete prerequisite course '{course_name}'."*
  - If progress $< 80\%$: *"Required course '{course_name}' progress is {progress}%, which is below the 80% completion requirement."*

### Rule 1.3: Prerequisite Assessment Passed
- **Condition**: If `assessment.prerequisite_assessment_id` is defined:
  - At least one attempt in `assessment_attempts` must exist for the student on the prerequisite assessment with `status == 'pass'` (accuracy $\ge 60\%$).
- **Result if Failed**:
  - Reason: *"You must first pass the prerequisite assessment '{prerequisite_title}'."*

### Rule 1.4: Maximum Attempt Limit
- **Condition**: Total previous attempts by the student on this assessment must be strictly less than `max_attempts` (default: 3).
  $$\text{Attempt Count} < \text{Max Attempts}$$
- **Result if Failed**:
  - Reason: *"You have reached the maximum allowed attempts limit ({attempt_count}/{max_attempts}) for this assessment."*

---

## 2. Academic Performance & Weak-Topic Rules

### Rule 2.1: Topic Accuracy Calculation
For each sub-domain / topic $T$:
$$\text{Accuracy}(T) = \frac{\sum_{q \in T} \text{obtained\_score}_q}{\sum_{q \in T} \text{question\_score}_q} \times 100\%$$
Where $\sum \text{question\_score}_q > 0$. If no questions have been attempted, accuracy defaults to $0.0\%$.

### Rule 2.2: Weak Topic Classification Threshold
A topic $T$ is flagged as **Weak** (`is_weak = True`) if and only if:
$$\text{Accuracy}(T) < 60.0\% \quad \lor \quad \text{Failed Questions}(T) \ge 2$$
Topics are ranked in ascending order of proficiency (lowest accuracy and highest failure count first).

---

## 3. Course Progress & Engagement Rules

### Rule 3.1: Course Progress Percentage
$$\text{Progress} = \begin{cases} 
100.0\% & \text{if } \text{certificate\_issued} = \text{True} \lor \text{is\_legacy\_completion} = \text{True} \\
\min\left(100.0, \frac{\text{total\_views} + \text{resource\_clicks}}{\text{total\_activities}} \times 100.0\right) & \text{otherwise}
\end{cases}$$

---

## 4. Derived Learning Efficiency Score (Phase 6)

$$\text{Efficiency} = \min\left(100, \max\left(0, 0.40 \cdot A + 0.30 \cdot P + 0.20 \cdot R + 0.10 \cdot C\right)\right)$$

Where:
- $A$: Overall Assessment Accuracy Percentage ($0 - 100$)
- $P$: Average Course Progress Percentage ($0 - 100$)
- $R$: Resource Utilization Ratio ($\min(100, \frac{\text{resource\_clicks}}{20} \times 100)$)
- $C$: Attempt Consistency Ratio ($\min(100, \frac{\text{questions\_attempted}}{50} \times 100)$)

---

## 5. Engagement vs Performance Diagnostics (Phase 5)

Students are categorized into four diagnostic quadrants based on engagement and accuracy:
- **High Engagement, Low Accuracy** ($\ge 5$ views / $\ge 10$ resources, $< 65\%$ accuracy): Time invested is high but comprehension gaps exist. Strategy: Targeted active practice.
- **Low Engagement, High Accuracy** ($< 5$ views, $\ge 65\%$ accuracy): High prior capability with low platform interaction. Strategy: Advanced challenge hackathons.
- **High Engagement, High Accuracy** ($\ge 5$ views, $\ge 65\%$ accuracy): Strong study routine and top-tier mastery. Strategy: Capstone assessments.
- **Low Engagement, Low Accuracy** ($< 5$ views, $< 65\%$ accuracy): Early or struggling student. Strategy: Foundational syllabus review and beginner quizzes.
