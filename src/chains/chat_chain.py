"""
Enhanced chat chain implementation using LangChain.
"""

from typing import List, Dict, Any, Optional
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq

from ..core.config import settings


class ChatChain:
    """Enhanced chat chain with memory and context management."""
    
    def __init__(self):
        """Initialize the chat chain."""
        # Initialize Groq LLM
        self.llm = ChatGroq(
            groq_api_key=settings.groq_api_key,
            model_name=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        # Create different prompt templates for different use cases
        self.chat_prompt = PromptTemplate(
            input_variables=["context", "history", "input"],
            template="""You are a helpful AI assistant. Use the following context and conversation history to provide a helpful response.

Context: {context}

Conversation History:
{history}

Human: {input}
Assistant:"""
        )
        
        self.analysis_prompt = PromptTemplate(
            input_variables=["context", "input"],
            template="""Analyze the following information and provide insights:

Context: {context}

Information to analyze: {input}

Analysis:"""
        )
        
        self.summary_prompt = PromptTemplate(
            input_variables=["content"],
            template="""Summarize the following content in a clear and concise way:

{content}

Summary:"""
        )
        
        # Create chains using the new pattern
        self.chat_chain = self.chat_prompt | self.llm
        self.analysis_chain = self.analysis_prompt | self.llm
        self.summary_chain = self.summary_prompt | self.llm
    
    def format_conversation_history(self, messages: List[BaseMessage]) -> str:
        """Format conversation history for prompt templates.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Formatted conversation history string
        """
        if not messages:
            return "No previous conversation."
        
        formatted_history = []
        for message in messages[-10:]:  # Keep last 10 messages
            if isinstance(message, HumanMessage):
                formatted_history.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                formatted_history.append(f"Assistant: {message.content}")
        
        return "\n".join(formatted_history)
    
    async def chat(
        self, 
        user_input: str, 
        context: str = "",
        history: List[BaseMessage] = None
    ) -> str:
        """Generate a chat response.
        
        Args:
            user_input: User's message
            context: Additional context information
            history: Conversation history
            
        Returns:
            Generated response
        """
        try:
            formatted_history = self.format_conversation_history(history or [])
            
            response = await self.chat_chain.ainvoke({
                "context": context,
                "history": formatted_history,
                "input": user_input
            })
            
            return response.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def analyze(self, content: str, context: str = "") -> str:
        """Analyze content and provide insights.
        
        Args:
            content: Content to analyze
            context: Additional context
            
        Returns:
            Analysis results
        """
        try:
            response = await self.analysis_chain.ainvoke({
                "context": context,
                "input": content
            })
            
            return response.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error during analysis: {str(e)}"
    
    async def summarize(self, content: str) -> str:
        """Summarize content.
        
        Args:
            content: Content to summarize
            
        Returns:
            Summary
        """
        try:
            response = await self.summary_chain.ainvoke({
                "content": content
            })
            
            return response.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error during summarization: {str(e)}"
    
    def get_chain_info(self) -> Dict[str, Any]:
        """Get information about the available chains.
        
        Returns:
            Dictionary with chain information
        """
        return {
            "available_chains": [
                "chat_chain",
                "analysis_chain", 
                "summary_chain"
            ],
            "model": settings.model_name,
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens
        }
