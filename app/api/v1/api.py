"""
API v1 router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, oauth, users, subjects, uploads, quizzes, exams, concept_maps, sessions, progress, grades

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(oauth.router, prefix="/auth/oauth", tags=["oauth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
api_router.include_router(concept_maps.router, prefix="/concept-maps", tags=["concept-maps"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(grades.router, prefix="/grades", tags=["grades"])
