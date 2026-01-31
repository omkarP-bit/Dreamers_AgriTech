"""
Seasonal weather patterns for different regions
This replaces historical weather data (which isn't available in free tier)
"""
from typing import Dict, Optional


# Seasonal patterns for Indian agricultural regions
SEASONAL_PATTERNS = {
    "Punjab": {
        "region": "North India",
        "patterns": {
            "kharif": {  # June-October (Monsoon season)
                "name": "Kharif/Monsoon Season",
                "months": [6, 7, 8, 9, 10],
                "avg_rainfall_mm": 800,
                "temperature_range": [25, 38],
                "humidity_avg": 75,
                "suitable_crops": ["rice", "cotton", "maize", "sugarcane", "millets"],
                "description": "Heavy monsoon rains, high humidity, warm temperatures"
            },
            "rabi": {  # November-March (Winter season)
                "name": "Rabi/Winter Season",
                "months": [11, 12, 1, 2, 3],
                "avg_rainfall_mm": 100,
                "temperature_range": [5, 25],
                "humidity_avg": 55,
                "suitable_crops": ["wheat", "barley", "mustard", "chickpea", "peas"],
                "description": "Cool dry weather, occasional winter rain, ideal for wheat"
            },
            "zaid": {  # April-May (Summer season)
                "name": "Zaid/Summer Season",
                "months": [4, 5],
                "avg_rainfall_mm": 50,
                "temperature_range": [30, 45],
                "humidity_avg": 40,
                "suitable_crops": ["watermelon", "cucumber", "muskmelon", "vegetables"],
                "description": "Hot and dry, requires irrigation"
            }
        }
    },
    
    "Haryana": {
        "region": "North India",
        "patterns": {
            "kharif": {
                "name": "Monsoon Season",
                "months": [6, 7, 8, 9],
                "avg_rainfall_mm": 600,
                "temperature_range": [25, 38],
                "humidity_avg": 70,
                "suitable_crops": ["rice", "cotton", "bajra", "jowar"],
                "description": "Monsoon dependent, moderate rainfall"
            },
            "rabi": {
                "name": "Winter Season",
                "months": [11, 12, 1, 2, 3],
                "avg_rainfall_mm": 80,
                "temperature_range": [7, 23],
                "humidity_avg": 60,
                "suitable_crops": ["wheat", "barley", "mustard", "gram"],
                "description": "Cool winters, wheat belt region"
            }
        }
    },
    
    "Maharashtra": {
        "region": "West India",
        "patterns": {
            "kharif": {
                "name": "Monsoon Season",
                "months": [6, 7, 8, 9, 10],
                "avg_rainfall_mm": 1200,
                "temperature_range": [24, 32],
                "humidity_avg": 80,
                "suitable_crops": ["rice", "cotton", "soybean", "sugarcane", "millets"],
                "description": "Heavy western ghats monsoon, high rainfall"
            },
            "rabi": {
                "name": "Winter Season",
                "months": [11, 12, 1, 2],
                "avg_rainfall_mm": 50,
                "temperature_range": [15, 28],
                "humidity_avg": 50,
                "suitable_crops": ["wheat", "chickpea", "jowar", "vegetables"],
                "description": "Mild winter, less rainfall"
            }
        }
    },
    
    "Uttar Pradesh": {
        "region": "North India",
        "patterns": {
            "kharif": {
                "name": "Monsoon Season",
                "months": [6, 7, 8, 9],
                "avg_rainfall_mm": 900,
                "temperature_range": [25, 38],
                "humidity_avg": 75,
                "suitable_crops": ["rice", "sugarcane", "cotton", "millets"],
                "description": "Good monsoon coverage, fertile plains"
            },
            "rabi": {
                "name": "Winter Season",
                "months": [11, 12, 1, 2, 3],
                "avg_rainfall_mm": 120,
                "temperature_range": [8, 25],
                "humidity_avg": 60,
                "suitable_crops": ["wheat", "barley", "peas", "mustard"],
                "description": "Major wheat producing region"
            }
        }
    },
    
    "Karnataka": {
        "region": "South India",
        "patterns": {
            "kharif": {
                "name": "Southwest Monsoon",
                "months": [6, 7, 8, 9],
                "avg_rainfall_mm": 800,
                "temperature_range": [22, 32],
                "humidity_avg": 75,
                "suitable_crops": ["rice", "ragi", "maize", "cotton"],
                "description": "Moderate monsoon, varied topography"
            },
            "rabi": {
                "name": "Northeast Monsoon",
                "months": [10, 11, 12],
                "avg_rainfall_mm": 400,
                "temperature_range": [18, 28],
                "humidity_avg": 65,
                "suitable_crops": ["ragi", "pulses", "oilseeds"],
                "description": "Post-monsoon crops, winter rain"
            }
        }
    },
    
    "Tamil Nadu": {
        "region": "South India",
        "patterns": {
            "kharif": {
                "name": "Southwest Monsoon",
                "months": [6, 7, 8, 9],
                "avg_rainfall_mm": 400,
                "temperature_range": [26, 35],
                "humidity_avg": 70,
                "suitable_crops": ["rice", "cotton", "millets"],
                "description": "Less rain from southwest monsoon"
            },
            "rabi": {
                "name": "Northeast Monsoon",
                "months": [10, 11, 12, 1],
                "avg_rainfall_mm": 900,
                "temperature_range": [22, 30],
                "humidity_avg": 75,
                "suitable_crops": ["rice", "pulses", "sugarcane"],
                "description": "Main rainy season, northeast monsoon critical"
            }
        }
    },
    
    "West Bengal": {
        "region": "East India",
        "patterns": {
            "kharif": {
                "name": "Monsoon Season",
                "months": [6, 7, 8, 9, 10],
                "avg_rainfall_mm": 1500,
                "temperature_range": [25, 35],
                "humidity_avg": 85,
                "suitable_crops": ["rice", "jute", "sugarcane"],
                "description": "Heavy monsoon, high humidity, rice bowl"
            },
            "rabi": {
                "name": "Winter Season",
                "months": [11, 12, 1, 2],
                "avg_rainfall_mm": 100,
                "temperature_range": [12, 28],
                "humidity_avg": 70,
                "suitable_crops": ["wheat", "mustard", "vegetables", "pulses"],
                "description": "Mild winter, vegetable production"
            }
        }
    }
}


