"""
AI processing background tasks
"""

from celery import current_task
from app.core.celery import celery
from app.core.database import SessionLocal
from app.services.ai_service import AIService


@celery.task(bind=True)
def generate_quiz_async(self, quiz_id: str, content: str, difficulty: str, num_questions: int):
    """Generate quiz questions asynchronously"""
    db = SessionLocal()
    try:
        from app.models.quiz import Quiz, QuizQuestion
        
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            return {"status": "error", "message": "Quiz not found"}
        
        # Update task progress
        current_task.update_state(state="PROGRESS", meta={"status": "Generating questions..."})
        
        # Initialize AI service
        ai_service = AIService()
        
        # Generate questions using AI
        ai_questions = await ai_service.generate_quiz_questions(content, difficulty, num_questions)
        
        # Create questions
        for ai_question in ai_questions:
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
            db.add(question)
        
        db.commit()
        
        return {"status": "success", "message": "Quiz generated successfully"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@celery.task(bind=True)
def generate_concept_map_async(self, concept_map_id: str, content: str):
    """Generate concept map asynchronously"""
    db = SessionLocal()
    try:
        from app.models.concept_map import ConceptMap, ConceptNode, ConceptConnection
        
        concept_map = db.query(ConceptMap).filter(ConceptMap.id == concept_map_id).first()
        if not concept_map:
            return {"status": "error", "message": "Concept map not found"}
        
        # Update task progress
        current_task.update_state(state="PROGRESS", meta={"status": "Generating concept map..."})
        
        # Initialize AI service
        ai_service = AIService()
        
        # Generate concept map using AI
        ai_concept_map = await ai_service.generate_concept_map(content)
        
        # Create nodes
        node_id_mapping = {}
        for i, ai_node in enumerate(ai_concept_map.get("nodes", [])):
            node = ConceptNode(
                concept_map_id=concept_map.id,
                label=ai_node["label"],
                x=ai_node.get("x", i * 100),
                y=ai_node.get("y", i * 100),
                type=ai_node.get("type", "main"),
                color=ai_node.get("color", "#3B82F6"),
                description=ai_node.get("description", ""),
                examples=ai_node.get("examples", []),
                ai_generated=True
            )
            db.add(node)
            db.flush()  # Get the ID
            node_id_mapping[ai_node["id"]] = str(node.id)
        
        # Create connections
        for ai_connection in ai_concept_map.get("connections", []):
            from_node_id = node_id_mapping.get(ai_connection["from"])
            to_node_id = node_id_mapping.get(ai_connection["to"])
            
            if from_node_id and to_node_id:
                connection = ConceptConnection(
                    concept_map_id=concept_map.id,
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    label=ai_connection.get("label", ""),
                    type=ai_connection.get("type", "direct"),
                    strength=ai_connection.get("strength", 1.0)
                )
                db.add(connection)
        
        db.commit()
        
        return {"status": "success", "message": "Concept map generated successfully"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@celery.task
def analyze_content_difficulty(content: str):
    """Analyze content difficulty level"""
    ai_service = AIService()
    
    try:
        # This would implement difficulty analysis
        # For now, return a placeholder
        return {
            "difficulty": "medium",
            "confidence": 0.8,
            "factors": ["vocabulary", "sentence_length", "complexity"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
