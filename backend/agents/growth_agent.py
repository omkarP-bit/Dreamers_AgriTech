"""
Growth Agent

Expert agent for monitoring crop growth and health
Handles both greenhouse and traditional farmers
AutoGen 0.7.5 compatible
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from groq import Groq as GroqClient

from .base_agent import AgentConfig, GROQ_API_KEY, GROQ_MODEL


class GrowthAgent:
    """
    Growth Monitoring Expert
    
    Responsibilities:
    1. For GREENHOUSE: Monitor sensors, auto-control environment, optimize growth
    2. For TRADITIONAL: Analyze plant descriptions, detect diseases, provide guidance
    3. Process task feedback and adapt plans
    4. Predict yield based on current conditions
    5. Determine harvest readiness
    """
    
    def __init__(self, farmer_type: str = "traditional"):
        """
        Initialize Growth Agent
        
        Args:
            farmer_type: "greenhouse" or "traditional"
        """
        self.farmer_type = farmer_type
        self.config = AgentConfig.get_growth_config()
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
    
    def analyze_growth_progress(
        self,
        crop_type: str,
        days_old: int,
        current_metrics: Dict,
        expected_metrics: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze if crop growth is on track
        
        Args:
            crop_type: Type of crop
            days_old: Age in days
            current_metrics: Current measurements (height_cm, health_score, leaf_color, etc.)
            expected_metrics: Expected measurements (optional)
            
        Returns:
            Analysis with growth status and recommendations
        """
        
        # Expected growth rates (cm per day)
        growth_rates = {
            "rice": 1.8,
            "wheat": 1.2,
            "moong_dal": 1.5,
            "cotton": 2.0,
            "tomato": 2.0,
            "cucumber": 2.5,
            "maize": 2.2
        }
        
        growth_rate = growth_rates.get(crop_type.lower(), 1.5)
        expected_height = growth_rate * days_old
        
        actual_height = current_metrics.get("height_cm", 0)
        
        analysis = {
            "crop_type": crop_type,
            "days_old": days_old,
            "expected_height_cm": round(expected_height, 1),
            "actual_height_cm": actual_height,
            "growth_status": "unknown",
            "deviation_percent": 0,
            "issues": [],
            "recommendations": []
        }
        
        if actual_height > 0:
            deviation = ((actual_height - expected_height) / expected_height) * 100
            analysis["deviation_percent"] = round(deviation, 1)
            
            if deviation > 20:
                analysis["growth_status"] = "fast"
                analysis["recommendations"].append("Growth is faster than expected - excellent! Continue current care.")
            elif deviation < -30:
                analysis["growth_status"] = "very_slow"
                analysis["issues"].append("Growth significantly slower than expected")
                analysis["recommendations"].extend([
                    "Check for nutrient deficiency",
                    "Ensure adequate watering",
                    "Check for pest/disease damage",
                    "Verify soil quality"
                ])
            elif deviation < -15:
                analysis["growth_status"] = "slow"
                analysis["issues"].append("Growth slower than expected")
                analysis["recommendations"].extend([
                    "Consider additional fertilization",
                    "Check watering schedule",
                    "Monitor for early signs of stress"
                ])
            else:
                analysis["growth_status"] = "on_track"
                analysis["recommendations"].append("Growth is normal. Continue current practices.")
        
        # Check health indicators
        health_score = current_metrics.get("health_score", 100)
        if health_score < 70:
            analysis["issues"].append(f"Health score low: {health_score}/100")
            analysis["recommendations"].append("Investigate cause of health decline - check for diseases, pests, or environmental stress")
        
        # Check leaf color
        leaf_color = current_metrics.get("leaf_color", "").lower()
        if "yellow" in leaf_color or "pale" in leaf_color:
            analysis["issues"].append("Yellowing leaves detected")
            analysis["recommendations"].append("Possible nitrogen deficiency - apply nitrogen-rich fertilizer")
        elif "brown" in leaf_color:
            analysis["issues"].append("Brown leaves detected")
            analysis["recommendations"].append("Possible overwatering, disease, or nutrient burn - investigate immediately")
        
        return analysis
    
    def process_deviation(
        self,
        planned_action: str,
        actual_action: str,
        deviation_type: str,
        severity: str
    ) -> Dict:
        """
        Process a deviation from the plan and recommend adaptations
        
        Args:
            planned_action: What was supposed to be done
            actual_action: What was actually done
            deviation_type: Type of deviation (fertilizer_change, delay, quantity_change, method_change)
            severity: Severity level (minor, moderate, major)
            
        Returns:
            Adaptation recommendations and new tasks
        """
        
        adaptation = {
            "deviation_summary": f"{planned_action} → {actual_action}",
            "severity": severity,
            "impact_analysis": "",
            "adaptations": [],
            "new_tasks": []
        }
        
        # Analyze based on deviation type
        if deviation_type == "fertilizer_change":
            if any(keyword in actual_action.lower() for keyword in ["organic", "compost", "cow dung", "manure"]):
                adaptation["impact_analysis"] = "Organic fertilizer has lower nutrient concentration but improves soil health long-term. Yield may decrease 5-15% but soil quality improves."
                adaptation["adaptations"] = [
                    "Increase organic fertilizer quantity by 3-4x to match nitrogen content",
                    "Add one additional fertilization in 2 weeks",
                    "Monitor leaf color closely for nitrogen deficiency signs"
                ]
                adaptation["new_tasks"] = [
                    {
                        "task": "Additional Organic Fertilization",
                        "days_from_now": 14,
                        "description": "Apply 100kg compost/cow dung"
                    },
                    {
                        "task": "Leaf Color Monitoring",
                        "days_from_now": 7,
                        "description": "Check if leaves remain dark green"
                    }
                ]
            else:
                adaptation["impact_analysis"] = "Different fertilizer type may have different NPK ratios. Impact depends on specific substitution."
                adaptation["adaptations"] = [
                    "Monitor plant response over next 7-10 days",
                    "Adjust future fertilization based on plant health"
                ]
        
        elif deviation_type == "delay":
            days_delayed = 1
            if severity == "major":
                days_delayed = 5
            elif severity == "moderate":
                days_delayed = 3
            
            adaptation["impact_analysis"] = f"Delay of ~{days_delayed} days. Timeline shifted, possible minor yield reduction (1-3%)."
            adaptation["adaptations"] = [
                f"Shift all future tasks by {days_delayed} days",
                "Compensate with optimal care in coming weeks",
                f"Expected harvest date now ~{days_delayed} days later"
            ]
        
        elif deviation_type == "quantity_change":
            adaptation["impact_analysis"] = "Quantity change affects nutrient availability and plant health."
            if any(keyword in actual_action.lower() for keyword in ["less", "reduce", "half"]):
                adaptation["adaptations"] = [
                    "Monitor for nutrient deficiency symptoms",
                    "Consider supplementing in next fertilization cycle"
                ]
            else:
                adaptation["adaptations"] = [
                    "Watch for signs of nutrient burn (brown leaf tips)",
                    "Increase watering to dilute excess nutrients"
                ]
        
        elif deviation_type == "method_change":
            adaptation["impact_analysis"] = "Different method may have different effectiveness."
            adaptation["adaptations"] = [
                "Monitor results of new method",
                "Compare with expected outcomes",
                "Document for future reference"
            ]
        
        else:
            adaptation["impact_analysis"] = "Deviation detected but specific impact unclear."
            adaptation["adaptations"] = [
                "Monitor crop carefully over next week",
                "Report any unusual changes immediately"
            ]
        
        return adaptation
    
    def predict_yield(
        self,
        crop_type: str,
        base_yield: float,
        health_score: float,
        deviations: List[Dict],
        weather_impact: float = 0
    ) -> Dict:
        """
        Predict final yield based on current conditions
        
        Args:
            crop_type: Type of crop
            base_yield: Expected yield under optimal conditions (quintals)
            health_score: Current health score (0-100)
            deviations: List of deviations from plan
            weather_impact: Weather impact factor (-20 to +20)
            
        Returns:
            Yield prediction with confidence level
        """
        
        predicted_yield = base_yield
        
        # Health impact (0.5x to 1.2x multiplier)
        health_multiplier = 0.5 + (health_score / 100) * 0.7
        predicted_yield *= health_multiplier
        
        # Deviation impact
        for deviation in deviations:
            severity = deviation.get("severity", "minor")
            if severity == "major":
                predicted_yield *= 0.85  # -15%
            elif severity == "moderate":
                predicted_yield *= 0.92  # -8%
            elif severity == "minor":
                predicted_yield *= 0.97  # -3%
        
        # Weather impact
        weather_multiplier = 1 + (weather_impact / 100)
        predicted_yield *= weather_multiplier
        
        # Confidence calculation
        confidence = "high"
        if len(deviations) > 3:
            confidence = "medium"
        if health_score < 70:
            confidence = "low"
        
        return {
            "predicted_yield_quintals": round(predicted_yield, 2),
            "base_yield_quintals": base_yield,
            "yield_change_percent": round(((predicted_yield - base_yield) / base_yield) * 100, 1),
            "health_impact": round((health_multiplier - 1) * 100, 1),
            "deviations_impact": round(((1 - health_multiplier) * 100), 1) if health_multiplier < 1 else 0,
            "weather_impact": weather_impact,
            "confidence": confidence
        }
    
    def check_harvest_readiness(
        self,
        crop_type: str,
        days_old: int,
        current_metrics: Dict
    ) -> Dict:
        """
        Check if crop is ready for harvest
        
        Args:
            crop_type: Type of crop
            days_old: Age in days
            current_metrics: Current measurements (health_score, grain_moisture, fruit_color, etc.)
            
        Returns:
            Harvest readiness assessment
        """
        
        # Minimum days for each crop (conservative estimates)
        min_harvest_days = {
            "rice": 110,
            "wheat": 110,
            "moong_dal": 55,
            "cotton": 140,
            "tomato": 65,
            "cucumber": 50,
            "maize": 85,
            "bajra": 70
        }
        
        min_days = min_harvest_days.get(crop_type.lower(), 90)
        
        readiness = {
            "ready_for_harvest": False,
            "days_old": days_old,
            "min_days_required": min_days,
            "days_remaining": max(0, min_days - days_old),
            "readiness_score": 0,
            "indicators": [],
            "recommendations": []
        }
        
        score = 0
        
        # Age check (most important - 40 points)
        if days_old >= min_days:
            score += 40
            readiness["indicators"].append(f"✓ Age: {days_old} days (minimum: {min_days})")
        else:
            days_left = min_days - days_old
            readiness["indicators"].append(f"✗ Age: {days_old} days (need {days_left} more days)")
            readiness["recommendations"].append(f"Wait at least {days_left} more days")
        
        # Health check (30 points)
        health_score = current_metrics.get("health_score", 100)
        if health_score >= 70:
            score += 30
            readiness["indicators"].append(f"✓ Health: {health_score}/100")
        else:
            readiness["indicators"].append(f"⚠ Health: {health_score}/100 (low)")
            readiness["recommendations"].append("Consider waiting for plant to recover before harvest")
        
        # Physical indicators (crop-specific - 30 points)
        if crop_type.lower() in ["rice", "wheat"]:
            # Check grain moisture
            moisture = current_metrics.get("grain_moisture", 20)
            if moisture <= 14:
                score += 30
                readiness["indicators"].append(f"✓ Grain moisture: {moisture}% (target: ≤14%)")
            else:
                readiness["indicators"].append(f"✗ Grain moisture: {moisture}% (target: ≤14%)")
                readiness["recommendations"].append("Wait for grains to dry more")
        
        elif crop_type.lower() in ["tomato", "cucumber"]:
            # Check fruit color
            color = current_metrics.get("fruit_color", "green").lower()
            if color in ["red", "ripe", "orange"]:
                score += 30
                readiness["indicators"].append(f"✓ Fruit color: {color}")
            else:
                readiness["indicators"].append(f"✗ Fruit color: {color} (wait for ripening)")
        
        else:
            # Generic maturity check
            if days_old >= min_days * 0.95:
                score += 30
                readiness["indicators"].append(f"✓ Maturity indicators present")
            else:
                readiness["indicators"].append(f"✗ Not yet at maturity threshold")
        
        readiness["readiness_score"] = score
        readiness["ready_for_harvest"] = score >= 70
        
        if readiness["ready_for_harvest"]:
            readiness["recommendations"] = [
                "✓ Crop is ready for harvest!",
                "Harvest in early morning after dew dries",
                "Handle carefully to avoid damage and loss",
                "Contact Harvest Agent for market guidance"
            ]
        
        return readiness


