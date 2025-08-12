"""
LangGraph workflow for orchestrating AI assistant operations.
"""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
import asyncio

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from ..core.agent import PersonalAssistant
from ..core.memory import MemoryManager
from ..chains.chat_chain import ChatChain


class AssistantState(TypedDict):
    """State for the assistant workflow."""
    messages: List[BaseMessage]
    user_input: str
    context: str
    response: str
    memory_queries: List[str]
    memory_results: List[tuple]
    workflow_step: str
    error: Optional[str]


class AssistantWorkflow:
    """LangGraph workflow for orchestrating AI assistant operations."""
    
    def __init__(self):
        """Initialize the workflow."""
        self.assistant = PersonalAssistant()
        self.memory_manager = MemoryManager(self.assistant.memory_manager.persist_directory)
        self.chat_chain = ChatChain()
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow.
        
        Returns:
            Configured StateGraph
        """
        # Create the workflow
        workflow = StateGraph(AssistantState)
        
        # Add nodes
        workflow.add_node("input_processor", self._process_input)
        workflow.add_node("memory_retriever", self._retrieve_memory)
        workflow.add_node("context_analyzer", self._analyze_context)
        workflow.add_node("response_generator", self._generate_response)
        workflow.add_node("memory_updater", self._update_memory)
        workflow.add_node("output_formatter", self._format_output)
        
        # Define the workflow edges
        workflow.set_entry_point("input_processor")
        
        workflow.add_edge("input_processor", "memory_retriever")
        workflow.add_edge("memory_retriever", "context_analyzer")
        workflow.add_edge("context_analyzer", "response_generator")
        workflow.add_edge("response_generator", "memory_updater")
        workflow.add_edge("memory_updater", "output_formatter")
        workflow.add_edge("output_formatter", END)
        
        # Compile the workflow
        return workflow.compile()
    
    async def _process_input(self, state: AssistantState) -> AssistantState:
        """Process user input and prepare for workflow.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        try:
            # Extract user input from the last message
            if state["messages"]:
                last_message = state["messages"][-1]
                if isinstance(last_message, HumanMessage):
                    state["user_input"] = last_message.content
            
            # Set workflow step
            state["workflow_step"] = "input_processed"
            
            return state
            
        except Exception as e:
            state["error"] = f"Error processing input: {str(e)}"
            return state
    
    async def _retrieve_memory(self, state: AssistantState) -> AssistantState:
        """Retrieve relevant memories for context.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        try:
            user_input = state["user_input"]
            
            # Search for relevant memories
            memory_results = self.memory_manager.search_memory(
                query=user_input,
                n_results=3
            )
            
            state["memory_results"] = memory_results
            state["workflow_step"] = "memory_retrieved"
            
            return state
            
        except Exception as e:
            state["error"] = f"Error retrieving memory: {str(e)}"
            return state
    
    async def _analyze_context(self, state: AssistantState) -> AssistantState:
        """Analyze context and prepare for response generation.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        try:
            # Format memory context
            memory_context = ""
            if state["memory_results"]:
                memory_context = "Relevant context from memory:\n"
                for content, score, metadata in state["memory_results"]:
                    if score > 0.7:  # Only include highly relevant memories
                        memory_context += f"- {content}\n"
            
            state["context"] = memory_context
            state["workflow_step"] = "context_analyzed"
            
            return state
            
        except Exception as e:
            state["error"] = f"Error analyzing context: {str(e)}"
            return state
    
    async def _generate_response(self, state: AssistantState) -> AssistantState:
        """Generate AI response using the chat chain.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        try:
            user_input = state["user_input"]
            context = state["context"]
            history = state["messages"][:-1] if len(state["messages"]) > 1 else []
            
            # Generate response using chat chain
            response = await self.chat_chain.chat(
                user_input=user_input,
                context=context,
                history=history
            )
            
            state["response"] = response
            state["workflow_step"] = "response_generated"
            
            return state
            
        except Exception as e:
            state["error"] = f"Error generating response: {str(e)}"
            return state
    
    async def _update_memory(self, state: AssistantState) -> AssistantState:
        """Update memory with new information.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        try:
            user_input = state["user_input"]
            response = state["response"]
            
            # Store important information in memory
            memory_content = f"User: {user_input}\nAssistant: {response}"
            
            # Check if this is important information
            important_keywords = [
                "remember", "important", "save", "note", "preference", 
                "like", "dislike", "always", "never", "favorite"
            ]
            
            is_important = any(keyword in user_input.lower() for keyword in important_keywords)
            
            if is_important:
                self.memory_manager.add_memory(
                    content=memory_content,
                    memory_type="important_info",
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "source": "workflow",
                        "workflow_step": state["workflow_step"]
                    }
                )
            
            state["workflow_step"] = "memory_updated"
            return state
            
        except Exception as e:
            state["error"] = f"Error updating memory: {str(e)}"
            return state
    
    async def _format_output(self, state: AssistantState) -> AssistantState:
        """Format the final output.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        try:
            # Add AI response to messages
            ai_message = AIMessage(content=state["response"])
            state["messages"].append(ai_message)
            
            state["workflow_step"] = "output_formatted"
            return state
            
        except Exception as e:
            state["error"] = f"Error formatting output: {str(e)}"
            return state
    
    async def process_message(
        self, 
        user_input: str, 
        messages: List[BaseMessage] = None
    ) -> Dict[str, Any]:
        """Process a user message through the workflow.
        
        Args:
            user_input: User's message
            messages: Previous conversation messages
            
        Returns:
            Workflow result
        """
        try:
            # Prepare initial state
            if messages is None:
                messages = []
            
            # Add user message
            user_message = HumanMessage(content=user_input)
            messages.append(user_message)
            
            initial_state = AssistantState(
                messages=messages,
                user_input=user_input,
                context="",
                response="",
                memory_queries=[],
                memory_results=[],
                workflow_step="started",
                error=None
            )
            
            # Execute workflow
            result = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": True,
                "response": result["response"],
                "workflow_step": result["workflow_step"],
                "memory_results": result["memory_results"],
                "error": result.get("error")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Workflow execution error: {str(e)}",
                "response": "I apologize, but I encountered an error processing your request."
            }
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the workflow.
        
        Returns:
            Workflow information
        """
        return {
            "workflow_name": "AI Assistant Workflow",
            "nodes": [
                "input_processor",
                "memory_retriever", 
                "context_analyzer",
                "response_generator",
                "memory_updater",
                "output_formatter"
            ],
            "description": "Orchestrates AI assistant operations using LangGraph"
        }
    
    async def run_workflow_test(self) -> Dict[str, Any]:
        """Run a test of the workflow.
        
        Returns:
            Test results
        """
        test_input = "Hello, how are you today?"
        test_messages = []
        
        result = await self.process_message(test_input, test_messages)
        
        return {
            "test_input": test_input,
            "result": result,
            "workflow_functional": result["success"]
        }
