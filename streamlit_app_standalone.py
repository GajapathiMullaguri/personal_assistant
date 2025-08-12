"""
Standalone Streamlit web interface for the AI personal assistant.
Enhanced with conversation persistence and context optimization features.
"""

import asyncio
import streamlit as st
from pathlib import Path
from datetime import datetime
import json
import sys
import os

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import the modules
from src.core.agent import PersonalAssistant
from src.core.memory import MemoryManager
from src.graphs.workflow import AssistantWorkflow
from src.core.config import settings


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "assistant" not in st.session_state:
        st.session_state.assistant = None
    
    if "workflow" not in st.session_state:
        st.session_state.workflow = None
    
    if "memory_manager" not in st.session_state:
        st.session_state.memory_manager = None
    
    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = "simple"  # "simple" or "workflow"
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(datetime.now().strftime("%Y%m%d_%H%M%S"))


def initialize_assistant():
    """Initialize the AI assistant components."""
    try:
        if st.session_state.assistant is None:
            st.session_state.assistant = PersonalAssistant()
        
        if st.session_state.workflow is None:
            st.session_state.workflow = AssistantWorkflow()
        
        if st.session_state.memory_manager is None:
            st.session_state.memory_manager = MemoryManager(settings.memory_persist_dir)
        
        return True
    except Exception as e:
        st.error(f"Error initializing assistant: {str(e)}")
        return False


def display_header():
    """Display the application header."""
    st.set_page_config(
        page_title="AI Personal Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 AI Personal Assistant")
    st.markdown("**Your intelligent companion with long-term memory and conversation persistence**")
    
    # Display model info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Model", settings.model_name)
    with col2:
        st.metric("Temperature", settings.temperature)
    with col3:
        st.metric("Max Tokens", settings.max_tokens)


def display_sidebar():
    """Display the sidebar with controls and information."""
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Chat mode selection
        chat_mode = st.selectbox(
            "Chat Mode",
            ["Simple", "Workflow"],
            index=0 if st.session_state.chat_mode == "simple" else 1
        )
        st.session_state.chat_mode = chat_mode.lower()
        
        st.divider()
        
        # Memory controls
        st.subheader("🧠 Memory Management")
        
        if st.button("View Memory Stats"):
            display_memory_stats()
        
        if st.button("View Memory Insights"):
            display_memory_insights()
        
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            if st.session_state.assistant:
                st.session_state.assistant.clear_conversation_memory()
            st.rerun()
        
        if st.button("Export Memories"):
            export_memories()
        
        st.divider()
        
        # System information
        st.subheader("ℹ️ System Info")
        st.info(f"Memory Directory: {settings.memory_persist_dir}")
        st.info(f"Debug Mode: {settings.debug}")
        st.info(f"Conversation ID: {st.session_state.conversation_id}")
        
        # Workflow information
        if st.session_state.workflow:
            st.subheader("🔄 Workflow Info")
            workflow_info = st.session_state.workflow.get_workflow_info()
            st.json(workflow_info)


def display_memory_stats():
    """Display memory statistics."""
    if st.session_state.memory_manager:
        stats = st.session_state.memory_manager.get_memory_stats()
        
        st.subheader("Memory Statistics")
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Memories", stats.get("total_memories", 0))
        with col2:
            st.metric("Avg Importance", f"{stats.get('average_importance_score', 0):.2f}")
        with col3:
            importance_range = stats.get("importance_score_range", {})
            st.metric("Importance Range", f"{importance_range.get('min', 0):.1f} - {importance_range.get('max', 0):.1f}")
        
        # Display type distribution
        if "type_distribution" in stats:
            st.subheader("Memory Type Distribution")
            type_data = stats["type_distribution"]
            if type_data:
                for mem_type, count in type_data.items():
                    st.write(f"**{mem_type.title()}**: {count}")
        
        # Display full stats
        with st.expander("Full Memory Statistics"):
            st.json(stats)


def display_memory_insights():
    """Display memory insights and conversation patterns."""
    if st.session_state.assistant:
        insights = st.session_state.assistant.get_memory_insights()
        
        st.subheader("Memory Insights")
        
        # Display conversation quality metrics
        if "conversation_quality" in insights:
            quality = insights["conversation_quality"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High Importance", quality.get("high_importance", 0))
            with col2:
                st.metric("Medium Importance", quality.get("medium_importance", 0))
            with col3:
                st.metric("Low Importance", quality.get("low_importance", 0))
        
        # Display recent conversations count
        if "recent_conversations" in insights:
            st.metric("Recent Conversations", insights.get("recent_conversations", 0))
        
        # Display full insights
        with st.expander("Full Memory Insights"):
            st.json(insights)


def export_memories():
    """Export memories to a file."""
    if st.session_state.memory_manager:
        export_path = Path("./data") / f"memories_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if st.session_state.memory_manager.export_memories(export_path):
            st.success(f"Memories exported to: {export_path}")
        else:
            st.error("Failed to export memories")


def display_chat_interface():
    """Display the main chat interface."""
    st.subheader("💬 Chat Interface")
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Process message based on chat mode
        if st.session_state.chat_mode == "workflow":
            response = process_message_with_workflow(user_input)
        else:
            response = process_message_simple(user_input)
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update the display
        st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_message_simple(user_input: str) -> str:
    """Process message using simple chat mode."""
    try:
        if st.session_state.assistant:
            # Use asyncio to run the async chat method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    st.session_state.assistant.chat(user_input)
                )
                return response
            finally:
                loop.close()
        else:
            return "Assistant not initialized. Please check the configuration."
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"


