# 🤖 AI Personal Assistant

An intelligent, agentic AI personal assistant built with Python, LangChain, and LangGraph, featuring advanced memory management and conversation persistence.

## ✨ Features

### Core Capabilities
- **Intelligent Chat**: Natural language conversations using Groq LLM
- **Long-term Memory**: Persistent memory system using ChromaDB vector database
- **Agentic Workflow**: Multi-step processing using LangGraph orchestration
- **Web Interface**: Beautiful Streamlit-based user interface

### 🧠 Enhanced Memory Features
- **Automatic Conversation Persistence**: Every conversation is automatically saved to long-term memory
- **Smart Context Retrieval**: Intelligent retrieval of relevant past conversations and information
- **Token Optimization**: Context is automatically summarized and optimized to reduce token usage
- **Importance Scoring**: Memories are automatically scored based on content and user indicators
- **Memory Quality Metrics**: Track and analyze memory quality and conversation patterns

### 🔄 Advanced Workflow
- **Multi-step Processing**: Input processing → Memory retrieval → Context analysis → Response generation → Memory updates
- **Context-aware Responses**: Responses are generated with full context from relevant memories
- **Memory Quality Scoring**: Each workflow execution includes memory quality metrics
- **Token-aware Context Management**: Intelligent context selection to optimize token usage

### 💾 Memory Management
- **Vector-based Search**: Semantic search using sentence transformers
- **Importance-based Filtering**: Filter memories by importance score and relevance
- **Automatic Summarization**: Long memories are automatically summarized for context
- **Memory Export/Import**: Full memory system backup and restore capabilities
- **Memory Insights**: Analytics on memory usage and conversation quality

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   LangGraph      │    │   LangChain     │
│                 │    │   Workflow       │    │   Chat Chains   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Agent Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Memory    │  │   Context   │  │      LLM Interface      │ │
│  │  Manager    │  │ Optimizer   │  │      (Groq)             │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  ChromaDB   │  │  Sentence   │  │      Configuration      │ │
│  │   Vector    │  │Transformers │  │      Management         │ │
│  │  Database   │  │ Embeddings  │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### LangGraph Workflow

```
User Input → Input Processor → Memory Retriever → Context Analyzer → Response Generator → Memory Updater → Output Formatter
     │              │                │                │                │                │                │
     │              ▼                ▼                ▼                ▼                ▼                ▼
     │        Process Input    Retrieve Relevant   Analyze Context   Generate AI      Persist          Format
     │        & Prepare        Memories with      & Calculate       Response with    Conversation      Final
     │        Workflow         Importance         Quality Score     Full Context     to Memory        Output
     └─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Groq API key
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd personal_assistant
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Create .env file with your Groq API key
GROQ_API_KEY=your_groq_api_key_here
MEMORY_PERSIST_DIR=./data/memory
```

5. **Run the application**
```bash
# Streamlit web interface
streamlit run streamlit_app_standalone.py

# Command-line interface
python main.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | Required |
| `MEMORY_PERSIST_DIR` | Memory storage directory | `./data/memory` |
| `MEMORY_COLLECTION_NAME` | ChromaDB collection name | `assistant_memories` |
| `MEMORY_EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `MEMORY_SIMILARITY_THRESHOLD` | Minimum similarity score | `0.3` |
| `MEMORY_MAX_RESULTS` | Maximum search results | `10` |
| `LLM_MODEL_NAME` | Groq model name | `llama3-8b-8192` |
| `LLM_TEMPERATURE` | Response creativity | `0.7` |
| `LLM_MAX_TOKENS` | Maximum response length | `4096` |

### Memory Types

- **`conversation`**: User-assistant exchanges (automatically persisted)
- **`important_info`**: Explicitly marked important information
- **`fact`**: General facts and knowledge
- **`preference`**: User preferences and likes/dislikes
- **`task`**: Tasks and action items
- **`other`**: Miscellaneous information

