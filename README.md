# AI College Learning Assistant

A production-quality prototype combining **Structured Student Data**, **RAG Course Knowledge**, **Deterministic Business Logic**, **Student Performance Analytics**, and **LLM Orchestration**.

This system is engineered for enterprise academic environments: it maintains strict separation between operational databases, accredited course content, institutional business rules, and AI synthesis.

---

## 🌟 Core System Pillars

```
+---------------------------------------------------------------------------------------+
|                                    NEXT.JS FRONTEND                                   |
|   Dashboard  |  AI Assistant  |  Performance Analytics  |  Practice Lab  | Assessments |
+-------------------------------------------+-------------------------------------------+
                                            | (REST APIs with X-Student-Id isolation)
+-------------------------------------------v-------------------------------------------+
|                               FASTAPI BACKEND & ORCHESTRATOR                          |
|                                                                                       |
|  +-----------------------+   +-----------------------+   +-------------------------+  |
|  |   Structured Data     |   |   Accredited RAG      |   |  Deterministic Logic    |  |
|  |   (SQLAlchemy / DB)   |   |   (MiniLM Vector Store|   |  (4-Rule Checklist)     |  |
|  |   Profile, Courses,   |   |   DBMS, Python, Apt., |   |  Active, Prereq Course, |  |
|  |   Engagement, Scores  |   |   8086, Web Dev)      |   |  Prereq Test, Max Att.  |  |
|  +-----------+-----------+   +-----------+-----------+   +------------+------------+  |
|              |                           |                            |               |
|              +--------------------+------+----------------------------+               |
|                                   |                                                   |
|                        +----------v-----------+                                       |
|                        |   AI Orchestrator    |                                       |
|                        | (Provenance & Memory)|                                       |
|                        +----------+-----------+                                       |
|                                   |                                                   |
|                        +----------v-----------+                                       |
|                        | Multi-Provider LLM   |                                       |
|                        | Gemini / OpenAI /    |                                       |
|                        | Local Synthesizer    |                                       |
|                        +----------------------+                                       |
+---------------------------------------------------------------------------------------+
```

1. **Strict Separation of Concerns**:
   - The LLM **never** has direct raw SQL access and **never** invents or overrides business rules.
   - Business calculations (weak topics, accuracy, eligibility) are computed deterministically in Python/SQL before being passed as verified context to the LLM.
2. **Zero-Hallucination Guardrails**:
   - Course explanations strictly reference accredited Markdown course notes with exact file and section citations.
   - Queries regarding missing topics or institutional administrative policies are gracefully refused.
3. **Deterministic Business Rules**:
   - Assessment eligibility runs through a strict 4-rule validation engine (Active Status, Prerequisite Course Progress $\ge 80\%$, Prerequisite Assessment Passed, Max Attempts Limit).
4. **Student Performance Analytics**:
   - Weak-topic engine ($<60\%$ accuracy or $\ge 2$ failed attempts).
   - Learning Efficiency Score ($0-100$) balancing accuracy and course engagement.
   - Engagement vs. Performance 4-Quadrant diagnostic matrix.
5. **Interactive Practice & Grading**:
   - On-demand curriculum-aligned quizzes with automated deterministic grading and answer explanations.
6. **Multi-Turn Contextual Memory**:
   - Conversational state tracking that resolves pronouns and anaphora (e.g., *"give me questions on the first one"* $\to$ resolves to previously discussed weak topic).

---

## 📊 Dataset Ingestion & Architecture

The system processes and integrates two real datasets:
1. `student_course_engagement.xlsx` (9,157 course engagement records across 245 courses).
2. `Untitled spreadsheet.xlsx` (18,299 assessment submissions with question-level JSON results).

### Relational Database Schema (`college_ai.db` / PostgreSQL DDL)
- `students`: 3,238 unique records.
- `courses`: 245 unique courses across CS, Engineering, and Aptitude.
- `student_courses` & `course_engagement`: 9,157 enrollment & engagement records.
- `assessments`: 2,084 unique assessments.
- `assessment_attempts`: 17,144 student assessment attempts.
- `assessment_question_results`: **492,499** individual question attempts indexed by topic, difficulty, and accuracy.

---

## 🛠️ Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend API** | FastAPI (Python 3.11) | High-performance asynchronous REST endpoints with automatic OpenAPI documentation. |
| **Data & ORM** | SQLAlchemy 2.0 & SQLite / PostgreSQL | Standardized ORM with migration-ready PostgreSQL DDL (`schema_postgres.sql`) and zero-dependency local SQLite storage (`college_ai.db`). |
| **Embeddings & RAG**| SentenceTransformers (`all-MiniLM-L6-v2`) | Fast, local, high-quality 384-dimensional semantic embeddings with cached offline vectors (`data/rag_cache/`). |
| **AI LLM Client** | Google Gemini (`gemini-2.5-flash`) / OpenAI / Local Synthesizer | Multi-provider abstraction with automatic fallback to deterministic synthesis if API keys are absent. |
| **Frontend UI** | Next.js 14 (App Router), TypeScript, Tailwind CSS | Modern responsive dashboard featuring real-time data visualizers, execution provenance drawers, and student switchers. |
| **Icons & Styling** | Lucide React | Clean, intuitive status indicators for eligibility checklists and confidence metrics. |

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and `npm`

