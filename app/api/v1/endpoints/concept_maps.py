"""
Concept map management endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.concept_map import (
    ConceptMapCreate, 
    ConceptMapUpdate, 
    ConceptMapResponse,
    ConceptNodeCreate,
    ConceptNodeUpdate,
    ConceptNodeResponse,
    ConceptConnectionCreate,
    ConceptConnectionUpdate,
    ConceptConnectionResponse,
    ConceptMapGenerationRequest,
    ConceptMapStats
)
from app.services.concept_map_service import ConceptMapService

router = APIRouter()


def get_concept_map_service(db: Session = Depends(get_db)) -> ConceptMapService:
    """Get concept map service"""
    return ConceptMapService(db)


@router.get("/", response_model=List[ConceptMapResponse])
async def get_concept_maps(
    subject_id: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Get all concept maps for the current user"""
    try:
        user_id = get_current_user_id(token)
        concept_maps = concept_map_service.get_concept_maps(user_id, subject_id)
        return concept_maps
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/", response_model=ConceptMapResponse, status_code=status.HTTP_201_CREATED)
async def create_concept_map(
    concept_map_data: ConceptMapCreate,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Create a new concept map"""
    try:
        user_id = get_current_user_id(token)
        concept_map = concept_map_service.create_concept_map(user_id, concept_map_data)
        return concept_map
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{concept_map_id}", response_model=ConceptMapResponse)
async def get_concept_map(
    concept_map_id: str,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Get a specific concept map"""
    try:
        user_id = get_current_user_id(token)
        concept_map = concept_map_service.get_concept_map(concept_map_id, user_id)
        
        if not concept_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept map not found"
            )
        
        return concept_map
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{concept_map_id}", response_model=ConceptMapResponse)
async def update_concept_map(
    concept_map_id: str,
    concept_map_data: ConceptMapUpdate,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Update a concept map"""
    try:
        user_id = get_current_user_id(token)
        concept_map = concept_map_service.update_concept_map(concept_map_id, user_id, concept_map_data)
        return concept_map
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{concept_map_id}")
async def delete_concept_map(
    concept_map_id: str,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Delete a concept map"""
    try:
        user_id = get_current_user_id(token)
        success = concept_map_service.delete_concept_map(concept_map_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept map not found"
            )
        
        return {"message": "Concept map deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{concept_map_id}/nodes", response_model=ConceptNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_concept_node(
    concept_map_id: str,
    node_data: ConceptNodeCreate,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Create a concept node"""
    try:
        user_id = get_current_user_id(token)
        node = concept_map_service.create_concept_node(concept_map_id, user_id, node_data)
        return node
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{concept_map_id}/nodes/{node_id}", response_model=ConceptNodeResponse)
async def update_concept_node(
    concept_map_id: str,
    node_id: str,
    node_data: ConceptNodeUpdate,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Update a concept node"""
    try:
        user_id = get_current_user_id(token)
        node = concept_map_service.update_concept_node(
            concept_map_id, 
            node_id, 
            user_id, 
            node_data.dict(exclude_unset=True)
        )
        return node
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{concept_map_id}/nodes/{node_id}")
async def delete_concept_node(
    concept_map_id: str,
    node_id: str,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Delete a concept node"""
    try:
        user_id = get_current_user_id(token)
        success = concept_map_service.delete_concept_node(concept_map_id, node_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept node not found"
            )
        
        return {"message": "Concept node deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{concept_map_id}/connections", response_model=ConceptConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_concept_connection(
    concept_map_id: str,
    connection_data: ConceptConnectionCreate,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Create a concept connection"""
    try:
        user_id = get_current_user_id(token)
        connection = concept_map_service.create_concept_connection(concept_map_id, user_id, connection_data)
        return connection
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{concept_map_id}/connections/{connection_id}", response_model=ConceptConnectionResponse)
async def update_concept_connection(
    concept_map_id: str,
    connection_id: str,
    connection_data: ConceptConnectionUpdate,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Update a concept connection"""
    try:
        user_id = get_current_user_id(token)
        connection = concept_map_service.update_concept_connection(
            concept_map_id, 
            connection_id, 
            user_id, 
            connection_data.dict(exclude_unset=True)
        )
        return connection
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{concept_map_id}/connections/{connection_id}")
async def delete_concept_connection(
    concept_map_id: str,
    connection_id: str,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Delete a concept connection"""
    try:
        user_id = get_current_user_id(token)
        success = concept_map_service.delete_concept_connection(concept_map_id, connection_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept connection not found"
            )
        
        return {"message": "Concept connection deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/generate", response_model=ConceptMapResponse, status_code=status.HTTP_201_CREATED)
async def generate_concept_map(
    generation_data: ConceptMapGenerationRequest,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Generate concept map using AI"""
    try:
        user_id = get_current_user_id(token)
        concept_map = await concept_map_service.generate_concept_map(user_id, generation_data)
        return concept_map
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/stats", response_model=ConceptMapStats)
async def get_concept_map_stats(
    subject_id: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    concept_map_service: ConceptMapService = Depends(get_concept_map_service)
):
    """Get concept map statistics"""
    try:
        user_id = get_current_user_id(token)
        stats = concept_map_service.get_concept_map_stats(user_id, subject_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
