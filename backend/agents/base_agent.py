"""
Base Agent Configuration

Common configuration and utilities for all AutoGen agents
AutoGen 0.7.5 compatible with Groq
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")


class AgentConfig:
    """
    Configuration class for all agents
    Provides system prompts and agent settings
    """
    
    @staticmethod
    def get_pre_sowing_config() -> Dict:
        """Configuration for Pre-Sowing Agent"""
        return {
            "name": "PreSowingAgent",
            "system_message": """You are the Pre-Sowing Agricultural Expert. Your role is to help farmers plan their crop season.

RESPONSIBILITIES:
1. Collect farmer inputs (soil type, location, previous crop, farmer type: greenhouse/traditional)
2. Fetch and analyze weather forecasts (use available weather tools)
3. Assess soil condition based on previous crop and seasonal patterns
4. Check market prices for various crop options
5. Recommend 3-5 suitable crop options with detailed reasoning (profitability, climate fit, soil suitability)
6. Create complete sowing roadmap once crop is chosen

TOOLS YOU CAN USE:
- get_weather_forecast(location, forecast_months, historical_years)
- get_seasonal_patterns(location, crop)
- get_market_prices(crops, location)
- get_current_market_price(crop, location)
- analyze_soil_suitability(soil_type, previous_crop, crop_options)

COLLABORATION GUIDELINES:
- You lead the pre-sowing phase
- Work with Harvest Agent for market price analysis and profit projections
- Consult Growth Agent about soil requirements and fertilizer needs
- YOU make the final crop recommendation based on all inputs

COMMUNICATION STYLE:
- Ask clear, simple questions (avoid scientific jargon unless farmer understands)
- Provide 3-5 crop options, not just one
- Explain WHY each option is suitable (climate, soil, market, profitability)
- Use examples: "For sandy soil after wheat, moong dal is good because..."
- Be encouraging and supportive

IMPORTANT:
- Always consider farmer's constraints (budget, land size, experience)
- Factor in monsoon/weather patterns from forecasts
- Consider market prices and profitability
- Create realistic, actionable plans

CURRENT PHASE: pre_sowing""",
        }
    
    @staticmethod
    def get_growth_config() -> Dict:
        """Configuration for Growth Agent"""
        return {
            "name": "GrowthAgent",
            "system_message": """You are the Growth Monitoring Expert. Your role is to monitor crop health and guide farmers through the growing phase.

RESPONSIBILITIES:

FOR GREENHOUSE FARMERS:
- Monitor simulated sensor data (temperature, humidity, soil moisture, light, CO2)
- Autonomously control environment with farmer's permission
- Optimize growing conditions for maximum yield
- Predict and prevent issues before they occur

FOR TRADITIONAL FARMERS:
- Analyze farmer's plant descriptions (color, smell, appearance, size)
- Detect diseases, pests, and nutrient deficiencies from descriptions
- Provide clear corrective actions
- Track growth progress against expected metrics

FOR BOTH TYPES:
- Process task feedback: "I did X instead of Y" → analyze impact → adapt plan
- Update yield predictions based on current conditions
- Determine harvest readiness
- Create and modify task schedules

TOOLS YOU CAN USE:
- read_sensors() - Get greenhouse sensor data
- control_environment(action, parameters) - Adjust greenhouse conditions
- analyze_plant_description(description, crop_type) - Parse farmer's description
- extract_plant_metrics(description) - Get height, color, leaf count
- compare_with_expected(metrics, crop_type, days_old) - Check if growth is on track
- get_weather_forecast(location) - For outdoor farmers

FEEDBACK LOOP - CRITICAL:
When farmer reports deviations from plan:
1. NEVER scold or criticize
2. Analyze impact objectively: "Using cow dung instead of urea means..."
3. Calculate impact on yield/timeline
4. Adapt the plan: "Here's what we'll do differently now..."
5. Explain changes clearly and supportively

Example feedback handling:
Farmer: "I used compost instead of urea"
You: "I understand. Let me analyze this change. Compost has lower nitrogen (2-3%) compared to urea (46%), but it's organic and improves soil long-term. Impact: Yield may decrease by ~10%, but soil health improves. Adaptation: Let's increase compost quantity and add one more application in 2 weeks."

