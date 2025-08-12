"""
Streamlit web interface for the AI personal assistant.
"""

import asyncio
import streamlit as st
from pathlib import Path
from datetime import datetime
import json

from ..core.agent import PersonalAssistant
from ..core.memory import MemoryManager
from ..graphs.workflow import AssistantWorkflow
from ..core.config import settings


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
    st.markdown("**Your intelligent companion with long-term memory**")
    
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
        st.json(stats)


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
    """Process message using simple chat mode.
    
    Args:
        user_input: User's message
        
    Returns:
        Assistant's response
    """
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
    """Process message using workflow mode.
    
    Args:
        user_input: User's message
        
    Returns:
        Assistant's response
    """
    try:
        if st.session_state.workflow:
            # Convert messages to LangChain format
            from langchain.schema import HumanMessage, AIMessage
            
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
        results = st.session_state.memory_manager.search_memory(
            query=search_query,
            n_results=5
        )
        
        if results:
            st.subheader("Search Results")
            for i, (content, score, metadata) in enumerate(results):
                with st.expander(f"Result {i+1} (Score: {score:.2f})"):
                    st.write(f"**Content:** {content}")
                    st.write(f"**Metadata:** {metadata}")
        else:
            st.info("No memories found matching your search.")


def display_add_memory():
    """Display interface for adding new memories."""
    st.subheader("➕ Add Memory")
    
    with st.form("add_memory_form"):
        memory_content = st.text_area("Memory content", height=100)
        memory_type = st.selectbox(
            "Memory type",
            ["conversation", "fact", "preference", "task", "other"]
        )
        metadata = st.text_input("Additional metadata (JSON format)", value="{}")
        
        submitted = st.form_submit_button("Add Memory")
        
        if submitted and memory_content and st.session_state.memory_manager:
            try:
                # Parse metadata
                metadata_dict = json.loads(metadata) if metadata else {}
                
                # Add memory
                memory_id = st.session_state.memory_manager.add_memory(
                    content=memory_content,
                    memory_type=memory_type,
                    metadata=metadata_dict
                )
                
                st.success(f"Memory added successfully! ID: {memory_id}")
                
            except json.JSONDecodeError:
                st.error("Invalid JSON format for metadata")
            except Exception as e:
                st.error(f"Error adding memory: {str(e)}")


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
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔍 Memory Search", "➕ Add Memory"])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_memory_search()
    
    with tab3:
        display_add_memory()
    
    # Display sidebar
    display_sidebar()


if __name__ == "__main__":
    main()
