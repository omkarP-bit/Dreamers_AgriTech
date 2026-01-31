"""
Plant Analysis Tools

Analyze farmer's natural language descriptions of their plants
to detect diseases, pests, and provide recommendations.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


# Disease/pest symptom database
SYMPTOM_DATABASE = {
    # Leaf color issues
    "yellowing": {
        "possible_causes": ["nitrogen_deficiency", "overwatering", "root_rot", "iron_deficiency"],
        "keywords": ["yellow", "yellowing", "pale", "light colored"],
        "questions": [
            "Are the older leaves or newer leaves turning yellow?",
            "Is the soil very wet or waterlogged?",
            "How long has this been happening?"
        ]
    },
    "browning": {
        "possible_causes": ["fungal_infection", "underwatering", "nutrient_burn", "leaf_spot"],
        "keywords": ["brown", "browning", "dark spots", "burnt"],
        "questions": [
            "Are the brown spots dry or wet?",
            "Did you recently apply fertilizer?",
            "Are the spots spreading?"
        ]
    },
    "wilting": {
        "possible_causes": ["underwatering", "root_damage", "bacterial_wilt", "heat_stress"],
        "keywords": ["wilting", "drooping", "limp", "sagging"],
        "questions": [
            "When did you last water the plants?",
            "Has the weather been very hot?",
            "Do the stems look healthy?"
        ]
    },
    "curling": {
        "possible_causes": ["aphids", "virus", "herbicide_damage", "calcium_deficiency"],
        "keywords": ["curling", "curled", "twisted", "deformed"],
        "questions": [
            "Do you see any small insects on the leaves?",
            "Were any chemicals sprayed nearby?",
            "Are new leaves also affected?"
        ]
    },
    
    # Growth issues
    "stunted": {
        "possible_causes": ["nutrient_deficiency", "poor_soil", "pest_damage", "disease"],
        "keywords": ["small", "not growing", "stunted", "short"],
        "questions": [
            "How old are the plants?",
            "What fertilizer have you been using?",
            "Do the plants look healthy otherwise?"
        ]
    },
    
    # Pest indicators
    "holes": {
        "possible_causes": ["caterpillars", "beetles", "grasshoppers"],
        "keywords": ["holes", "eaten", "chewed", "damaged leaves"],
        "questions": [
            "Can you see any insects on the plants?",
            "Are the holes small or large?",
            "When did you first notice this?"
        ]
    },
    "sticky": {
        "possible_causes": ["aphids", "whiteflies", "scale_insects"],
        "keywords": ["sticky", "honeydew", "shiny leaves"],
        "questions": [
            "Do you see small insects underneath the leaves?",
            "Are there ants on the plants?",
            "Is there black mold growing?"
        ]
    },
    "webbing": {
        "possible_causes": ["spider_mites", "webworms"],
        "keywords": ["webs", "webbing", "silky threads"],
        "questions": [
            "Are the webs fine like spider webs or thick?",
            "Do you see tiny moving dots on leaves?",
            "Are leaves becoming dry and crispy?"
        ]
    },
    
    # Smell indicators
    "foul_smell": {
        "possible_causes": ["root_rot", "bacterial_infection", "overwatering"],
        "keywords": ["smell", "odor", "stink", "rotten"],
        "questions": [
            "Where is the smell coming from - soil or plant?",
            "How often are you watering?",
            "Is the soil staying wet for days?"
        ]
    },
    "musty_smell": {
        "possible_causes": ["fungal_infection", "mold", "poor_drainage"],
        "keywords": ["musty", "moldy", "damp smell"],
        "questions": [
            "Do you see any white or gray powder on leaves?",
            "Is the area well-ventilated?",
            "Has it been very humid?"
        ]
    }
}

# Disease database with detailed info
DISEASE_DATABASE = {
    "nitrogen_deficiency": {
        "name": "Nitrogen Deficiency",
        "symptoms": ["Older leaves turn yellow", "Slow growth", "Pale green color"],
        "causes": ["Lack of nitrogen fertilizer", "Poor soil", "Leaching from heavy rain"],
        "treatment": [
            "Apply nitrogen-rich fertilizer (urea, ammonium sulfate)",
            "Use organic options: cow dung, compost, neem cake",
            "Apply 50-100g per plant depending on size",
            "Results visible in 7-10 days"
        ],
        "prevention": [
            "Regular fertilization every 2-3 weeks",
            "Maintain organic matter in soil",
            "Avoid overwatering which leaches nutrients"
        ],
        "severity": "moderate"
    },
    "overwatering": {
        "name": "Overwatering / Root Rot",
        "symptoms": ["Yellow leaves", "Wilting despite wet soil", "Foul smell from soil", "Root damage"],
        "causes": ["Watering too frequently", "Poor drainage", "Heavy clay soil"],
        "treatment": [
            "STOP watering immediately",
            "Improve drainage by adding holes to soil",
            "Remove affected plants if severely damaged",
            "Let soil dry out before next watering",
            "Apply fungicide if root rot is severe"
        ],
        "prevention": [
            "Water only when top 2-3 inches of soil is dry",
            "Ensure good drainage",
            "Use well-draining soil mix"
        ],
        "severity": "high"
    },
    "aphids": {
        "name": "Aphid Infestation",
        "symptoms": ["Small green/black insects on leaves", "Sticky honeydew", "Curled leaves", "Ants on plants"],
        "causes": ["Warm weather", "Nearby infested plants", "Nitrogen-rich soil (attracts aphids)"],
        "treatment": [
            "Spray with soapy water (1 tbsp dish soap in 1L water)",
            "Neem oil spray (5ml per liter water)",
            "Introduce ladybugs (natural predator)",
            "Remove heavily infested leaves",
            "Repeat treatment every 3-4 days"
        ],
        "prevention": [
            "Regular inspection of plants",
            "Companion planting with marigolds",
            "Avoid excessive nitrogen fertilizer"
        ],
        "severity": "moderate"
    },
    "fungal_infection": {
        "name": "Fungal Infection (General)",
        "symptoms": ["White/gray powder on leaves", "Brown spots", "Leaf decay", "Musty smell"],
        "causes": ["High humidity", "Poor air circulation", "Overhead watering", "Infected seeds"],
        "treatment": [
            "Remove infected leaves immediately",
            "Apply fungicide (carbendazim, mancozeb)",
            "Improve air circulation",
            "Avoid wetting leaves when watering",
            "Spray neem oil as organic alternative"
        ],
        "prevention": [
            "Water at base of plant, not leaves",
            "Ensure good spacing between plants",
            "Don't water in evening (promotes fungal growth)",
            "Use disease-free seeds"
        ],
        "severity": "moderate"
    },
    "bacterial_wilt": {
        "name": "Bacterial Wilt",
        "symptoms": ["Sudden wilting", "No recovery after watering", "Brown vascular tissue", "Plant death"],
        "causes": ["Infected soil", "Contaminated tools", "Insect vectors"],
        "treatment": [
            "⚠️ No effective treatment once infected",
            "Remove and destroy infected plants",
            "Do NOT compost infected plants",
            "Sterilize tools with bleach solution",
            "Don't plant same crop in that area for 2 years"
        ],
        "prevention": [
            "Use disease-resistant varieties",
            "Rotate crops",
            "Control insect pests",
            "Avoid working in wet conditions"
        ],
        "severity": "critical"
    },
    "spider_mites": {
        "name": "Spider Mite Infestation",
        "symptoms": ["Tiny dots on leaves", "Fine webbing", "Yellow/bronze leaves", "Leaves drop off"],
        "causes": ["Hot, dry weather", "Dusty conditions", "Stressed plants"],
        "treatment": [
            "Spray plants with strong water jet (dislodges mites)",
            "Neem oil spray",
            "Insecticidal soap",
            "Increase humidity around plants",
            "Repeat every 3 days for 2 weeks"
        ],
        "prevention": [
            "Regular water spraying on leaf undersides",
            "Maintain plant health",
            "Avoid water stress"
        ],
        "severity": "moderate"
    }
}


def extract_keywords(text: str) -> List[str]:
    """Extract relevant keywords from farmer's description"""
    text = text.lower()
    found_keywords = []
    
    for symptom, data in SYMPTOM_DATABASE.items():
        for keyword in data["keywords"]:
            if keyword in text:
                found_keywords.append(symptom)
                break
    
    return found_keywords