### 1. Backend Setup

```bash
# Navigate to project root
cd d:/Startups/CollegeAI

# (Optional) Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install backend dependencies
pip install -r requirements.txt
```

*(Optional) Configure AI API Keys in `.env`:*
```env
GEMINI_API_KEY=your_gemini_api_key
# or
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./college_ai.db
```
> **Note**: If no LLM API key is provided, the system automatically runs using its built-in **Deterministic Local Synthesizer**, delivering full grounded responses and tool traces with zero setup.

### 2. (Optional) Run Database ETL
The local SQLite database (`college_ai.db`) is already fully populated with all 492,499 question records. To re-run the ETL pipeline from source Excel files:
```bash
python -m backend.database.etl
```

### 3. Launch Backend API Server
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Launch Next.js Frontend
In a new terminal:
```bash
cd d:/Startups/CollegeAI/frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Comprehensive Automated Test Suite (20 Scenarios)

The test suite validates all 20 required evaluation scenarios across Database queries, RAG semantic retrieval, Deterministic Business Logic, Multi-turn Conversational Memory, Security isolation, and Edge cases.

### Run Tests
```bash
python -m unittest backend.tests.test_suite_20 -v
```

### 20-Scenario Verification Matrix
All 20 test cases pass with 100% success rate:

| # | Scenario | Component | Expected Outcome | Status |
|---|---|---|---|:---:|
| 1 | Database Question | Student Profile API | Returns real student name, enrolled courses, total video watch hours | **PASS** |
| 2 | Course Engagement | Engagement API | Returns exact video views, resource downloads, and attendance % | **PASS** |
| 3 | Performance Question | Performance API | Calculates overall student accuracy, questions attempted, score | **PASS** |
| 4 | Weak-Topic Question | Performance Service | Identifies topics with $<60\%$ accuracy or $\ge 2$ fails | **PASS** |
| 5 | Assessment History | Student History API | Lists completed attempts, scores, and timestamps | **PASS** |
| 6 | RAG Curriculum Question | RAG Service | Explains 1NF, 2NF, 3NF, BCNF using course notes | **PASS** |
| 7 | Source Verification | RAG Vector Store | Includes exact source document and section citations | **PASS** |
| 8 | Missing RAG Information | Hallucination Guardrail | Returns factual refusal for un-indexed topics | **PASS** |
| 9 | Business-Rule Explanation | Rule Engine | Explains 4 formal rules governing assessment access | **PASS** |
| 10 | Ineligible Assessment | Rule Engine | Rejects ineligible student with explicit failed prerequisite | **PASS** |
| 11 | Eligible Assessment | Rule Engine | Approves student meeting all 4 prerequisite criteria | **PASS** |
| 12 | Multi-Source Synthesis | AI Orchestrator | Combines DB profile + RAG course notes + Rule check | **PASS** |
| 13 | Follow-up with Memory | Conversational Memory | Resolves *"tell me about the first one"* to prior weak topic | **PASS** |
| 14 | Personalized Study Plan | AI Study Coach | Recommends specific priority topic with action steps | **PASS** |
| 15 | Practice Lab & Grading | Practice Service | Generates quiz and deterministically grades answers | **PASS** |
| 16 | Invalid Student Handling | Security / Error Guard | Returns HTTP 404 with structured error response | **PASS** |
| 17 | Unauthorized Access | Tenant Isolation | Prevents student from accessing unenrolled course data | **PASS** |
| 18 | Zero-History Student | Boundary Analysis | Returns clean zeroed metrics without division-by-zero errors | **PASS** |
| 19 | Difficulty-Tier Analysis | Analytics Service | Breaks down accuracy across Easy, Medium, and Hard tiers | **PASS** |
| 20 | Out-of-Scope Policy Query | Hallucination Guardrail | Gracefully refuses queries on ungrounded college policies | **PASS** |

---

## 🖥️ Demo Flows Walkthrough

### Flow 1: Weak Topics $\to$ Explain Concept $\to$ Practice Quiz
1. **Identify Weak Topics**:
   - Switch to Aarav Sharma (`02754054-361a-4025-be96-1bd8a049ae18`) in the Navbar.
   - Navigate to **AI Assistant** or **Performance Tab**. Notice top weak topics (e.g., *Alligation and Mixture*: 18.2% accuracy, *Profit and Loss*: 25.0% accuracy).
2. **Ask Assistant**:
   - Type: `"What are my weak topics and can you explain the first one?"`
   - The assistant lists weak topics from the database, resolves *"the first one"* to *Alligation and Mixture*, and retrieves accredited curriculum notes with citations (`aptitude_topics.md`).
3. **Practice**:
   - In the chat, click **Start Interactive Quiz**, or go to the **Practice Lab** tab.
   - Complete the 5-question generated quiz and click **Submit Quiz**. The system instantly grades your answers, reveals full step-by-step explanations, and records your score.

### Flow 2: Assessment Eligibility Checklist
1. Navigate to the **Assessments** tab.
2. Select **Python Level 2 Assessment** (Assessment ID: `901`).
3. The deterministic rule engine displays the real-time 4-rule audit checklist:
   - `[✓]` Assessment Active
   - `[✗]` Prerequisite Course Progress $\ge 80\%$ *(Current: 20% - FAILED)*
   - `[✓]` Prerequisite Assessment Passed
   - `[✓]` Attempts Remaining ($0 / 3$)
   - **Status Badge**: `INELIGIBLE` with clear remediation advice.
4. Next, select an assessment where prerequisites are satisfied (e.g. Assessment `7` or `341`).
   - Notice all 4 rules show `[✓]` with status `ELIGIBLE: Ready to Attempt`.

---

## 📁 Project Directory Structure

```
CollegeAI/
├── backend/
│   ├── ai/
│   │   ├── llm_client.py           # Multi-provider LLM abstraction (Gemini/OpenAI/Local)
│   │   ├── memory.py               # Multi-turn conversation state & pronoun resolution
│   │   └── orchestrator.py         # Intent classifier, tool dispatcher & data tracer
│   ├── api/
│   │   ├── routes_assistant.py     # AI Chat endpoint
│   │   ├── routes_assessment.py    # Assessment catalog & eligibility check
│   │   ├── routes_performance.py   # Weak topics, efficiency score, diagnostics
│   │   ├── routes_practice.py      # Grounded quiz generation & grading
│   │   └── routes_student.py       # Student profile & course engagement
│   ├── business_logic/
│   │   └── rule_engine.py          # Deterministic 4-rule assessment evaluation
│   ├── database/
│   │   ├── connection.py           # SQLAlchemy database session factory
│   │   ├── etl.py                  # Ingestion pipeline for both Excel files
│   │   └── schema_postgres.sql     # Enterprise PostgreSQL DDL schema
│   ├── models/
│   │   ├── db_models.py            # SQLAlchemy database tables
│   │   └── schemas.py              # Pydantic v2 validation models
│   ├── rag/
│   │   ├── chunker.py              # Semantic markdown header chunker
│   │   ├── rag_service.py          # Grounded course search with refusal logic
│   │   └── vector_store.py         # SentenceTransformer vector store with caching
│   ├── services/
│   │   ├── performance_service.py  # Analytics, efficiency score & quadrant engine
│   │   ├── practice_service.py     # Curriculum quiz generator & grading
│   │   ├── student_service.py      # Profile & enrollment services
│   │   └── study_coach_service.py  # Personalized roadmap recommender
│   ├── tests/
│   │   └── test_suite_20.py        # Automated test suite for all 20 scenarios
│   └── main.py                     # FastAPI application entrypoint
├── data/
│   ├── knowledge_base/             # Accredited curriculum markdown documents
│   │   ├── aptitude_topics.md
│   │   ├── dbms_normalization.md
│   │   ├── microprocessors_8086.md
│   │   ├── python_programming.md
│   │   └── web_development.md
│   └── rag_cache/                  # Cached vectors & chunks (all-MiniLM-L6-v2)
├── docs/
│   ├── architecture.md             # System architecture & component design
│   ├── business_rules.md           # Formal business logic specification
│   ├── data_dictionary.md          # Complete data dictionary & field mappings
│   ├── testing.md                  # Test suite documentation & scenario details
│   └── use_cases.md                # Supported user personas & interaction flows
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js 14 App Router
│   │   ├── components/             # UI Tab components (Assistant, Performance, etc.)
│   │   └── lib/api.ts              # Type-safe API client
│   └── package.json
├── requirements.txt                # Python backend dependencies
└── README.md                       # Root documentation & quickstart
```

---

## 📚 Detailed Documentation Links
- [System Architecture](docs/architecture.md)
- [Business Rules Engine](docs/business_rules.md)
- [Data Dictionary](docs/data_dictionary.md)
- [Test Suite & Verification Matrix](docs/testing.md)
- [Use Cases & User Journeys](docs/use_cases.md)

---

## 📄 License
This project was developed for the AI Engineering Assessment. Internal and educational use permitted.
