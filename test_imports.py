#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all the main imports."""
    try:
        print("Testing imports...")
        
        # Test core imports
        from src.core.config import settings
        print("✅ Core config imported successfully")
        
        from src.core.memory import MemoryManager
        print("✅ Memory manager imported successfully")
        
        from src.core.agent import PersonalAssistant
        print("✅ Agent imported successfully")
        
        # Test chains imports
        from src.chains.chat_chain import ChatChain
        print("✅ Chat chain imported successfully")
        
        # Test workflow imports
        from src.graphs.workflow import AssistantWorkflow
        print("✅ Workflow imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
