"""
Concept map service
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.concept_map import ConceptMap, ConceptNode, ConceptConnection
from app.models.upload import Upload
from app.schemas.concept_map import (
    ConceptMapCreate, 
    ConceptMapUpdate,
    ConceptNodeCreate,
    ConceptConnectionCreate,
    ConceptMapGenerationRequest
)
from app.core.exceptions import NotFoundError, ValidationError
from app.services.ai_service import AIService


class ConceptMapService:
    """Concept map service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    def create_concept_map(self, user_id: str, concept_map_data: ConceptMapCreate) -> ConceptMap:
        """Create a new concept map"""
        concept_map = ConceptMap(
            user_id=user_id,
            subject_id=concept_map_data.subject_id,
            title=concept_map_data.title,
            is_public=concept_map_data.is_public,
            description=concept_map_data.description,
            tags=concept_map_data.tags
        )
        
        self.db.add(concept_map)
        self.db.commit()
        self.db.refresh(concept_map)
        
        # Add nodes if provided
        if concept_map_data.nodes:
            for node_data in concept_map_data.nodes:
                self._create_concept_node(concept_map.id, node_data)
        
        # Add connections if provided
        if concept_map_data.connections:
            for connection_data in concept_map_data.connections:
                self._create_concept_connection(concept_map.id, connection_data)
        
        return concept_map
    
    def get_concept_maps(self, user_id: str, subject_id: Optional[str] = None) -> List[ConceptMap]:
        """Get all concept maps for a user"""
        query = self.db.query(ConceptMap).filter(ConceptMap.user_id == user_id)
        
        if subject_id:
            query = query.filter(ConceptMap.subject_id == subject_id)
        
        return query.all()
    
    def get_concept_map(self, concept_map_id: str, user_id: str) -> Optional[ConceptMap]:
        """Get a specific concept map"""
        return self.db.query(ConceptMap).filter(
            ConceptMap.id == concept_map_id,
            ConceptMap.user_id == user_id
        ).first()
    
    def update_concept_map(self, concept_map_id: str, user_id: str, concept_map_data: ConceptMapUpdate) -> ConceptMap:
        """Update a concept map"""
        concept_map = self.get_concept_map(concept_map_id, user_id)
        if not concept_map:
            raise NotFoundError("Concept map", concept_map_id)
        
        # Update fields
        for field, value in concept_map_data.dict(exclude_unset=True).items():
            setattr(concept_map, field, value)
        
        self.db.commit()
        self.db.refresh(concept_map)
        
        return concept_map
    
    def delete_concept_map(self, concept_map_id: str, user_id: str) -> bool:
        """Delete a concept map"""
        concept_map = self.get_concept_map(concept_map_id, user_id)
        if not concept_map:
            return False
        
        self.db.delete(concept_map)
        self.db.commit()
        
        return True
    
    def create_concept_node(self, concept_map_id: str, user_id: str, node_data: ConceptNodeCreate) -> ConceptNode:
        """Create a concept node"""
        # Verify concept map belongs to user
        concept_map = self.get_concept_map(concept_map_id, user_id)
        if not concept_map:
            raise NotFoundError("Concept map", concept_map_id)
        
        node = ConceptNode(
            concept_map_id=concept_map_id,
            label=node_data.label,
            x=node_data.x,
            y=node_data.y,
            type=node_data.type,
            color=node_data.color,
            description=node_data.description,
            examples=node_data.examples,
            source_upload_id=node_data.source_upload_id
        )
        
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        
        return node
    
    def update_concept_node(self, concept_map_id: str, node_id: str, user_id: str, node_data: Dict[str, Any]) -> ConceptNode:
        """Update a concept node"""
        # Verify concept map belongs to user
        concept_map = self.get_concept_map(concept_map_id, user_id)
        if not concept_map:
            raise NotFoundError("Concept map", concept_map_id)
        
        node = self.db.query(ConceptNode).filter(
            ConceptNode.id == node_id,
            ConceptNode.concept_map_id == concept_map_id
        ).first()
        
        if not node:
            raise NotFoundError("Concept node", node_id)
        
        # Update fields
        for field, value in node_data.items():
            if hasattr(node, field):
                setattr(node, field, value)
        
        self.db.commit()
        self.db.refresh(node)
        
        return node
    
    def delete_concept_node(self, concept_map_id: str, node_id: str, user_id: str) -> bool:
        """Delete a concept node"""
        # Verify concept map belongs to user
        concept_map = self.get_concept_map(concept_map_id, user_id)
        if not concept_map:
            return False
        
        node = self.db.query(ConceptNode).filter(
            ConceptNode.id == node_id,
            ConceptNode.concept_map_id == concept_map_id
        ).first()
        
        if not node:
            return False
        
        self.db.delete(node)
        self.db.commit()
        
        return True
    
    def create_concept_connection(self, concept_map_id: str, user_id: str, connection_data: ConceptConnectionCreate) -> ConceptConnection:
        """Create a concept connection"""
        # Verify concept map belongs to user
        concept_map = self.get_concept_map(concept_map_id, user_id)
        if not concept_map:
            raise NotFoundError("Concept map", concept_map_id)
        
        connection = ConceptConnection(
            concept_map_id=concept_map_id,
            from_node_id=connection_data.from_node_id,
            to_node_id=connection_data.to_node_id,
            label=connection_data.label,
            type=connection_data.type,
            strength=connection_data.strength
        )
        
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        
        return connection
    
    def update_concept_connection(self, concept_map_id: str, connection_id: str, user_id: str, connection_data: Dict[str, Any]) -> ConceptConnection:
        """Update a concept connection"""
        # Verify concept map belongs to user
        concept_map = self.get_concept_map(concept_map_id, user_id)
        if not concept_map:
            raise NotFoundError("Concept map", concept_map_id)
        
        connection = self.db.query(ConceptConnection).filter(
            ConceptConnection.id == connection_id,
            ConceptConnection.concept_map_id == concept_map_id
        ).first()
        
        if not connection:
            raise NotFoundError("Concept connection", connection_id)
        
        # Update fields
        for field, value in connection_data.items():
            if hasattr(connection, field):
                setattr(connection, field, value)
        
        self.db.commit()
        self.db.refresh(connection)
        
        return connection
    
    def delete_concept_connection(self, concept_map_id: str, connection_id: str, user_id: str) -> bool:
        """Delete a concept connection"""
        # Verify concept map belongs to user
        concept_map = self.get_concept_map(concept_map_id, user_id)
        if not concept_map:
            return False
        
        connection = self.db.query(ConceptConnection).filter(
            ConceptConnection.id == connection_id,
            ConceptConnection.concept_map_id == concept_map_id
        ).first()
        
        if not connection:
            return False
        
        self.db.delete(connection)
        self.db.commit()
        
        return True
    
    def generate_concept_map(self, user_id: str, generation_data: ConceptMapGenerationRequest) -> ConceptMap:
        """Generate concept map using AI"""
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
            raise ValidationError("No content available for concept map generation")
        
        # Generate concept map using AI
        ai_concept_map = await self.ai_service.generate_concept_map(content)
        
        # Create concept map
        concept_map = ConceptMap(
            user_id=user_id,
            subject_id=generation_data.subject_id,
            title=generation_data.title,
            is_public=generation_data.is_public,
            tags=generation_data.tags
        )
        
        self.db.add(concept_map)
        self.db.commit()
        self.db.refresh(concept_map)
        
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
            self.db.add(node)
            self.db.flush()  # Get the ID
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
                self.db.add(connection)
        
        self.db.commit()
        self.db.refresh(concept_map)
        
        return concept_map
    
    def _create_concept_node(self, concept_map_id: str, node_data: ConceptNodeCreate) -> ConceptNode:
        """Create a concept node"""
        node = ConceptNode(
            concept_map_id=concept_map_id,
            label=node_data.label,
            x=node_data.x,
            y=node_data.y,
            type=node_data.type,
            color=node_data.color,
            description=node_data.description,
            examples=node_data.examples,
            source_upload_id=node_data.source_upload_id
        )
        
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        
        return node
    
    def _create_concept_connection(self, concept_map_id: str, connection_data: ConceptConnectionCreate) -> ConceptConnection:
        """Create a concept connection"""
        connection = ConceptConnection(
            concept_map_id=concept_map_id,
            from_node_id=connection_data.from_node_id,
            to_node_id=connection_data.to_node_id,
            label=connection_data.label,
            type=connection_data.type,
            strength=connection_data.strength
        )
        
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        
        return connection
    
    def get_concept_map_stats(self, user_id: str, subject_id: Optional[str] = None) -> Dict[str, Any]:
        """Get concept map statistics"""
        query = self.db.query(ConceptMap).filter(ConceptMap.user_id == user_id)
        
        if subject_id:
            query = query.filter(ConceptMap.subject_id == subject_id)
        
        concept_maps = query.all()
        
        total_maps = len(concept_maps)
        total_nodes = sum(len(cm.nodes) for cm in concept_maps)
        total_connections = sum(len(cm.connections) for cm in concept_maps)
        average_nodes = total_nodes / total_maps if total_maps > 0 else 0
        
        public_maps = sum(1 for cm in concept_maps if cm.is_public)
        private_maps = total_maps - public_maps
        
        return {
            "total_maps": total_maps,
            "total_nodes": total_nodes,
            "total_connections": total_connections,
            "average_nodes_per_map": average_nodes,
            "public_maps": public_maps,
            "private_maps": private_maps
        }
