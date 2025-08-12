"""
Main entry point for the AI Personal Assistant.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.agent import PersonalAssistant
from src.core.memory import MemoryManager
from src.graphs.workflow import AssistantWorkflow
from src.core.config import settings


async def main():
    """Main application function."""
    print("🤖 AI Personal Assistant")
    print("=" * 50)
    
    try:
        # Initialize components
        print("Initializing AI Assistant...")
        assistant = PersonalAssistant()
        
        print("Initializing Memory Manager...")
        memory_manager = MemoryManager(settings.memory_persist_dir)
        
        print("Initializing Workflow...")
        workflow = AssistantWorkflow()
        
        print("✅ All components initialized successfully!")
        print(f"📁 Memory directory: {settings.memory_persist_dir}")
        print(f"🤖 Model: {settings.model_name}")
        print(f"🌡️ Temperature: {settings.temperature}")
        
        # Test the workflow
        print("\n🧪 Testing workflow...")
        test_result = await workflow.run_workflow_test()
        
        if test_result["workflow_functional"]:
            print("✅ Workflow test passed!")
        else:
            print("❌ Workflow test failed!")
            print(f"Error: {test_result['result'].get('error', 'Unknown error')}")
        
        # Interactive chat loop
        print("\n💬 Starting interactive chat...")
        print("Type 'quit' to exit, 'memory' to view memory stats, 'help' for commands")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'memory':
                    stats = memory_manager.get_memory_stats()
                    print(f"🧠 Memory Stats: {stats}")
                elif user_input.lower() == 'help':
                    print("Available commands:")
                    print("- 'quit': Exit the application")
                    print("- 'memory': View memory statistics")
                    print("- 'help': Show this help message")
                    print("- Any other text: Chat with the AI assistant")
                elif user_input:
                    print("🤖 Assistant: ", end="", flush=True)
                    
                    # Process message using workflow
                    result = await workflow.process_message(user_input)
                    
                    if result["success"]:
                        print(result["response"])
                    else:
                        print(f"Error: {result.get('error', 'Unknown error')}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    except Exception as e:
        print(f"❌ Failed to initialize application: {str(e)}")
        print("Please check your configuration and ensure all dependencies are installed.")
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)
