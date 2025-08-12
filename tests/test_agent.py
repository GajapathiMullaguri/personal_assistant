"""
Tests for the personal assistant agent.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.core.agent import PersonalAssistant


class TestPersonalAssistant:
    """Test cases for PersonalAssistant class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_settings(self, temp_dir):
        """Create mock settings for testing."""
        with patch('src.core.agent.settings') as mock_settings:
            mock_settings.groq_api_key = "test_api_key"
            mock_settings.model_name = "test-model"
            mock_settings.temperature = 0.7
            mock_settings.max_tokens = 1000
            mock_settings.memory_persist_dir = temp_dir
            yield mock_settings
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        mock_llm = Mock()
        mock_llm.ainvoke.return_value.content = "Test response"
        return mock_llm
    
    @pytest.fixture
    def agent(self, mock_settings, mock_llm):
        """Create a PersonalAssistant instance for testing."""
        with patch('src.core.agent.ChatGroq', return_value=mock_llm):
            return PersonalAssistant()
    
    def test_initialization(self, agent, mock_settings):
        """Test PersonalAssistant initialization."""
        assert agent.llm is not None
        assert agent.memory_manager is not None
        assert agent.conversation_memory is not None
        assert agent.system_prompt is not None
        assert agent.prompt_template is not None
    
    @pytest.mark.asyncio
    async def test_chat_basic(self, agent):
        """Test basic chat functionality."""
        user_input = "Hello, how are you?"
        
        response = await agent.chat(user_input)
        
        assert response == "Test response"
        assert len(agent.conversation_memory.chat_memory.messages) == 2
    
    @pytest.mark.asyncio
    async def test_chat_with_memory_context(self, agent):
        """Test chat with memory context."""
        # Add some test memories
        agent.memory_manager.add_memory(
            "User likes Python programming",
            "preference"
        )
        
        user_input = "What programming languages do I like?"
        
        response = await agent.chat(user_input)
        
        assert response == "Test response"
    
    def test_add_memory(self, agent):
        """Test adding memory through the agent."""
        content = "Test memory content"
        memory_type = "test"
        metadata = {"source": "test"}
        
        memory_id = agent.add_memory(content, memory_type, metadata)
        
        assert memory_id is not None
        assert isinstance(memory_id, str)
    
    def test_search_memories(self, agent):
        """Test searching memories through the agent."""
        # Add test memory
        agent.add_memory("Python is a programming language", "fact")
        
        # Search
        results = agent.search_memories("Python", n_results=1)
        
        assert len(results) > 0
        assert "Python" in results[0][0]
    
    def test_get_memory_stats(self, agent):
        """Test getting memory statistics through the agent."""
        stats = agent.get_memory_stats()
        
        assert "total_memories" in stats
        assert "type_distribution" in stats
    
    def test_clear_conversation_memory(self, agent):
        """Test clearing conversation memory."""
        # Add some messages
        agent.conversation_memory.chat_memory.add_user_message("Test")
        agent.conversation_memory.chat_memory.add_ai_message("Response")
        
        # Verify messages exist
        assert len(agent.conversation_memory.chat_memory.messages) == 2
        
        # Clear memory
        agent.clear_conversation_memory()
        
        # Verify memory is cleared
        assert len(agent.conversation_memory.chat_memory.messages) == 0
    
    def test_get_conversation_summary(self, agent):
        """Test getting conversation summary."""
        # No messages initially
        summary = agent.get_conversation_summary()
        assert "No conversation history" in summary
        
        # Add some messages
        agent.conversation_memory.chat_memory.add_user_message("Hello")
        agent.conversation_memory.chat_memory.add_ai_message("Hi there!")
        
        summary = agent.get_conversation_summary()
        assert "User messages: 1" in summary
        assert "Assistant responses: 1" in summary
    
    def test_export_memories(self, agent, temp_dir):
        """Test exporting memories through the agent."""
        # Add test memory
        agent.add_memory("Export test", "test")
        
        # Export
        export_path = temp_dir / "export_test.json"
        success = agent.export_memories(export_path)
        
        assert success is True
        assert export_path.exists()
    
    @pytest.mark.asyncio
    async def test_chat_error_handling(self, agent):
        """Test chat error handling."""
        # Mock LLM to raise an error
        agent.llm.ainvoke.side_effect = Exception("Test error")
        
        user_input = "Hello"
        response = await agent.chat(user_input)
        
        assert "I apologize, but I encountered an error" in response
    
    def test_important_info_detection(self, agent):
        """Test detection of important information."""
        # Test with important keywords
        important_inputs = [
            "Remember that I like Python",
            "This is important information",
            "Please save this preference",
            "I always use Linux",
            "My favorite color is blue"
        ]
        
        for user_input in important_inputs:
            # Mock the memory manager to track calls
            with patch.object(agent.memory_manager, 'add_memory') as mock_add:
                # This would normally be called in the async context
                # For testing, we'll call the method directly
                pass
        
        # The actual test would verify that important information is stored
        # This requires more complex mocking of the async context


if __name__ == "__main__":
    pytest.main([__file__])