def analyze_plant_description(description: str, crop_type: Optional[str] = None) -> Dict:
    """
    Main function to analyze farmer's plant description
    
    Args:
        description: Natural language description from farmer
        crop_type: Optional crop type for context
        
    Returns:
        Analysis with possible issues and recommendations
    """
    # Extract keywords
    symptoms = extract_keywords(description)
    
    if not symptoms:
        return {
            "status": "unclear",
            "message": "I couldn't identify specific symptoms from your description. Can you provide more details?",
            "clarifying_questions": [
                "What color are the leaves?",
                "Are there any spots or holes on the leaves?",
                "How is the plant's growth - normal, slow, or stunted?",
                "Do you see any insects?",
                "Any unusual smell?"
            ]
        }
    
    # Aggregate possible causes
    possible_issues = {}
    for symptom in symptoms:
        for cause in SYMPTOM_DATABASE[symptom]["possible_causes"]:
            if cause in possible_issues:
                possible_issues[cause] += 1
            else:
                possible_issues[cause] = 1
    
    # Sort by frequency (most likely issues first)
    sorted_issues = sorted(possible_issues.items(), key=lambda x: x[1], reverse=True)
    
    # Get top 3 most likely issues
    top_issues = [issue[0] for issue in sorted_issues[:3]]
    
    # Build detailed analysis
    analysis = {
        "symptoms_detected": symptoms,
        "likely_issues": [],
        "recommendations": [],
        "severity": "low",
        "clarifying_questions": []
    }
    
    max_severity_rank = 0
    severity_ranking = {"low": 0, "moderate": 1, "high": 2, "critical": 3}
    
    for issue in top_issues:
        if issue in DISEASE_DATABASE:
            disease_info = DISEASE_DATABASE[issue]
            analysis["likely_issues"].append({
                "name": disease_info["name"],
                "confidence": "high" if possible_issues[issue] >= 2 else "medium",
                "symptoms": disease_info["symptoms"],
                "treatment": disease_info["treatment"]
            })
            
            # Track highest severity
            issue_severity = severity_ranking.get(disease_info["severity"], 0)
            if issue_severity > max_severity_rank:
                max_severity_rank = issue_severity
                analysis["severity"] = disease_info["severity"]
    
    # Generate recommendations
    if analysis["likely_issues"]:
        # Take treatment from most likely issue
        primary_issue = analysis["likely_issues"][0]
        analysis["recommendations"] = primary_issue["treatment"]
        
        # Add clarifying questions if confidence is not high
        if primary_issue["confidence"] != "high":
            # Get questions from symptom database
            for symptom in symptoms:
                analysis["clarifying_questions"].extend(SYMPTOM_DATABASE[symptom]["questions"])
            # Remove duplicates
            analysis["clarifying_questions"] = list(set(analysis["clarifying_questions"]))[:3]
    
    return analysis


