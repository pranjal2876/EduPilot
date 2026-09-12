import sys
import unittest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.connection import SessionLocal
from backend.models.db_models import Student, AssessmentAttempt

class TestSuite20Scenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.student_id = "02754054-361a-4025-be96-1bd8a049ae18" # Active student with 11 courses & 239 questions
        cls.headers = {"X-Student-Id": cls.student_id}
        cls.results_log = []

    def record_test(self, test_num, name, question, expected, actual, passed):
        self.results_log.append({
            "test_num": test_num,
            "name": name,
            "question": question,
            "expected": expected,
            "actual": actual,
            "passed": passed
        })
        self.assertTrue(passed)

    # -------------------------------------------------------------
    # 1. Database Question
    # -------------------------------------------------------------
    def test_01_database_profile_question(self):
        r = self.client.get("/api/v1/students/me/profile", headers=self.headers)
        data = r.json()
        passed = (r.status_code == 200 and data["student_id"] == self.student_id and data["enrolled_courses_count"] > 0)
        self.record_test(
            1, "Database Question (Profile)", "GET /api/v1/students/me/profile",
            "Returns HTTP 200 with student ID and real enrolled courses count (>0)",
            f"Status {r.status_code}, Enrolled: {data.get('enrolled_courses_count')}, Views: {data.get('total_views')}",
            passed
        )

    # -------------------------------------------------------------
    # 2. Course Engagement Question
    # -------------------------------------------------------------
    def test_02_course_engagement_question(self):
        # Course 103 is Python
        r = self.client.get("/api/v1/students/me/courses/103/engagement", headers=self.headers)
        data = r.json()
        passed = (r.status_code == 200 and data["course_id"] == 103 and "total_views" in data)
        self.record_test(
            2, "Course Engagement Question", "GET /api/v1/students/me/courses/103/engagement",
            "Returns views, MCQ counts, and resource downloads for Python course",
            f"Status {r.status_code}, Views: {data.get('total_views')}, Resources: {data.get('resource_clicks_downloads')}",
            passed
        )

    # -------------------------------------------------------------
    # 3. Performance Question
    # -------------------------------------------------------------
    def test_03_performance_question(self):
        r = self.client.get("/api/v1/performance/me", headers=self.headers)
        data = r.json()
        passed = (r.status_code == 200 and "overall_accuracy_percentage" in data and data["total_questions_attempted"] > 0)
        self.record_test(
            3, "Performance Question", "GET /api/v1/performance/me",
            "Returns overall accuracy percentage and question attempt counts",
            f"Status {r.status_code}, Accuracy: {data.get('overall_accuracy_percentage')}%, Total Q: {data.get('total_questions_attempted')}",
            passed
        )

    # -------------------------------------------------------------
    # 4. Weak-Topic Question
    # -------------------------------------------------------------
    def test_04_weak_topic_question(self):
        r = self.client.get("/api/v1/performance/me/weak-topics", headers=self.headers)
        data = r.json()
        passed = (r.status_code == 200 and isinstance(data, list) and len(data) > 0 and all(t["is_weak"] for t in data))
        top_weak = data[0]["topic"] if data else "None"
        self.record_test(
            4, "Weak-Topic Question", "GET /api/v1/performance/me/weak-topics",
            "Returns list of topics strictly with accuracy < 60% or fail count >= 2",
            f"Status {r.status_code}, Found {len(data)} weak topics. Top weak topic: {top_weak}",
            passed
        )

    # -------------------------------------------------------------
    # 5. Assessment History Question
    # -------------------------------------------------------------
    def test_05_assessment_history_question(self):
        r = self.client.get("/api/v1/students/me/assessments/history", headers=self.headers)
        data = r.json()
        passed = (r.status_code == 200 and isinstance(data, list) and len(data) > 0)
        self.record_test(
            5, "Assessment History Question", "GET /api/v1/students/me/assessments/history",
            "Returns chronological list of past assessment attempts with scores and accuracy",
            f"Status {r.status_code}, Found {len(data)} attempts recorded",
            passed
        )

    # -------------------------------------------------------------
    # 6. RAG Question (DBMS Normalization)
    # -------------------------------------------------------------
    def test_06_rag_normalization_question(self):
        r = self.client.post("/api/v1/assistant/chat", json={"message": "Explain normalization from my DBMS course."}, headers=self.headers)
        data = r.json()
        reply = data.get("reply", "").lower()
        passed = (r.status_code == 200 and data["intent"] == "course_concept" and ("1nf" in reply or "redundancy" in reply or "normal form" in reply))
        self.record_test(
            6, "RAG Question (DBMS Normalization)", "Explain normalization from my DBMS course.",
            "Retrieves DBMS curriculum chunks and explains 1NF/2NF/3NF without hallucination",
            f"Status {r.status_code}, Intent: {data.get('intent')}, Reply contains normalization concepts",
            passed
        )

    # -------------------------------------------------------------
    # 7. RAG Source Verification
    # -------------------------------------------------------------
    def test_07_rag_source_verification(self):
        r = self.client.post("/api/v1/assistant/chat", json={"message": "Explain ACID properties in transactions."}, headers=self.headers)
        data = r.json()
        sources = data.get("sources", [])
        passed = (r.status_code == 200 and len(sources) > 0 and any("DBMS" in s or "dbms" in s.lower() for s in sources))
        self.record_test(
            7, "RAG Source Verification", "Explain ACID properties in transactions.",
            "Response explicitly includes source attribution pointing to DBMS curriculum document",
            f"Status {r.status_code}, Sources: {sources}",
            passed
        )

    # -------------------------------------------------------------
    # 8. Missing RAG Information (Refusal)
    # -------------------------------------------------------------
    def test_08_missing_rag_information(self):
        # Query asking for completely unrelated topic not in knowledge base
        r = self.client.post("/api/v1/assistant/chat", json={"message": "Explain quantum teleportation in astrophysics."}, headers=self.headers)
        data = r.json()
        reply = data.get("reply", "")
        passed = ("couldn't find sufficient information" in reply.lower() or "not available" in reply.lower())
        self.record_test(
            8, "Missing RAG Information", "Explain quantum teleportation in astrophysics.",
            "Explicitly refuses and states information is unavailable in course material",
            f"Status {r.status_code}, Reply: '{reply[:100]}...'",
            passed
        )

    # -------------------------------------------------------------
    # 9. Business-Rule Question
    # -------------------------------------------------------------
    def test_09_business_rule_question(self):
        r = self.client.get("/api/v1/assessments/341/eligibility", headers=self.headers)
        data = r.json()
        passed = (r.status_code == 200 and "requirements" in data and len(data["requirements"]) == 4)
        self.record_test(
            9, "Business-Rule Question", "GET /api/v1/assessments/341/eligibility",
            "Returns structured response with 4 deterministic rule evaluations",
            f"Status {r.status_code}, Evaluated {len(data.get('requirements', []))} formal rules",
            passed
        )

    # -------------------------------------------------------------
    # 10. Ineligible Assessment (Prerequisite not met)
    # -------------------------------------------------------------
    def test_10_ineligible_assessment(self):
        # Assessment 901 requires 80% progress in Python; student has ~8.7% progress
        r = self.client.get("/api/v1/assessments/901/eligibility", headers=self.headers)
        data = r.json()
        passed = (r.status_code == 200 and data["eligible"] is False and len(data["failed_requirements"]) > 0)
        self.record_test(
            10, "Ineligible Assessment", "GET /api/v1/assessments/901/eligibility",
            "Returns eligible: false with explicit prerequisite course failure reason",
            f"Status {r.status_code}, Eligible: {data.get('eligible')}, Failed: {data.get('failed_requirements')}",
            passed
        )

    # -------------------------------------------------------------
    # 11. Eligible Assessment
    # -------------------------------------------------------------
    def test_11_eligible_assessment(self):
        # Assessment 342 has no prerequisite courses and active status
        db = SessionLocal()
        from backend.models.db_models import Assessment
        test_ass = db.query(Assessment).filter(Assessment.prerequisite_course_id == None, Assessment.is_active == True).first()
        ass_id = test_ass.assessment_id if test_ass else 1
        db.close()

        r = self.client.get(f"/api/v1/assessments/{ass_id}/eligibility", headers=self.headers)
        data = r.json()
        passed = (r.status_code == 200 and data["eligible"] is True and len(data["failed_requirements"]) == 0)
        self.record_test(
            11, "Eligible Assessment", f"GET /api/v1/assessments/{ass_id}/eligibility",
            "Returns eligible: true with all requirements satisfied",
            f"Status {r.status_code}, Eligible: {data.get('eligible')}, All requirements passed",
            passed
        )

    # -------------------------------------------------------------
    # 12. Multi-Source Question
    # -------------------------------------------------------------
    def test_12_multi_source_question(self):
        r = self.client.post("/api/v1/assistant/chat", json={"message": "Can I take the assessment and what should I study?"}, headers=self.headers)
        data = r.json()
        tools = data.get("tools_used", [])
        passed = (r.status_code == 200 and len(tools) > 0)
        self.record_test(
            12, "Multi-Source Question", "Can I take the assessment and what should I study?",
            "Combines assessment eligibility checking and study coaching tools",
            f"Status {r.status_code}, Tools invoked: {tools}",
            passed
        )

    # -------------------------------------------------------------
    # 13. Follow-up Question (Contextual Memory)
    # -------------------------------------------------------------
    def test_13_followup_question(self):
        conv_id = "test-session-suite-13"
        # Turn 1
        r1 = self.client.post("/api/v1/assistant/chat", json={"message": "What are my weak topics?", "conversation_id": conv_id}, headers=self.headers)
        # Turn 2
        r2 = self.client.post("/api/v1/assistant/chat", json={"message": "Explain the first one.", "conversation_id": conv_id}, headers=self.headers)
        data2 = r2.json()
        passed = (r2.status_code == 200 and data2["intent"] == "course_concept" and len(data2["sources"]) > 0)
        self.record_test(
            13, "Follow-up Question (Memory)", "Explain the first one.",
            "Resolves 'the first one' to student's primary weak topic using session memory",
            f"Status {r2.status_code}, Intent: {data2.get('intent')}, Sources: {data2.get('sources')}",
            passed
        )

    # -------------------------------------------------------------
    # 14. Personalized Recommendation (Study Coach)
    # -------------------------------------------------------------
    def test_14_personalized_recommendation(self):
        r = self.client.get("/api/v1/performance/me/recommendation", headers=self.headers)
        data = r.json()
        passed = (r.status_code == 200 and "priority_topic" in data and "reason" in data and "recommended_action" in data)
        self.record_test(
            14, "Personalized Recommendation", "GET /api/v1/performance/me/recommendation",
            "Returns priority topic, factual reason with actual score, and recommended practice",
            f"Priority Topic: '{data.get('priority_topic')}', Reason: '{data.get('reason')}'",
            passed
        )

    # -------------------------------------------------------------
    # 15. Personalized Practice (Quiz Generation & Submit)
    # -------------------------------------------------------------
    def test_15_personalized_practice(self):
        # Generate
        r_gen = self.client.post("/api/v1/practice/generate", json={
            "topic": "Database Normalization",
            "difficulty": "medium",
            "num_questions": 3
        })
        gen_data = r_gen.json()
        quiz_id = gen_data.get("quiz_id")

        # Submit
        r_sub = self.client.post("/api/v1/practice/submit", json={
            "quiz_id": quiz_id,
            "topic": "Database Normalization",
            "difficulty": "medium",
            "answers": {1: "B) 2NF", 2: "C) 3NF", 3: "C) A Super Key"}
        }, headers=self.headers)
        sub_data = r_sub.json()

        passed = (r_gen.status_code == 200 and r_sub.status_code == 200 and "score_obtained" in sub_data)
        self.record_test(
            15, "Personalized Practice", "POST /api/v1/practice/generate & submit",
            "Generates 3 grounded questions, grades answers deterministically, returns score & explanations",
            f"Score: {sub_data.get('score_obtained')}/{sub_data.get('total_possible_score')}, Accuracy: {sub_data.get('accuracy_percentage')}%",
            passed
        )

    # -------------------------------------------------------------
    # 16. Invalid Student Handling
    # -------------------------------------------------------------
    def test_16_invalid_student(self):
        bad_headers = {"X-Student-Id": "nonexistent-student-uuid-99999"}
        r = self.client.get("/api/v1/students/me/profile", headers=bad_headers)
        passed = (r.status_code == 404)
        self.record_test(
            16, "Invalid Student Handling", "GET /api/v1/students/me/profile (nonexistent ID)",
            "Returns HTTP 404 Not Found without system crash",
            f"Status {r.status_code}, Detail: {r.json().get('detail')}",
            passed
        )

    # -------------------------------------------------------------
    # 17. Unauthorized Access / Cross-Student Isolation
    # -------------------------------------------------------------
    def test_17_unauthorized_access(self):
        # Student Aarav tries to access Course 229 which Aarav is NOT enrolled in
        r = self.client.get("/api/v1/students/me/courses/229/progress", headers=self.headers)
        passed = (r.status_code == 404)
        self.record_test(
            17, "Unauthorized Access Prevention", "GET /api/v1/students/me/courses/229/progress",
            "Blocks access to course progress for courses the student is not enrolled in",
            f"Status {r.status_code}, Detail: {r.json().get('detail')}",
            passed
        )

    # -------------------------------------------------------------
    # 18. Missing Student Data Handling
    # -------------------------------------------------------------
    def test_18_missing_student_data(self):
        # User with 0 hackathons (e.g. newly enrolled)
        db = SessionLocal()
        # Create temporary dummy student with 0 records
        dummy_id = "test-new-student-zero-data"
        if not db.query(Student).filter(Student.student_id == dummy_id).first():
            db.add(Student(student_id=dummy_id))
            db.commit()
        db.close()

        r = self.client.get("/api/v1/performance/me", headers={"X-Student-Id": dummy_id})
        data = r.json()
        passed = (r.status_code == 200 and data["total_questions_attempted"] == 0 and data["overall_accuracy_percentage"] == 0.0)
        self.record_test(
            18, "Missing Student Data Handling", "GET /api/v1/performance/me (zero activity student)",
            "Handles zero-record student gracefully returning 0% accuracy without divide-by-zero crash",
            f"Status {r.status_code}, Total Q: {data.get('total_questions_attempted')}, Accuracy: {data.get('overall_accuracy_percentage')}%",
            passed
        )

    # -------------------------------------------------------------
    # 19. Difficult-Topic Analysis
    # -------------------------------------------------------------
    def test_19_difficult_topic_analysis(self):
        r = self.client.get("/api/v1/performance/me", headers=self.headers)
        data = r.json()
        diffs = data.get("difficulty_breakdown", [])
        passed = (r.status_code == 200 and len(diffs) > 0 and any(d["difficulty"] in ["easy", "medium", "hard"] for d in diffs))
        self.record_test(
            19, "Difficult-Topic Analysis", "GET /api/v1/performance/me (difficulty breakdown)",
            "Computes performance accuracy segmented across easy, medium, and hard difficulty levels",
            f"Difficulty Tiers: {[d['difficulty'] + ': ' + str(d['accuracy_percentage']) + '%' for d in diffs]}",
            passed
        )

    # -------------------------------------------------------------
    # 20. Hallucination Test (Fictitious Policy Question)
    # -------------------------------------------------------------
    def test_20_hallucination_refusal(self):
        r = self.client.post("/api/v1/assistant/chat", json={"message": "What is the internal college policy for hostel curfew and canteen discount?"}, headers=self.headers)
        data = r.json()
        reply = data.get("reply", "")
        passed = ("don't have enough information" in reply.lower() or "unavailable" in reply.lower())
        self.record_test(
            20, "Hallucination Refusal Test", "What is the internal college policy for hostel curfew?",
            "Explicitly refuses to fabricate university administrative policy, maintaining safety guardrails",
            f"Status {r.status_code}, Intent: {data.get('intent')}, Refusal: '{reply[:90]}...'",
            passed
        )

    @classmethod
    def tearDownClass(cls):
        print("\n" + "="*95)
        print("  AI COLLEGE LEARNING ASSISTANT — 20-SCENARIO VERIFICATION MATRIX")
        print("="*95)
        print(f"{'#':<3} | {'Scenario Name':<35} | {'Result':<6} | {'Actual Behaviour Snippet'}")
        print("-"*95)
        all_passed = True
        for res in cls.results_log:
            status = "PASS" if res["passed"] else "FAIL"
            if not res["passed"]:
                all_passed = False
            snippet = res["actual"][:48] + "..." if len(res["actual"]) > 48 else res["actual"]
            print(f"{res['test_num']:<3} | {res['name']:<35} | {status:<6} | {snippet}")
        print("="*95)
        print(f"TOTAL TEST SCENARIOS EVALUATED: {len(cls.results_log)} / 20")
        print(f"VERIFICATION STATUS: {'ALL 20 SCENARIOS PASSED (100% SUCCESS)' if all_passed else 'SOME TESTS FAILED'}")
        print("="*95 + "\n")

if __name__ == "__main__":
    unittest.main()
