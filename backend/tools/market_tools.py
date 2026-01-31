"""
Market Tools - Fetch and analyze crop market prices

Since we don't have a real market API, we'll use:
1. Mock data with realistic prices
2. Simulated price fluctuations based on season/demand
3. Tool functions that agents can call
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random


# Mock market price database (₹ per quintal)
MOCK_MARKET_PRICES = {
    "rice": {
        "base_price": 2500,
        "volatility": 0.15,  # ±15% variation
        "peak_months": [10, 11, 12],  # Oct-Dec (harvest season = lower price)
        "low_months": [6, 7, 8],  # Jun-Aug (pre-harvest = higher price)
    },
    "wheat": {
        "base_price": 2100,
        "volatility": 0.12,
        "peak_months": [4, 5],  # Apr-May
        "low_months": [11, 12],
    },
    "cotton": {
        "base_price": 6200,
        "volatility": 0.20,
        "peak_months": [11, 12, 1],  # Nov-Jan
        "low_months": [6, 7],
    },
    "moong_dal": {
        "base_price": 7000,
        "volatility": 0.18,
        "peak_months": [3, 4, 5],  # Mar-May
        "low_months": [10, 11],
    },
    "sugarcane": {
        "base_price": 350,  # per ton
        "volatility": 0.10,
        "peak_months": [12, 1, 2],  # Dec-Feb
        "low_months": [7, 8],
    },
    "tomato": {
        "base_price": 1500,
        "volatility": 0.35,  # High volatility
        "peak_months": [12, 1, 2],
        "low_months": [6, 7, 8],
    },
    "potato": {
        "base_price": 800,
        "volatility": 0.25,
        "peak_months": [3, 4],
        "low_months": [10, 11],
    },
    "onion": {
        "base_price": 1200,
        "volatility": 0.30,
        "peak_months": [11, 12],
        "low_months": [6, 7],
    },
    "maize": {
        "base_price": 1800,
        "volatility": 0.15,
        "peak_months": [10, 11],
        "low_months": [5, 6],
    },
    "bajra": {
        "base_price": 2000,
        "volatility": 0.14,
        "peak_months": [10, 11],
        "low_months": [6, 7],
    },
}

# Mock marketplaces with location data
MOCK_MARKETPLACES = {
    "punjab": [
        {"name": "Ludhiana Mandi", "distance_km": 15, "transport_cost_per_km": 3},
        {"name": "Jalandhar Grain Market", "distance_km": 30, "transport_cost_per_km": 3},
        {"name": "Amritsar Agricultural Market", "distance_km": 45, "transport_cost_per_km": 3},
        {"name": "Local Trader (Village)", "distance_km": 0, "transport_cost_per_km": 0, "price_discount": 0.10},
    ],
    "maharashtra": [
        {"name": "Pune Mandi", "distance_km": 20, "transport_cost_per_km": 4},
        {"name": "Mumbai APMC", "distance_km": 80, "transport_cost_per_km": 4},
        {"name": "Nashik Market", "distance_km": 40, "transport_cost_per_km": 4},
        {"name": "Local Trader", "distance_km": 0, "transport_cost_per_km": 0, "price_discount": 0.12},
    ],
    "default": [
        {"name": "District Mandi", "distance_km": 15, "transport_cost_per_km": 3},
        {"name": "Regional Market", "distance_km": 35, "transport_cost_per_km": 3},
        {"name": "Local Trader", "distance_km": 0, "transport_cost_per_km": 0, "price_discount": 0.10},
    ]
}


def get_current_market_price(crop: str, location: Optional[str] = None) -> Dict:
    """
    Get current market price for a crop with seasonal adjustments
    
    Args:
        crop: Crop name (e.g., "rice", "wheat")
        location: Optional location for regional price variation
        
    Returns:
        Dict with price info
    """
    crop = crop.lower().replace(" ", "_")
    
    if crop not in MOCK_MARKET_PRICES:
        # Return a generic price if crop not in database
        return {
            "crop": crop,
            "price_per_quintal": 2000,
            "currency": "INR",
            "unit": "quintal",
            "date": datetime.now().isoformat(),
            "note": "Generic price - crop not in database"
        }
    
    crop_data = MOCK_MARKET_PRICES[crop]
    base_price = crop_data["base_price"]
    volatility = crop_data["volatility"]
    
    # Seasonal price adjustment
    current_month = datetime.now().month
    if current_month in crop_data["peak_months"]:
        # Harvest season = more supply = lower price
        seasonal_factor = 1 - (volatility * 0.5)
    elif current_month in crop_data["low_months"]:
        # Pre-harvest = less supply = higher price
        seasonal_factor = 1 + (volatility * 0.5)
    else:
        seasonal_factor = 1.0
    
    # Random daily fluctuation (±5%)
    daily_fluctuation = 1 + random.uniform(-0.05, 0.05)
    
    # Regional variation (±10% based on location)
    regional_factor = 1.0
    if location:
        location_lower = location.lower()
        if "punjab" in location_lower or "haryana" in location_lower:
            regional_factor = 1.05  # Higher prices in wheat belt
        elif "maharashtra" in location_lower or "karnataka" in location_lower:
            regional_factor = 0.95  # Slightly lower in south
    
    final_price = base_price * seasonal_factor * daily_fluctuation * regional_factor
    
    return {
        "crop": crop,
        "price_per_quintal": round(final_price, 2),
        "base_price": base_price,
        "seasonal_factor": round(seasonal_factor, 2),
        "currency": "INR",
        "unit": "quintal",
        "date": datetime.now().isoformat(),
        "location": location or "National Average",
        "trend": "increasing" if seasonal_factor > 1.05 else "decreasing" if seasonal_factor < 0.95 else "stable"
    }


def get_market_prices(crops: List[str], location: Optional[str] = None) -> List[Dict]:
    """
    Get market prices for multiple crops
    
    Args:
        crops: List of crop names
        location: Optional location
        
    Returns:
        List of price dictionaries
    """
    return [get_current_market_price(crop, location) for crop in crops]


def find_marketplaces(crop: str, location: str, quantity_quintals: float) -> List[Dict]:
    """
    Find marketplaces near the farmer's location
    
    Args:
        crop: Crop to sell
        location: Farmer's location
        quantity_quintals: Quantity to sell (in quintals)
        
    Returns:
        List of marketplace options with net prices
    """
    # Determine region
    location_lower = location.lower()
    if "punjab" in location_lower or "ludhiana" in location_lower or "jalandhar" in location_lower:
        region = "punjab"
    elif "maharashtra" in location_lower or "pune" in location_lower or "mumbai" in location_lower:
        region = "maharashtra"
    else:
        region = "default"
    
    marketplaces = MOCK_MARKETPLACES.get(region, MOCK_MARKETPLACES["default"])
    
    # Get current crop price
    base_price_info = get_current_market_price(crop, location)
    base_price = base_price_info["price_per_quintal"]
    
    results = []
    for marketplace in marketplaces:
        # Calculate transport cost
        transport_cost_total = marketplace["distance_km"] * marketplace["transport_cost_per_km"] * quantity_quintals
        transport_cost_per_quintal = transport_cost_total / quantity_quintals if quantity_quintals > 0 else 0
        
        # Apply discount if local trader
        price_multiplier = 1 - marketplace.get("price_discount", 0)
        market_price = base_price * price_multiplier
        
        # Add small random variation (±2%) to each marketplace
        market_price = market_price * (1 + random.uniform(-0.02, 0.02))
        
        # Net price after transport
        net_price_per_quintal = market_price - transport_cost_per_quintal
        total_earnings = net_price_per_quintal * quantity_quintals
        
        results.append({
            "marketplace_name": marketplace["name"],
            "distance_km": marketplace["distance_km"],
            "market_price_per_quintal": round(market_price, 2),
            "transport_cost_per_quintal": round(transport_cost_per_quintal, 2),
            "net_price_per_quintal": round(net_price_per_quintal, 2),
            "total_earnings": round(total_earnings, 2),
            "payment_terms": "Immediate" if "Trader" in marketplace["name"] else "Within 2-3 days",
            "recommendation_score": round(net_price_per_quintal / base_price, 2)  # Higher is better
        })
    
    # Sort by net price (descending)
    results.sort(key=lambda x: x["net_price_per_quintal"], reverse=True)
    
    return results


def get_price_forecast(crop: str, months_ahead: int = 3) -> List[Dict]:
    """
    Forecast future prices based on seasonal patterns
    
    Args:
        crop: Crop name
        months_ahead: Number of months to forecast
        
    Returns:
        List of monthly price forecasts
    """
    crop = crop.lower().replace(" ", "_")
    
    if crop not in MOCK_MARKET_PRICES:
        return []
    
    crop_data = MOCK_MARKET_PRICES[crop]
    base_price = crop_data["base_price"]
    volatility = crop_data["volatility"]
    
    forecasts = []
    current_date = datetime.now()
    
    for i in range(1, months_ahead + 1):
        future_date = current_date + timedelta(days=30 * i)
        future_month = future_date.month
        
        # Seasonal adjustment
        if future_month in crop_data["peak_months"]:
            seasonal_factor = 1 - (volatility * 0.5)
            trend = "decreasing"
        elif future_month in crop_data["low_months"]:
            seasonal_factor = 1 + (volatility * 0.5)
            trend = "increasing"
        else:
            seasonal_factor = 1.0
            trend = "stable"
        
        forecast_price = base_price * seasonal_factor
        
        forecasts.append({
            "month": future_date.strftime("%B %Y"),
            "forecasted_price": round(forecast_price, 2),
            "trend": trend,
            "confidence": "medium"  # Since we're using mock data
        })
    
    return forecasts


def calculate_profit(
    yield_quintals: float,
    selling_price_per_quintal: float,
    seed_cost: float = 0,
    fertilizer_cost: float = 0,
    labor_cost: float = 0,
    irrigation_cost: float = 0,
    other_costs: float = 0
) -> Dict:
    """
    Calculate profit/loss for a crop season
    
    Args:
        yield_quintals: Total yield
        selling_price_per_quintal: Price at which crop sold
        Various cost parameters
        
    Returns:
        Profit analysis dictionary
    """
    total_revenue = yield_quintals * selling_price_per_quintal
    total_costs = seed_cost + fertilizer_cost + labor_cost + irrigation_cost + other_costs
    net_profit = total_revenue - total_costs
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    roi = (net_profit / total_costs * 100) if total_costs > 0 else 0
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_costs": round(total_costs, 2),
        "net_profit": round(net_profit, 2),
        "profit_margin_percent": round(profit_margin, 2),
        "roi_percent": round(roi, 2),
        "cost_breakdown": {
            "seed": seed_cost,
            "fertilizer": fertilizer_cost,
            "labor": labor_cost,
            "irrigation": irrigation_cost,
            "other": other_costs
        },
        "profitability": "High" if profit_margin > 30 else "Medium" if profit_margin > 15 else "Low"
    }


# Tool registration for AutoGen agents
def register_market_tools():
    """
    Returns list of tool definitions for AutoGen agents
    """
    return [
        {
            "name": "get_current_market_price",
            "description": "Get current market price for a specific crop with seasonal adjustments",
            "parameters": {
                "type": "object",
                "properties": {
                    "crop": {"type": "string", "description": "Name of the crop (e.g., 'rice', 'wheat')"},
                    "location": {"type": "string", "description": "Optional location for regional pricing"}
                },
                "required": ["crop"]
            }
        },
        {
            "name": "get_market_prices",
            "description": "Get market prices for multiple crops at once",
            "parameters": {
                "type": "object",
                "properties": {
                    "crops": {"type": "array", "items": {"type": "string"}, "description": "List of crop names"},
                    "location": {"type": "string", "description": "Optional location"}
                },
                "required": ["crops"]
            }
        },
        {
            "name": "find_marketplaces",
            "description": "Find best marketplaces to sell crops with transport cost analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "crop": {"type": "string", "description": "Crop to sell"},
                    "location": {"type": "string", "description": "Farmer's location"},
                    "quantity_quintals": {"type": "number", "description": "Quantity to sell in quintals"}
                },
                "required": ["crop", "location", "quantity_quintals"]
            }
        },
        {
            "name": "get_price_forecast",
            "description": "Get price forecast for upcoming months",
            "parameters": {
                "type": "object",
                "properties": {
                    "crop": {"type": "string", "description": "Crop name"},
                    "months_ahead": {"type": "integer", "description": "Number of months to forecast (default 3)"}
                },
                "required": ["crop"]
            }
        },
        {
            "name": "calculate_profit",
            "description": "Calculate profit/loss and ROI for a crop season",
            "parameters": {
                "type": "object",
                "properties": {
                    "yield_quintals": {"type": "number"},
                    "selling_price_per_quintal": {"type": "number"},
                    "seed_cost": {"type": "number"},
                    "fertilizer_cost": {"type": "number"},
                    "labor_cost": {"type": "number"},
                    "irrigation_cost": {"type": "number"},
                    "other_costs": {"type": "number"}
                },
                "required": ["yield_quintals", "selling_price_per_quintal"]
            }
        }
    ]


if __name__ == "__main__":
    # Test the tools
    print("=== Testing Market Tools ===\n")
    
    # Test 1: Single crop price
    print("1. Current price for rice:")
    rice_price = get_current_market_price("rice", "Punjab")
    print(json.dumps(rice_price, indent=2))
    
    # Test 2: Multiple crops
    print("\n2. Prices for multiple crops:")
    prices = get_market_prices(["rice", "wheat", "moong_dal"], "Maharashtra")
    for p in prices:
        print(f"  {p['crop']}: ₹{p['price_per_quintal']}/quintal ({p['trend']})")
    
    # Test 3: Find marketplaces
    print("\n3. Best marketplaces for 50 quintals of wheat:")
    marketplaces = find_marketplaces("wheat", "Punjab", 50)
    for m in marketplaces[:3]:  # Top 3
        print(f"  {m['marketplace_name']}: ₹{m['net_price_per_quintal']}/quintal (Total: ₹{m['total_earnings']})")
    
    # Test 4: Price forecast
    print("\n4. Rice price forecast:")
    forecast = get_price_forecast("rice", 3)
    for f in forecast:
        print(f"  {f['month']}: ₹{f['forecasted_price']} ({f['trend']})")
    
    # Test 5: Profit calculation
    print("\n5. Profit calculation example:")
    profit = calculate_profit(
        yield_quintals=50,
        selling_price_per_quintal=2500,
        seed_cost=5000,
        fertilizer_cost=8000,
        labor_cost=12000,
        irrigation_cost=3000,
        other_costs=2000
    )
    print(f"  Net Profit: ₹{profit['net_profit']} ({profit['profitability']} profitability)")
    print(f"  ROI: {profit['roi_percent']}%")