class SeasonalPatterns:
    """Seasonal weather pattern utilities"""
    
    @staticmethod
    def get_pattern_for_location(location: str) -> Optional[Dict]:
        """
        Get seasonal pattern for a location
        
        Args:
            location: Location string (e.g., "Punjab", "Ludhiana, Punjab")
        
        Returns:
            Seasonal pattern dict or None
        """
        # Extract state/region from location
        location_upper = location.upper()
        
        for state, pattern in SEASONAL_PATTERNS.items():
            if state.upper() in location_upper:
                return pattern
        
        # Default fallback - return Punjab pattern as generic North India
        return SEASONAL_PATTERNS.get("Punjab")
    
    @staticmethod
    def get_current_season(location: str, month: int) -> Optional[Dict]:
        """
        Get current agricultural season based on location and month
        
        Args:
            location: Location string
            month: Month number (1-12)
        
        Returns:
            Current season dict or None
        """
        pattern = SeasonalPatterns.get_pattern_for_location(location)
        
        if not pattern:
            return None
        
        for season_name, season_data in pattern["patterns"].items():
            if month in season_data["months"]:
                return {
                    "season_type": season_name,
                    **season_data
                }
        
        return None
    
    @staticmethod
    def predict_next_6_months_weather(location: str, current_month: int) -> Dict:
        """
        Predict weather for next 6 months based on seasonal patterns
        
        Args:
            location: Location string
            current_month: Current month (1-12)
        
        Returns:
            Dict with 6-month weather prediction
        """
        pattern = SeasonalPatterns.get_pattern_for_location(location)
        
        if not pattern:
            return {"error": "Location pattern not found"}
        
        predictions = []
        
        for i in range(6):
            month = ((current_month + i - 1) % 12) + 1
            season = SeasonalPatterns.get_current_season(location, month)
            
            if season:
                predictions.append({
                    "month": month,
                    "season": season["name"],
                    "expected_rainfall_mm": season["avg_rainfall_mm"] / len(season["months"]),
                    "temperature_range": season["temperature_range"],
                    "humidity": season["humidity_avg"],
                    "suitable_crops": season["suitable_crops"]
                })
        
        return {
            "location": location,
            "region": pattern["region"],
            "predictions": predictions,
            "note": "Based on historical seasonal patterns"
        }
    
    @staticmethod
    def get_crop_recommendations(location: str, month: int) -> Dict:
        """
        Get crop recommendations based on location and planting month
        
        Args:
            location: Location string
            month: Planting month (1-12)
        
        Returns:
            Dict with crop recommendations
        """
        season = SeasonalPatterns.get_current_season(location, month)
        
        if not season:
            return {"error": "Could not determine season"}
        
        return {
            "season": season["name"],
            "recommended_crops": season["suitable_crops"],
            "weather_characteristics": season["description"],
            "rainfall_expectation": season["avg_rainfall_mm"],
            "temperature_range": season["temperature_range"],
            "planting_month": month
        }
    
    @staticmethod
    def get_all_available_locations() -> list:
        """Get list of all available locations"""
        return list(SEASONAL_PATTERNS.keys())


