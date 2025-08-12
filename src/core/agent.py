"""
Main personal assistant agent implementation.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncGenerator
from pathlib import Path

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

from .memory import MemoryManager
from .config import settings


class PersonalAssistant:
    """Main personal assistant agent with memory and chat capabilities."""
    
    def __init__(self):
        """Initialize the personal assistant."""
        # Initialize Groq LLM
        self.llm = ChatGroq(
            groq_api_key=settings.groq_api_key,
            model_name=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(settings.memory_persist_dir)
        
        # Initialize conversation memory
        self.conversation_memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 messages in conversation
            return_messages=True
        )
        
        # System prompt
        self.system_prompt = """You are an intelligent and helpful personal AI assistant. 
        You have access to long-term memory and can remember past conversations and important information.
        
        Your capabilities include:
        - Engaging in natural conversations
        - Remembering important information from past interactions
        - Providing helpful and accurate responses
        - Learning from user preferences and patterns
        
        Always be helpful, friendly, and professional. Use the context from memory when relevant to provide more personalized responses.
        
        {memory_context}
        """
        
        # Initialize prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
    
    async def chat(
        self, 
        user_input: str, 
        user_id: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Process a chat message from the user.
        
        Args:
            user_input: The user's message
            user_id: Optional user identifier for personalization
            stream: Whether to stream the response
            
        Returns:
            The assistant's response
        """
        # Get relevant memories
        relevant_memories = self.memory_manager.search_memory(
            query=user_input,
            n_results=3,
            filter_metadata={"user_id": user_id} if user_id else None
        )
        
        # Format memory context
        memory_context = ""
        if relevant_memories:
            memory_context = "\n\nRelevant context from memory:\n"
            for content, score, metadata in relevant_memories:
                if score > 0.7:  # Only include highly relevant memories
                    memory_context += f"- {content}\n"
        
        # Get conversation history
        chat_history = self.conversation_memory.chat_memory.messages
        
        # Prepare prompt variables
        prompt_vars = {
            "input": user_input,
            "chat_history": chat_history,
            "memory_context": memory_context
        }
        
        # Generate response
        if stream:
            return self._stream_response(prompt_vars)
        else:
            return await self._generate_response(prompt_vars)
    
    async def _generate_response(self, prompt_vars: Dict[str, Any]) -> str:
        """Generate a response using the LLM.
        
        Args:
            prompt_vars: Variables for the prompt template
            
        Returns:
            Generated response
        """
        try:
            # Format messages
            messages = self.prompt_template.format_messages(**prompt_vars)
            
            # Generate response
            response = await self.llm.ainvoke(messages)
            response_content = response.content
            
            # Store in conversation memory
            self.conversation_memory.chat_memory.add_user_message(prompt_vars["input"])
            self.conversation_memory.chat_memory.add_ai_message(response_content)
            
            # Store important information in long-term memory
            await self._store_important_info(prompt_vars["input"], response_content)
            
            return response_content
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            return error_msg
    
    def _stream_response(self, prompt_vars: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Stream a response from the LLM.
        
        Args:
            prompt_vars: Variables for the prompt template
            
        Yields:
            Response chunks
        """
        try:
            # Format messages
            messages = self.prompt_template.format_messages(**prompt_vars)
            
            # Stream response
            for chunk in self.llm.stream(messages):
                if chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            yield f"I apologize, but I encountered an error: {str(e)}"
    
    async def _store_important_info(self, user_input: str, response: str):
        """Store important information from the conversation in long-term memory.
        
        Args:
            user_input: The user's input
            response: The assistant's response
        """
        # Simple heuristic to determine if information is worth storing
        important_keywords = [
            "remember", "important", "save", "note", "preference", 
            "like", "dislike", "always", "never", "favorite"
        ]
        
        is_important = any(keyword in user_input.lower() for keyword in important_keywords)
        
        if is_important:
            # Store the important information
            memory_content = f"User: {user_input}\nAssistant: {response}"
            self.memory_manager.add_memory(
                content=memory_content,
                memory_type="important_info",
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "source": "conversation"
                }
            )
    
    def add_memory(
        self, 
        content: str, 
        memory_type: str = "user_input",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add information to long-term memory.
        
        Args:
            content: Content to remember
            memory_type: Type of memory
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        return self.memory_manager.add_memory(
            content=content,
            memory_type=memory_type,
            metadata=metadata
        )
    
    def search_memories(
        self, 
        query: str, 
        n_results: int = 5,
        memory_type: Optional[str] = None
    ) -> List[tuple]:
        """Search for relevant memories.
        
        Args:
            query: Search query
            n_results: Number of results to return
            memory_type: Filter by memory type
            
        Returns:
            List of (content, similarity_score, metadata) tuples
        """
        return self.memory_manager.search_memory(
            query=query,
            n_results=n_results,
            memory_type=memory_type
        )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system.
        
        Returns:
            Memory statistics
        """
        return self.memory_manager.get_memory_stats()
    
    def clear_conversation_memory(self):
        """Clear the current conversation memory."""
        self.conversation_memory.clear()
    
    def export_memories(self, filepath: Path) -> bool:
        """Export all memories to a file.
        
        Args:
            filepath: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        return self.memory_manager.export_memories(filepath)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation.
        
        Returns:
            Conversation summary
        """
        messages = self.conversation_memory.chat_memory.messages
        
        if not messages:
            return "No conversation history available."
        
        # Create a simple summary
        user_messages = [msg.content for msg in messages if isinstance(msg, HumanMessage)]
        ai_messages = [msg.content for msg in messages if isinstance(msg, AIMessage)]
        
        summary = f"Conversation Summary:\n"
        summary += f"- User messages: {len(user_messages)}\n"
        summary += f"- Assistant responses: {len(ai_messages)}\n"
        
        if user_messages:
            summary += f"- Last user message: {user_messages[-1][:100]}...\n"
        
        return summary
