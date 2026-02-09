"""
Part 2: AI Chat Tools Implementation
Author: Abdu Alim Arlikhozhaev
Date: February 2026

This implements AI chat tools using Claude API with function calling capabilities.
Demonstrates clean architecture, error handling, and production-ready patterns.
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import datetime

class WeatherTool:
    """Tool for fetching weather information."""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Return the tool definition for Claude."""
        return {
            "name": "get_weather",
            "description": "Get current weather information for a specific location. Returns temperature, conditions, and forecast.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state/country, e.g. 'Vancouver, BC' or 'San Francisco, CA'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit to use. Defaults to celsius."
                    }
                },
                "required": ["location"]
            }
        }
    
    @staticmethod
    def execute(location: str, unit: str = "celsius") -> Dict[str, Any]:
        """
        Execute the weather tool.
        
        In a production system, this would call a real weather API.
        For this demo, it returns simulated data.
        """
        # Simulated weather data
        weather_data = {
            "location": location,
            "temperature": 15 if unit == "celsius" else 59,
            "unit": unit,
            "conditions": "Partly cloudy",
            "humidity": 65,
            "wind_speed": 12,
            "forecast": [
                {"day": "Today", "high": 18, "low": 12, "conditions": "Partly cloudy"},
                {"day": "Tomorrow", "high": 20, "low": 14, "conditions": "Sunny"},
                {"day": "Day after", "high": 17, "low": 13, "conditions": "Rainy"}
            ]
        }
        
        return weather_data


class CalculatorTool:
    """Tool for performing mathematical calculations."""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Return the tool definition for Claude."""
        return {
            "name": "calculator",
            "description": "Perform mathematical calculations. Supports basic arithmetic, powers, roots, and common mathematical functions.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate, e.g. '2 + 2', 'sqrt(16)', '2^3'"
                    }
                },
                "required": ["expression"]
            }
        }
    
    @staticmethod
    def execute(expression: str) -> Dict[str, Any]:
        """
        Execute the calculator tool.
        
        Uses safe evaluation to compute mathematical expressions.
        """
        try:
            # Safe evaluation using limited namespace
            import math
            
            # Prepare safe namespace
            safe_dict = {
                'sqrt': math.sqrt,
                'pow': math.pow,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'exp': math.exp,
                'pi': math.pi,
                'e': math.e,
            }
            
            # Replace ^ with ** for exponentiation
            expression = expression.replace('^', '**')
            
            # Evaluate
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            return {
                "expression": expression,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "success": False
            }


class DatabaseTool:
    """Tool for querying a simple in-memory database."""
    
    def __init__(self):
        # Simulated database
        self.data = {
            "users": [
                {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "engineer"},
                {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "designer"},
                {"id": 3, "name": "Carol Wang", "email": "carol@example.com", "role": "manager"},
            ],
            "projects": [
                {"id": 1, "name": "Weather App", "status": "active", "lead_id": 1},
                {"id": 2, "name": "ML Pipeline", "status": "planning", "lead_id": 3},
                {"id": 3, "name": "Data Viz Tool", "status": "completed", "lead_id": 2},
            ]
        }
    
    def get_definition(self) -> Dict[str, Any]:
        """Return the tool definition for Claude."""
        return {
            "name": "query_database",
            "description": "Query the company database for information about users, projects, or other entities.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "enum": ["users", "projects"],
                        "description": "The database table to query"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filters to apply to the query, e.g. {'role': 'engineer'}"
                    }
                },
                "required": ["table"]
            }
        }
    
    def execute(self, table: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the database query."""
        try:
            results = self.data.get(table, [])
            
            # Apply filters if provided
            if filters:
                filtered_results = []
                for item in results:
                    match = True
                    for key, value in filters.items():
                        if item.get(key) != value:
                            match = False
                            break
                    if match:
                        filtered_results.append(item)
                results = filtered_results
            
            return {
                "table": table,
                "results": results,
                "count": len(results),
                "success": True
            }
        except Exception as e:
            return {
                "table": table,
                "error": str(e),
                "success": False
            }