# Crop database with characteristics
CROP_DATABASE = {
    "rice": {
        "name": "Rice",
        "varieties": ["Basmati", "IR64", "Swarna", "Pusa"],
        "growing_season": "kharif",
        "duration_days": 120,
        "water_requirement": "high",
        "soil_preference": ["clay", "loam"],
        "temperature_range": [20, 35],
        "rainfall_requirement_mm": 800,
        "nutrients_needed": {"N": "high", "P": "medium", "K": "medium"}
    },
    "wheat": {
        "name": "Wheat",
        "varieties": ["HD2967", "PBW343", "Lok1"],
        "growing_season": "rabi",
        "duration_days": 120,
        "water_requirement": "medium",
        "soil_preference": ["loam", "clay-loam"],
        "temperature_range": [10, 25],
        "rainfall_requirement_mm": 300,
        "nutrients_needed": {"N": "high", "P": "high", "K": "medium"}
    },
    "cotton": {
        "name": "Cotton",
        "varieties": ["Bt Cotton", "Hybrid varieties"],
        "growing_season": "kharif",
        "duration_days": 150,
        "water_requirement": "medium",
        "soil_preference": ["black soil", "loam"],
        "temperature_range": [21, 35],
        "rainfall_requirement_mm": 600,
        "nutrients_needed": {"N": "high", "P": "medium", "K": "high"}
    },
    "sugarcane": {
        "name": "Sugarcane",
        "varieties": ["Co86032", "CoJ64"],
        "growing_season": "year-round",
        "duration_days": 300,
        "water_requirement": "very high",
        "soil_preference": ["loam", "clay-loam"],
        "temperature_range": [20, 35],
        "rainfall_requirement_mm": 1500,
        "nutrients_needed": {"N": "very high", "P": "high", "K": "high"}
    },
    "moong_dal": {
        "name": "Moong Dal (Green Gram)",
        "varieties": ["Pusa Vishal", "SML668"],
        "growing_season": "kharif",
        "duration_days": 60,
        "water_requirement": "low",
        "soil_preference": ["loam", "sandy-loam"],
        "temperature_range": [25, 35],
        "rainfall_requirement_mm": 400,
        "nutrients_needed": {"N": "low", "P": "medium", "K": "medium"},
        "special": "Nitrogen-fixing crop, improves soil"
    },
    "chickpea": {
        "name": "Chickpea (Chana)",
        "varieties": ["Pusa256", "KAK2"],
        "growing_season": "rabi",
        "duration_days": 100,
        "water_requirement": "low",
        "soil_preference": ["loam", "clay-loam"],
        "temperature_range": [10, 30],
        "rainfall_requirement_mm": 300,
        "nutrients_needed": {"N": "low", "P": "medium", "K": "medium"},
        "special": "Nitrogen-fixing crop"
    },
    "maize": {
        "name": "Maize (Corn)",
        "varieties": ["Hybrid varieties"],
        "growing_season": "kharif",
        "duration_days": 90,
        "water_requirement": "medium",
        "soil_preference": ["loam", "sandy-loam"],
        "temperature_range": [20, 30],
        "rainfall_requirement_mm": 500,
        "nutrients_needed": {"N": "high", "P": "medium", "K": "medium"}
    }
}

def get_seasonal_patterns(location: str, crop: Optional[str] = None) -> Dict:
    """Module-level wrapper for orchestrator"""
    from datetime import datetime
    current_month = datetime.now().month
    season = SeasonalPatterns.get_current_season(location, current_month)
    prediction = SeasonalPatterns.predict_next_6_months_weather(location, current_month)
    return {
        "location": location,
        "current_season": season,
        "next_6_months_forecast": prediction
    }


def analyze_soil_suitability(soil_type: str, previous_crop: Optional[str] = None, crop_options: Optional[list] = None) -> Dict:
    """Module-level wrapper for soil analysis"""
    if not crop_options:
        crop_options = list(CROP_DATABASE.keys())
    
    soil_compatibility = {
        "clay": ["rice", "wheat", "cotton"],
        "loam": ["rice", "wheat", "maize", "moong_dal"],
        "sandy": ["moong_dal"],
        "black": ["cotton", "chickpea"]
    }
    
    suitable = soil_compatibility.get(soil_type.lower(), ["rice", "wheat"])
    return {
        "soil_type": soil_type,
        "suitable_crops": [c for c in crop_options if c in suitable],
        "summary": f"{soil_type} soil is suitable for: {', '.join(suitable)}"
    }


def register_seasonal_tools() -> Dict:
    """Register seasonal tools"""
    return {
        "get_seasonal_patterns": get_seasonal_patterns,
        "analyze_soil_suitability": analyze_soil_suitability
    }