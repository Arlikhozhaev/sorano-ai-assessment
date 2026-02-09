# SoranoAI Technical Assessment

**Name**: Abdu Alim Arlikhozhaev 
**Email**: arlikhozhaevca@gmail.com
**Date**: February 9, 2026  

---

## What I Built

I completed both parts of the SoranoAI technical assessment:

**Part 1**: A python script that compares two AI weather models (IFS and AIFS) against the real-world ERA5 data. It calculates error metrics and creates visual images showing which of the models is more accurate.

**Part 2**: An AI assistant (powered by Claude) that can use tools to help with tasks like checking weather, doing calculations, and querying the database.

---

## Quick Start

### Part 1: Forecast Verification
```bash

# Install the dependencies
pip install xarray netCDF4 numpy matplotlib scipy scikit-learn cdsapi

# Run the analysis
python part1_forecast_verification.py
```

### Part 2: AI Chat Tools
```bash

# Install the dependencies
pip install anthropic python-dotenv

# Create .env file with your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Run the demo
python part2_ai_chat_tools.py

# Or try an interactive mode
python part2_interactive.py
```

---

## How Part 1 Works?

First, the script loads two forecast files (IFS and AIFS), then it proceeds to find the times they have in common, downloads corresponding ERA5 data, and computes three metrics for each time:
- **MAE** (Mean Absolute Error) - average error magnitude
- **RMSE** (Root Mean Square Error) - penalizes larger errors more
- **R²** (Coefficient of Determination) - how well the forecast predicts patterns

Eventually, it generates a three-panel plot showing how each model performs over time.

**Note**: The forecasts are for January 2026, but ERA5 data isn't available for 2026 yet, so I used January 2025 as ground truth. This is why the error values are higher than typical - it's comparing different years.

## How Part 2 Works?

The AI assistant has three tools you can use:

1. **Weather Tool** - Returns weather info for any location (simulated data for this demo)
2. **Calculator Tool** - Does math calculations safely (supports sqrt, sin, cos, etc.)
3. **Database Tool** - Queries an in-memory database of users and projects

When you ask a question, Claude instantly figures out which tool(s) it needs, executes them, and then gives you a natural language response. It remembers conversation context so you can ask follow-up questions.

## Technical Approach

### Part 1
The reason I used xarray is because it's designed for climate data and handles multi-dimensional arrays well. The main challenge was that the forecast files had different time resolutions and coordinate names. So, I solved this by:
- Detecting coordinate names automatically (some files use 'time', others use 'valid_time')
- Interpolating ERA5 data to match the forecast grid
- Handling missing values properly

### Part 2
I separated each tool into its own classes so it's easier to test and maintain any of those. The AIAssistant class manages the conversation loop and routes tool calls. I added iteration limits (max 5) in order to prevent infinite loops if Claude gets stuck.

The interactive mode was a bonus I added to make demoing easier.

## Key Features

**Part 1:**
- Handles 61 overlapping forecast times
- Automatic grid interpolation
- Professional visualizations
- Comprehensive error handling

**Part 2:**
- Three working tools with proper schemas
- Multi-turn conversation support
- Interactive CLI mode
- Clean, modular code

## What I Learned

This project taught me:
- How forecast verification works in meteorology
- Claude's function calling API and how to build agentic systems
- Handling real-world data inconsistencies (different formats, missing values)
- Writing production-quality Python with proper error handling

The biggest challenge in Part 1 was the ERA5 year mismatch. In Part 2, it was making sure the tool execution loop doesn't hang.

---

## Files

- `part1_forecast_verification.py` - Weather forecast analysis script
- `forecast_verification.png` - Visualization of forecast performance
- `part2_ai_chat_tools.py` - AI assistant implementation
- `part2_interactive.py` - Interactive chat mode
- `requirements.txt` - Python dependencies
- `.env.example` - API key template
- `README.md` - This file

---

## Development Notes

I used Claude AI to help generate some boilerplate code and debug issues. However, I:
- Reviewed and modified all generated code
- Made all architectural decisions myself
- Wrote all documentation in my own words
- Fully understood every component

Total time: about 3-4 hours including testing and documentation.

---

**Abdu Alim Arlikhozhaev**  
📧 arlikhozhaevca@gmail.com  
🔗 [GitHub](https://github.com/Arlikhozhaev) | [LinkedIn](https://www.linkedin.com/in/arlikhozhaev/)
