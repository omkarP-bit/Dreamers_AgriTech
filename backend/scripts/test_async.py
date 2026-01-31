"""
Farm AI - Async Agent Testing Suite

Tests the orchestrator with real Groq API calls
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from agents.orchestrator import create_orchestrator


def print_header():
    """Print test suite header"""
    print("\n" + "    ╔══════════════════════════════════════════════════════════════════╗")
    print("    ║                                                                  ║")
    print("    ║       🌾 FARM AI - Async Agent Testing Suite 🌾                  ║")
    print("    ║                                                                  ║")
    print("    ║  Real LLM calls via Groq + RoundRobinGroupChat                  ║")
    print("    ║                                                                  ║")
    print("    ╚══════════════════════════════════════════════════════════════════╝\n")


async def test_pre_sowing_conversation():
    """Test a complete pre-sowing conversation"""
    print("\n" + "="*70)
    print("           🌾 PRE-SOWING CONVERSATION TEST")
    print("="*70 + "\n")
    
    print("✓ Creating orchestrator...")
    orch = create_orchestrator(season_id=1, phase="pre_sowing", farmer_type="traditional")
    
    # Test messages
    messages = [
        "Hello! I want to grow crops in Punjab. My soil is loamy.",
        "What are my best options for the upcoming season?",
        "I'll choose wheat. What should I do next?",
        "When should I start planting?"
    ]
    
    print("\n✓ Orchestrator ready! Starting conversation...\n")
    print("="*70 + "\n")
    
    for i, msg in enumerate(messages, 1):
        print(f"👨‍🌾 Farmer (Message {i}/{len(messages)}): {msg}")
        print("⏳ Processing...\n")
        
        try:
            # CRITICAL: Await the async function!
            result = await orch.process_message(msg)
            
            if result["success"]:
                print(f"✅ Response received!")
                print(f"\n📝 Final Response:\n{result['final_response']}\n")
                
                if result["agent_debate"]:
                    print(f"🤖 Active Agents: {', '.join(result['active_agents'])}")
                    print(f"💬 Total responses: {len(result['agent_debate'])}\n")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}\n")
                break
            
            print("-"*70 + "\n")
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("\n" + "="*70)
    print("           ✅ CONVERSATION TEST COMPLETE")
    print("="*70 + "\n")


async def interactive_mode():
    """Interactive chat with agents"""
    print("\n" + "="*70)
    print("                     🌾 FARM AI - Interactive Mode")
    print("="*70 + "\n")
    
    print("✓ Creating orchestrator...")
    orch = create_orchestrator(season_id=1, phase="pre_sowing", farmer_type="traditional")
    
    print("✓ Orchestrator ready!")
    print("Type your messages. Type 'quit' to exit.\n")
    
    while True:
        try:
            # Get user input
            user_input = input("👨‍🌾 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n✓ Goodbye!\n")
                break
            
            # Process message
            print("⏳ Processing...\n")
            
            # CRITICAL: Await the async function!
            result = await orch.process_message(user_input)
            
            if result["success"]:
                print(f"🤖 AI: {result['final_response']}\n")
                
                if result["agent_debate"]:
                    print(f"   (Agents consulted: {', '.join(result['active_agents'])})\n")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}\n")
            
        except KeyboardInterrupt:
            print("\n\n✓ Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")
            import traceback
            traceback.print_exc()


async def main_menu():
    """Main menu for test suite"""
    while True:
        print("📋 Choose an option:")
        print("  1. Run pre-sowing conversation test (4 messages)")
        print("  2. Interactive mode (chat with agents)")
        print("  3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            await test_pre_sowing_conversation()
            input("\n⏸️  Press Enter to continue...")
        elif choice == "2":
            await interactive_mode()
            input("\n⏸️  Press Enter to continue...")
        elif choice == "3":
            print("\n✓ Goodbye!\n")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.\n")


def main():
    """Entry point"""
    print_header()
    
    try:
        # Run async main menu
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()