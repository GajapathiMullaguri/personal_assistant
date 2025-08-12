#!/usr/bin/env python3
"""
Test script to verify the enhanced features work correctly.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_features():
    """Test the enhanced memory and context features."""
    try:
        print("Testing enhanced features...")
        
        # Test core imports
        from src.core.config import settings
        print("✅ Core config imported successfully")
        
        from src.core.memory import MemoryManager
        print("✅ Enhanced memory manager imported successfully")
        
        from src.core.agent import PersonalAssistant
        print("✅ Enhanced agent imported successfully")
        
        # Test memory manager features
        memory_manager = MemoryManager(Path("./data/memory"))
        print("✅ Memory manager initialized successfully")
        
        # Test adding memory with importance score
        memory_id = memory_manager.add_memory(
            content="This is a test memory with high importance",
            memory_type="test",
            importance_score=0.9
        )
        print(f"✅ Added memory with importance score: {memory_id}")
        
        # Test conversation memory
        conv_id = memory_manager.add_conversation_memory(
            user_input="What is the weather like?",
            assistant_response="I don't have access to real-time weather information.",
            metadata={"test": True}
        )
        print(f"✅ Added conversation memory: {conv_id}")
        
        # Test optimized context retrieval
        context = memory_manager.get_optimized_context(
            query="weather",
            max_tokens=200,
            n_results=3,
            include_summaries=True
        )
        print(f"✅ Optimized context retrieved: {len(context)} characters")
        
        # Test search with importance filtering
        results = memory_manager.search_memory(
            query="test",
            n_results=5,
            min_importance=0.5
        )
        print(f"✅ Search with importance filtering: {len(results)} results")
        
        # Test memory stats
        stats = memory_manager.get_memory_stats()
        print(f"✅ Memory stats retrieved: {stats.get('total_memories', 0)} total memories")
        
        print("\n🎉 All enhanced features working!")
        return True
        
    except Exception as e:
        print(f"❌ Feature test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_features()