def process_message_with_workflow(user_input: str) -> str:
    """Process message using workflow mode."""
    try:
        if st.session_state.workflow:
            # Convert messages to LangChain format
            from langchain_core.messages import HumanMessage, AIMessage
            
            lc_messages = []
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))
            
            # Use asyncio to run the async workflow
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    st.session_state.workflow.process_message(user_input, lc_messages)
                )
                
                if result["success"]:
                    # Display workflow insights
                    if "context_tokens" in result and "memory_quality_score" in result:
                        st.sidebar.success(f"Context: ~{result['context_tokens']} tokens | Quality: {result['memory_quality_score']:.2f}")
                    
                    return result["response"]
                else:
                    return f"Workflow error: {result.get('error', 'Unknown error')}"
            finally:
                loop.close()
        else:
            return "Workflow not initialized. Please check the configuration."
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"


def display_memory_search():
    """Display memory search interface."""
    st.subheader("🔍 Memory Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("Search memories", key="memory_search")
    
    with col2:
        search_button = st.button("Search", key="search_btn")
    
    if search_button and search_query and st.session_state.memory_manager:
        # Search with importance filtering
        results = st.session_state.memory_manager.search_memory(
            query=search_query,
            n_results=5,
            min_importance=0.3  # Only show moderately important memories
        )
        
        if results:
            st.subheader("Search Results")
            for i, (content, score, metadata) in enumerate(results):
                importance = metadata.get('importance_score', 0.5)
                memory_type = metadata.get('type', 'memory')
                
                with st.expander(f"Result {i+1} (Score: {score:.2f}, Importance: {importance:.2f}, Type: {memory_type})"):
                    st.write(f"**Content:** {content}")
                    st.write(f"**Metadata:** {metadata}")
        else:
            st.info("No memories found matching your search.")
    
    # Show optimized context preview
    if search_query and st.session_state.memory_manager:
        st.subheader("📊 Optimized Context Preview")
        optimized_context = st.session_state.memory_manager.get_optimized_context(
            query=search_query,
            max_tokens=300,
            n_results=3,
            include_summaries=True
        )
        
        if optimized_context:
            st.info("**Preview of how this query would be contextualized:**")
            st.text(optimized_context)
        else:
            st.info("No relevant context found for this query.")


def display_add_memory():
    """Display interface for adding new memories."""
    st.subheader("➕ Add Memory")
    
    with st.form("add_memory_form"):
        memory_content = st.text_area("Memory content", height=100)
        memory_type = st.selectbox(
            "Memory type",
            ["conversation", "fact", "preference", "task", "important_info", "other"]
        )
        importance_score = st.slider(
            "Importance score",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.1,
            help="0.0 = Low importance, 1.0 = High importance"
        )
        metadata = st.text_input("Additional metadata (JSON format)", value="{}")
        
        submitted = st.form_submit_button("Add Memory")
        
        if submitted and memory_content and st.session_state.memory_manager:
            try:
                # Parse metadata
                metadata_dict = json.loads(metadata) if metadata else {}
                
                # Add memory with importance score
                memory_id = st.session_state.memory_manager.add_memory(
                    content=memory_content,
                    memory_type=memory_type,
                    metadata=metadata_dict,
                    importance_score=importance_score
                )
                
                st.success(f"Memory added successfully! ID: {memory_id}")
                
            except json.JSONDecodeError:
                st.error("Invalid JSON format for metadata")
            except Exception as e:
                st.error(f"Error adding memory: {str(e)}")


def display_conversation_analysis():
    """Display conversation analysis and insights."""
    st.subheader("📈 Conversation Analysis")
    
    if st.session_state.messages:
        # Analyze current conversation
        user_messages = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
        assistant_messages = [msg["content"] for msg in st.session_state.messages if msg["role"] == "assistant"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Messages", len(st.session_state.messages))
        with col2:
            st.metric("User Messages", len(user_messages))
        with col3:
            st.metric("Assistant Responses", len(assistant_messages))
        
        # Show conversation flow
        st.subheader("Conversation Flow")
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.write(f"👤 **User {i//2 + 1}:** {msg['content']}")
            else:
                st.write(f"🤖 **Assistant {i//2 + 1}:** {msg['content']}")
            if i < len(st.session_state.messages) - 1:
                st.divider()
    else:
        st.info("No conversation history available. Start chatting to see analysis!")


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Initialize assistant
    if not initialize_assistant():
        st.error("Failed to initialize the AI assistant. Please check your configuration.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Chat", 
        "🔍 Memory Search", 
        "➕ Add Memory",
        "📈 Analysis",
        "⚙️ Settings"
    ])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_memory_search()
    
    with tab3:
        display_add_memory()
    
    with tab4:
        display_conversation_analysis()
    
    with tab5:
        st.subheader("⚙️ Configuration Settings")
        st.json({
            "model_name": settings.model_name,
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens,
            "memory_persist_dir": str(settings.memory_persist_dir),
            "memory_collection_name": settings.memory_collection_name,
            "memory_embedding_model": settings.memory_embedding_model,
            "memory_similarity_threshold": settings.memory_similarity_threshold,
            "memory_max_results": settings.memory_max_results
        })
    
    # Display sidebar
    display_sidebar()


if __name__ == "__main__":
    main()
