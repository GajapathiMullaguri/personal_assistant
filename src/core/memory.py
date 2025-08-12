"""
Long-term memory system using ChromaDB for vector storage.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document


class MemoryManager:
    """Manages long-term memory using ChromaDB vector database."""
    
    def __init__(self, persist_directory: Path):
        """Initialize the memory manager.
        
        Args:
            persist_directory: Directory to persist memory data
        """
        self.persist_directory = persist_directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="assistant_memories",
            metadata={"description": "Long-term memory for AI assistant"}
        )
    
    def add_memory(
        self, 
        content: str, 
        memory_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Add a new memory entry.
        
        Args:
            content: The content to remember
            memory_type: Type of memory (conversation, fact, task, etc.)
            metadata: Additional metadata
            timestamp: When the memory was created
            
        Returns:
            Memory ID
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()
        
        # Prepare metadata
        memory_metadata = {
            "type": memory_type,
            "timestamp": timestamp.isoformat(),
            "content_length": len(content)
        }
        if metadata:
            memory_metadata.update(metadata)
        
        # Generate unique ID
        memory_id = str(uuid.uuid4())
        
        # Add to collection
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[memory_metadata],
            ids=[memory_id]
        )
        
        return memory_id
    
    def search_memory(
        self, 
        query: str, 
        n_results: int = 5,
        memory_type: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for relevant memories.
        
        Args:
            query: Search query
            n_results: Number of results to return
            memory_type: Filter by memory type
            filter_metadata: Additional metadata filters
            
        Returns:
            List of (content, similarity_score, metadata) tuples
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Prepare where clause for filtering
        where_clause = {}
        if memory_type:
            where_clause["type"] = memory_type
        if filter_metadata:
            where_clause.update(filter_metadata)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0]
            )):
                # Calculate similarity score (1 - distance)
                distance = results['distances'][0][i] if results['distances'] else 0
                similarity = 1 - distance
                formatted_results.append((doc, similarity, metadata))
        
        return formatted_results
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Retrieve a specific memory by ID.
        
        Args:
            memory_id: The memory ID to retrieve
            
        Returns:
            Tuple of (content, metadata) or None if not found
        """
        try:
            result = self.collection.get(ids=[memory_id])
            if result['documents'] and result['metadatas']:
                return result['documents'][0], result['metadatas'][0]
        except Exception:
            pass
        return None
    
    def update_memory(
        self, 
        memory_id: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing memory.
        
        Args:
            memory_id: The memory ID to update
            content: New content
            metadata: Updated metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing memory
            existing = self.get_memory_by_id(memory_id)
            if not existing:
                return False
            
            # Generate new embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Prepare updated metadata
            updated_metadata = existing[1].copy()
            updated_metadata["last_updated"] = datetime.now().isoformat()
            updated_metadata["content_length"] = len(content)
            if metadata:
                updated_metadata.update(metadata)
            
            # Update in collection
            self.collection.update(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[updated_metadata]
            )
            return True
            
        except Exception:
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory entry.
        
        Args:
            memory_id: The memory ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            count = self.collection.count()
            
            # Get sample memories for type analysis
            sample = self.collection.get(limit=1000)
            type_counts = {}
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    memory_type = metadata.get('type', 'unknown')
                    type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
            
            return {
                "total_memories": count,
                "type_distribution": type_counts,
                "persist_directory": str(self.persist_directory)
            }
        except Exception:
            return {"error": "Could not retrieve statistics"}
    
    def clear_all_memories(self) -> bool:
        """Clear all memories from the system.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(where={})
            return True
        except Exception:
            return False
    
    def export_memories(self, filepath: Path) -> bool:
        """Export all memories to a JSON file.
        
        Args:
            filepath: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            all_memories = self.collection.get()
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_memories": len(all_memories['ids']),
                "memories": []
            }
            
            for i, memory_id in enumerate(all_memories['ids']):
                memory_data = {
                    "id": memory_id,
                    "content": all_memories['documents'][i],
                    "metadata": all_memories['metadatas'][i]
                }
                export_data["memories"].append(memory_data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception:
            return False
