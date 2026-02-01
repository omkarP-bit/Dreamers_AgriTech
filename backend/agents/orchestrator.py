"""
Agent Orchestrator - ENHANCED WITH CONTEXT MEMORY

Improvements:
1. Conversation memory (agents remember previous messages)
2. Dynamic agent context updates (agents recreated with farmer info in system message)
3. Farmer context extraction (no repeated questions)
4. Better agent response selection (picks most relevant response)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_core.tools import FunctionTool

from .groq_wrapper import GroqChatCompletionClient
from .base_agent import (
    AgentConfig,
    ConversationLogger,
    GROQ_API_KEY,
    GROQ_MODEL
)

# Import tools
from tools.weather_tools import get_weather_forecast
from tools.seasonal_patterns import get_seasonal_patterns, analyze_soil_suitability
from tools.market_tools import (
    get_current_market_price,
    get_market_prices,
    find_marketplaces,
    get_price_forecast,
    calculate_profit
)
from tools.greenhouse_sim import (
    read_sensors,
    control_environment,
    get_recommendations
)
from tools.plant_analysis import (
    analyze_plant_description,
    extract_plant_metrics,
    compare_with_expected
)


class FarmingAgentOrchestrator:
    """
    Orchestrates multi-agent conversations for farming assistance
    
    Uses RoundRobinGroupChat so ANY agent can respond to ANY question,
    but adds conversation memory AND dynamic context injection so agents
    remember farmer information and don't repeat questions.
    """
    
    def __init__(
        self, 
        season_id: int, 
        current_phase: str = "pre_sowing", 
        farmer_type: str = "traditional"
    ):
        """Initialize orchestrator"""
        print(f"\n{'='*60}")
        print(f"  Initializing Farming Agent Orchestrator")
        print(f"{'='*60}")
        print(f"  Season ID: {season_id}")
        print(f"  Phase: {current_phase}")
        print(f"  Farmer Type: {farmer_type}")
        print(f"{'='*60}\n")
        
        self.season_id = season_id
        self.current_phase = current_phase
        self.farmer_type = farmer_type
        
        # Initialize conversation logger
        self.logger = ConversationLogger(season_id)
        print("  ✓ Conversation logger initialized")
        
        # Create model client ONCE
        self.model_client = self._create_model_client()
        print("  ✓ Groq model client created")
        
        # Wrap tools
        self.wrapped_tools = self._wrap_tools()
        print(f"  ✓ Wrapped {len(self.wrapped_tools)} tools")
        
        # Initialize agents with tools
        self.agents = self._initialize_agents()
        print(f"  ✓ Initialized {len(self.agents)} agents")
        
        # Initialize group chat (RoundRobinGroupChat)
        self.group_chat = None
        self._setup_group_chat()
        print("  ✓ Group chat configured")
        
        # Farmer context (extracted from conversation)
        self.farmer_context = {
            "soil_type": None,
            "location": None,
            "previous_crop": None,
            "farmer_type": farmer_type,
            "current_crop": None
        }
        
        print(f"\n{'='*60}")
        print(f"  Orchestrator Ready!")
        print(f"{'='*60}\n")
    
    def _wrap_tools(self) -> Dict[str, FunctionTool]:
        """Wrap tool functions as FunctionTool objects"""
        print("\n  Wrapping tools as FunctionTool objects...")
        
        wrapped = {}
        
        # Common tools
        wrapped["get_weather_forecast"] = FunctionTool(
            get_weather_forecast,
            description="Get weather forecast and analysis for a location"
        )
        wrapped["get_seasonal_patterns"] = FunctionTool(
            get_seasonal_patterns,
            description="Get seasonal weather patterns for crop planning"
        )
        wrapped["analyze_soil_suitability"] = FunctionTool(
            analyze_soil_suitability,
            description="Analyze soil suitability for different crops"
        )
        wrapped["get_current_market_price"] = FunctionTool(
            get_current_market_price,
            description="Get current market price for a crop"
        )
        wrapped["get_market_prices"] = FunctionTool(
            get_market_prices,
            description="Get market prices for multiple crops"
        )
        wrapped["find_marketplaces"] = FunctionTool(
            find_marketplaces,
            description="Find best marketplaces to sell crops"
        )
        wrapped["get_price_forecast"] = FunctionTool(
            get_price_forecast,
            description="Get price forecast for upcoming months"
        )
        wrapped["calculate_profit"] = FunctionTool(
            calculate_profit,
            description="Calculate profit/loss and ROI"
        )
        
        # Farmer-type specific tools
        if self.farmer_type == "greenhouse":
            wrapped["read_sensors"] = FunctionTool(
                read_sensors,
                description="Read greenhouse sensor data"
            )
            wrapped["control_environment"] = FunctionTool(
                control_environment,
                description="Control greenhouse environment"
            )
            wrapped["get_recommendations"] = FunctionTool(
                get_recommendations,
                description="Get greenhouse management recommendations"
            )
        
        if self.farmer_type == "traditional":
            wrapped["analyze_plant_description"] = FunctionTool(
                analyze_plant_description,
                description="Analyze plant health from farmer description"
            )
            wrapped["extract_plant_metrics"] = FunctionTool(
                extract_plant_metrics,
                description="Extract metrics from plant description"
            )
            wrapped["compare_with_expected"] = FunctionTool(
                compare_with_expected,
                description="Compare plant metrics with expected values"
            )
        
        print(f"    ✓ Wrapped {len(wrapped)} tools")
        return wrapped
    
    def _create_model_client(self) -> GroqChatCompletionClient:
        """Create Groq model client"""
        return GroqChatCompletionClient(
            api_key=GROQ_API_KEY,
            model=GROQ_MODEL,
            temperature=0.7,
            max_tokens=2000
        )
    
    def _get_tools_for_agent(self, agent_type: str) -> List[FunctionTool]:
        """Get tools for a specific agent"""
        tool_assignments = {
            "pre_sowing": [
                "get_weather_forecast",
                "get_seasonal_patterns", 
                "analyze_soil_suitability",
                "get_market_prices",
                "get_price_forecast"
            ],
            "growth": [
                "get_weather_forecast",
                *(["read_sensors", "control_environment", "get_recommendations"] 
                  if self.farmer_type == "greenhouse" 
                  else ["analyze_plant_description", "extract_plant_metrics", "compare_with_expected"])
            ],
            "harvest": [
                "get_current_market_price",
                "find_marketplaces",
                "calculate_profit",
                "get_price_forecast"
            ]
        }
        
        tool_names = tool_assignments.get(agent_type, [])
        tools = [self.wrapped_tools[name] for name in tool_names if name in self.wrapped_tools]
        
        print(f"\n    Tools for {agent_type}: {[t._func.__name__ for t in tools]}")
        
        return tools
    
    def _initialize_agents(self) -> Dict[str, AssistantAgent]:
        """Initialize all three expert agents WITH TOOLS"""
        
        print(f"\n  Initializing agents with tools...")
        agents = {}
        
        # Pre-Sowing Agent
        print(f"\n  Creating Pre-Sowing Agent:")
        pre_sowing_config = AgentConfig.get_pre_sowing_config()
        pre_sowing_tools = self._get_tools_for_agent("pre_sowing")
        
        agents["pre_sowing"] = AssistantAgent(
            name=pre_sowing_config["name"],
            system_message=pre_sowing_config["system_message"],
            model_client=self.model_client,
            tools=pre_sowing_tools
        )
        print(f"    ✓ Created with {len(pre_sowing_tools)} tools")
        
        # Growth Agent
        print(f"\n  Creating Growth Agent:")
        growth_config = AgentConfig.get_growth_config()
        growth_tools = self._get_tools_for_agent("growth")
        
        agents["growth"] = AssistantAgent(
            name=growth_config["name"],
            system_message=growth_config["system_message"],
            model_client=self.model_client,
            tools=growth_tools
        )
        print(f"    ✓ Created with {len(growth_tools)} tools")
        
        # Harvest Agent
        print(f"\n  Creating Harvest Agent:")
        harvest_config = AgentConfig.get_harvest_config()
        harvest_tools = self._get_tools_for_agent("harvest")
        
        agents["harvest"] = AssistantAgent(
            name=harvest_config["name"],
            system_message=harvest_config["system_message"],
            model_client=self.model_client,
            tools=harvest_tools
        )
        print(f"    ✓ Created with {len(harvest_tools)} tools")
        
        return agents
    
    def _setup_group_chat(self):
        """Setup RoundRobinGroupChat - agents take turns speaking"""
        
        participant_list = [
            self.agents["pre_sowing"],
            self.agents["growth"],
            self.agents["harvest"]
        ]
        
        # RoundRobinGroupChat: all agents can respond
        self.group_chat = RoundRobinGroupChat(
            participants=participant_list,
            max_turns=3  # Each agent gets one turn
        )
    
    def _extract_farmer_info(self, message: str):
        """Extract farmer information from message and update context"""
        message_lower = message.lower()
        
        # Extract soil type
        soil_types = ["sandy", "loamy", "clay", "black", "red", "alluvial"]
        for soil in soil_types:
            if soil in message_lower:
                if self.farmer_context["soil_type"] != soil:
                    self.farmer_context["soil_type"] = soil
                    print(f"    📝 Extracted soil type: {soil}")
                break
        
        # Extract location (expanded list with more locations)
        locations = ["punjab", "jalgaon", "maharashtra", "delhi", "mumbai", "bangalore", "ludhiana", 
                    "nashik", "karnataka", "tamil nadu", "haryana", "uttar pradesh", "madhya pradesh",
                    "rajasthan", "telangana", "andhra pradesh", "patna", "indore", "nagpur"]
        for loc in locations:
            if loc in message_lower:
                if self.farmer_context["location"] != loc:
                    self.farmer_context["location"] = loc
                    print(f"    📝 Extracted location: {loc}")
                break
        
        # Extract farmer type
        if "greenhouse" in message_lower:
            self.farmer_context["farmer_type"] = "greenhouse"
        elif "traditional" in message_lower:
            self.farmer_context["farmer_type"] = "traditional"
        
        # Extract previous crop (expanded list with more crops)
        crops = ["tomatoes", "tomato", "wheat", "rice", "cotton", "maize", "moong", "dal",
                "banana", "bananas", "sugarcane", "onion", "onions", "potato", "potatoes",
                "millet", "soybean", "groundnut", "cabbage", "brinjal", "chili", "chilli",
                "cumin", "coriander", "turmeric", "garlic", "carrot"]
        for crop in crops:
            if crop in message_lower:
                if self.farmer_context["previous_crop"] != crop:
                    self.farmer_context["previous_crop"] = crop
                    print(f"    📝 Extracted previous crop: {crop}")
                break
    
    def _update_agent_contexts(self):
        """
        🔥 KEY FIX: Update all agents' system messages with current farmer context
        
        This ensures agents ALWAYS have latest context in their system prompt.
        Agents are RECREATED with enhanced system messages that include farmer context.
        This makes it IMPOSSIBLE for agents to ignore the farmer information.
        """
        
        if not any(v for v in self.farmer_context.values() if v):
            print("    ℹ️  No farmer context to inject yet")
            return  # No context to add
        
        print(f"\n  🔄 Updating agent contexts with farmer information...")
        
        # Build context block with STRONG visual markers
        context_block = "\n\n" + "🔴"*30 + "\n"
        context_block += "⚠️  CRITICAL FARMER INFORMATION (DO NOT ASK AGAIN):\n"
        context_block += "🔴"*30 + "\n\n"
        
        for key, value in self.farmer_context.items():
            if value:
                context_block += f"✅ {key.replace('_', ' ').upper()}: {value}\n"
        
        context_block += "\n" + "🔴"*30
        context_block += "\n⚠️  YOU ALREADY KNOW THIS INFORMATION - DO NOT ASK FOR IT AGAIN!"
        context_block += "\n⚠️  Use this information directly in your responses!"
        context_block += "\n🔴"*30 + "\n"
        
        print(f"    Context block created ({len(context_block)} chars)")
        
        # RECREATE each agent with enhanced system message
        for agent_key in list(self.agents.keys()):
            print(f"    Recreating {agent_key} agent with context...")
            
            # Get base config
            if agent_key == "pre_sowing":
                base_config = AgentConfig.get_pre_sowing_config()
            elif agent_key == "growth":
                base_config = AgentConfig.get_growth_config()
            else:  # harvest
                base_config = AgentConfig.get_harvest_config()
            
            # Create enhanced system message
            enhanced_message = base_config["system_message"] + context_block
            
            # Get tools for this agent
            tools = self._get_tools_for_agent(agent_key)
            
            # RECREATE agent with enhanced system message
            self.agents[agent_key] = AssistantAgent(
                name=base_config["name"],
                system_message=enhanced_message,
                model_client=self.model_client,
                tools=tools
            )
            
            print(f"      ✓ {agent_key} agent recreated with context")
        
        # RECREATE group chat with updated agents
        print(f"    Recreating group chat with updated agents...")
        self._setup_group_chat()
        print(f"      ✓ Group chat recreated")
        
        print(f"  ✅ All agents updated with farmer context\n")
    
    def _build_conversation_context(self) -> str:
        """
        Build context string from conversation history and farmer info
        
        THIS IS KEY: Agents get conversation memory!
        """
        context_parts = []
        
        # Add farmer context if available
        if any(v for v in self.farmer_context.values() if v):
            context_parts.append("="*60)
            context_parts.append("FARMER INFORMATION (already provided, do NOT ask again):")
            context_parts.append("="*60)
            for key, value in self.farmer_context.items():
                if value:
                    context_parts.append(f"  • {key.replace('_', ' ').title()}: {value}")
            context_parts.append("")
            context_parts.append("IMPORTANT: Do NOT ask for information already provided above!")
            context_parts.append("="*60)
            context_parts.append("")
        
        # Add recent conversation history (last 4 exchanges)
        history = self.logger.get_conversation()
        if len(history) > 1:
            context_parts.append("RECENT CONVERSATION HISTORY:")
            context_parts.append("-"*60)
            for msg in history[-8:]:  # Last 8 messages (4 exchanges)
                speaker = msg.get("speaker", "Unknown")
                content = msg.get("message", "")
                # Show full message (agents need context)
                context_parts.append(f"{speaker}: {content}")
            context_parts.append("-"*60)
            context_parts.append("")
        
        # Add current phase context
        context_parts.append(f"CURRENT CROP PHASE: {self.current_phase}")
        context_parts.append("")
        
        return "\n".join(context_parts)
    
    async def process_message(self, farmer_message: str) -> Dict:
        """
        🔥 ENHANCED: Process a message with dynamic agent context updates
        
        Key improvements:
        1. Extract farmer info from message
        2. UPDATE agent system messages with farmer context
        3. Include conversation history in message
        4. Run group chat
        5. Select best response
        """
        
        print(f"\n{'='*60}")
        print(f"  Processing Farmer Message")
        print(f"{'='*60}")
        print(f"  Message: '{farmer_message[:100]}{'...' if len(farmer_message) > 100 else ''}'")
        print(f"  Phase: {self.current_phase}")
        print(f"{'='*60}\n")
        
        # 1. Extract any farmer info from message
        self._extract_farmer_info(farmer_message)
        
        # 2. 🔥 UPDATE AGENT CONTEXTS - This is the key fix!
        self._update_agent_contexts()
        
        # Log farmer message
        self.logger.log("Farmer", farmer_message)
        responses = []
        
        try:
            # 3. Build conversation context
            context = self._build_conversation_context()
            
            # Create message WITH context
            full_message = f"{context}\nFARMER'S CURRENT QUESTION:\n{farmer_message}"
            
            print(f"  📝 Built context ({len(context)} chars)")
            print(f"  📤 Sending to all agents via RoundRobinGroupChat...")
            
            # Create task message
            task_message = TextMessage(
                content=full_message,
                source="Farmer"
            )
            
            # 4. Run the group chat (all agents respond)
            print(f"  ⏳ Running RoundRobinGroupChat...")
            result = await self.group_chat.run(task=task_message)
            
            print(f"  ✓ Chat completed\n")
            
            # 5. Extract agent responses
            print(f"  📥 Extracting agent responses...")
            responses = self._extract_responses(result)
            
            if not responses:
                print(f"  ⚠ No responses extracted")
            
            # Log all responses
            for response in responses:
                self.logger.log(response["agent"], response["message"])
            
            # 6. Select most relevant response
            if responses:
                final_response, selected_agent = self._get_most_relevant_response(responses, farmer_message)
            else:
                final_response = "I'm processing your request. Could you provide more details?"
                selected_agent = "System"
            
            print(f"\n  ✅ Final response from {selected_agent} ({len(final_response)} chars)")
            print(f"{'='*60}\n")
            
            return {
                "final_response": final_response,
                "selected_agent": selected_agent,
                "agent_debate": responses,
                "conversation_history": self.logger.get_conversation(),
                "active_agents": list(set(r["agent"] for r in responses)),
                "phase": self.current_phase,
                "farmer_context": self.farmer_context,
                "success": True
            }
            
        except Exception as e:
            print(f"\n  ❌ ERROR in process_message:")
            print(f"  {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            return {
                "final_response": f"I encountered an issue: {str(e)}. Please try again.",
                "agent_debate": [],
                "conversation_history": self.logger.get_conversation(),
                "active_agents": [],
                "phase": self.current_phase,
                "success": False,
                "error": str(e)
            }
    
    def _extract_responses(self, result) -> List[Dict]:
        """Extract agent responses from chat result"""
        responses = []
        
        try:
            messages = []
            
            if hasattr(result, 'messages'):
                messages = result.messages
                print(f"    Found {len(messages)} messages in result.messages")
            elif hasattr(result, 'chat_history'):
                messages = result.chat_history
                print(f"    Found {len(messages)} messages in result.chat_history")
            elif isinstance(result, list):
                messages = result
                print(f"    Result is list with {len(messages)} items")
            
            for i, msg in enumerate(messages):
                agent_name = None
                content = None
                
                if hasattr(msg, 'source'):
                    agent_name = msg.source
                elif hasattr(msg, 'name'):
                    agent_name = msg.name
                elif isinstance(msg, dict):
                    agent_name = msg.get('source') or msg.get('name')
                
                if hasattr(msg, 'content'):
                    content = msg.content
                elif isinstance(msg, dict):
                    content = msg.get('content')
                elif isinstance(msg, str):
                    content = msg
                
                if agent_name and content and agent_name not in ["Farmer", "System", "user"]:
                    if not any(r["agent"] == agent_name and r["message"] == content for r in responses):
                        responses.append({
                            "agent": agent_name,
                            "message": str(content),
                            "timestamp": datetime.now().isoformat()
                        })
                        print(f"    ✓ Added response from {agent_name}")
            
            print(f"  Total responses extracted: {len(responses)}")
            
        except Exception as e:
            print(f"  ⚠ Error extracting responses: {e}")
        
        return responses
    
    def _get_most_relevant_response(self, responses: List[Dict], farmer_message: str) -> tuple[str, str]:
        """
        Select most relevant response based on:
        1. Message content (what farmer is asking about)
        2. Current phase (preference for phase-appropriate agent)
        
        Returns: (response_text, agent_name)
        """
        if not responses:
            return "No response available.", "System"
        
        print(f"\n  🎯 Selecting most relevant response...")
        print(f"  Current phase: {self.current_phase}")
        print(f"  Farmer message: '{farmer_message[:60]}...'")
        
        # Keyword-based topic detection
        message_lower = farmer_message.lower()
        
        # Topic keywords for each agent
        pre_sowing_keywords = ["plant", "sow", "crop", "choose", "select", "recommend", "soil", "season", "weather forecast", "which crop"]
        growth_keywords = ["grow", "water", "fertilizer", "leaves", "health", "disease", "pest", "yellow", "brown", "tall", "height"]
        harvest_keywords = ["harvest", "sell", "market", "price", "profit", "ready", "mature", "mandi"]
        
        # Score each response
        scores = []
        for response in responses:
            agent_name = response["agent"]
            score = 0
            
            # Agent name cleanup
            agent_type = None
            if "presowing" in agent_name.lower() or "pre-sowing" in agent_name.lower():
                agent_type = "pre_sowing"
            elif "growth" in agent_name.lower():
                agent_type = "growth"
            elif "harvest" in agent_name.lower():
                agent_type = "harvest"
            
            # Keyword matching
            if agent_type == "pre_sowing":
                score += sum(10 for kw in pre_sowing_keywords if kw in message_lower)
            elif agent_type == "growth":
                score += sum(10 for kw in growth_keywords if kw in message_lower)
            elif agent_type == "harvest":
                score += sum(10 for kw in harvest_keywords if kw in message_lower)
            
            # Phase bonus (prefer current phase agent, but don't make it dominant)
            if agent_type == self.current_phase:
                score += 5
            
            # Response quality heuristics
            response_text = response["message"]
            
            # Penalize very short responses (likely not helpful)
            if len(response_text) < 50:
                score -= 20
            
            # Reward responses that ask clarifying questions (shows engagement)
            if "?" in response_text:
                score += 3
            
            # Reward responses with specific recommendations
            if any(word in response_text.lower() for word in ["recommend", "suggest", "should", "would advise"]):
                score += 5
            
            scores.append((score, agent_name, response_text))
            print(f"    {agent_name}: score={score}")
        
        # Sort by score (highest first)
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Return highest scoring response
        selected_score, selected_agent, selected_text = scores[0]
        print(f"  ✓ Selected {selected_agent} (score: {selected_score})\n")
        
        return selected_text, selected_agent
    
    def update_phase(self, new_phase: str):
        """Update current phase"""
        if new_phase not in ["pre_sowing", "growth", "harvest"]:
            raise ValueError(f"Invalid phase: {new_phase}")
        
        old_phase = self.current_phase
        self.current_phase = new_phase
        print(f"\n  ✓ Phase updated: {old_phase} → {new_phase}\n")
    
    def get_conversation_summary(self) -> Dict:
        """Get conversation summary for database"""
        return self.logger.export_for_db()
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.logger.get_conversation()
    
    def reset_conversation(self):
        """Reset conversation and farmer context"""
        self._setup_group_chat()
        self.logger = ConversationLogger(self.season_id)
        self.farmer_context = {
            "soil_type": None,
            "location": None,
            "previous_crop": None,
            "farmer_type": self.farmer_type,
            "current_crop": None
        }
        print(f"  ✓ Conversation reset for season {self.season_id}")
    
    def get_agents_info(self) -> Dict:
        """Get agent information"""
        return {
            "pre_sowing": {
                "name": self.agents["pre_sowing"].name,
                "role": "Crop planning and soil analysis",
                "active": self.current_phase == "pre_sowing"
            },
            "growth": {
                "name": self.agents["growth"].name,
                "role": "Growth monitoring and adaptation",
                "active": self.current_phase == "growth"
            },
            "harvest": {
                "name": self.agents["harvest"].name,
                "role": "Harvest timing and market guidance",
                "active": self.current_phase == "harvest"
            },
            "current_phase": self.current_phase,
            "farmer_type": self.farmer_type,
            "season_id": self.season_id,
            "farmer_context": self.farmer_context
        }


def create_orchestrator(
    season_id: int,
    phase: str = "pre_sowing",
    farmer_type: str = "traditional"
) -> FarmingAgentOrchestrator:
    """Factory function to create orchestrator instance"""
    return FarmingAgentOrchestrator(season_id, phase, farmer_type)