"""
Tests for the memory management system.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.core.memory import MemoryManager


class TestMemoryManager:
    """Test cases for MemoryManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def memory_manager(self, temp_dir):
        """Create a MemoryManager instance for testing."""
        return MemoryManager(temp_dir)
    
    def test_initialization(self, memory_manager, temp_dir):
        """Test MemoryManager initialization."""
        assert memory_manager.persist_directory == temp_dir
        assert memory_manager.collection is not None
        assert memory_manager.embedding_model is not None
    
    def test_add_memory(self, memory_manager):
        """Test adding a memory entry."""
        content = "Test memory content"
        memory_type = "test"
        metadata = {"test_key": "test_value"}
        
        memory_id = memory_manager.add_memory(
            content=content,
            memory_type=memory_type,
            metadata=metadata
        )
        
        assert memory_id is not None
        assert isinstance(memory_id, str)
        
        # Verify memory was added
        retrieved = memory_manager.get_memory_by_id(memory_id)
        assert retrieved is not None
        assert retrieved[0] == content
        assert retrieved[1]["type"] == memory_type
        assert retrieved[1]["test_key"] == "test_value"
    
    def test_search_memory(self, memory_manager):
        """Test memory search functionality."""
        # Add test memories
        memory_manager.add_memory("Python programming language", "fact")
        memory_manager.add_memory("Machine learning algorithms", "fact")
        memory_manager.add_memory("Data science projects", "project")
        
        # Search for relevant memories
        results = memory_manager.search_memory("Python", n_results=2)
        
        assert len(results) > 0
        assert any("Python" in result[0] for result in results)
    
    def test_update_memory(self, memory_manager):
        """Test updating an existing memory."""
        # Add initial memory
        memory_id = memory_manager.add_memory("Original content", "test")
        
        # Update memory
        updated_content = "Updated content"
        success = memory_manager.update_memory(
            memory_id=memory_id,
            content=updated_content,
            metadata={"updated": True}
        )
        
        assert success is True
        
        # Verify update
        retrieved = memory_manager.get_memory_by_id(memory_id)
        assert retrieved[0] == updated_content
        assert retrieved[1]["updated"] is True
    
    def test_delete_memory(self, memory_manager):
        """Test deleting a memory entry."""
        # Add memory
        memory_id = memory_manager.add_memory("Content to delete", "test")
        
        # Verify it exists
        assert memory_manager.get_memory_by_id(memory_id) is not None
        
        # Delete memory
        success = memory_manager.delete_memory(memory_id)
        assert success is True
        
        # Verify it's gone
        assert memory_manager.get_memory_by_id(memory_id) is None
    
    def test_get_memory_stats(self, memory_manager):
        """Test getting memory statistics."""
        # Add some memories
        memory_manager.add_memory("Test 1", "type1")
        memory_manager.add_memory("Test 2", "type2")
        memory_manager.add_memory("Test 3", "type1")
        
        stats = memory_manager.get_memory_stats()
        
        assert "total_memories" in stats
        assert "type_distribution" in stats
        assert stats["total_memories"] >= 3
        assert "type1" in stats["type_distribution"]
        assert "type2" in stats["type_distribution"]
    
    def test_export_memories(self, memory_manager, temp_dir):
        """Test exporting memories to file."""
        # Add test memories
        memory_manager.add_memory("Export test 1", "export")
        memory_manager.add_memory("Export test 2", "export")
        
        # Export to file
        export_path = temp_dir / "export_test.json"
        success = memory_manager.export_memories(export_path)
        
        assert success is True
        assert export_path.exists()
        
        # Verify export content
        import json
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        assert "memories" in export_data
        assert len(export_data["memories"]) >= 2
    
    def test_clear_all_memories(self, memory_manager):
        """Test clearing all memories."""
        # Add some memories
        memory_manager.add_memory("Test 1", "clear")
        memory_manager.add_memory("Test 2", "clear")
        
        # Verify they exist
        stats_before = memory_manager.get_memory_stats()
        assert stats_before["total_memories"] >= 2
        
        # Clear all memories
        success = memory_manager.clear_all_memories()
        assert success is True
        
        # Verify they're gone
        stats_after = memory_manager.get_memory_stats()
        assert stats_after["total_memories"] == 0


if __name__ == "__main__":
    pytest.main([__file__])