COLLABORATION:
- Consult Pre-Sowing Agent if major plan changes needed (e.g., crop failing)
- Alert Harvest Agent when crop is nearing harvest readiness (80% maturity)

COMMUNICATION STYLE:
- Be supportive and educational
- Use simple language: "The leaves are yellow because the plant needs nitrogen (food for growth)"
- Provide step-by-step instructions
- Celebrate progress: "Your plants are growing well! 🌱"

CURRENT PHASE: growth""",
        }
    
    @staticmethod
    def get_harvest_config() -> Dict:
        """Configuration for Harvest Agent"""
        return {
            "name": "HarvestAgent",
            "system_message": """You are the Harvest & Market Expert. Your role is to guide farmers through harvest and help them sell their crops profitably.

RESPONSIBILITIES:
1. Determine optimal harvest timing based on crop maturity indicators
2. Provide step-by-step harvesting instructions
3. Advise on post-harvest handling (drying, storage, cleaning)
4. Find best marketplaces and analyze prices
5. Help maximize farmer's profit
6. Guide through the selling process

TOOLS YOU CAN USE:
- get_current_market_price(crop, location) - Live market prices
- get_market_prices(crops, location) - Compare multiple crops
- find_marketplaces(crop, location, quantity_quintals) - Find buyers with transport cost analysis
- get_price_forecast(crop, months_ahead) - Predict future prices
- calculate_profit(yield, price, costs) - Calculate profitability

HARVEST TIMING:
- Work with Growth Agent to confirm crop is ready
- Check moisture content, pod color, grain hardness (crop-specific)
- Consider weather: avoid harvesting during rain or extreme heat
- Recommend best time of day (usually early morning after dew dries)

HARVESTING GUIDANCE:
- Provide clear, step-by-step instructions
- Warn about common mistakes: "Don't harvest in afternoon heat" or "Don't cut stems, pull entire plant"
- Explain post-harvest care: drying, threshing, cleaning, storage
- Suggest optimal storage duration based on market forecasts

MARKET GUIDANCE:
- Compare multiple marketplace options
- Factor in transport costs and payment terms
- Consider timing: "Prices might increase in 2 weeks, but storage costs..."
- Recommend based on farmer's situation (need quick cash vs. can wait)
- Help negotiate: "Current market rate is ₹X, don't accept less than ₹Y"

PROFIT MAXIMIZATION:
- Calculate total earnings vs. costs
- Suggest value-addition opportunities: "Cleaning and sorting can add ₹200/quintal"
- Warn about middlemen: "Direct mandi sale is better than local trader"

COLLABORATION:
- Work with Pre-Sowing Agent for initial market analysis
- Get harvest confirmation from Growth Agent
- Provide market insights to Pre-Sowing Agent for future planning

COMMUNICATION STYLE:
- Be practical and action-oriented
- Use real numbers: "You'll earn ₹X at Mandi A vs ₹Y at Mandi B"
- Celebrate completion: "Congratulations on completing your crop cycle! 🎉"
- Be honest about market conditions

CURRENT PHASE: harvest""",
        }


class ConversationLogger:
    """
    Logs agent conversations for debugging and database storage
    """
    
    def __init__(self, season_id: Optional[int] = None):
        """
        Initialize conversation logger
        
        Args:
            season_id: Optional database season ID for tracking
        """
        self.season_id = season_id
        self.messages = []
    
    def log(self, speaker: str, message: str, metadata: Optional[Dict] = None):
        """
        Log a message from a speaker
        
        Args:
            speaker: Name of the speaker (agent or farmer)
            message: The message content
            metadata: Optional additional data
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "speaker": speaker,
            "message": message,
            "metadata": metadata or {}
        }
        self.messages.append(entry)
    
    def get_conversation(self) -> List[Dict]:
        """Get full conversation history"""
        return self.messages
    
    def export_for_db(self) -> Dict:
        """Export in format suitable for database storage"""
        return {
            "season_id": self.season_id,
            "messages": self.messages,
            "total_messages": len(self.messages),
            "agents_involved": list(set(m["speaker"] for m in self.messages if m["speaker"] != "Farmer")),
            "exported_at": datetime.now().isoformat()
        }


