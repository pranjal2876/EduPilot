import json
import logging
import pandas as pd
from datetime import datetime
from backend.config import settings
from backend.database.connection import init_db, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ETL")

def parse_iso_datetime(val):
    if pd.isna(val) or val is None or val == "" or str(val) == "NaT":
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
    val_str = str(val).strip()
    try:
        dt = pd.to_datetime(val_str)
        return dt.to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def run_etl():
    logger.info("Initializing database schema...")
    init_db()

    raw_conn = engine.raw_connection()
    cursor = raw_conn.cursor()

    if settings.DATABASE_URL.startswith("sqlite"):
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("PRAGMA synchronous = OFF")
        cursor.execute("PRAGMA journal_mode = MEMORY")

    # -------------------------------------------------------------
    # 1. INGEST student_course_engagement.xlsx
    # -------------------------------------------------------------
    p1 = settings.COURSE_ENGAGEMENT_PATH
    logger.info(f"Loading Course Engagement data from: {p1}")
    df_eng = pd.read_excel(p1)
    logger.info(f"Loaded {len(df_eng)} engagement records. Processing courses and students...")

    students_set = set()
    courses_dict = {}
    student_courses_rows = []
    course_engagement_rows = []

    records_eng = df_eng.to_dict("records")
    for row in records_eng:
        user_id = str(row["user_id"]).strip()
        course_id = int(row["course_id"])
        students_set.add(user_id)

        if course_id not in courses_dict:
            courses_dict[course_id] = (
                course_id,
                str(row.get("course_title", "Unknown Course")).strip(),
                str(row.get("course_domain", "General")).strip(),
                str(row.get("course_sub_domain", "General")).strip(),
                str(row.get("course_level", "beginner")).strip(),
                int(row.get("course_hours", 0) if pd.notna(row.get("course_hours")) else 0),
                int(row.get("total_chapters_in_course", 0) if pd.notna(row.get("total_chapters_in_course")) else 0),
                int(row.get("total_activities_in_course", 0) if pd.notna(row.get("total_activities_in_course")) else 0),
            )

        enrolled_at = parse_iso_datetime(row.get("enrolled_at"))
        is_legacy = bool(row.get("is_legacy_completion", False))
        cert_issued = bool(row.get("certificate_issued", False))
        cert_at = parse_iso_datetime(row.get("certificate_issued_at"))
        cert_link = str(row["certificate_link"]) if pd.notna(row.get("certificate_link")) else None

        student_courses_rows.append((
            user_id,
            course_id,
            enrolled_at,
            1 if is_legacy else 0,
            1 if cert_issued else 0,
            cert_at,
            cert_link
        ))

        tot_views = int(row.get("total_views", 0) if pd.notna(row.get("total_views")) else 0)
        first_view = parse_iso_datetime(row.get("first_viewed_at"))
        last_view = parse_iso_datetime(row.get("last_viewed_at"))
        mcq_count = int(row.get("mcq_attempted_count", 0) if pd.notna(row.get("mcq_attempted_count")) else 0)
        mcq_score = int(row.get("mcq_total_score_obtained", 0) if pd.notna(row.get("mcq_total_score_obtained")) else 0)
        res_clicks = int(row.get("resource_clicks_downloads", 0) if pd.notna(row.get("resource_clicks_downloads")) else 0)

        v_json, mcq_json, res_json = None, None, None
        eng_raw = row.get("engagement_json")
        if pd.notna(eng_raw):
            try:
                parsed = json.loads(eng_raw) if isinstance(eng_raw, str) else eng_raw
                if isinstance(parsed, dict):
                    v_json = json.dumps(parsed.get("views", []))
                    mcq_json = json.dumps(parsed.get("mcq_submissions", []))
                    res_json = json.dumps(parsed.get("resource_clicks_downloads", []))
            except Exception:
                pass

        course_engagement_rows.append((
            user_id,
            course_id,
            tot_views,
            first_view,
            last_view,
            mcq_count,
            mcq_score,
            res_clicks,
            v_json,
            mcq_json,
            res_json
        ))

    logger.info(f"Unique courses found: {len(courses_dict)}")

    # -------------------------------------------------------------
    # 2. INGEST Untitled spreadsheet.xlsx (Hackathons)
    # -------------------------------------------------------------
    p2 = settings.HACKATHON_SUBMISSIONS_PATH
    logger.info(f"Loading Hackathon Submissions data from: {p2}")
    df_sub = pd.read_excel(p2)
    logger.info(f"Loaded {len(df_sub)} hackathon submission rows. Parsing questions...")

    assessments_dict = {}
    attempts_rows = []
    question_results_rows = []
    attempt_counter = 1000000

    records_sub = df_sub.to_dict("records")
    for row in records_sub:
        user_id = str(row["user_id"]).strip()
        students_set.add(user_id)
        hackathon_id = int(row["hackathon_id"])
        num_q = int(row.get("num_questions", 0) if pd.notna(row.get("num_questions")) else 0)

        sub_raw = row.get("submission_json")
        q_list = []
        if pd.notna(sub_raw) and sub_raw:
            try:
                q_list = json.loads(sub_raw) if isinstance(sub_raw, str) else sub_raw
            except Exception:
                q_list = []

        skill = "General"
        sub_domain = "Technical"
        if q_list and isinstance(q_list, list) and len(q_list) > 0:
            first_q = q_list[0]
            skill = first_q.get("skill") or "General"
            q_subs = first_q.get("question_sub_domain")
            if isinstance(q_subs, list) and len(q_subs) > 0:
                sub_domain = q_subs[0]
            elif isinstance(q_subs, str) and q_subs:
                sub_domain = q_subs

        if hackathon_id not in assessments_dict:
            assessments_dict[hackathon_id] = {
                "id": hackathon_id,
                "title": f"Assessment #{hackathon_id} ({skill} - {sub_domain})",
                "domain": str(skill),
                "sub_domain": str(sub_domain),
                "num_questions": num_q,
                "passing_score": 60.0,
                "max_attempts": 3,
                "is_active": 1,
                "prereq_course_id": None,
                "prereq_assessment_id": None
            }

        if not q_list or not isinstance(q_list, list):
            continue

        first_q = q_list[0]
        parsed_attempt_id = first_q.get("attempt_id")
        if parsed_attempt_id and isinstance(parsed_attempt_id, int):
            att_id = parsed_attempt_id
        else:
            attempt_counter += 1
            att_id = attempt_counter

        round_id = first_q.get("round_id")
        sub_time = parse_iso_datetime(first_q.get("submission_time") or first_q.get("create_at"))

        tot_score = sum(float(q.get("obtained_score", 0) or 0) for q in q_list)
        max_score = sum(float(q.get("question_score", 0) or 0) for q in q_list)
        acc = (tot_score / max_score) if max_score > 0 else 0.0
        status = "pass" if acc >= 0.60 else "fail"

        attempts_rows.append((
            att_id,
            user_id,
            hackathon_id,
            round_id,
            sub_time or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            len(q_list),
            tot_score,
            max_score,
            round(acc, 4),
            status
        ))

        for q in q_list:
            qid = int(q.get("question_id") or 0)
            q_skill = q.get("skill") or skill
            subs = q.get("question_sub_domain")
            q_topic = "General"
            if isinstance(subs, list) and len(subs) > 0:
                q_topic = str(subs[0]).strip()
            elif isinstance(subs, str) and subs:
                q_topic = str(subs).strip()

            diff = str(q.get("difficulty") or "medium").strip().lower()
            q_type = str(q.get("question_type") or "mcq").strip()
            q_status = str(q.get("status") or "unAttempted").strip()
            obt_s = float(q.get("obtained_score", 0) or 0)
            max_s = float(q.get("question_score", 0) or 0)
            q_time = parse_iso_datetime(q.get("submission_time") or q.get("create_at"))

            question_results_rows.append((
                att_id,
                user_id,
                hackathon_id,
                qid,
                q_skill,
                q_topic,
                diff,
                q_type,
                q_status,
                obt_s,
                max_s,
                q_time
            ))

    # Benchmark assessments for business rule testing
    if 341 in assessments_dict:
        assessments_dict[341]["title"] = "Full Stack & Aptitude Benchmark Assessment"
        assessments_dict[341]["prereq_course_id"] = 103 # Python
        assessments_dict[341]["max_attempts"] = 3
        assessments_dict[341]["passing_score"] = 60.0

    assessments_dict[901] = {
        "id": 901,
        "title": "Advanced Python Certification Assessment",
        "domain": "Coding",
        "sub_domain": "Python",
        "num_questions": 25,
        "passing_score": 70.0,
        "max_attempts": 2,
        "is_active": 1,
        "prereq_course_id": 103,
        "prereq_assessment_id": None
    }
    assessments_dict[902] = {
        "id": 902,
        "title": "Advanced SQL & Database Mastery Assessment",
        "domain": "Technologies",
        "sub_domain": "SQL",
        "num_questions": 30,
        "passing_score": 65.0,
        "max_attempts": 3,
        "is_active": 1,
        "prereq_course_id": 118,
        "prereq_assessment_id": None
    }
    assessments_dict[999] = {
        "id": 999,
        "title": "Archived Legacy Systems Evaluation",
        "domain": "Legacy",
        "sub_domain": "COBOL",
        "num_questions": 15,
        "passing_score": 50.0,
        "max_attempts": 1,
        "is_active": 0,
        "prereq_course_id": None,
        "prereq_assessment_id": None
    }

    # -------------------------------------------------------------
    # 3. BULK INSERT
    # -------------------------------------------------------------
    logger.info("Executing bulk database inserts...")

    # Students
    logger.info(f"Inserting {len(students_set)} unique students...")
    student_rows = [(uid, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")) for uid in students_set]
    cursor.executemany(
        "INSERT OR IGNORE INTO students (student_id, created_at) VALUES (?, ?)",
        student_rows
    )

    # Courses
    logger.info(f"Inserting {len(courses_dict)} courses...")
    cursor.executemany(
        """INSERT OR REPLACE INTO courses 
        (course_id, course_title, course_domain, course_sub_domain, course_level, course_hours, total_chapters, total_activities) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        list(courses_dict.values())
    )

    # Student courses
    logger.info(f"Inserting {len(student_courses_rows)} student course enrollments...")
    cursor.executemany(
        """INSERT OR IGNORE INTO student_courses 
        (student_id, course_id, enrolled_at, is_legacy_completion, certificate_issued, certificate_issued_at, certificate_link) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        student_courses_rows
    )

    # Course engagement
    logger.info(f"Inserting {len(course_engagement_rows)} course engagement records...")
    cursor.executemany(
        """INSERT OR IGNORE INTO course_engagement 
        (student_id, course_id, total_views, first_viewed_at, last_viewed_at, mcq_attempted_count, 
         mcq_total_score_obtained, resource_clicks_downloads, views_json, mcq_submissions_json, resource_clicks_json) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        course_engagement_rows
    )

    # Assessments
    logger.info(f"Inserting {len(assessments_dict)} assessments...")
    assessment_tuples = [
        (
            a["id"], a["title"], a["domain"], a["sub_domain"], a["num_questions"],
            a["passing_score"], a["max_attempts"], a["is_active"],
            a["prereq_course_id"], a["prereq_assessment_id"]
        )
        for a in assessments_dict.values()
    ]
    cursor.executemany(
        """INSERT OR REPLACE INTO assessments 
        (assessment_id, title, domain, sub_domain, num_questions, passing_score, max_attempts, is_active, prerequisite_course_id, prerequisite_assessment_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        assessment_tuples
    )

    # Assessment attempts
    unique_attempts = {}
    for att in attempts_rows:
        unique_attempts[att[0]] = att
    logger.info(f"Inserting {len(unique_attempts)} assessment attempts...")
    cursor.executemany(
        """INSERT OR IGNORE INTO assessment_attempts 
        (attempt_id, student_id, assessment_id, round_id, submitted_at, total_questions_attempted, total_score_obtained, total_possible_score, accuracy_rate, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        list(unique_attempts.values())
    )

    # Question results
    logger.info(f"Inserting {len(question_results_rows)} assessment question results...")
    batch_size = 50000
    for i in range(0, len(question_results_rows), batch_size):
        batch = question_results_rows[i:i + batch_size]
        cursor.executemany(
            """INSERT INTO assessment_question_results 
            (attempt_id, student_id, assessment_id, question_id, skill, topic, difficulty, question_type, status, obtained_score, question_score, submission_time) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            batch
        )
        logger.info(f"  Inserted {min(i + batch_size, len(question_results_rows))} / {len(question_results_rows)} question results...")

    if settings.DATABASE_URL.startswith("sqlite"):
        cursor.execute("PRAGMA foreign_keys = ON")

    raw_conn.commit()
    cursor.close()
    raw_conn.close()

    logger.info("ETL Pipeline completed successfully! All data normalized and indexed.")

if __name__ == "__main__":
    run_etl()
