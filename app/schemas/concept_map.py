"""
Concept map schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator


class ConceptNodeBase(BaseModel):
    """Base concept node schema"""
    label: str
    x: float
    y: float
    type: str = "main"  # main, sub, detail
    color: str = "#3B82F6"
    description: Optional[str] = None
    examples: List[str] = []


class ConceptNodeCreate(ConceptNodeBase):
    """Concept node creation schema"""
    source_upload_id: Optional[str] = None


class ConceptNodeUpdate(BaseModel):
    """Concept node update schema"""
    label: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    type: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    examples: Optional[List[str]] = None


class ConceptNodeResponse(ConceptNodeBase):
    """Concept node response schema"""
    id: str
    concept_map_id: str
    source_upload_id: Optional[str] = None
    ai_generated: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ConceptConnectionBase(BaseModel):
    """Base concept connection schema"""
    from_node_id: str
    to_node_id: str
    label: Optional[str] = None
    type: str = "direct"  # direct, hierarchical, causal
    strength: float = 1.0  # 0-1


class ConceptConnectionCreate(ConceptConnectionBase):
    """Concept connection creation schema"""
    pass


class ConceptConnectionUpdate(BaseModel):
    """Concept connection update schema"""
    label: Optional[str] = None
    type: Optional[str] = None
    strength: Optional[float] = None


class ConceptConnectionResponse(ConceptConnectionBase):
    """Concept connection response schema"""
    id: str
    concept_map_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ConceptMapBase(BaseModel):
    """Base concept map schema"""
    title: str
    is_public: bool = False
    description: Optional[str] = None
    tags: List[str] = []


class ConceptMapCreate(ConceptMapBase):
    """Concept map creation schema"""
    subject_id: str
    nodes: Optional[List[ConceptNodeCreate]] = []
    connections: Optional[List[ConceptConnectionCreate]] = []


class ConceptMapUpdate(BaseModel):
    """Concept map update schema"""
    title: Optional[str] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class ConceptMapResponse(ConceptMapBase):
    """Concept map response schema"""
    id: str
    user_id: str
    subject_id: str
    nodes: List[ConceptNodeResponse] = []
    connections: List[ConceptConnectionResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ConceptMapGenerationRequest(BaseModel):
    """Concept map generation request schema"""
    subject_id: str
    title: str
    source_upload_ids: Optional[List[str]] = None
    is_public: bool = False
    tags: List[str] = []


class ConceptMapStats(BaseModel):
    """Concept map statistics schema"""
    total_maps: int
    total_nodes: int
    total_connections: int
    average_nodes_per_map: float
    public_maps: int
    private_maps: int
