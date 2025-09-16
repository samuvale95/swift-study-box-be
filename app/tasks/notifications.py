"""
Notification background tasks
"""

from celery import current_task
from app.core.celery import celery
from app.core.database import SessionLocal


@celery.task
def send_email_notification(user_id: str, subject: str, message: str):
    """Send email notification to user"""
    db = SessionLocal()
    try:
        from app.models.user import User
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # This would implement actual email sending
        # For now, just log the notification
        print(f"Sending email to {user.email}: {subject}")
        
        return {"status": "success", "message": "Email sent successfully"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@celery.task
def send_processing_complete_notification(user_id: str, upload_id: str):
    """Send notification when file processing is complete"""
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.models.upload import Upload
        
        user = db.query(User).filter(User.id == user_id).first()
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        
        if not user or not upload:
            return {"status": "error", "message": "User or upload not found"}
        
        subject = "File Processing Complete"
        message = f"Your file '{upload.name}' has been processed successfully."
        
        # Send notification
        send_email_notification.delay(user_id, subject, message)
        
        return {"status": "success", "message": "Notification sent"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@celery.task
def send_achievement_notification(user_id: str, achievement_id: str):
    """Send notification when user unlocks an achievement"""
    db = SessionLocal()
    try:
        from app.models.user import User
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        subject = "Achievement Unlocked!"
        message = f"Congratulations! You've unlocked a new achievement."
        
        # Send notification
        send_email_notification.delay(user_id, subject, message)
        
        return {"status": "success", "message": "Achievement notification sent"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@celery.task
def send_goal_reminder(user_id: str, goal_id: str):
    """Send reminder for user goals"""
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.models.progress import Goal
        
        user = db.query(User).filter(User.id == user_id).first()
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        
        if not user or not goal:
            return {"status": "error", "message": "User or goal not found"}
        
        subject = "Goal Reminder"
        message = f"Don't forget about your goal: {goal.title}"
        
        # Send notification
        send_email_notification.delay(user_id, subject, message)
        
        return {"status": "success", "message": "Goal reminder sent"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()
