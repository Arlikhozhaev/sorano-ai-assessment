"""
Part 2: AI Chat Tools - Enhanced Interactive Version
Author: Abdu Alim Arlikhozhaev
Date: February 2026

This is an enhanced version with interactive CLI mode and additional features.
Run this for a more interactive demonstration of capabilities.
"""

import os
import sys
from dotenv import load_dotenv
from part2_ai_chat_tools import AIAssistant

def print_header():
    """Print welcome header."""
    print("\n" + "="*70)
    print("   🤖 SORANO AI - INTERACTIVE CHAT ASSISTANT   ")
    print("="*70)
    print("\nWelcome! I'm an AI assistant with access to several tools:")
    print("  🌤️  Weather Information")
    print("  🔢 Mathematical Calculator")
    print("  📊 Database Queries")
    print("\nType 'help' for examples, 'reset' to clear history, 'quit' to exit.")
    print("="*70 + "\n")

def print_help():
    """Print help message with example queries."""
    print("\n" + "="*70)
    print("EXAMPLE QUERIES")
    print("="*70)
    print("\n🌤️  Weather Queries:")
    print("   • What's the weather in Vancouver?")
    print("   • Tell me the temperature in Tokyo in Celsius")
    print("   • Is it going to rain in London?")
    print("\n🔢 Calculator Queries:")
    print("   • Calculate 2 + 2")
    print("   • What's the square root of 256?")
    print("   • Compute 2^10")
    print("   • Calculate sin(pi/2)")
    print("\n📊 Database Queries:")
    print("   • Show me all engineers")
    print("   • List active projects")
    print("   • Who leads the Weather App project?")
    print("   • Find users with role manager")
    print("\n🔗 Multi-Tool Queries:")
    print("   • What's the weather in SF and who is working on the ML Pipeline?")
    print("   • Calculate 3*40*4 and tell me about our engineers")
    print("\n💡 Tips:")
    print("   • Ask follow-up questions - I remember context!")
    print("   • Be specific about locations for weather")
    print("   • Use natural language - I'll figure out what you need")
    print("="*70 + "\n")

def interactive_mode(assistant: AIAssistant):
    """Run the assistant in interactive CLI mode."""
    print_header()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle commands
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for chatting! Goodbye!\n")
                break
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            if user_input.lower() == 'reset':
                assistant.reset_conversation()
                continue
            
            if user_input.lower() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                print_header()
                continue
            
            # Process with assistant
            response = assistant.chat(user_input)
            
            print()  # Add spacing
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for chatting! Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for examples.\n")

def run_benchmark_suite(assistant: AIAssistant):
    """Run a comprehensive benchmark suite to test all capabilities."""
    print("\n" + "="*70)
    print("RUNNING BENCHMARK SUITE")
    print("="*70)
    
    benchmarks = [
        {
            "name": "Single Tool - Weather",
            "query": "What's the weather in Vancouver, BC?"
        },
        {
            "name": "Single Tool - Calculator",
            "query": "Calculate the square root of 144"
        },
        {
            "name": "Single Tool - Database",
            "query": "Show me all projects with status active"
        },
        {
            "name": "Multi-Tool - Weather + Database",
            "query": "What's the weather in San Francisco and who leads the Weather App?"
        },
        {
            "name": "Complex Reasoning",
            "query": "If each of our engineers works 40 hours per week and we have a 4-week month, what's our total engineering capacity in hours?"
        },
        {
            "name": "Context Follow-up",
            "query": "What about if we add one more engineer?",
            "skip_reset": True
        },
    ]
    
    for i, benchmark in enumerate(benchmarks, 1):
        print(f"\n{'='*70}")
        print(f"Benchmark {i}/{len(benchmarks)}: {benchmark['name']}")
        print(f"{'='*70}")
        
        if not benchmark.get('skip_reset', False):
            assistant.reset_conversation()
        
        assistant.chat(benchmark['query'])
        
        print(f"\n✅ Benchmark {i} completed")
    
    print(f"\n{'='*70}")
    print("ALL BENCHMARKS COMPLETED SUCCESSFULLY")
    print(f"{'='*70}\n")

def main():
    """Main execution function."""

    # Load environment variables 
    load_dotenv()

    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not found in environment.")
        print("\nOptions to fix this:")
        print("1. Set environment variable: export ANTHROPIC_API_KEY='your-key'")
        print("2. Create .env file with: ANTHROPIC_API_KEY=your-key")
        print("3. Modify this script to use the provided key directly\n")
        return
    
    # Initialize assistant
    assistant = AIAssistant(api_key)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            print("\nRunning demonstration mode...")
            from part2_ai_chat_tools import main as demo_main
            demo_main()
        elif sys.argv[1] == '--benchmark':
            run_benchmark_suite(assistant)
        elif sys.argv[1] == '--help':
            print("\nUsage:")
            print("  python part2_interactive.py           # Interactive mode")
            print("  python part2_interactive.py --demo    # Run demos")
            print("  python part2_interactive.py --benchmark   # Run benchmarks")
            print("  python part2_interactive.py --help    # Show this help")
        else:
            print(f"\n❌ Unknown argument: {sys.argv[1]}")
            print("Use --help to see available options")
    else:
        # Default to interactive mode
        interactive_mode(assistant)

if __name__ == "__main__":
    main()
