"""
Quiz service
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.quiz import Quiz, QuizQuestion, UserAnswer
from app.models.upload import Upload
from app.schemas.quiz import (
    QuizCreate, 
    QuizUpdate, 
    QuizQuestionCreate,
    QuizAnswer,
    QuizGenerationRequest
)
from app.core.exceptions import NotFoundError, ValidationError
from app.services.ai_service import AIService


class QuizService:
    """Quiz service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    def create_quiz(self, user_id: str, quiz_data: QuizCreate) -> Quiz:
        """Create a new quiz"""
        quiz = Quiz(
            user_id=user_id,
            subject_id=quiz_data.subject_id,
            title=quiz_data.title,
            difficulty=quiz_data.difficulty,
            time_limit=quiz_data.time_limit,
            description=quiz_data.description,
            tags=quiz_data.tags
        )
        
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        
        # Add questions if provided
        if quiz_data.questions:
            for question_data in quiz_data.questions:
                self._create_quiz_question(quiz.id, question_data)
        
        return quiz
    
    def get_quizzes(self, user_id: str, subject_id: Optional[str] = None) -> List[Quiz]:
        """Get all quizzes for a user"""
        query = self.db.query(Quiz).filter(Quiz.user_id == user_id)
        
        if subject_id:
            query = query.filter(Quiz.subject_id == subject_id)
        
        return query.all()
    
    def get_quiz(self, quiz_id: str, user_id: str) -> Optional[Quiz]:
        """Get a specific quiz"""
        return self.db.query(Quiz).filter(
            Quiz.id == quiz_id,
            Quiz.user_id == user_id
        ).first()
    
    def update_quiz(self, quiz_id: str, user_id: str, quiz_data: QuizUpdate) -> Quiz:
        """Update a quiz"""
        quiz = self.get_quiz(quiz_id, user_id)
        if not quiz:
            raise NotFoundError("Quiz", quiz_id)
        
        # Update fields
        for field, value in quiz_data.dict(exclude_unset=True).items():
            setattr(quiz, field, value)
        
        self.db.commit()
        self.db.refresh(quiz)
        
        return quiz
    
    def delete_quiz(self, quiz_id: str, user_id: str) -> bool:
        """Delete a quiz"""
        quiz = self.get_quiz(quiz_id, user_id)
        if not quiz:
            return False
        
        self.db.delete(quiz)
        self.db.commit()
        
        return True
    
    def start_quiz(self, quiz_id: str, user_id: str) -> Quiz:
        """Start a quiz session"""
        quiz = self.get_quiz(quiz_id, user_id)
        if not quiz:
            raise NotFoundError("Quiz", quiz_id)
        
        if not quiz.is_active:
            raise ValidationError("Quiz is not active")
        
        return quiz
    
    def submit_quiz(self, quiz_id: str, user_id: str, answers: List[QuizAnswer]) -> Dict[str, Any]:
        """Submit quiz answers"""
        quiz = self.get_quiz(quiz_id, user_id)
        if not quiz:
            raise NotFoundError("Quiz", quiz_id)
        
        # Calculate score
        total_score = 0
        max_score = 0
        correct_answers = 0
        
        for answer in answers:
            question = self.db.query(QuizQuestion).filter(
                QuizQuestion.id == answer.question_id,
                QuizQuestion.quiz_id == quiz_id
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
            user_answer = UserAnswer(
                user_id=user_id,
                quiz_question_id=question.id,
                answer=answer.answer,
                is_correct=is_correct,
                time_spent=answer.time_spent
            )
            self.db.add(user_answer)
        
        self.db.commit()
        
        # Calculate percentage
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            "quiz_id": quiz_id,
            "score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "correct_answers": correct_answers,
            "total_questions": len(answers),
            "completed_at": datetime.utcnow()
        }
    
    def generate_quiz(self, user_id: str, generation_data: QuizGenerationRequest) -> Quiz:
        """Generate quiz using AI"""
        # Get content from source uploads
        content = ""
        if generation_data.source_upload_ids:
            uploads = self.db.query(Upload).filter(
                Upload.id.in_(generation_data.source_upload_ids),
                Upload.user_id == user_id
            ).all()
            
            for upload in uploads:
                if upload.metadata and upload.metadata.get("extracted_text"):
                    content += upload.metadata["extracted_text"] + "\n"
        
        if not content:
            raise ValidationError("No content available for quiz generation")
        
        # Generate questions using AI
        ai_questions = await self.ai_service.generate_quiz_questions(
            content, 
            generation_data.difficulty, 
            generation_data.num_questions
        )
        
        # Create quiz
        quiz = Quiz(
            user_id=user_id,
            subject_id=generation_data.subject_id,
            title=generation_data.title,
            difficulty=generation_data.difficulty,
            time_limit=generation_data.time_limit,
            tags=generation_data.tags
        )
        
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        
        # Create questions
        for i, ai_question in enumerate(ai_questions):
            question = QuizQuestion(
                quiz_id=quiz.id,
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
        self.db.refresh(quiz)
        
        return quiz
    
    def _create_quiz_question(self, quiz_id: str, question_data: QuizQuestionCreate) -> QuizQuestion:
        """Create a quiz question"""
        question = QuizQuestion(
            quiz_id=quiz_id,
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
    
    def _check_answer(self, question: QuizQuestion, answer: Union[int, List[int], str]) -> bool:
        """Check if answer is correct"""
        if question.type == "single":
            return answer == question.correct_answer
        elif question.type == "multiple":
            if isinstance(answer, list) and isinstance(question.correct_answer, list):
                return set(answer) == set(question.correct_answer)
        return False
    
    def get_quiz_stats(self, user_id: str, subject_id: Optional[str] = None) -> Dict[str, Any]:
        """Get quiz statistics"""
        query = self.db.query(Quiz).filter(Quiz.user_id == user_id)
        
        if subject_id:
            query = query.filter(Quiz.subject_id == subject_id)
        
        quizzes = query.all()
        
        total_quizzes = len(quizzes)
        total_questions = sum(len(quiz.questions) for quiz in quizzes)
        
        # Calculate average score from user answers
        user_answers = self.db.query(UserAnswer).filter(UserAnswer.user_id == user_id).all()
        total_score = sum(1 for answer in user_answers if answer.is_correct)
        total_answers = len(user_answers)
        average_score = (total_score / total_answers * 100) if total_answers > 0 else 0
        
        # Calculate difficulty distribution
        difficulty_dist = {}
        for quiz in quizzes:
            difficulty_dist[quiz.difficulty] = difficulty_dist.get(quiz.difficulty, 0) + 1
        
        return {
            "total_quizzes": total_quizzes,
            "total_questions": total_questions,
            "average_score": average_score,
            "total_time": 0,  # Would need to track from study sessions
            "completion_rate": 0,  # Would need to track from study sessions
            "difficulty_distribution": difficulty_dist
        }
