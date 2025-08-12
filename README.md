# Agentic AI Personal Assistant

A sophisticated AI personal assistant built with Python, LangChain, and LangGraph, featuring long-term memory and a modern Streamlit interface.

## 🏗️ Project Architecture

```
personal_assistant/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py          # Main agent implementation
│   │   ├── memory.py         # Long-term memory system
│   │   └── config.py         # Configuration management
│   ├── chains/
│   │   ├── __init__.py
│   │   └── chat_chain.py     # LangChain chat implementation
│   ├── graphs/
│   │   ├── __init__.py
│   │   └── workflow.py       # LangGraph workflow definitions
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py  # Streamlit interface
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_memory.py
│   └── test_chat_chain.py
├── data/
│   └── memory/               # Memory storage directory
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py                   # Application entry point
└── README.md
```

## 🧠 LangGraph Architecture

Our assistant uses LangGraph to create a sophisticated workflow that orchestrates multiple AI agents and tools:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  Input Router   │───▶│  Memory Agent   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Chat Agent     │    │  Memory Store   │
                       │  (Groq LLM)     │    │  (Vector DB)    │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Response      │    │  Memory Update  │
                       │  Generator     │    │  & Storage      │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  User Output   │
                       └─────────────────┘
```

## 🚀 Features

- **Intelligent Chat Interface**: Powered by Groq's fast LLM inference
- **Long-term Memory**: Persistent memory using vector databases
- **Agentic Workflows**: LangGraph-powered multi-agent orchestration
- **Modern UI**: Clean Streamlit interface with real-time chat
- **Modular Architecture**: Easy to extend and customize

## 🛠️ Technology Stack

- **Python 3.9+**
- **LangChain**: LLM orchestration and chains
- **LangGraph**: Multi-agent workflow management
- **Groq**: Fast LLM inference
- **Streamlit**: Web interface
- **ChromaDB**: Vector database for memory
- **Pydantic**: Data validation and settings

## 📦 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd personal_assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Groq API key
```

## 🔑 Configuration

Create a `.env` file with the following variables:
```env
GROQ_API_KEY=your_groq_api_key_here
MEMORY_PERSIST_DIR=./data/memory
```

## 🚀 Usage

### Running the Streamlit App
```bash
streamlit run src/ui/streamlit_app.py
```

### Running from Command Line
```bash
python main.py
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

## 📁 Project Structure Details

- **`src/core/`**: Core agent logic and memory management
- **`src/chains/`**: LangChain implementations for chat and reasoning
- **`src/graphs/`**: LangGraph workflow definitions and state management
- **`src/ui/`**: Streamlit interface components
- **`tests/`**: Comprehensive test suite
- **`data/`**: Persistent storage for memory and user data

## 🔄 Workflow

1. **Input Processing**: User input is received and routed to appropriate agents
2. **Memory Retrieval**: Relevant context is retrieved from long-term memory
3. **LLM Processing**: Groq LLM processes the input with context
4. **Response Generation**: Intelligent response is generated and formatted
5. **Memory Update**: New information is stored in long-term memory
6. **Output Delivery**: Response is delivered to the user interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangChain team for the amazing framework
- LangGraph for workflow orchestration
- Groq for fast LLM inference
- Streamlit for the beautiful UI framework