def extract_plant_metrics(description: str) -> Dict:
    """
    Extract quantitative metrics from description
    
    Examples:
    - "30cm tall" -> height: 30
    - "dark green leaves" -> color: "dark_green"
    """
    metrics = {}
    
    # Height extraction
    height_match = re.search(r'(\d+)\s*(cm|centimeter|inch)', description.lower())
    if height_match:
        height = int(height_match.group(1))
        unit = height_match.group(2)
        if "inch" in unit:
            height = height * 2.54  # Convert to cm
        metrics["height_cm"] = height
    
    # Color extraction
    color_keywords = {
        "dark green": "healthy",
        "light green": "possibly_nitrogen_deficient",
        "yellow": "nutrient_deficient",
        "brown": "damaged",
        "pale": "weak"
    }
    for color, status in color_keywords.items():
        if color in description.lower():
            metrics["leaf_color"] = color
            metrics["color_status"] = status
            break
    
    # Leaf count (rough estimate)
    leaf_match = re.search(r'(\d+)\s*leaves', description.lower())
    if leaf_match:
        metrics["leaf_count"] = int(leaf_match.group(1))
    
    return metrics


def compare_with_expected(
    actual_metrics: Dict,
    crop_type: str,
    days_old: int
) -> Dict:
    """
    Compare actual metrics with expected values for crop age
    
    Returns assessment: "on_track", "slow", "fast"
    """
    # Expected growth rates (cm per day)
    growth_rates = {
        "tomato": 2.0,
        "moong_dal": 1.5,
        "rice": 1.8,
        "wheat": 1.2,
        "cucumber": 2.5
    }
    
    growth_rate = growth_rates.get(crop_type.lower(), 1.5)
    expected_height = growth_rate * days_old
    
    assessment = {
        "expected_height_cm": round(expected_height, 1),
        "actual_height_cm": actual_metrics.get("height_cm", 0),
        "growth_status": "unknown"
    }
    
    if "height_cm" in actual_metrics:
        actual_height = actual_metrics["height_cm"]
        deviation = (actual_height - expected_height) / expected_height * 100
        
        if deviation > 20:
            assessment["growth_status"] = "fast"
            assessment["message"] = "Growing faster than expected! 🌱"
        elif deviation < -20:
            assessment["growth_status"] = "slow"
            assessment["message"] = "Growth is slower than expected. Check nutrition and water."
        else:
            assessment["growth_status"] = "on_track"
            assessment["message"] = "Growth is normal ✓"
        
        assessment["deviation_percent"] = round(deviation, 1)
    
    return assessment


