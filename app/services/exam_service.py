"""
Exam service
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.exam import Exam, ExamQuestion, ExamUserAnswer
from app.models.upload import Upload
from app.schemas.exam import (
    ExamCreate, 
    ExamUpdate, 
    ExamQuestionCreate,
    ExamAnswer,
    ExamGenerationRequest
)
from app.core.exceptions import NotFoundError, ValidationError
from app.services.ai_service import AIService


class ExamService:
    """Exam service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    def create_exam(self, user_id: str, exam_data: ExamCreate) -> Exam:
        """Create a new exam"""
        exam = Exam(
            user_id=user_id,
            subject_id=exam_data.subject_id,
            title=exam_data.title,
            difficulty=exam_data.difficulty,
            time_limit=exam_data.time_limit,
            total_points=exam_data.total_points,
            passing_score=exam_data.passing_score,
            description=exam_data.description,
            instructions=exam_data.instructions,
            tags=exam_data.tags
        )
        
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        
        # Add questions if provided
        if exam_data.questions:
            for question_data in exam_data.questions:
                self._create_exam_question(exam.id, question_data)
        
        return exam
    
    def get_exams(self, user_id: str, subject_id: Optional[str] = None) -> List[Exam]:
        """Get all exams for a user"""
        query = self.db.query(Exam).filter(Exam.user_id == user_id)
        
        if subject_id:
            query = query.filter(Exam.subject_id == subject_id)
        
        return query.all()
    
    def get_exam(self, exam_id: str, user_id: str) -> Optional[Exam]:
        """Get a specific exam"""
        return self.db.query(Exam).filter(
            Exam.id == exam_id,
            Exam.user_id == user_id
        ).first()
    
    def update_exam(self, exam_id: str, user_id: str, exam_data: ExamUpdate) -> Exam:
        """Update an exam"""
        exam = self.get_exam(exam_id, user_id)
        if not exam:
            raise NotFoundError("Exam", exam_id)
        
        # Update fields
        for field, value in exam_data.dict(exclude_unset=True).items():
            setattr(exam, field, value)
        
        self.db.commit()
        self.db.refresh(exam)
        
        return exam
    
    def delete_exam(self, exam_id: str, user_id: str) -> bool:
        """Delete an exam"""
        exam = self.get_exam(exam_id, user_id)
        if not exam:
            return False
        
        self.db.delete(exam)
        self.db.commit()
        
        return True
    
    def start_exam(self, exam_id: str, user_id: str) -> Exam:
        """Start an exam session"""
        exam = self.get_exam(exam_id, user_id)
        if not exam:
            raise NotFoundError("Exam", exam_id)
        
        if not exam.is_active:
            raise ValidationError("Exam is not active")
        
        return exam
    
    def submit_exam(self, exam_id: str, user_id: str, answers: List[ExamAnswer]) -> Dict[str, Any]:
        """Submit exam answers"""
        exam = self.get_exam(exam_id, user_id)
        if not exam:
            raise NotFoundError("Exam", exam_id)
        
        # Calculate score
        total_score = 0
        max_score = 0
        correct_answers = 0
        
        for answer in answers:
            question = self.db.query(ExamQuestion).filter(
                ExamQuestion.id == answer.question_id,
                ExamQuestion.exam_id == exam_id
            ).first()
            
            if not question:
                continue
            
            max_score += question.points
            
            # Check if answer is correct
            is_correct = self._check_answer(question, answer.answer)
            if is_correct:
                total_score += question.points
                correct_answers += 1
            
            # Save user answer
            user_answer = ExamUserAnswer(
                user_id=user_id,
                exam_question_id=question.id,
                answer=answer.answer,
                is_correct=is_correct,
                time_spent=answer.time_spent
            )
            self.db.add(user_answer)
        
        self.db.commit()
        
        # Calculate percentage and pass status
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        passed = percentage >= exam.passing_score
        
        return {
            "exam_id": exam_id,
            "score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "passed": passed,
            "correct_answers": correct_answers,
            "total_questions": len(answers),
            "completed_at": datetime.utcnow()
        }
    
    def generate_exam(self, user_id: str, generation_data: ExamGenerationRequest) -> Exam:
        """Generate exam using AI"""
        # Get content from source uploads
        content = ""
        if generation_data.source_upload_ids:
            uploads = self.db.query(Upload).filter(
                Upload.id.in_(generation_data.source_upload_ids),
                Upload.user_id == user_id
            ).all()
            
            for upload in uploads:
                if upload.file_metadata and upload.file_metadata.get("extracted_text"):
                    content += upload.file_metadata["extracted_text"] + "\n"
        
        if not content:
            raise ValidationError("No content available for exam generation")
        
        # Generate questions using AI
        ai_questions = self.ai_service.generate_quiz_questions(
            content, 
            generation_data.difficulty, 
            generation_data.num_questions
        )
        
        # Calculate total points
        total_points = sum(q.get("points", 1) for q in ai_questions)
        
        # Create exam
        exam = Exam(
            user_id=user_id,
            subject_id=generation_data.subject_id,
            title=generation_data.title,
            difficulty=generation_data.difficulty,
            time_limit=generation_data.time_limit,
            total_points=total_points,
            passing_score=generation_data.passing_score,
            tags=generation_data.tags
        )
        
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        
        # Create questions
        for ai_question in ai_questions:
            question = ExamQuestion(
                exam_id=exam.id,
                type=ai_question["type"],
                question=ai_question["question"],
                options=ai_question["options"],
                correct_answer=ai_question["correct_answer"],
                explanation=ai_question["explanation"],
                difficulty=ai_question["difficulty"],
                points=ai_question.get("points", 1),
                ai_generated=True
            )
            self.db.add(question)
        
        self.db.commit()
        self.db.refresh(exam)
        
        return exam
    
    def _create_exam_question(self, exam_id: str, question_data: ExamQuestionCreate) -> ExamQuestion:
        """Create an exam question"""
        question = ExamQuestion(
            exam_id=exam_id,
            type=question_data.type,
            question=question_data.question,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            difficulty=question_data.difficulty,
            points=question_data.points,
            source_upload_id=question_data.source_upload_id
        )
        
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        
        return question
    
    def _check_answer(self, question: ExamQuestion, answer: Union[int, List[int], str]) -> bool:
        """Check if answer is correct"""
        if question.type == "single":
            return answer == question.correct_answer
        elif question.type == "multiple":
            if isinstance(answer, list) and isinstance(question.correct_answer, list):
                return set(answer) == set(question.correct_answer)
        elif question.type == "open":
            # For open questions, we might need more sophisticated checking
            # For now, just check if answer is not empty
            return bool(answer and str(answer).strip())
        return False
    
    def get_exam_stats(self, user_id: str, subject_id: Optional[str] = None) -> Dict[str, Any]:
        """Get exam statistics"""
        query = self.db.query(Exam).filter(Exam.user_id == user_id)
        
        if subject_id:
            query = query.filter(Exam.subject_id == subject_id)
        
        exams = query.all()
        
        total_exams = len(exams)
        total_questions = sum(len(exam.questions) for exam in exams)
        
        # Calculate average score and pass rate from user answers
        user_answers = self.db.query(ExamUserAnswer).filter(ExamUserAnswer.user_id == user_id).all()
        total_score = sum(1 for answer in user_answers if answer.is_correct)
        total_answers = len(user_answers)
        average_score = (total_score / total_answers * 100) if total_answers > 0 else 0
        
        # Calculate pass rate (simplified)
        passed_exams = 0
        for exam in exams:
            exam_answers = [a for a in user_answers if a.exam_question_id in [q.id for q in exam.questions]]
            if exam_answers:
                exam_score = sum(1 for a in exam_answers if a.is_correct)
                exam_percentage = (exam_score / len(exam_answers) * 100) if exam_answers else 0
                if exam_percentage >= exam.passing_score:
                    passed_exams += 1
        
        pass_rate = (passed_exams / total_exams * 100) if total_exams > 0 else 0
        
        # Calculate difficulty distribution
        difficulty_dist = {}
        for exam in exams:
            difficulty_dist[exam.difficulty] = difficulty_dist.get(exam.difficulty, 0) + 1
        
        return {
            "total_exams": total_exams,
            "total_questions": total_questions,
            "average_score": average_score,
            "pass_rate": pass_rate,
            "total_time": 0,  # Would need to track from study sessions
            "completion_rate": 0,  # Would need to track from study sessions
            "difficulty_distribution": difficulty_dist
        }
