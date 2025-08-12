"""
Tests for the chat chain implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from langchain.schema import HumanMessage, AIMessage

from src.chains.chat_chain import ChatChain


class TestChatChain:
    """Test cases for ChatChain class."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        with patch('src.chains.chat_chain.settings') as mock_settings:
            mock_settings.groq_api_key = "test_api_key"
            mock_settings.model_name = "test-model"
            mock_settings.temperature = 0.7
            mock_settings.max_tokens = 1000
            yield mock_settings
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        mock_llm = Mock()
        mock_llm.ainvoke.return_value = {"text": "Test response"}
        return mock_llm
    
    @pytest.fixture
    def chat_chain(self, mock_settings, mock_llm):
        """Create a ChatChain instance for testing."""
        with patch('src.chains.chat_chain.ChatGroq', return_value=mock_llm):
            return ChatChain()
    
    def test_initialization(self, chat_chain, mock_settings):
        """Test ChatChain initialization."""
        assert chat_chain.llm is not None
        assert chat_chain.chat_prompt is not None
        assert chat_chain.analysis_prompt is not None
        assert chat_chain.summary_prompt is not None
        assert chat_chain.chat_chain is not None
        assert chat_chain.analysis_chain is not None
        assert chat_chain.summary_chain is not None
    
    def test_format_conversation_history_empty(self, chat_chain):
        """Test formatting empty conversation history."""
        history = []
        formatted = chat_chain.format_conversation_history(history)
        
        assert formatted == "No previous conversation."
    
    def test_format_conversation_history_with_messages(self, chat_chain):
        """Test formatting conversation history with messages."""
        history = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
            HumanMessage(content="How are you?"),
            AIMessage(content="I'm doing well, thanks!")
        ]
        
        formatted = chat_chain.format_conversation_history(history)
        
        assert "Human: Hello" in formatted
        assert "Assistant: Hi there!" in formatted
        assert "Human: How are you?" in formatted
        assert "Assistant: I'm doing well, thanks!" in formatted
    
    def test_format_conversation_history_limit(self, chat_chain):
        """Test that conversation history is limited to last 10 messages."""
        # Create more than 10 messages
        history = []
        for i in range(15):
            history.append(HumanMessage(content=f"Message {i}"))
            history.append(AIMessage(content=f"Response {i}"))
        
        formatted = chat_chain.format_conversation_history(history)
        
        # Should only contain last 10 messages (5 exchanges)
        assert "Message 10" in formatted
        assert "Message 14" in formatted
        assert "Message 0" not in formatted
        assert "Message 5" not in formatted
    
    @pytest.mark.asyncio
    async def test_chat_basic(self, chat_chain):
        """Test basic chat functionality."""
        user_input = "Hello, how are you?"
        context = "Test context"
        history = []
        
        response = await chat_chain.chat(user_input, context, history)
        
        assert response == "Test response"
    
    @pytest.mark.asyncio
    async def test_chat_with_history(self, chat_chain):
        """Test chat with conversation history."""
        user_input = "What did we talk about?"
        context = "Previous conversation context"
        history = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!")
        ]
        
        response = await chat_chain.chat(user_input, context, history)
        
        assert response == "Test response"
    
    @pytest.mark.asyncio
    async def test_chat_error_handling(self, chat_chain):
        """Test chat error handling."""
        # Mock the chain to raise an error
        chat_chain.chat_chain.ainvoke.side_effect = Exception("Test error")
        
        user_input = "Hello"
        response = await chat_chain.chat(user_input)
        
        assert "I apologize, but I encountered an error" in response
    
    @pytest.mark.asyncio
    async def test_analyze_basic(self, chat_chain):
        """Test basic analysis functionality."""
        content = "Python is a programming language"
        context = "Programming languages context"
        
        response = await chat_chain.analyze(content, context)
        
        assert response == "Test response"
    
    @pytest.mark.asyncio
    async def test_analyze_error_handling(self, chat_chain):
        """Test analysis error handling."""
        # Mock the chain to raise an error
        chat_chain.analysis_chain.ainvoke.side_effect = Exception("Test error")
        
        content = "Test content"
        response = await chat_chain.analyze(content)
        
        assert "I apologize, but I encountered an error during analysis" in response
    
    @pytest.mark.asyncio
    async def test_summarize_basic(self, chat_chain):
        """Test basic summarization functionality."""
        content = "This is a long piece of text that needs to be summarized into a shorter version."
        
        response = await chat_chain.summarize(content)
        
        assert response == "Test response"
    
    @pytest.mark.asyncio
    async def test_summarize_error_handling(self, chat_chain):
        """Test summarization error handling."""
        # Mock the chain to raise an error
        chat_chain.summary_chain.ainvoke.side_effect = Exception("Test error")
        
        content = "Test content"
        response = await chat_chain.summarize(content)
        
        assert "I apologize, but I encountered an error during summarization" in response
    
    def test_get_chain_info(self, chat_chain, mock_settings):
        """Test getting chain information."""
        info = chat_chain.get_chain_info()
        
        assert "available_chains" in info
        assert "chat_chain" in info["available_chains"]
        assert "analysis_chain" in info["available_chains"]
        assert "summary_chain" in info["available_chains"]
        assert info["model"] == mock_settings.model_name
        assert info["temperature"] == mock_settings.temperature
        assert info["max_tokens"] == mock_settings.max_tokens
    
    def test_prompt_templates(self, chat_chain):
        """Test that prompt templates are properly configured."""
        # Test chat prompt
        chat_vars = chat_chain.chat_prompt.input_variables
        assert "context" in chat_vars
        assert "history" in chat_vars
        assert "input" in chat_vars
        
        # Test analysis prompt
        analysis_vars = chat_chain.analysis_prompt.input_variables
        assert "context" in analysis_vars
        assert "input" in analysis_vars
        
        # Test summary prompt
        summary_vars = chat_chain.summary_prompt.input_variables
        assert "content" in summary_vars


if __name__ == "__main__":
    pytest.main([__file__])
