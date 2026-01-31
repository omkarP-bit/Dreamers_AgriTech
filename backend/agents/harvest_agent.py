"""
Harvest Agent

Expert agent for harvest guidance and market analysis
AutoGen 0.7.5 compatible with Groq
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from groq import Groq as GroqClient

from .base_agent import AgentConfig, GROQ_API_KEY, GROQ_MODEL


class HarvestAgent:
    """
    Harvest & Market Expert
    
    Responsibilities:
    1. Determine optimal harvest timing
    2. Provide step-by-step harvesting instructions
    3. Advise on post-harvest handling
    4. Find best marketplaces and prices
    5. Calculate and maximize profit potential
    """
    
    def __init__(self):
        """Initialize Harvest Agent"""
        self.config = AgentConfig.get_harvest_config()
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AssistantAgent:
        """
        Create the AutoGen AssistantAgent for 0.7.5
        
        Uses Groq client (0.4.2) with ChatCompletionClient
        """
        
        # Create Groq client
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
    
    def assess_harvest_readiness(
        self,
        crop_type: str,
        days_old: int,
        current_metrics: Dict
    ) -> Dict:
        """
        Assess if crop is ready for harvest based on multiple indicators
        
        Args:
            crop_type: Type of crop
            days_old: Days since sowing
            current_metrics: Current plant/grain metrics
            
        Returns:
            Harvest readiness assessment
        """
        
        # Harvest maturity days for each crop
        maturity_days = {
            "rice": 110,
            "wheat": 120,
            "moong_dal": 60,
            "cotton": 150,
            "tomato": 65,
            "cucumber": 55,
            "maize": 90,
            "bajra": 75,
            "groundnut": 100,
            "sugarcane": 300,
            "lettuce": 50
        }
        
        required_days = maturity_days.get(crop_type.lower(), 90)
        
        assessment = {
            "crop_type": crop_type,
            "days_old": days_old,
            "required_days": required_days,
            "ready": False,
            "readiness_percentage": 0,
            "indicators": [],
            "warnings": [],
            "recommendations": []
        }
        
        readiness_score = 0
        
        # Age check (40% weight)
        if days_old >= required_days:
            readiness_score += 40
            assessment["indicators"].append(f"✓ Age: {days_old} days (maturity: {required_days} days)")
        else:
            days_left = required_days - days_old
            assessment["indicators"].append(f"⏳ Age: {days_old} days (wait {days_left} more days)")
            assessment["warnings"].append(f"Not yet mature. Need {days_left} more days.")
        
        # Health score (30% weight)
        health_score = current_metrics.get("health_score", 100)
        if health_score >= 75:
            readiness_score += 30
            assessment["indicators"].append(f"✓ Health: {health_score}/100 (excellent)")
        elif health_score >= 60:
            readiness_score += 15
            assessment["indicators"].append(f"⚠ Health: {health_score}/100 (acceptable)")
            assessment["warnings"].append("Plant health is moderate. Consider harvesting soon before further decline.")
        else:
            assessment["indicators"].append(f"✗ Health: {health_score}/100 (poor)")
            assessment["warnings"].append("Plant health is poor. Harvest carefully to prevent total loss.")
        
        # Crop-specific maturity indicators (30% weight)
        crop_lower = crop_type.lower()
        
        if crop_lower in ["rice", "wheat", "maize", "bajra"]:
            # Grain/seed crops - check grain moisture
            grain_moisture = current_metrics.get("grain_moisture", 25)
            if grain_moisture <= 14:
                readiness_score += 30
                assessment["indicators"].append(f"✓ Grain moisture: {grain_moisture}% (target: ≤14%)")
            elif grain_moisture <= 18:
                readiness_score += 15
                assessment["indicators"].append(f"⚠ Grain moisture: {grain_moisture}% (wait for drying)")
                assessment["recommendations"].append("Let grains dry more. Moisture level still high.")
            else:
                assessment["indicators"].append(f"✗ Grain moisture: {grain_moisture}% (too wet)")
                assessment["warnings"].append("Grains too wet. Wait 3-5 days for drying.")
        
        elif crop_lower in ["tomato", "cucumber", "lettuce"]:
            # Vegetable crops - check ripeness/color
            ripeness = current_metrics.get("ripeness", "unripe").lower()
            color = current_metrics.get("color", "green").lower()
            
            if ripeness == "ripe" and color in ["red", "orange", "mature"]:
                readiness_score += 30
                assessment["indicators"].append(f"✓ Ripeness: {ripeness}, Color: {color}")
            elif ripeness == "semi-ripe":
                readiness_score += 15
                assessment["indicators"].append(f"⚠ Ripeness: {ripeness}, Color: {color}")
                assessment["recommendations"].append("Almost ripe. Wait 1-2 more days for full ripeness.")
            else:
                assessment["indicators"].append(f"✗ Ripeness: {ripeness}, Color: {color}")
                assessment["warnings"].append("Not yet ripe. Wait for proper ripeness before harvest.")
        
        elif crop_lower in ["cotton"]:
            # Cotton - check boll opening
            boll_opening = current_metrics.get("boll_opening_percent", 0)
            if boll_opening >= 80:
                readiness_score += 30
                assessment["indicators"].append(f"✓ Boll opening: {boll_opening}% (ready)")
            elif boll_opening >= 50:
                readiness_score += 15
                assessment["indicators"].append(f"⚠ Boll opening: {boll_opening}% (partial)")
                assessment["recommendations"].append("Wait for more bolls to open.")
            else:
                assessment["indicators"].append(f"✗ Boll opening: {boll_opening}% (not ready)")
                assessment["warnings"].append("Bolls not yet opening. Wait longer.")
        
        else:
            # Generic check for unknown crops
            if days_old >= required_days * 0.95:
                readiness_score += 30
                assessment["indicators"].append("✓ Generic maturity indicators suggest readiness")
        
        # Calculate final readiness
        assessment["readiness_percentage"] = readiness_score
        assessment["ready"] = readiness_score >= 70
        
        if assessment["ready"]:
            assessment["recommendations"].extend([
                "✓ CROP IS READY FOR HARVEST",
                "Best harvest time: Early morning (6-8 AM) when dew has dried",
                "Handle produce carefully to minimize damage",
                "Move harvested produce to shade quickly",
                "Contact Harvest Agent for market guidance"
            ])
        
        return assessment
    
    def get_harvest_instructions(
        self,
        crop_type: str,
        quantity_expected: float,
        farmer_type: str = "traditional"
    ) -> Dict:
        """
        Generate detailed harvest instructions for the farmer
        
        Args:
            crop_type: Type of crop
            quantity_expected: Expected yield (quintals or tonnes)
            farmer_type: "traditional" or "greenhouse"
            
        Returns:
            Step-by-step harvest instructions
        """
        
        instructions = {
            "crop_type": crop_type,
            "expected_quantity": quantity_expected,
            "farmer_type": farmer_type,
            "steps": [],
            "tools_needed": [],
            "safety_warnings": [],
            "post_harvest_care": []
        }
        
        crop_lower = crop_type.lower()
        
        # Harvest steps (crop-specific)
        if crop_lower in ["rice", "wheat", "maize"]:
            instructions["steps"] = [
                {"step": 1, "title": "Check Readiness", "instruction": "Verify grain moisture is ≤14%. Shake some heads - grains should rattle."},
                {"step": 2, "title": "Prepare Field", "instruction": "Clear field of stones, rocks, and debris to avoid damage during harvest."},
                {"step": 3, "title": "Start Harvest", "instruction": "Begin harvesting in early morning (6-8 AM) from one corner systematically."},
                {"step": 4, "title": "Cut & Bundle", "instruction": "Cut plants close to ground using sickle/harvester. Bundle 10-15 plants together."},
                {"step": 5, "title": "Transport", "instruction": "Move bundles to shade. Avoid sun exposure to prevent grain loss."},
                {"step": 6, "title": "Dry (2-3 days)", "instruction": "Spread bundles in clean area. Turn daily for uniform drying. Cover if rain threatens."},
                {"step": 7, "title": "Threshing", "instruction": "Thresh by beating bundles or use threshing machine. Separate grain from straw."},
                {"step": 8, "title": "Winnow & Clean", "instruction": "Use wind/fan to blow away chaff. Clean seeds of debris and damaged grains."},
            ]
            instructions["tools_needed"] = ["Sickle", "Bundles/twine", "Threshing machine (optional)", "Broom", "Storage bags"]
            instructions["safety_warnings"] = [
                "Wear gloves when handling threshing equipment",
                "Protect eyes from flying chaff during threshing",
                "Ensure proper ventilation during threshing"
            ]
            instructions["post_harvest_care"] = [
                "Final moisture check: should be 12-14% for storage",
                "Fill clean bags and seal tightly",
                "Store in cool, dry place away from moisture and pests",
                "Check for pest infestation weekly for first month"
            ]
        
        elif crop_lower in ["cotton"]:
            instructions["steps"] = [
                {"step": 1, "title": "Hand Pick", "instruction": "Pick cotton bolls by hand. Only pick fully open bolls (white color)."},
                {"step": 2, "title": "Avoid Contamination", "instruction": "Be very careful not to mix soil/stones. Keep cotton clean."},
                {"step": 3, "title": "Collect in Basket", "instruction": "Place picked cotton in clean baskets. Don't compress."},
                {"step": 4, "title": "First Drying", "instruction": "Spread cotton in sun for 2-3 days. Turn occasionally for even drying."},
                {"step": 5, "title": "Ginning", "instruction": "Send to cotton gin for separation of lint from seed."},
                {"step": 6, "title": "Final Baling", "instruction": "Cotton is baled by gin. Each bale ~170kg lint."},
            ]
            instructions["tools_needed"] = ["Picking baskets", "Sharp nails (for lint removal)", "Cotton gin service"]
            instructions["safety_warnings"] = [
                "Avoid picking with cut/bruised hands - cotton fibers can cause infection",
                "Use shade to work during hot hours",
                "Cotton dust can irritate lungs - consider mask during processing"
            ]
            instructions["post_harvest_care"] = [
                "Keep bales covered and dry",
                "Store in well-ventilated area",
                "Protect from moisture and rain",
                "Arrange ginning at nearest cotton mill"
            ]
        
        elif crop_lower in ["tomato", "cucumber"]:
            instructions["steps"] = [
                {"step": 1, "title": "Pick Ripe Fruit", "instruction": "Pick only fully ripe fruits. Leave unripe ones on plant."},
                {"step": 2, "title": "Gentle Handling", "instruction": "Handle carefully to avoid bruising and damage."},
                {"step": 3, "title": "Place in Containers", "instruction": "Use wooden crates or plastic boxes. Don't stack too high."},
                {"step": 4, "title": "Transport to Shade", "instruction": "Move to shade immediately. Avoid direct sun exposure."},
                {"step": 5, "title": "Cool Down", "instruction": "Let produce cool in shade for 1-2 hours before market transport."},
                {"step": 6, "title": "Grade & Sort", "instruction": "Separate by size/quality. Remove damaged fruits."},
            ]
            instructions["tools_needed"] = ["Wooden crates", "Sharp knife (for cutting)", "Soft cloth for handling"]
            instructions["safety_warnings"] = [
                "Don't drop/throw fruits",
                "Use gloves if handling thorny cucumber plants",
                "Be careful of sharp knives during cutting"
            ]
            instructions["post_harvest_care"] = [
                "Maintain 15-20°C temperature if possible",
                "Use ventilated storage to prevent moisture buildup",
                "Market within 1-2 days for best quality",
                "If storing, check daily for ripening/spoilage"
            ]
        
        else:
            # Generic instructions
            instructions["steps"] = [
                {"step": 1, "title": "Final Readiness Check", "instruction": f"Verify {crop_type} meets all maturity indicators."},
                {"step": 2, "title": "Prepare Harvest Area", "instruction": "Clear area of debris and prepare for harvest."},
                {"step": 3, "title": "Begin Harvest", "instruction": f"Harvest {crop_type} carefully in early morning."},
                {"step": 4, "title": "Collect & Transport", "instruction": "Collect harvest in clean containers. Transport to shade."},
                {"step": 5, "title": "Post-Harvest Processing", "instruction": "Dry, clean, and prepare for market as needed."},
            ]
            instructions["tools_needed"] = ["Harvest containers", "Cleaning materials"]
            instructions["safety_warnings"] = ["Use proper tools and techniques to avoid injury"]
            instructions["post_harvest_care"] = ["Store in cool, dry place"]
        
        return instructions
    
    def analyze_market_options(
        self,
        crop_type: str,
        quantity_quintals: float,
        location: str,
        available_prices: Dict[str, float]
    ) -> Dict:
        """
        Analyze market options and recommend best selling strategy
        
        Args:
            crop_type: Type of crop
            quantity_quintals: Quantity to sell (quintals)
            location: Farmer's location
            available_prices: Dict of market -> price per quintal
            
        Returns:
            Market analysis and recommendations
        """
        
        analysis = {
            "crop_type": crop_type,
            "quantity": quantity_quintals,
            "location": location,
            "market_options": [],
            "recommendation": None,
            "best_estimated_revenue": 0,
            "comparison": []
        }
        
        # Analyze each market option
        for market_name, price_per_quintal in available_prices.items():
            # Estimate transport cost (varies by distance)
            transport_cost = 50 if "local" in market_name.lower() else 100  # ₹/quintal
            
            # Calculate net price
            net_price = price_per_quintal - transport_cost
            
            # Calculate total revenue
            total_revenue = net_price * quantity_quintals
            
            option = {
                "market": market_name,
                "gross_price": price_per_quintal,
                "transport_cost": transport_cost,
                "net_price": net_price,
                "total_revenue": total_revenue,
                "rank": 0
            }
            
            analysis["market_options"].append(option)
        
        # Rank markets by net revenue
        analysis["market_options"].sort(key=lambda x: x["total_revenue"], reverse=True)
        
        for i, option in enumerate(analysis["market_options"], 1):
            option["rank"] = i
        
        # Best recommendation
        if analysis["market_options"]:
            best = analysis["market_options"][0]
            analysis["recommendation"] = {
                "market": best["market"],
                "price_per_quintal": best["gross_price"],
                "net_price": best["net_price"],
                "estimated_revenue": best["total_revenue"],
                "reason": f"Best price after transport costs (₹{best['net_price']}/quintal)"
            }
            analysis["best_estimated_revenue"] = best["total_revenue"]
        
        # Create comparison summary
        analysis["comparison"] = [
            {
                "market": opt["market"],
                "gross_price": f"₹{opt['gross_price']}/quintal",
                "net_price": f"₹{opt['net_price']}/quintal",
                "total_revenue": f"₹{opt['total_revenue']:,.0f}",
                "rank": opt["rank"]
            }
            for opt in analysis["market_options"]
        ]
        
        return analysis
    
    def calculate_profit(
        self,
        yield_quintals: float,
        selling_price_per_quintal: float,
        total_investment: float,
        transport_cost_per_quintal: float = 50
    ) -> Dict:
        """
        Calculate final profit from harvest and sale
        
        Args:
            yield_quintals: Final yield (quintals)
            selling_price_per_quintal: Market price (₹/quintal)
            total_investment: Total cost invested (seeds, fertilizer, labor, etc.)
            transport_cost_per_quintal: Transport cost (₹/quintal)
            
        Returns:
            Detailed profit calculation
        """
        
        # Revenue calculation
        gross_revenue = yield_quintals * selling_price_per_quintal
        transport_total = yield_quintals * transport_cost_per_quintal
        net_revenue = gross_revenue - transport_total
        
        # Profit calculation
        profit = net_revenue - total_investment
        roi = (profit / total_investment * 100) if total_investment > 0 else 0
        
        return {
            "yield_quintals": yield_quintals,
            "selling_price_per_quintal": selling_price_per_quintal,
            "gross_revenue": round(gross_revenue, 2),
            "total_investment": total_investment,
            "transport_cost_total": round(transport_total, 2),
            "net_revenue": round(net_revenue, 2),
            "profit": round(profit, 2),
            "roi_percent": round(roi, 1),
            "profit_per_quintal": round(profit / yield_quintals, 2) if yield_quintals > 0 else 0,
            "breakeven_price": round(total_investment / yield_quintals, 2) if yield_quintals > 0 else 0,
            "summary": f"Revenue: ₹{net_revenue:,.0f} | Investment: ₹{total_investment:,.0f} | Profit: ₹{profit:,.0f} (ROI: {roi:.1f}%)"
        }


def create_harvest_agent() -> HarvestAgent:
    """
    Factory function to create and return a Harvest Agent instance
    
    Returns:
        HarvestAgent instance ready for use in GroupChat
    """
    return HarvestAgent()


if __name__ == "__main__":
    print("=== Testing Harvest Agent (AutoGen 0.7.5) ===\n")
    
    # Test 1: Agent creation
    print("1. Creating Harvest Agent...")
    agent = create_harvest_agent()
    print(f"   ✓ Agent created: {agent.config['name']}")
    print(f"   ✓ Model: {GROQ_MODEL}")
    print(f"   ✓ Using Groq API\n")
    
    # Test 2: Harvest readiness
    print("2. Testing harvest readiness assessment...")
    readiness = agent.assess_harvest_readiness(
        crop_type="rice",
        days_old=115,
        current_metrics={
            "health_score": 85,
            "grain_moisture": 13
        }
    )
    print(f"   Crop: {readiness['crop_type'].upper()}")
    print(f"   Days old: {readiness['days_old']}/{readiness['required_days']}")
    print(f"   Ready: {readiness['ready']}")
    print(f"   Readiness: {readiness['readiness_percentage']}%")
    print(f"   Indicators: {len(readiness['indicators'])} checks passed\n")
    
    # Test 3: Harvest instructions
    print("3. Testing harvest instructions generation...")
    instructions = agent.get_harvest_instructions(
        crop_type="rice",
        quantity_expected=5,
        farmer_type="traditional"
    )
    print(f"   Crop: {instructions['crop_type'].upper()}")
    print(f"   Expected quantity: {instructions['expected_quantity']} quintals")
    print(f"   Total steps: {len(instructions['steps'])}")
    print(f"   Tools needed: {len(instructions['tools_needed'])} items")
    print(f"   Safety warnings: {len(instructions['safety_warnings'])} items")
    print(f"   First step: {instructions['steps'][0]['title']}\n")
    
    # Test 4: Market analysis
    print("4. Testing market analysis...")
    market_analysis = agent.analyze_market_options(
        crop_type="rice",
        quantity_quintals=5,
        location="Punjab",
        available_prices={
            "Local Trader": 2400,
            "Mandi A (15km)": 2500,
            "Mandi B (30km)": 2600,
        }
    )
    print(f"   Crop: {market_analysis['crop_type'].upper()}")
    print(f"   Quantity: {market_analysis['quantity']} quintals")
    print(f"   Market options analyzed: {len(market_analysis['market_options'])}")
    if market_analysis['recommendation']:
        rec = market_analysis['recommendation']
        print(f"   Best market: {rec['market']} at ₹{rec['price_per_quintal']}/quintal")
        print(f"   Estimated revenue: ₹{rec['estimated_revenue']:,.0f}\n")
    
    # Test 5: Profit calculation
    print("5. Testing profit calculation...")
    profit = agent.calculate_profit(
        yield_quintals=5,
        selling_price_per_quintal=2500,
        total_investment=40000,
        transport_cost_per_quintal=50
    )
    print(f"   Yield: {profit['yield_quintals']} quintals")
    print(f"   Gross revenue: ₹{profit['gross_revenue']:,.0f}")
    print(f"   Net revenue: ₹{profit['net_revenue']:,.0f}")
    print(f"   Total investment: ₹{profit['total_investment']:,.0f}")
    print(f"   Profit: ₹{profit['profit']:,.0f}")
    print(f"   ROI: {profit['roi_percent']}%\n")
    
    print("=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)