def generate_care_instructions(issue: str) -> List[str]:
    """Generate step-by-step care instructions for an issue"""
    if issue in DISEASE_DATABASE:
        return DISEASE_DATABASE[issue]["treatment"]
    return ["Contact agricultural expert for guidance"]


# Tool registration for AutoGen
def register_plant_analysis_tools():
    """Returns tool definitions for AutoGen"""
    return [
        {
            "name": "analyze_plant_description",
            "description": "Analyze farmer's natural language description of plant health to detect issues",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Farmer's description of the plant"},
                    "crop_type": {"type": "string", "description": "Type of crop (optional)"}
                },
                "required": ["description"]
            }
        },
        {
            "name": "extract_plant_metrics",
            "description": "Extract quantitative metrics (height, color, etc.) from description",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"}
                },
                "required": ["description"]
            }
        },
        {
            "name": "compare_with_expected",
            "description": "Compare actual plant metrics with expected values for crop age",
            "parameters": {
                "type": "object",
                "properties": {
                    "actual_metrics": {"type": "object"},
                    "crop_type": {"type": "string"},
                    "days_old": {"type": "integer"}
                },
                "required": ["actual_metrics", "crop_type", "days_old"]
            }
        }
    ]


if __name__ == "__main__":
    print("=== Testing Plant Analysis Tools ===\n")
    
    # Test 1: Analyze yellowing leaves
    print("Test 1: Farmer describes yellowing leaves")
    description1 = "My tomato plants have yellow leaves on the bottom. The soil has been very wet for the past week."
    analysis1 = analyze_plant_description(description1, "tomato")
    print(f"Symptoms detected: {analysis1['symptoms_detected']}")
    print(f"Severity: {analysis1['severity']}")
    if analysis1['likely_issues']:
        print(f"Most likely issue: {analysis1['likely_issues'][0]['name']}")
        print("Recommendations:")
        for i, rec in enumerate(analysis1['recommendations'][:3], 1):
            print(f"  {i}. {rec}")
    
    # Test 2: Analyze insect damage
    print("\n\nTest 2: Farmer describes insect damage")
    description2 = "There are small holes in the leaves and I can see tiny green insects. The leaves are also sticky."
    analysis2 = analyze_plant_description(description2)
    print(f"Symptoms detected: {analysis2['symptoms_detected']}")
    if analysis2['likely_issues']:
        print(f"Most likely issue: {analysis2['likely_issues'][0]['name']}")
        print("Treatment:")
        for i, treatment in enumerate(analysis2['recommendations'][:3], 1):
            print(f"  {i}. {treatment}")
    
    # Test 3: Extract metrics
    print("\n\nTest 3: Extract plant metrics")
    description3 = "Plants are 30cm tall with dark green leaves. I count about 12 leaves per plant."
    metrics = extract_plant_metrics(description3)
    print(f"Extracted metrics: {metrics}")
    
    # Test 4: Compare with expected
    print("\n\nTest 4: Compare with expected growth")
    comparison = compare_with_expected(metrics, "tomato", days_old=15)
    print(f"Expected height: {comparison['expected_height_cm']}cm")
    print(f"Actual height: {comparison['actual_height_cm']}cm")
    print(f"Status: {comparison['growth_status']}")
    print(f"Message: {comparison['message']}")
    
    # Test 5: Vague description
    print("\n\nTest 5: Vague description")
    description5 = "My plants don't look good"
    analysis5 = analyze_plant_description(description5)
    print(f"Status: {analysis5['status']}")
    print("Clarifying questions:")
    for q in analysis5.get('clarifying_questions', []):
        print(f"  - {q}")