"""
AI service for content processing and generation
"""

import openai
from typing import List, Dict, Any, Optional
import PyPDF2
import pytesseract
from PIL import Image
import io
import re

from app.core.config import settings
from app.core.exceptions import AIProcessingError


class AIService:
    """AI service for content processing and generation"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    async def extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise AIProcessingError(f"Failed to extract PDF text: {str(e)}")
    
    async def count_pdf_pages(self, file_content: bytes) -> int:
        """Count pages in PDF"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            return len(pdf_reader.pages)
        except Exception as e:
            raise AIProcessingError(f"Failed to count PDF pages: {str(e)}")
    
    async def extract_image_text(self, file_content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(io.BytesIO(file_content))
            text = pytesseract.image_to_string(image, lang='ita+eng')
            return text.strip()
        except Exception as e:
            raise AIProcessingError(f"Failed to extract image text: {str(e)}")
    
    async def get_image_dimensions(self, file_content: bytes) -> Dict[str, int]:
        """Get image dimensions"""
        try:
            image = Image.open(io.BytesIO(file_content))
            return {"width": image.width, "height": image.height}
        except Exception as e:
            raise AIProcessingError(f"Failed to get image dimensions: {str(e)}")
    
    async def extract_video_text(self, file_content: bytes) -> str:
        """Extract text from video (placeholder - would need video processing)"""
        # This would require video processing libraries like moviepy
        # For now, return placeholder
        return "Video text extraction not implemented yet"
    
    async def get_video_duration(self, file_content: bytes) -> int:
        """Get video duration in seconds (placeholder)"""
        # This would require video processing libraries
        return 0
    
    async def generate_summary(self, text: str) -> str:
        """Generate summary of text using AI"""
        if not settings.OPENAI_API_KEY:
            return self._generate_simple_summary(text)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries of educational content in Italian."},
                    {"role": "user", "content": f"Create a summary of the following text:\n\n{text[:4000]}"}  # Limit text length
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fallback to simple summary
            return self._generate_simple_summary(text)
    
    async def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using AI"""
        if not settings.OPENAI_API_KEY:
            return self._extract_simple_keywords(text)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts key terms and concepts from educational content. Return only the keywords separated by commas."},
                    {"role": "user", "content": f"Extract the most important keywords from this text:\n\n{text[:4000]}"}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            keywords_text = response.choices[0].message.content.strip()
            return [kw.strip() for kw in keywords_text.split(",") if kw.strip()]
        except Exception as e:
            # Fallback to simple keyword extraction
            return self._extract_simple_keywords(text)
    
    async def detect_language(self, text: str) -> str:
        """Detect language of text"""
        # Simple language detection based on common words
        italian_words = ['il', 'la', 'di', 'che', 'e', 'un', 'una', 'per', 'con', 'del', 'della']
        english_words = ['the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that', 'he']
        
        text_lower = text.lower()
        italian_count = sum(1 for word in italian_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        return "it" if italian_count > english_count else "en"
    
    async def generate_quiz_questions(self, content: str, difficulty: str = "medium", num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions from content"""
        if not settings.OPENAI_API_KEY:
            return self._generate_simple_quiz(content, num_questions)
        
        try:
            prompt = f"""
            Generate {num_questions} quiz questions from the following content.
            Difficulty level: {difficulty}
            Return the questions in JSON format with this structure:
            [
                {{
                    "question": "Question text",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": 0,
                    "explanation": "Explanation of the correct answer",
                    "difficulty": "{difficulty}"
                }}
            ]
            
            Content:
            {content[:3000]}
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educator creating quiz questions. Always return valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            import json
            questions_text = response.choices[0].message.content.strip()
            return json.loads(questions_text)
        except Exception as e:
            # Fallback to simple quiz generation
            return self._generate_simple_quiz(content, num_questions)
    
    async def generate_concept_map(self, content: str) -> Dict[str, Any]:
        """Generate concept map from content"""
        if not settings.OPENAI_API_KEY:
            return self._generate_simple_concept_map(content)
        
        try:
            prompt = f"""
            Create a concept map from the following content.
            Return in JSON format with this structure:
            {{
                "nodes": [
                    {{"id": "1", "label": "Main Concept", "type": "main", "x": 0, "y": 0, "description": "Description"}},
                    {{"id": "2", "label": "Sub Concept", "type": "sub", "x": 100, "y": 100, "description": "Description"}}
                ],
                "connections": [
                    {{"from": "1", "to": "2", "label": "relationship", "type": "hierarchical"}}
                ]
            }}
            
            Content:
            {content[:3000]}
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educator creating concept maps. Always return valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            import json
            concept_map_text = response.choices[0].message.content.strip()
            return json.loads(concept_map_text)
        except Exception as e:
            # Fallback to simple concept map
            return self._generate_simple_concept_map(content)
    
    def _generate_simple_summary(self, text: str) -> str:
        """Generate simple summary without AI"""
        sentences = text.split('.')
        return '. '.join(sentences[:3]) + '.'
    
    def _extract_simple_keywords(self, text: str) -> List[str]:
        """Extract simple keywords without AI"""
        # Simple keyword extraction based on word frequency
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 10 most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _generate_simple_quiz(self, content: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate simple quiz without AI"""
        questions = []
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            if len(sentence) > 20:  # Only use substantial sentences
                questions.append({
                    "question": f"What is mentioned in: '{sentence[:50]}...'?",
                    "options": [
                        "Option A",
                        "Option B", 
                        "Option C",
                        "Option D"
                    ],
                    "correct_answer": 0,
                    "explanation": "This is a placeholder explanation.",
                    "difficulty": "medium"
                })
        
        return questions
    
    def _generate_simple_concept_map(self, content: str) -> Dict[str, Any]:
        """Generate simple concept map without AI"""
        words = re.findall(r'\b\w+\b', content.lower())
        unique_words = list(set([w for w in words if len(w) > 4]))[:10]
        
        nodes = []
        for i, word in enumerate(unique_words):
            nodes.append({
                "id": str(i),
                "label": word.title(),
                "type": "main" if i < 3 else "sub",
                "x": (i % 3) * 100,
                "y": (i // 3) * 100,
                "description": f"Concept related to {word}"
            })
        
        connections = []
        for i in range(len(nodes) - 1):
            connections.append({
                "from": str(i),
                "to": str(i + 1),
                "label": "related to",
                "type": "direct"
            })
        
        return {
            "nodes": nodes,
            "connections": connections
        }