class AIAssistant:
    """Main AI Assistant class using Claude with tool calling."""
    
    def __init__(self, api_key: str):
        """
        Initialize the AI Assistant.
        
        Args:
            api_key: Anthropic API key
        """
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        
        # Initialize tools
        self.weather_tool = WeatherTool()
        self.calculator_tool = CalculatorTool()
        self.database_tool = DatabaseTool()
        
        # Tool registry
        self.tools = [
            self.weather_tool.get_definition(),
            self.calculator_tool.get_definition(),
            self.database_tool.get_definition(),
        ]
        
        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []
    
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        Execute a tool by name with given input.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result
        """
        if tool_name == "get_weather":
            return self.weather_tool.execute(**tool_input)
        elif tool_name == "calculator":
            return self.calculator_tool.execute(**tool_input)
        elif tool_name == "query_database":
            return self.database_tool.execute(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def _process_tool_calls(self, response) -> List[Dict[str, Any]]:
        """
        Process tool calls from Claude's response.
        
        Args:
            response: Claude API response
            
        Returns:
            List of tool results
        """
        tool_results = []
        
        for content_block in response.content:
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input
                tool_use_id = content_block.id
                
                print(f"\n🔧 Executing tool: {tool_name}")
                print(f"   Input: {json.dumps(tool_input, indent=2)}")
                
                # Execute the tool
                result = self._execute_tool(tool_name, tool_input)
                
                print(f"   Result: {json.dumps(result, indent=2)}")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(result)
                })
        
        return tool_results
    
    def chat(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Send a message and get a response, handling tool calls automatically.
        
        Args:
            user_message: The user's message
            max_iterations: Maximum number of tool call iterations
            
        Returns:
            Claude's final response
        """
        print(f"\n💬 User: {user_message}")
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=self.tools,
                messages=self.conversation_history
            )
            
            # Check if Claude wants to use tools
            has_tool_use = any(block.type == "tool_use" for block in response.content)
            
            if has_tool_use:
                # Add assistant's response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Process tool calls
                tool_results = self._process_tool_calls(response)
                
                # Add tool results to history
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                # No more tool calls, extract final response
                final_response = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_response += block.text
                
                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })
                
                print(f"\n🤖 Assistant: {final_response}")
                return final_response
        
        return "Maximum iterations reached. Please try rephrasing your question."
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        print("\n🔄 Conversation reset.")


def main():
    """Main execution function demonstrating the AI Assistant."""
    
    print("="*70)
    print("SORANO AI INTERNSHIP - PART 2: AI CHAT TOOLS")
    print("="*70)
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

    # Get API key from environment or use provided key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not found in environment.")
        print("Please set it using: export ANTHROPIC_API_KEY='your-key-here'")
        print("Or modify this script to use the provided key directly.")
        return
    
    # Initialize assistant
    assistant = AIAssistant(api_key)
    
    # Demo conversations
    print("\n" + "="*70)
    print("DEMO 1: Weather Query")
    print("="*70)
    assistant.chat("What's the weather like in Vancouver, BC?")
    
    print("\n" + "="*70)
    print("DEMO 2: Calculator")
    print("="*70)
    assistant.chat("Can you calculate the square root of 144 plus 2 to the power of 5?")
    
    print("\n" + "="*70)
    print("DEMO 3: Database Query")
    print("="*70)
    assistant.chat("Show me all engineers in the database")
    
    print("\n" + "="*70)
    print("DEMO 4: Multi-Tool Query")
    print("="*70)
    assistant.reset_conversation()
    assistant.chat("What's the weather in San Francisco, and who is leading the Weather App project?")
    
    print("\n" + "="*70)
    print("DEMO 5: Complex Calculation with Context")
    print("="*70)
    assistant.chat("If we have 3 engineers and each works 40 hours per week, how many total hours is that per month (assuming 4 weeks)?")
    
    print("\n✅ All demos completed successfully!")


if __name__ == "__main__":
    main()
