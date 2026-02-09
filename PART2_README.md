# Part 2: AI Chat Tools - Implementation Guide

## What I Built?

An AI assistant powered by Claude that can use tools to help with tasks. It has three tools: weather lookup, calculator, and database queries. The assistant figures out which tools it needs, uses them, and gives you a natural answer.

## Quick Start

### Install the Dependencies
```bash
pip install anthropic python-dotenv
```

### Set Up an API Key

Create an `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

The scripts automatically load this file.

### Run It

**Demo mode** (shows 5 examples):
```bash
python part2_ai_chat_tools.py
```

**Interactive mode** (chat with it):
```bash
python part2_interactive.py
```

**Benchmark mode** (runs tests):
```bash
python part2_interactive.py --benchmark
```

## How It Works

When you ask a question, Claude:
1. Figures out which tool(s) it needs
2. Calls those tools with the right parameters
3. Gets the results back
4. Gives you a natural language answer

For example:
- **You**: "What's the weather in Vancouver?"
- **Claude**: Calls `get_weather` tool with location="Vancouver"
- **Tool returns**: Temperature, conditions, and etc.
- **Claude**: "The weather in Vancouver is 15°C and partly cloudy..."

## The Three Tools

### 1. Weather Tool
Returns weather info for any location. (Uses simulated data for this demo - in production this would call a real weather API.)

**Try:**
- "What's the weather in Tokyo?"
- "Is it going to rain in London?"

### 2. Calculator Tool
Does math calculations safely. Supports basic operations plus sqrt, sin, cos, etc.

**Try:**
- "Calculate sqrt(144)"
- "What's 2^10?"
- "Compute sin(pi/2)"

### 3. Database Tool
Queries an in-memory database of users and projects.

**Try:**
- "Show me all engineers"
- "List active projects"
- "Who leads the Weather App project?"

## Code Structure

I separated each tool into its own class so they're easier to test:
```python
class WeatherTool:
    @staticmethod
    def get_definition():
        # Returns the schema Claude needs
    
    @staticmethod
    def execute(location, unit):
        # Does the actual work
```

The `AIAssistant` class manages everything:
- Registers tools with Claude
- Handles the conversation loop
- Routes tool calls to the right place
- Maintains conversation history

## Key Design Decisions

**Why separate tool classes?**
- Easier to test each tool individually
- Can add new tools without changing existing ones
- Cleaner code organization

**Why the iteration limit?**
- Without it, Claude could get stuck calling tools forever
- 5 iterations is enough for any reasonable task
- Prevents infinite loops

**Why store conversation history?**
- Lets you ask follow-up questions
- Claude remembers the context
- Makes conversations feel natural

## Example Sessions

### Single Tool
```
You: What's the weather in Vancouver?
🔧 Tool: get_weather
Assistant: It's currently 15°C and partly cloudy in Vancouver...
```

### Multiple Tools
```
You: What's the weather in SF and who leads the Weather App?
🔧 Tool: get_weather (for San Francisco)
🔧 Tool: query_database (for projects)
🔧 Tool: query_database (for user details)
Assistant: San Francisco is 59°F and sunny. The Weather App is led by 
Alice Johnson (alice@example.com).
```

### Multi-Step Calculation
```
You: 3 engineers × 40 hours/week × 4 weeks = ?
🔧 Tool: calculator
Assistant: That's 480 hours per month.
```

## Adding a New Tool

Here's how to extend the system:

1. Create your tool class:
```python
class EmailTool:
    @staticmethod
    def get_definition():
        return {
            "name": "send_email",
            "description": "Send an email",
            "input_schema": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    
    @staticmethod
    def execute(to, subject, body):
        # Send the email
        return {"success": True, "message_id": "123"}
```

2. Register it in `AIAssistant.__init__`:
```python
self.email_tool = EmailTool()
self.tools.append(self.email_tool.get_definition())
```

3. Add to `_execute_tool`:
```python
if tool_name == "send_email":
    return self.email_tool.execute(**tool_input)
```

That's it!

## What I Learned

Building this taught me:
- How Claude's function calling API works
- How to design agentic systems that don't get stuck
- Proper error handling for AI tools
- Making conversations feel natural

The trickiest part was making sure the conversation loop doesn't hang if something goes wrong.

## Production Improvements

If I were to deploy this for real use, I'd:
- Connect to actual weather APIs (OpenWeatherMap)
- Use a real database (PostgreSQL)
- Add conversation persistence (save chat history)
- Implement async tool execution (faster)
- Add rate limiting
- Create a web UI (Streamlit or Gradio)
- Add authentication

## Technical Details

**Tools I used:**
- Claude's Messages API with tool calling
- Python type hints for better code quality
- Error handling with try-catch blocks
- Conversation history management

**Time to build:** About 2 hours including testing

**Lines of code:** ~400 (including comments)

---

Built for SoranoAI Technical Assessment - February 2026