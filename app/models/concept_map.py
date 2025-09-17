"""
Concept map model and related schemas
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.base import BaseModel


class ConceptMap(BaseModel):
    """Concept map model"""
    
    __tablename__ = "concept_maps"
    
    # Basic info
    title = Column(String(255), nullable=False)
    is_public = Column(Boolean, default=False)
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False)
    
    # Additional metadata
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    
    # Relationships
    user = relationship("User", back_populates="concept_maps")
    subject = relationship("Subject", back_populates="concept_maps")
    nodes = relationship("ConceptNode", back_populates="concept_map", cascade="all, delete-orphan")
    connections = relationship("ConceptConnection", back_populates="concept_map", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="concept_map")


class ConceptNode(BaseModel):
    """Concept node model"""
    
    __tablename__ = "concept_nodes"
    
    # Basic info
    label = Column(String(255), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    type = Column(String(50), default="main")  # main, sub, detail
    color = Column(String(7), default="#3B82F6")  # Hex color
    
    # Foreign keys
    concept_map_id = Column(String(36), ForeignKey("concept_maps.id"), nullable=False)
    source_upload_id = Column(String(36), ForeignKey("uploads.id"), nullable=True)
    
    # Content
    description = Column(Text, nullable=True)
    examples = Column(JSON, default=list)
    
    # AI generation
    ai_generated = Column(Boolean, default=False)
    
    # Relationships
    concept_map = relationship("ConceptMap", back_populates="nodes")
    source_upload = relationship("Upload", back_populates="concept_nodes")
    outgoing_connections = relationship("ConceptConnection", foreign_keys="ConceptConnection.from_node_id", back_populates="from_node")
    incoming_connections = relationship("ConceptConnection", foreign_keys="ConceptConnection.to_node_id", back_populates="to_node")


class ConceptConnection(BaseModel):
    """Concept connection model"""
    
    __tablename__ = "concept_connections"
    
    # Basic info
    label = Column(String(255), nullable=True)
    type = Column(String(50), default="direct")  # direct, hierarchical, causal
    strength = Column(Float, default=1.0)  # 0-1
    
    # Foreign keys
    concept_map_id = Column(String(36), ForeignKey("concept_maps.id"), nullable=False)
    from_node_id = Column(String(36), ForeignKey("concept_nodes.id"), nullable=False)
    to_node_id = Column(String(36), ForeignKey("concept_nodes.id"), nullable=False)
    
    # Relationships
    concept_map = relationship("ConceptMap", back_populates="connections")
    from_node = relationship("ConceptNode", foreign_keys=[from_node_id], back_populates="outgoing_connections")
    to_node = relationship("ConceptNode", foreign_keys=[to_node_id], back_populates="incoming_connections")
