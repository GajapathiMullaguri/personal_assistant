"""
Long-term memory system using ChromaDB for vector storage.
Enhanced with conversation persistence and context optimization.
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
        timestamp: Optional[datetime] = None,
        importance_score: Optional[float] = None
    ) -> str:
        """Add a new memory entry.
        
        Args:
            content: The content to remember
            memory_type: Type of memory (conversation, fact, task, etc.)
            metadata: Additional metadata
            timestamp: When the memory was created
            importance_score: Importance score (0.0 to 1.0)
            
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
            "content_length": len(content),
            "importance_score": importance_score or self._calculate_importance_score(content, memory_type)
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
    
    def add_conversation_memory(
        self,
        user_input: str,
        assistant_response: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a conversation exchange to long-term memory.
        
        Args:
            user_input: User's message
            assistant_response: Assistant's response
            conversation_id: Optional conversation identifier
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        # Combine user input and assistant response
        conversation_content = f"User: {user_input}\nAssistant: {assistant_response}"
        
        # Calculate importance based on content
        importance_score = self._calculate_conversation_importance(user_input, assistant_response)
        
        # Prepare metadata
        conv_metadata = {
            "conversation_id": conversation_id or str(uuid.uuid4()),
            "user_input_length": len(user_input),
            "assistant_response_length": len(assistant_response),
            "total_length": len(conversation_content)
        }
        if metadata:
            conv_metadata.update(metadata)
        
        return self.add_memory(
            content=conversation_content,
            memory_type="conversation",
            metadata=conv_metadata,
            importance_score=importance_score
        )
    
    def _calculate_importance_score(self, content: str, memory_type: str) -> float:
        """Calculate importance score for memory content.
        
        Args:
            content: Content to score
            memory_type: Type of memory
            
        Returns:
            Importance score (0.0 to 1.0)
        """
        base_score = 0.5
        
        # Type-based scoring
        type_scores = {
            "important_info": 0.9,
            "fact": 0.8,
            "preference": 0.7,
            "conversation": 0.6,
            "task": 0.7,
            "other": 0.5
        }
        base_score = type_scores.get(memory_type, base_score)
        
        # Content-based scoring
        important_keywords = [
            "remember", "important", "save", "note", "preference", 
            "like", "dislike", "always", "never", "favorite",
            "critical", "essential", "key", "vital", "crucial"
        ]
        
        keyword_bonus = sum(0.1 for keyword in important_keywords if keyword.lower() in content.lower())
        base_score = min(1.0, base_score + keyword_bonus)
        
        # Length-based scoring (very short or very long might be less important)
        if len(content) < 10:
            base_score *= 0.8
        elif len(content) > 500:
            base_score *= 0.9
        
        return round(base_score, 2)
    
    def _calculate_conversation_importance(self, user_input: str, assistant_response: str) -> float:
        """Calculate importance score for conversation exchanges.
        
        Args:
            user_input: User's message
            assistant_response: Assistant's response
            
        Returns:
            Importance score (0.0 to 1.0)
        """
        base_score = 0.6
        
        # Check for important keywords in user input
        important_keywords = [
            "remember", "important", "save", "note", "preference", 
            "like", "dislike", "always", "never", "favorite",
            "critical", "essential", "key", "vital", "crucial"
        ]
        
        keyword_bonus = sum(0.1 for keyword in important_keywords if keyword.lower() in user_input.lower())
        base_score = min(1.0, base_score + keyword_bonus)
        
        # Check if user is asking for help or information
        question_indicators = ["how", "what", "when", "where", "why", "can you", "help", "explain"]
        if any(indicator in user_input.lower() for indicator in question_indicators):
            base_score += 0.1
        
        # Check response quality (longer, more detailed responses might indicate important topics)
        if len(assistant_response) > 100:
            base_score += 0.1
        
        return round(min(1.0, base_score), 2)
    
    def search_memory(
        self, 
        query: str, 
        n_results: int = 5,
        memory_type: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_importance: Optional[float] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for relevant memories.
        
        Args:
            query: Search query
            n_results: Number of results to return
            memory_type: Filter by memory type
            filter_metadata: Additional metadata filters
            min_importance: Minimum importance score threshold
            
        Returns:
            List of (content, similarity_score, metadata) tuples
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Prepare where clause for filtering
        where_clause = {}
        if memory_type:
            where_clause["type"] = memory_type
        if min_importance is not None:
            where_clause["importance_score"] = {"$gte": min_importance}
        if filter_metadata:
            where_clause.update(filter_metadata)
        
        # Search with higher n_results to allow for importance filtering
        search_n = min(n_results * 2, 20)  # Get more results for better filtering
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=search_n,
            where=where_clause if where_clause else None
        )
        
        # Format and score results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0]
            )):
                # Calculate similarity score (1 - distance)
                distance = results['distances'][0][i] if results['distances'] else 0
                similarity = 1 - distance
                
                # Get importance score
                importance = metadata.get('importance_score', 0.5)
                
                # Combine similarity and importance for final score
                final_score = (similarity * 0.7) + (importance * 0.3)
                
                formatted_results.append((doc, final_score, metadata))
        
        # Sort by final score and return top n_results
        formatted_results.sort(key=lambda x: x[1], reverse=True)
        return formatted_results[:n_results]
    
    def get_optimized_context(
        self,
        query: str,
        max_tokens: int = 1000,
        n_results: int = 10,
        include_summaries: bool = True
    ) -> str:
        """Get optimized context for a query, prioritizing important and relevant memories.
        
        Args:
            query: Search query
            max_tokens: Maximum tokens for context
            n_results: Number of memories to consider
            include_summaries: Whether to include memory summaries
            
        Returns:
            Optimized context string
        """
        # Get relevant memories with importance filtering
        memories = self.search_memory(
            query=query,
            n_results=n_results,
            min_importance=0.4  # Only include moderately important memories
        )
        
        if not memories:
            return ""
        
        # Sort by importance and relevance
        memories.sort(key=lambda x: (x[2].get('importance_score', 0.5), x[1]), reverse=True)
        
        # Build optimized context
        context_parts = []
        current_tokens = 0
        
        for content, score, metadata in memories:
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            estimated_tokens = len(content) // 4
            
            # Check if adding this memory would exceed token limit
            if current_tokens + estimated_tokens > max_tokens:
                break
            
            # Format memory content
            memory_type = metadata.get('type', 'memory')
            importance = metadata.get('importance_score', 0.5)
            timestamp = metadata.get('timestamp', '')
            
            if include_summaries and len(content) > 200:
                # Summarize long memories
                summary = self._summarize_content(content)
                formatted_memory = f"[{memory_type.upper()}] {summary} (Importance: {importance:.2f})"
            else:
                formatted_memory = f"[{memory_type.upper()}] {content} (Importance: {importance:.2f})"
            
            context_parts.append(formatted_memory)
            current_tokens += estimated_tokens
        
        if not context_parts:
            return ""
        
        # Join context parts
        context = "\n\n".join(context_parts)
        
        # Add context header
        header = f"Relevant context from {len(context_parts)} memories (Total: ~{current_tokens} tokens):"
        return f"{header}\n{context}"
    
    def _summarize_content(self, content: str, max_length: int = 150) -> str:
        """Create a simple summary of content.
        
        Args:
            content: Content to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized content
        """
        if len(content) <= max_length:
            return content
        
        # Simple summarization: take first sentence or first max_length characters
        sentences = content.split('.')
        if sentences and len(sentences[0]) <= max_length:
            summary = sentences[0].strip()
            if not summary.endswith('.'):
                summary += '.'
            return summary
        
        # Fallback: truncate and add ellipsis
        return content[:max_length-3] + "..."
    
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
            
            # Get sample memories for analysis
            sample = self.collection.get(limit=1000)
            type_counts = {}
            importance_scores = []
            
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    memory_type = metadata.get('type', 'unknown')
                    type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
                    
                    importance = metadata.get('importance_score', 0.5)
                    importance_scores.append(importance)
            
            # Calculate average importance
            avg_importance = sum(importance_scores) / len(importance_scores) if importance_scores else 0
            
            return {
                "total_memories": count,
                "type_distribution": type_counts,
                "average_importance_score": round(avg_importance, 2),
                "importance_score_range": {
                    "min": min(importance_scores) if importance_scores else 0,
                    "max": max(importance_scores) if importance_scores else 0
                },
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