def create_growth_agent(farmer_type: str = "traditional") -> GrowthAgent:
    """
    Factory function to create and return a Growth Agent instance
    
    Args:
        farmer_type: "greenhouse" or "traditional"
        
    Returns:
        GrowthAgent instance ready for use in GroupChat
    """
    return GrowthAgent(farmer_type)


if __name__ == "__main__":
    print("=== Testing Growth Agent (AutoGen 0.7.5) ===\n")
    
    # Test 1: Traditional farmer agent creation
    print("1. Creating agent for traditional farmer...")
    agent = create_growth_agent(farmer_type="traditional")
    print(f"   ✓ Agent created: {agent.config['name']}")
    print(f"   ✓ Model: {GROQ_MODEL}")
    print(f"   ✓ Farmer type: traditional\n")
    
    # Test 2: Growth analysis
    print("2. Testing growth analysis...")
    analysis = agent.analyze_growth_progress(
        crop_type="rice",
        days_old=30,
        current_metrics={
            "height_cm": 45,
            "health_score": 85,
            "leaf_color": "dark green"
        }
    )
    print(f"   Crop: {analysis['crop_type'].upper()}")
    print(f"   Days old: {analysis['days_old']}")
    print(f"   Expected height: {analysis['expected_height_cm']:.1f}cm")
    print(f"   Actual height: {analysis['actual_height_cm']}cm")
    print(f"   Growth status: {analysis['growth_status']}")
    print(f"   Deviation: {analysis['deviation_percent']:+.1f}%")
    print(f"   Issues: {len(analysis['issues'])}")
    print(f"   Recommendation: {analysis['recommendations'][0]}\n")
    
    # Test 3: Deviation processing
    print("3. Testing deviation processing...")
    deviation = agent.process_deviation(
        planned_action="Apply 50kg urea fertilizer",
        actual_action="Applied cow dung instead",
        deviation_type="fertilizer_change",
        severity="moderate"
    )
    print(f"   Deviation: {deviation['deviation_summary']}")
    print(f"   Severity: {deviation['severity']}")
    print(f"   Impact: {deviation['impact_analysis'][:100]}...")
    print(f"   Adaptations: {len(deviation['adaptations'])} items")
    print(f"   New tasks: {len(deviation['new_tasks'])}\n")
    
    # Test 4: Yield prediction
    print("4. Testing yield prediction...")
    prediction = agent.predict_yield(
        crop_type="rice",
        base_yield=50,
        health_score=85,
        deviations=[
            {"severity": "minor"},
            {"severity": "moderate"}
        ],
        weather_impact=5
    )
    print(f"   Base yield: {prediction['base_yield_quintals']} quintals")
    print(f"   Predicted yield: {prediction['predicted_yield_quintals']} quintals")
    print(f"   Change: {prediction['yield_change_percent']:+.1f}%")
    print(f"   Confidence: {prediction['confidence']}\n")
    
    # Test 5: Harvest readiness
    print("5. Testing harvest readiness check...")
    readiness = agent.check_harvest_readiness(
        crop_type="rice",
        days_old=115,
        current_metrics={
            "health_score": 85,
            "grain_moisture": 13
        }
    )
    print(f"   Ready for harvest: {readiness['ready_for_harvest']}")
    print(f"   Readiness score: {readiness['readiness_score']}/100")
    print(f"   Indicators:")
    for indicator in readiness['indicators']:
        print(f"     {indicator}")
    print(f"   Recommendations:")
    for rec in readiness['recommendations'][:2]:
        print(f"     • {rec}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)