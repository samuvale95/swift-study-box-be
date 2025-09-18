"""
Grade service for academic transcript management
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.grade import Grade
from app.models.subject import Subject
from app.schemas.grade import (
    GradeCreate, 
    GradeUpdate, 
    GradeStats, 
    GradeSummary,
    AcademicYearStats
)
from app.core.exceptions import NotFoundError, ValidationError


class GradeService:
    """Grade service for academic transcript management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_grade(self, user_id: str, grade_data: GradeCreate) -> Grade:
        """Create a new grade entry"""
        # Verify subject exists and belongs to user
        subject = self.db.query(Subject).filter(
            Subject.id == grade_data.subject_id,
            Subject.user_id == user_id
        ).first()
        
        if not subject:
            raise NotFoundError("Subject", grade_data.subject_id)
        
        # Validate grade data
        if grade_data.grade < 0:
            raise ValidationError("Grade cannot be negative")
        
        if grade_data.max_grade and grade_data.grade > grade_data.max_grade:
            raise ValidationError("Grade cannot be higher than max grade")
        
        grade = Grade(
            user_id=user_id,
            subject_id=grade_data.subject_id,
            exam_name=grade_data.exam_name,
            grade=grade_data.grade,
            max_grade=grade_data.max_grade,
            credits=grade_data.credits,
            exam_date=grade_data.exam_date,
            academic_year=grade_data.academic_year,
            semester=grade_data.semester,
            professor=grade_data.professor,
            notes=grade_data.notes
        )
        
        self.db.add(grade)
        self.db.commit()
        self.db.refresh(grade)
        
        return grade
    
    def get_grades(self, user_id: str, subject_id: Optional[str] = None, 
                   academic_year: Optional[str] = None, 
                   semester: Optional[str] = None) -> List[Grade]:
        """Get all grades for a user with optional filters"""
        query = self.db.query(Grade).filter(Grade.user_id == user_id)
        
        if subject_id:
            query = query.filter(Grade.subject_id == subject_id)
        
        if academic_year:
            query = query.filter(Grade.academic_year == academic_year)
        
        if semester:
            query = query.filter(Grade.semester == semester)
        
        return query.order_by(Grade.exam_date.desc()).all()
    
    def get_grade(self, grade_id: str, user_id: str) -> Optional[Grade]:
        """Get a specific grade"""
        return self.db.query(Grade).filter(
            Grade.id == grade_id,
            Grade.user_id == user_id
        ).first()
    
    def update_grade(self, grade_id: str, user_id: str, grade_data: GradeUpdate) -> Grade:
        """Update a grade"""
        grade = self.get_grade(grade_id, user_id)
        if not grade:
            raise NotFoundError("Grade", grade_id)
        
        # Update fields
        for field, value in grade_data.dict(exclude_unset=True).items():
            setattr(grade, field, value)
        
        self.db.commit()
        self.db.refresh(grade)
        
        return grade
    
    def delete_grade(self, grade_id: str, user_id: str) -> bool:
        """Delete a grade"""
        grade = self.get_grade(grade_id, user_id)
        if not grade:
            return False
        
        self.db.delete(grade)
        self.db.commit()
        
        return True
    
    def get_grade_stats(self, user_id: str, subject_id: Optional[str] = None) -> GradeStats:
        """Get comprehensive grade statistics"""
        query = self.db.query(Grade).filter(Grade.user_id == user_id)
        
        if subject_id:
            query = query.filter(Grade.subject_id == subject_id)
        
        grades = query.all()
        
        if not grades:
            return GradeStats(
                total_credits=0,
                earned_credits=0,
                average_grade=0.0,
                weighted_average=0.0,
                total_exams=0,
                passed_exams=0,
                failed_exams=0,
                current_gpa=0.0,
                academic_progress=0.0,
                by_semester={},
                by_subject={}
            )
        
        # Basic statistics
        total_exams = len(grades)
        passed_exams = sum(1 for g in grades if g.is_passed)
        failed_exams = total_exams - passed_exams
        
        # Calculate averages (only for passed exams)
        passed_grades = [g for g in grades if g.is_passed]
        total_grade = sum(g.grade for g in passed_grades)
        average_grade = total_grade / len(passed_grades) if passed_grades else 0.0
        
        # Weighted average by credits (only for passed exams)
        total_weighted = sum(g.grade * (g.credits or 1) for g in passed_grades)
        total_credits_weight = sum(g.credits or 1 for g in passed_grades)
        weighted_average = total_weighted / total_credits_weight if total_credits_weight > 0 else 0.0
        
        # Credits
        total_credits = sum(g.credits or 0 for g in grades)
        earned_credits = sum(g.credits or 0 for g in grades if g.is_passed)
        
        # GPA calculation (assuming 30 is max grade)
        gpa = (weighted_average / 30) * 4 if weighted_average > 0 else 0.0
        
        # Academic progress
        academic_progress = (earned_credits / total_credits * 100) if total_credits > 0 else 0.0
        
        # By semester
        by_semester = {}
        for grade in grades:
            key = f"{grade.academic_year}_{grade.semester or 'unknown'}"
            if key not in by_semester:
                by_semester[key] = {
                    "exams": 0,
                    "average": 0.0,
                    "credits": 0,
                    "passed": 0
                }
            
            by_semester[key]["exams"] += 1
            by_semester[key]["credits"] += grade.credits or 0
            if grade.is_passed:
                by_semester[key]["passed"] += 1
        
        # Calculate semester averages (only for passed exams)
        for key in by_semester:
            semester_grades = [g for g in grades if f"{g.academic_year}_{g.semester or 'unknown'}" == key]
            passed_semester_grades = [g for g in semester_grades if g.is_passed]
            if passed_semester_grades:
                by_semester[key]["average"] = sum(g.grade for g in passed_semester_grades) / len(passed_semester_grades)
            else:
                by_semester[key]["average"] = 0.0
        
        # By subject
        by_subject = {}
        for grade in grades:
            subject_name = grade.subject.name if grade.subject else "Unknown"
            if subject_name not in by_subject:
                by_subject[subject_name] = {
                    "exams": 0,
                    "average": 0.0,
                    "credits": 0,
                    "passed": 0,
                    "last_grade": None,
                    "last_exam_date": None
                }
            
            by_subject[subject_name]["exams"] += 1
            by_subject[subject_name]["credits"] += grade.credits or 0
            if grade.is_passed:
                by_subject[subject_name]["passed"] += 1
            
            # Keep track of latest grade
            if (by_subject[subject_name]["last_exam_date"] is None or 
                grade.exam_date > by_subject[subject_name]["last_exam_date"]):
                by_subject[subject_name]["last_grade"] = grade.grade
                by_subject[subject_name]["last_exam_date"] = grade.exam_date
        
        # Calculate subject averages (only for passed exams)
        for subject_name in by_subject:
            subject_grades = [g for g in grades if g.subject and g.subject.name == subject_name]
            passed_subject_grades = [g for g in subject_grades if g.is_passed]
            if passed_subject_grades:
                by_subject[subject_name]["average"] = sum(g.grade for g in passed_subject_grades) / len(passed_subject_grades)
            else:
                by_subject[subject_name]["average"] = 0.0
        
        return GradeStats(
            total_credits=total_credits,
            earned_credits=earned_credits,
            average_grade=average_grade,
            weighted_average=weighted_average,
            total_exams=total_exams,
            passed_exams=passed_exams,
            failed_exams=failed_exams,
            current_gpa=gpa,
            academic_progress=academic_progress,
            by_semester=by_semester,
            by_subject=by_subject
        )
    
    def get_grade_summary(self, user_id: str) -> List[GradeSummary]:
        """Get grade summary by subject for dashboard"""
        # Get all subjects with their grades
        subjects = self.db.query(Subject).filter(Subject.user_id == user_id).all()
        
        summaries = []
        for subject in subjects:
            grades = self.db.query(Grade).filter(
                Grade.user_id == user_id,
                Grade.subject_id == subject.id
            ).order_by(Grade.exam_date.desc()).all()
            
            if not grades:
                continue
            
            total_exams = len(grades)
            passed_grades = [g for g in grades if g.is_passed]
            average_grade = sum(g.grade for g in passed_grades) / len(passed_grades) if passed_grades else 0.0
            passed_exams = len(passed_grades)
            total_credits = sum(g.credits or 0 for g in grades)
            
            summaries.append(GradeSummary(
                subject_name=subject.name,
                subject_id=subject.id,
                total_exams=total_exams,
                average_grade=average_grade,
                last_grade=grades[0].grade,
                last_exam_date=grades[0].exam_date,
                credits=total_credits,
                is_passed=passed_exams == total_exams
            ))
        
        return summaries
