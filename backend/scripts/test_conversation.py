"""
Minimal Agent Test Script

Tests the agents directly without MongoDB complications
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import create_orchestrator


def main():
    print("\n" + "="*70)
    print("🌾 FARM AI - Minimal Agent Test".center(70))
    print("="*70 + "\n")
    
    try:
        print("✓ Creating orchestrator...")
        orchestrator = create_orchestrator(
            season_id=1,
            phase="pre_sowing",
            farmer_type="traditional"
        )
        print("✓ Orchestrator created successfully!")
        
        print("\n✓ Agent Info:")
        agents_info = orchestrator.get_agents_info()
        for agent_name, info in agents_info.items():
            if isinstance(info, dict) and "name" in info:
                print(f"  - {info['name']}: {info.get('role', 'N/A')}")
        
        print("\n" + "="*70)
        print("Interactive Mode - Type messages to chat with agents".center(70))
        print("Type 'quit' to exit".center(70))
        print("="*70 + "\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n📤 Processing message...")
            response = orchestrator.process_message(user_input)
            
            print(f"\n🤖 Agent Response:")
            print(response.get('final_response', 'No response'))
            print()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()