## 📊 Memory System

### Automatic Conversation Persistence
Every conversation is automatically saved to long-term memory with:
- User input and assistant response
- Automatic importance scoring
- Metadata including timestamp and source
- Conversation ID for tracking

### Context Optimization
The system automatically optimizes context retrieval by:
- **Token Management**: Limits context to specified token budget
- **Importance Filtering**: Prioritizes high-importance memories
- **Smart Summarization**: Automatically summarizes long memories
- **Relevance Scoring**: Combines semantic similarity with importance

### Memory Quality Metrics
Track memory system performance with:
- **Importance Scores**: 0.0 (low) to 1.0 (high)
- **Relevance Scores**: Semantic similarity to queries
- **Combined Quality**: Weighted combination of importance and relevance
- **Type Distribution**: Breakdown by memory type
- **Conversation Quality**: Analysis of recent conversations

## 🎯 Usage Examples

### Basic Chat
```python
from src.core.agent import PersonalAssistant

assistant = PersonalAssistant()
response = await assistant.chat("Hello, how are you today?")
print(response)
```

### Memory Management
```python
# Add memory with importance score
memory_id = assistant.add_memory(
    content="User prefers dark mode interfaces",
    memory_type="preference",
    importance_score=0.8
)

# Search memories with importance filtering
results = assistant.search_memories(
    query="interface preferences",
    min_importance=0.6
)

# Get optimized context
context = assistant.get_optimized_context(
    query="user interface",
    max_tokens=500
)
```

### Workflow Processing
```python
from src.graphs.workflow import AssistantWorkflow

workflow = AssistantWorkflow()
result = await workflow.process_message("What did we discuss about AI yesterday?")

print(f"Response: {result['response']}")
print(f"Context tokens: {result['context_tokens']}")
print(f"Memory quality: {result['memory_quality_score']}")
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Test enhanced features
python test_enhanced_features.py

# Run unit tests
pytest tests/

# Test specific components
pytest tests/test_memory.py -v
pytest tests/test_agent.py -v
pytest tests/test_workflow.py -v
```

## 📁 Project Structure

```
personal_assistant/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py          # Enhanced agent with conversation persistence
│   │   ├── memory.py         # Enhanced memory manager with optimization
│   │   └── config.py         # Configuration management
│   ├── chains/
│   │   ├── __init__.py
│   │   └── chat_chain.py     # LangChain chat implementations
│   ├── graphs/
│   │   ├── __init__.py
│   │   └── workflow.py       # Enhanced LangGraph workflow
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py  # Enhanced Streamlit interface
├── tests/                    # Test suite
├── data/                     # Data storage
├── requirements.txt          # Dependencies
├── main.py                   # CLI entry point
├── streamlit_app_standalone.py  # Enhanced standalone Streamlit app
├── test_enhanced_features.py # Feature test script
└── README.md                 # This file
```

## 🔄 Workflow Steps

1. **Input Processor**: Analyzes user input and prepares workflow
2. **Memory Retriever**: Gets optimized context from long-term memory
3. **Context Analyzer**: Evaluates memory quality and relevance
4. **Response Generator**: Creates AI response with full context
5. **Memory Updater**: Persists conversation and important information
6. **Output Formatter**: Formats final response for user

## 📈 Performance Features

- **Token Optimization**: Automatic context summarization to reduce token usage
- **Memory Quality Scoring**: Continuous evaluation of memory relevance and importance
- **Smart Caching**: Efficient memory retrieval with importance-based filtering
- **Context Budgeting**: Intelligent allocation of token budget for context vs. response

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: LLM orchestration framework
- **LangGraph**: Multi-agent workflow orchestration
- **Groq**: Fast LLM inference
- **ChromaDB**: Vector database for memory storage
- **Streamlit**: Web interface framework
- **Sentence Transformers**: Text embedding models

---

**Built with ❤️ using Python, LangChain, and LangGraph**
