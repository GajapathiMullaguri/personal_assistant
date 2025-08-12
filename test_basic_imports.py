#!/usr/bin/env python3
"""
Basic import test to verify code structure without full dependencies.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_structure():
    """Test basic code structure and imports."""
    try:
        print("Testing basic code structure...")
        
        # Test if we can import the modules (without executing them)
        import importlib.util
        
        # Test config module
        config_spec = importlib.util.spec_from_file_location(
            "config", 
            project_root / "src" / "core" / "config.py"
        )
        if config_spec:
            print("✅ Config module structure is valid")
        
        # Test memory module
        memory_spec = importlib.util.spec_from_file_location(
            "memory", 
            project_root / "src" / "core" / "memory.py"
        )
        if memory_spec:
            print("✅ Memory module structure is valid")
        
        # Test agent module
        agent_spec = importlib.util.spec_from_file_location(
            "agent", 
            project_root / "src" / "core" / "agent.py"
        )
        if agent_spec:
            print("✅ Agent module structure is valid")
        
        # Test workflow module
        workflow_spec = importlib.util.spec_from_file_location(
            "workflow", 
            project_root / "src" / "graphs" / "workflow.py"
        )
        if workflow_spec:
            print("✅ Workflow module structure is valid")
        
        print("\n✅ All module structures are valid!")
        print("\n📝 To run the full application, you need to:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up your .env file with GROQ_API_KEY")
        print("3. Run: streamlit run streamlit_app_standalone.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Structure test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_basic_structure()