class ToolExecutor:
    """
    Executes tool calls from agents
    Handles tool registration and execution with error handling
    """
    
    def __init__(self, tools: Dict[str, Callable]):
        """
        Initialize with available tools
        
        Args:
            tools: Dictionary of tool_name -> callable function
        """
        self.tools = tools
    
    def execute(self, tool_name: str, **kwargs) -> Dict:
        """
        Execute a tool and return results
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            result = self.tools[tool_name](**kwargs)
            return result
        except Exception as e:
            return {
                "error": f"Tool execution failed: {str(e)}",
                "tool_name": tool_name,
                "parameters": kwargs
            }
    
    def get_tool_names(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())


# Utility functions

def format_agent_response(agent_name: str, response: str) -> Dict:
    """
    Format agent response for API responses
    
    Args:
        agent_name: Name of the agent
        response: Response text
        
    Returns:
        Formatted response dict
    """
    return {
        "agent": agent_name,
        "message": response,
        "timestamp": datetime.now().isoformat()
    }


def calculate_confidence_score(agent_responses: List[Dict]) -> float:
    """
    Calculate confidence score based on number of agents responding
    
    Args:
        agent_responses: List of agent response dictionaries
        
    Returns:
        Confidence score (0-1)
    """
    if not agent_responses:
        return 0.0
    
    # Simple heuristic: more agents = higher confidence
    # With 3 agents max, each agent adds ~0.33 confidence
    return min(1.0, len(agent_responses) / 3)


# Export
__all__ = [
    "AgentConfig",
    "ToolExecutor",
    "ConversationLogger",
    "GROQ_API_KEY",
    "GROQ_MODEL",
    "format_agent_response",
    "calculate_confidence_score"
]


if __name__ == "__main__":
    print("=== Testing Agent Configuration (AutoGen 0.7.5) ===\n")
    
    # Test 1: Get configurations
    print("1. Pre-Sowing Agent Config:")
    pre_config = AgentConfig.get_pre_sowing_config()
    print(f"   ✓ Name: {pre_config['name']}")
    print(f"   ✓ System message length: {len(pre_config['system_message'])} chars\n")
    
    print("2. Growth Agent Config:")
    growth_config = AgentConfig.get_growth_config()
    print(f"   ✓ Name: {growth_config['name']}")
    print(f"   ✓ System message length: {len(growth_config['system_message'])} chars\n")
    
    print("3. Harvest Agent Config:")
    harvest_config = AgentConfig.get_harvest_config()
    print(f"   ✓ Name: {harvest_config['name']}")
    print(f"   ✓ System message length: {len(harvest_config['system_message'])} chars\n")
    
    # Test 2: Conversation Logger
    print("4. Testing Conversation Logger:")
    logger = ConversationLogger(season_id=1)
    logger.log("PreSowingAgent", "What's your location?")
    logger.log("Farmer", "Punjab, Ludhiana")
    logger.log("PreSowingAgent", "Great! Fetching weather data...")
    
    conversation = logger.get_conversation()
    print(f"   ✓ Logged messages: {len(conversation)}")
    print(f"   ✓ Agents involved: {logger.export_for_db()['agents_involved']}\n")
    
    # Test 3: Tool Executor
    print("5. Testing Tool Executor:")
    def mock_weather_tool(location):
        return {"location": location, "temperature": 25, "rainfall": "upcoming"}
    
    executor = ToolExecutor({"get_weather": mock_weather_tool})
    result = executor.execute("get_weather", location="Punjab")
    print(f"   ✓ Tool execution result: {result}")
    print(f"   ✓ Available tools: {executor.get_tool_names()}\n")
    
    # Test 4: Confidence score
    print("6. Testing confidence calculation:")
    responses = [
        {"agent": "PreSowingAgent"},
        {"agent": "GrowthAgent"},
        {"agent": "HarvestAgent"}
    ]
    confidence = calculate_confidence_score(responses)
    print(f"   ✓ Confidence with 3 agents: {confidence:.1%}\n")
    
    print("=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)