import logging
from typing import Dict, Any, List
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.models.db_models import Assessment, AssessmentAttempt, StudentCourse, Course, CourseEngagement
from backend.models.schemas import AssessmentEligibilityResponse, AssessmentRequirement

logger = logging.getLogger("RuleEngine")

class BusinessRuleEngine:
    def check_assessment_eligibility(
        self, 
        db: Session, 
        student_id: str, 
        assessment_id: int
    ) -> AssessmentEligibilityResponse:
        """
        Phase 9: Deterministic Business Rule Engine
        Evaluates assessment eligibility against four formal institutional rules:
        1. Assessment Active Status: The assessment must be actively open for submissions.
        2. Prerequisite Course Completion: Required course must be completed (or progress >= 80% / certified).
        3. Prerequisite Assessment Passed: Prerequisite assessment attempt must exist and have status 'pass'.
        4. Maximum Attempt Limit: Total previous attempts must be strictly less than max_attempts.
        """
        assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
        if not assessment:
            return AssessmentEligibilityResponse(
                assessment_id=assessment_id,
                title="Unknown Assessment",
                eligible=False,
                requirements=[],
                failed_requirements=["Assessment Not Found"],
                reasons=[f"Assessment ID {assessment_id} does not exist in the academic catalog."]
            )

        requirements: List[AssessmentRequirement] = []
        failed_reqs: List[str] = []
        reasons: List[str] = []

        # -------------------------------------------------------------
        # Rule 1: Assessment Active Status
        # -------------------------------------------------------------
        is_active = bool(assessment.is_active)
        req_active = AssessmentRequirement(
            name="Assessment Active Status",
            satisfied=is_active,
            detail="Assessment is open for submissions" if is_active else "Assessment is currently archived/inactive"
        )
        requirements.append(req_active)
        if not is_active:
            failed_reqs.append(req_active.name)
            reasons.append(f"Assessment '{assessment.title}' is currently closed/inactive.")

        # -------------------------------------------------------------
        # Rule 2: Prerequisite Course Completion
        # -------------------------------------------------------------
        if assessment.prerequisite_course_id is not None:
            prereq_course = db.query(Course).filter(Course.course_id == assessment.prerequisite_course_id).first()
            course_name = prereq_course.course_title if prereq_course else f"Course #{assessment.prerequisite_course_id}"
            
            sc = db.query(StudentCourse).filter(
                StudentCourse.student_id == student_id,
                StudentCourse.course_id == assessment.prerequisite_course_id
            ).first()

            if not sc:
                req_course = AssessmentRequirement(
                    name="Prerequisite Course Completion",
                    satisfied=False,
                    detail=f"Not enrolled in required prerequisite course: {course_name}"
                )
                requirements.append(req_course)
                failed_reqs.append(req_course.name)
                reasons.append(f"You must enroll in and complete prerequisite course '{course_name}'.")
            else:
                # Check course completion or progress threshold
                is_certified = bool(sc.certificate_issued or sc.is_legacy_completion)
                ce = db.query(CourseEngagement).filter(
                    CourseEngagement.student_id == student_id,
                    CourseEngagement.course_id == assessment.prerequisite_course_id
                ).first()
                tot_acts = prereq_course.total_activities if prereq_course and prereq_course.total_activities > 0 else 50
                progress = 100.0 if is_certified else (
                    min(100.0, round(((ce.total_views + ce.resource_clicks_downloads) / tot_acts) * 100.0, 1)) if ce else 0.0
                )
                
                course_passed = is_certified or (progress >= 80.0)
                req_course = AssessmentRequirement(
                    name="Prerequisite Course Completion",
                    satisfied=course_passed,
                    detail=f"Prerequisite course '{course_name}' progress: {progress:.1f}% (Required: 80% or certificate)"
                )
                requirements.append(req_course)
                if not course_passed:
                    failed_reqs.append(req_course.name)
                    reasons.append(f"Required course '{course_name}' progress is {progress:.1f}%, which is below the 80% completion requirement.")
        else:
            requirements.append(AssessmentRequirement(
                name="Prerequisite Course Completion",
                satisfied=True,
                detail="No prerequisite course required"
            ))

        # -------------------------------------------------------------
        # Rule 3: Prerequisite Assessment Passed
        # -------------------------------------------------------------
        if assessment.prerequisite_assessment_id is not None:
            prereq_att = db.query(AssessmentAttempt).filter(
                AssessmentAttempt.student_id == student_id,
                AssessmentAttempt.assessment_id == assessment.prerequisite_assessment_id,
                AssessmentAttempt.status == "pass"
            ).first()

            prereq_meta = db.query(Assessment).filter(
                Assessment.assessment_id == assessment.prerequisite_assessment_id
            ).first()
            prereq_title = prereq_meta.title if prereq_meta else f"Assessment #{assessment.prerequisite_assessment_id}"

            has_passed_prereq = (prereq_att is not None)
            req_prereq_ass = AssessmentRequirement(
                name="Prerequisite Assessment Passed",
                satisfied=has_passed_prereq,
                detail=f"Passed prerequisite assessment '{prereq_title}'" if has_passed_prereq else f"Has not yet passed prerequisite assessment '{prereq_title}'"
            )
            requirements.append(req_prereq_ass)
            if not has_passed_prereq:
                failed_reqs.append(req_prereq_ass.name)
                reasons.append(f"You must first pass the prerequisite assessment '{prereq_title}'.")
        else:
            requirements.append(AssessmentRequirement(
                name="Prerequisite Assessment Passed",
                satisfied=True,
                detail="No prerequisite assessment required"
            ))

        # -------------------------------------------------------------
        # Rule 4: Maximum Attempt Limit
        # -------------------------------------------------------------
        attempt_count = db.query(func.count(AssessmentAttempt.attempt_id)).filter(
            AssessmentAttempt.student_id == student_id,
            AssessmentAttempt.assessment_id == assessment_id
        ).scalar() or 0

        max_limit = assessment.max_attempts or 3
        within_limit = (attempt_count < max_limit)
        req_attempts = AssessmentRequirement(
            name="Maximum Attempt Limit",
            satisfied=within_limit,
            detail=f"Used {attempt_count} of {max_limit} permitted attempts"
        )
        requirements.append(req_attempts)
        if not within_limit:
            failed_reqs.append(req_attempts.name)
            reasons.append(f"You have reached the maximum allowed attempts limit ({attempt_count}/{max_limit}) for this assessment.")

        is_eligible = (len(failed_reqs) == 0)

        return AssessmentEligibilityResponse(
            assessment_id=assessment.assessment_id,
            title=assessment.title,
            eligible=is_eligible,
            requirements=requirements,
            failed_requirements=failed_reqs,
            reasons=reasons
        )

rule_engine = BusinessRuleEngine()
