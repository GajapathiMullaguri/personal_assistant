"""
LangGraph workflow for orchestrating AI assistant operations.
Enhanced with optimized context retrieval and conversation persistence.
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
    context_tokens: int
    memory_quality_score: float


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
        """Retrieve relevant memories for context using optimized retrieval.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        try:
            user_input = state["user_input"]
            
            # Use optimized context retrieval
            optimized_context = self.memory_manager.get_optimized_context(
                query=user_input,
                max_tokens=600,  # Reserve tokens for conversation and response
                n_results=6,     # Get more memories for better context
                include_summaries=True
            )
            
            # Get raw memory results for analysis
            memory_results = self.memory_manager.search_memory(
                query=user_input,
                n_results=8,
                min_importance=0.3  # Include moderately important memories
            )
            
            state["context"] = optimized_context
            state["memory_results"] = memory_results
            state["context_tokens"] = len(optimized_context) // 4  # Rough token estimation
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
            # Calculate memory quality score based on relevance and importance
            memory_results = state["memory_results"]
            if memory_results:
                # Calculate average relevance and importance scores
                relevance_scores = [score for _, score, _ in memory_results]
                importance_scores = [meta.get('importance_score', 0.5) for _, _, meta in memory_results]
                
                avg_relevance = sum(relevance_scores) / len(relevance_scores)
                avg_importance = sum(importance_scores) / len(importance_scores)
                
                # Combined quality score (70% relevance, 30% importance)
                memory_quality_score = (avg_relevance * 0.7) + (avg_importance * 0.3)
            else:
                memory_quality_score = 0.0
            
            state["memory_quality_score"] = round(memory_quality_score, 2)
            state["workflow_step"] = "context_analyzed"
            
            return state
            
        except Exception as e:
            state["error"] = f"Error analyzing context: {str(e)}"
            return state
    
    async def _generate_response(self, state: AssistantState) -> AssistantState:
        """Generate AI response using the chat chain with optimized context.
        
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
        """Update memory with new information and persist conversation.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        try:
            user_input = state["user_input"]
            response = state["response"]
            
            # Automatically persist conversation to long-term memory
            self.memory_manager.add_conversation_memory(
                user_input=user_input,
                assistant_response=response,
                metadata={
                    "source": "workflow",
                    "workflow_step": state["workflow_step"],
                    "memory_quality_score": state["memory_quality_score"],
                    "context_tokens": state["context_tokens"]
                }
            )
            
            # Store important information in memory (if not already done)
            important_keywords = [
                "remember", "important", "save", "note", "preference", 
                "like", "dislike", "always", "never", "favorite",
                "critical", "essential", "key", "vital", "crucial"
            ]
            
            is_important = any(keyword in user_input.lower() for keyword in important_keywords)
            
            if is_important:
                memory_content = f"User: {user_input}\nAssistant: {response}"
                self.memory_manager.add_memory(
                    content=memory_content,
                    memory_type="important_info",
                    importance_score=0.9,  # High importance for explicitly marked content
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "source": "workflow",
                        "workflow_step": state["workflow_step"],
                        "explicitly_important": True
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
                error=None,
                context_tokens=0,
                memory_quality_score=0.0
            )
            
            # Execute workflow
            result = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": True,
                "response": result["response"],
                "workflow_step": result["workflow_step"],
                "memory_results": result["memory_results"],
                "context_tokens": result["context_tokens"],
                "memory_quality_score": result["memory_quality_score"],
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
            "description": "Orchestrates AI assistant operations using LangGraph with optimized context retrieval",
            "features": [
                "Automatic conversation persistence",
                "Optimized context retrieval",
                "Memory quality scoring",
                "Token-aware context management",
                "Importance-based memory prioritization"
            ]
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
    
    def get_memory_insights(self) -> Dict[str, Any]:
        """Get insights about memory usage and workflow performance.
        
        Returns:
            Memory insights
        """
        return self.assistant.get_memory_insights()
