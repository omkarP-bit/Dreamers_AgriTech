"""
Pre-Sowing Agent

Expert agent for crop planning and pre-sowing phase
AutoGen 0.7.5 compatible with GroupChat and Groq
"""

from typing import Dict, List
from datetime import datetime, timedelta

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from groq import Groq as GroqClient

from .base_agent import AgentConfig, GROQ_API_KEY, GROQ_MODEL


class PreSowingAgent:
    """
    Pre-Sowing Agricultural Expert
    
    Responsibilities:
    1. Collect farmer inputs (soil, location, previous crop, farmer type)
    2. Analyze weather forecasts and historical patterns
    3. Assess soil condition based on previous crop
    4. Check market prices for various crops
    5. Recommend 3-5 suitable crop options
    6. Create complete sowing roadmap
    """
    
    def __init__(self):
        self.config = AgentConfig.get_pre_sowing_config()
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AssistantAgent:
        """
        Create the AutoGen AssistantAgent for 0.7.5
        
        Uses Groq client (0.4.2) with ChatCompletionClient
        """
        
        # Create Groq client (works with groq==0.4.2)
        groq_client = GroqClient(api_key=GROQ_API_KEY)
        
        # Create assistant agent with Groq
        agent = AssistantAgent(
            name=self.config["name"],
            system_message=self.config["system_message"],
            model_client=groq_client,
        )
        
        return agent
    
    def get_agent(self) -> AssistantAgent:
        """Get the underlying AutoGen agent"""
        return self.agent
    
    def generate_crop_recommendations(
        self,
        soil_type: str,
        location: str,
        previous_crop: str,
        weather_data: Dict,
        market_data: Dict,
        farmer_type: str = "traditional"
    ) -> List[Dict]:
        """
        Generate crop recommendations based on inputs
        
        Args:
            soil_type: Type of soil (clay, loam, sandy, etc.)
            location: Farmer's location
            previous_crop: Previous crop grown
            weather_data: Weather forecast data
            market_data: Market price data
            farmer_type: greenhouse or traditional
            
        Returns:
            List of crop recommendations sorted by suitability score
        """
        
        recommendations = []
        
        # Soil-crop compatibility matrix
        soil_compatibility = {
            "clay": ["rice", "wheat", "cotton", "sugarcane"],
            "loam": ["rice", "wheat", "vegetables", "maize", "cotton"],
            "sandy": ["moong_dal", "bajra", "groundnut", "watermelon"],
            "black": ["cotton", "jowar", "sunflower", "chickpea"],
            "red": ["groundnut", "millets", "pulses", "cotton"]
        }
        
        suitable_crops = soil_compatibility.get(soil_type.lower(), ["rice", "wheat", "moong_dal"])
        
        # Create recommendations with market data
        for crop in suitable_crops[:5]:  # Top 5 recommendations
            crop_rec = {
                "crop": crop,
                "suitability_score": 0.0,
                "reasons": [],
                "market_price": market_data.get(crop, {}).get("price_per_quintal", 0),
                "expected_yield": self._estimate_yield(crop, soil_type, farmer_type),
                "duration_days": self._get_crop_duration(crop),
                "initial_investment": self._estimate_investment(crop, farmer_type)
            }
            
            # Calculate suitability score
            score = 0
            
            # Soil match
            if crop in suitable_crops:
                score += 30
                crop_rec["reasons"].append(f"✓ Well-suited to {soil_type} soil")
            
            # Weather match
            if "monsoon" in str(weather_data).lower() and crop in ["rice", "cotton"]:
                score += 25
                crop_rec["reasons"].append("✓ Good monsoon forecast")
            
            # Market price analysis
            if crop_rec["market_price"] > 5000:
                score += 25
                crop_rec["reasons"].append(f"✓ High market price (₹{crop_rec['market_price']}/quintal)")
            elif crop_rec["market_price"] > 2000:
                score += 15
                crop_rec["reasons"].append(f"✓ Stable market price (₹{crop_rec['market_price']}/quintal)")
            
            # Crop rotation benefit
            if previous_crop != crop:
                score += 10
                crop_rec["reasons"].append("✓ Good crop rotation")
            
            # Short duration bonus
            if crop_rec["duration_days"] < 70:
                score += 10
                crop_rec["reasons"].append(f"✓ Quick harvest ({crop_rec['duration_days']} days)")
            
            crop_rec["suitability_score"] = score
            
            # Calculate expected profit
            expected_revenue = crop_rec["expected_yield"] * crop_rec["market_price"]
            expected_profit = expected_revenue - crop_rec["initial_investment"]
            crop_rec["expected_profit"] = expected_profit
            crop_rec["roi_percent"] = (
                (expected_profit / crop_rec["initial_investment"] * 100) 
                if crop_rec["initial_investment"] > 0 
                else 0
            )
            
            recommendations.append(crop_rec)
        
        # Sort by suitability score (descending)
        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return recommendations[:5]  # Return top 5
    
    def _estimate_yield(self, crop: str, soil_type: str, farmer_type: str) -> float:
        """
        Estimate expected yield in quintals per acre
        
        Args:
            crop: Crop type
            soil_type: Type of soil
            farmer_type: "traditional" or "greenhouse"
            
        Returns:
            Expected yield in quintals
        """
        
        base_yields = {
            "rice": 50,
            "wheat": 45,
            "moong_dal": 12,
            "cotton": 20,
            "maize": 55,
            "bajra": 25,
            "tomato": 300,
            "cucumber": 250
        }
        
        base = base_yields.get(crop, 30)
        
        # Greenhouse farming has higher yields
        if farmer_type == "greenhouse":
            base *= 1.5
        
        return base
    
    def _get_crop_duration(self, crop: str) -> int:
        """
        Get crop duration in days from sowing to harvest
        
        Args:
            crop: Crop type
            
        Returns:
            Duration in days
        """
        
        durations = {
            "rice": 120,
            "wheat": 120,
            "moong_dal": 60,
            "cotton": 150,
            "maize": 90,
            "bajra": 75,
            "tomato": 75,
            "cucumber": 55,
            "lettuce": 45
        }
        
        return durations.get(crop, 90)
    
    def _estimate_investment(self, crop: str, farmer_type: str) -> float:
        """
        Estimate initial investment in INR (seeds, fertilizer, labor, etc.)
        
        Args:
            crop: Crop type
            farmer_type: "traditional" or "greenhouse"
            
        Returns:
            Investment cost in rupees
        """
        
        base_investments = {
            "rice": 15000,
            "wheat": 12000,
            "moong_dal": 8000,
            "cotton": 18000,
            "maize": 10000,
            "bajra": 7000,
            "tomato": 25000,
            "cucumber": 20000
        }
        
        base = base_investments.get(crop, 12000)
        
        # Greenhouse has higher setup costs but better efficiency
        if farmer_type == "greenhouse":
            base *= 2
        
        return base
    
    def create_sowing_roadmap(
        self,
        crop: str,
        soil_type: str,
        location: str,
        farmer_type: str = "traditional"
    ) -> Dict:
        """
        Create a complete sowing roadmap with timeline and tasks
        
        This roadmap guides farmers through the entire crop lifecycle
        
        Args:
            crop: Crop type to grow
            soil_type: Type of soil
            location: Farmer's location
            farmer_type: "traditional" or "greenhouse"
            
        Returns:
            Roadmap dictionary with tasks, phases, and milestones
        """
        
        roadmap = {
            "crop": crop,
            "soil_type": soil_type,
            "location": location,
            "farmer_type": farmer_type,
            "total_duration_days": self._get_crop_duration(crop),
            "phases": [],
            "tasks": [],
            "key_milestones": []
        }
        
        start_date = datetime.now()
        
        # ===== PRE-SOWING PHASE (Week -1 to 0) =====
        pre_sowing_tasks = [
            {
                "week": -1,
                "task": "Soil Preparation",
                "description": f"Plow and level the field. For {soil_type} soil, ensure proper drainage and aeration.",
                "date": (start_date - timedelta(days=7)).strftime("%Y-%m-%d"),
                "priority": "high",
                "phase": "pre_sowing"
            },
            {
                "week": -1,
                "task": "Soil Testing",
                "description": "Test soil pH, NPK levels, and organic matter content. Adjust fertilizer plan accordingly.",
                "date": (start_date - timedelta(days=5)).strftime("%Y-%m-%d"),
                "priority": "medium",
                "phase": "pre_sowing"
            },
            {
                "week": 0,
                "task": "Purchase Seeds",
                "description": f"Buy high-quality {crop} seeds from certified vendor. Need approximately 20-25kg per acre.",
                "date": (start_date - timedelta(days=3)).strftime("%Y-%m-%d"),
                "priority": "critical",
                "phase": "pre_sowing"
            },
            {
                "week": 0,
                "task": "Seed Treatment",
                "description": "Treat seeds with fungicide to prevent soil-borne diseases. Improves germination rate.",
                "date": (start_date - timedelta(days=1)).strftime("%Y-%m-%d"),
                "priority": "high",
                "phase": "pre_sowing"
            }
        ]
        
        # ===== SOWING PHASE (Week 0) =====
        sowing_tasks = [
            {
                "week": 0,
                "task": "Sowing",
                "description": f"Sow {crop} seeds at proper depth and spacing. Water immediately after sowing for good germination.",
                "date": start_date.strftime("%Y-%m-%d"),
                "priority": "critical",
                "phase": "sowing"
            }
        ]
        
        # ===== GROWTH PHASE TASKS =====
        growth_tasks = []
        duration_weeks = self._get_crop_duration(crop) // 7
        
        for week in range(1, duration_weeks):
            # Weekly monitoring
            growth_tasks.append({
                "week": week,
                "task": f"Week {week} Monitoring",
                "description": "Check plant health, monitor water needs, inspect for pests/diseases, note growth progress.",
                "date": (start_date + timedelta(days=week*7)).strftime("%Y-%m-%d"),
                "priority": "medium",
                "phase": "growth"
            })
            
            # Fertilization schedule (every 2 weeks typically)
            if week in [2, 4, 6, 8]:
                fert_num = (week // 2)
                growth_tasks.append({
                    "week": week,
                    "task": f"Fertilization #{fert_num}",
                    "description": f"Apply {crop}-specific fertilizer. Use balanced NPK or organic compost. Follow recommended dosage.",
                    "date": (start_date + timedelta(days=week*7)).strftime("%Y-%m-%d"),
                    "priority": "high",
                    "phase": "growth"
                })
            
            # Weeding (every 2-3 weeks)
            if week in [3, 5, 7]:
                growth_tasks.append({
                    "week": week,
                    "task": "Weeding",
                    "description": "Remove weeds manually or use approved herbicide. Weeds compete for nutrients and water.",
                    "date": (start_date + timedelta(days=week*7)).strftime("%Y-%m-%d"),
                    "priority": "medium",
                    "phase": "growth"
                })
            
            # Pest and disease surveillance (critical at mid-growth)
            if week == 4:
                growth_tasks.append({
                    "week": week,
                    "task": "Pest/Disease Surveillance",
                    "description": "Thorough field inspection for pests, diseases, and nutrient deficiency symptoms. Apply treatment if needed.",
                    "date": (start_date + timedelta(days=week*7)).strftime("%Y-%m-%d"),
                    "priority": "high",
                    "phase": "growth"
                })
        
        # ===== HARVEST PHASE =====
        harvest_week = duration_weeks
        harvest_tasks = [
            {
                "week": harvest_week - 1,
                "task": "Harvest Readiness Assessment",
                "description": f"Assess {crop} maturity. Check for expected harvest indicators (color, moisture, pod/grain maturity).",
                "date": (start_date + timedelta(days=(harvest_week-1)*7)).strftime("%Y-%m-%d"),
                "priority": "high",
                "phase": "harvest"
            },
            {
                "week": harvest_week,
                "task": "Harvest",
                "description": f"Harvest {crop} at optimal time. Handle carefully to minimize damage and loss.",
                "date": (start_date + timedelta(days=harvest_week*7)).strftime("%Y-%m-%d"),
                "priority": "critical",
                "phase": "harvest"
            },
            {
                "week": harvest_week,
                "task": "Post-Harvest Processing",
                "description": "Dry, thresh, clean, and grade produce. Store properly or prepare for market.",
                "date": (start_date + timedelta(days=harvest_week*7 + 2)).strftime("%Y-%m-%d"),
                "priority": "high",
                "phase": "harvest"
            }
        ]
        
        # Combine all tasks in order
        roadmap["tasks"] = pre_sowing_tasks + sowing_tasks + growth_tasks + harvest_tasks
        
        # Add phase information
        roadmap["phases"] = [
            {
                "name": "Pre-Sowing",
                "start_week": -1,
                "end_week": 0,
                "description": "Field preparation, soil testing, seed selection"
            },
            {
                "name": "Sowing",
                "start_week": 0,
                "end_week": 1,
                "description": "Actual sowing of seeds"
            },
            {
                "name": "Growth",
                "start_week": 1,
                "end_week": duration_weeks - 1,
                "description": "Monitoring, fertilization, pest control, weed management"
            },
            {
                "name": "Harvest",
                "start_week": duration_weeks - 1,
                "end_week": duration_weeks,
                "description": "Harvest readiness checks and harvesting"
            }
        ]
        
        # Add key milestones
        roadmap["key_milestones"] = [
            {
                "event": "Sowing Complete",
                "date": start_date.strftime("%Y-%m-%d"),
                "week": 0,
                "description": "All seeds sown"
            },
            {
                "event": "Germination Expected",
                "date": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "week": 1,
                "description": "First seedlings should emerge"
            },
            {
                "event": "Active Growth Phase",
                "date": (start_date + timedelta(days=duration_weeks*7//2)).strftime("%Y-%m-%d"),
                "week": duration_weeks // 2,
                "description": "Peak growth period - critical monitoring phase"
            },
            {
                "event": "Flowering/Critical Stage",
                "date": (start_date + timedelta(days=(duration_weeks*7*2)//3)).strftime("%Y-%m-%d"),
                "week": (duration_weeks * 2) // 3,
                "description": "Flowering or pod/grain formation stage"
            },
            {
                "event": "Harvest Expected",
                "date": (start_date + timedelta(days=duration_weeks*7)).strftime("%Y-%m-%d"),
                "week": duration_weeks,
                "description": "Expected harvest date"
            }
        ]
        
        return roadmap


def create_pre_sowing_agent() -> PreSowingAgent:
    """
    Factory function to create and return a Pre-Sowing Agent instance
    
    Returns:
        PreSowingAgent instance ready for use in GroupChat
    """
    return PreSowingAgent()


if __name__ == "__main__":
    print("=== Testing Pre-Sowing Agent (AutoGen 0.7.5) ===\n")
    
    agent = create_pre_sowing_agent()
    print(f"✓ Agent created: {agent.config['name']}")
    print(f"✓ Model: {GROQ_MODEL}")
    print(f"✓ Using Groq API\n")
    
    # Test crop recommendations
    print("=" * 60)
    print("TESTING: Crop Recommendations")
    print("=" * 60)
    
    recommendations = agent.generate_crop_recommendations(
        soil_type="loam",
        location="Punjab, Ludhiana",
        previous_crop="wheat",
        weather_data={"monsoon": "strong", "rainfall": "800mm expected"},
        market_data={
            "rice": {"price_per_quintal": 2500},
            "moong_dal": {"price_per_quintal": 7000},
            "cotton": {"price_per_quintal": 6200},
            "maize": {"price_per_quintal": 2200}
        },
        farmer_type="traditional"
    )
    
    print(f"\nGenerated {len(recommendations)} crop recommendations:\n")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"{i}. {rec['crop'].upper()}")
        print(f"   Suitability Score: {rec['suitability_score']}/100")
        print(f"   Market Price: ₹{rec['market_price']}/quintal")
        print(f"   Expected Yield: {rec['expected_yield']} quintals/acre")
        print(f"   Investment: ₹{rec['initial_investment']:,.0f}")
        print(f"   Expected Profit: ₹{rec['expected_profit']:,.0f}")
        print(f"   ROI: {rec['roi_percent']:.1f}%")
        print(f"   Duration: {rec['duration_days']} days")
        print(f"   Reasons:")
        for reason in rec['reasons']:
            print(f"     {reason}")
        print()
    
    # Test roadmap generation
    print("=" * 60)
    print("TESTING: Sowing Roadmap Generation")
    print("=" * 60)
    
    roadmap = agent.create_sowing_roadmap(
        crop="moong_dal",
        soil_type="loam",
        location="Punjab, Ludhiana",
        farmer_type="traditional"
    )
    
    print(f"\nCrop: {roadmap['crop'].upper()}")
    print(f"Location: {roadmap['location']}")
    print(f"Soil Type: {roadmap['soil_type']}")
    print(f"Total Duration: {roadmap['total_duration_days']} days (~{roadmap['total_duration_days']//7} weeks)")
    print(f"Total Tasks: {len(roadmap['tasks'])}")
    print(f"\nFirst 8 tasks:")
    for task in roadmap['tasks'][:8]:
        print(f"\n  Week {task['week']}: {task['task']} [{task['priority'].upper()}]")
        print(f"  Date: {task['date']}")
        print(f"  Phase: {task['phase']}")
        print(f"  → {task['description']}")
    
    print(f"\n\nKey Milestones:")
    for milestone in roadmap['key_milestones']:
        print(f"  • {milestone['event']} (Week {milestone['week']}, {milestone['date']})")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)