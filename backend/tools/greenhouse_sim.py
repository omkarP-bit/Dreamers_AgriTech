"""
Greenhouse Simulation Tools

Simulates greenhouse sensor data and plant growth for greenhouse farmers.
Provides deterministic simulation for demo consistency.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random
import math


class GreenhousePlant:
    """
    Represents a plant in the greenhouse with growth parameters
    """
    
    CROP_PARAMETERS = {
        "tomato": {
            "optimal_temp": (20, 25),  # °C
            "optimal_humidity": (60, 80),  # %
            "optimal_moisture": (60, 75),  # %
            "optimal_light": (40000, 60000),  # lux
            "growth_rate": 2.5,  # cm/day under optimal conditions
            "max_height": 180,  # cm
            "days_to_harvest": 75,
            "water_needs": 2.5,  # liters/day
            "fertilizer_frequency": 7,  # days
        },
        "moong_dal": {
            "optimal_temp": (25, 30),
            "optimal_humidity": (60, 70),
            "optimal_moisture": (50, 65),
            "optimal_light": (30000, 50000),
            "growth_rate": 1.8,
            "max_height": 50,
            "days_to_harvest": 60,
            "water_needs": 1.5,
            "fertilizer_frequency": 10,
        },
        "lettuce": {
            "optimal_temp": (15, 20),
            "optimal_humidity": (50, 70),
            "optimal_moisture": (65, 80),
            "optimal_light": (20000, 35000),
            "growth_rate": 1.2,
            "max_height": 25,
            "days_to_harvest": 45,
            "water_needs": 1.0,
            "fertilizer_frequency": 14,
        },
        "cucumber": {
            "optimal_temp": (22, 28),
            "optimal_humidity": (70, 85),
            "optimal_moisture": (70, 85),
            "optimal_light": (45000, 65000),
            "growth_rate": 3.0,
            "max_height": 200,
            "days_to_harvest": 55,
            "water_needs": 3.0,
            "fertilizer_frequency": 5,
        }
    }
    
    def __init__(self, crop_type: str, sowing_date: datetime):
        self.crop_type = crop_type.lower()
        self.sowing_date = sowing_date
        self.params = self.CROP_PARAMETERS.get(self.crop_type, self.CROP_PARAMETERS["tomato"])
        
        # Growth state
        self.height = 0.5  # Starting height in cm
        self.leaf_count = 2  # Starting leaves
        self.health_score = 100.0
        self.days_old = 0
        
        # Cumulative stress factors
        self.stress_history = []
        
    def get_age_days(self, current_date: datetime) -> int:
        """Calculate plant age in days"""
        return (current_date - self.sowing_date).days
    
    def calculate_growth_factor(self, conditions: Dict) -> float:
        """
        Calculate growth factor (0-1.5) based on environmental conditions
        1.0 = optimal, <1.0 = stressed, >1.0 = boosted (e.g., CO2 enrichment)
        """
        temp = conditions.get("temperature", 25)
        humidity = conditions.get("humidity", 70)
        moisture = conditions.get("soil_moisture", 65)
        light = conditions.get("light_intensity", 40000)
        co2 = conditions.get("co2_level", 400)  # ppm
        
        # Temperature factor
        temp_min, temp_max = self.params["optimal_temp"]
        if temp_min <= temp <= temp_max:
            temp_factor = 1.0
        elif temp < temp_min:
            temp_factor = max(0.3, 1 - (temp_min - temp) * 0.05)
        else:
            temp_factor = max(0.3, 1 - (temp - temp_max) * 0.05)
        
        # Humidity factor
        hum_min, hum_max = self.params["optimal_humidity"]
        if hum_min <= humidity <= hum_max:
            hum_factor = 1.0
        else:
            deviation = min(abs(humidity - hum_min), abs(humidity - hum_max))
            hum_factor = max(0.5, 1 - deviation * 0.01)
        
        # Moisture factor
        moist_min, moist_max = self.params["optimal_moisture"]
        if moist_min <= moisture <= moist_max:
            moist_factor = 1.0
        else:
            deviation = min(abs(moisture - moist_min), abs(moisture - moist_max))
            moist_factor = max(0.4, 1 - deviation * 0.015)
        
        # Light factor
        light_min, light_max = self.params["optimal_light"]
        if light_min <= light <= light_max:
            light_factor = 1.0
        elif light < light_min:
            light_factor = max(0.5, light / light_min)
        else:
            light_factor = 1.0  # More light doesn't hurt much
        
        # CO2 boost (400-1000 ppm is beneficial)
        if 400 <= co2 <= 1000:
            co2_factor = 1 + (co2 - 400) * 0.0002  # Up to 1.12x boost
        else:
            co2_factor = 1.0
        
        # Combined factor
        growth_factor = temp_factor * hum_factor * moist_factor * light_factor * co2_factor
        
        # Calculate stress (anything below 0.8 is stressful)
        if growth_factor < 0.8:
            stress_level = (0.8 - growth_factor) * 100
            self.stress_history.append(stress_level)
            if len(self.stress_history) > 7:  # Keep last 7 days
                self.stress_history.pop(0)
        
        return growth_factor
    
    def grow(self, conditions: Dict, days: float = 1.0):
        """
        Simulate plant growth for given number of days
        """
        self.days_old = self.get_age_days(datetime.now())
        
        growth_factor = self.calculate_growth_factor(conditions)
        
        # Height growth (sigmoid curve approaching max height)
        growth_potential = self.params["max_height"] - self.height
        daily_growth = self.params["growth_rate"] * growth_factor * (growth_potential / self.params["max_height"])
        self.height += daily_growth * days
        
        # Leaf growth (roughly proportional to height)
        expected_leaves = int((self.height / self.params["max_height"]) * 50)
        if expected_leaves > self.leaf_count:
            self.leaf_count = min(expected_leaves, 100)
        
        # Health score update
        avg_stress = sum(self.stress_history) / len(self.stress_history) if self.stress_history else 0
        self.health_score = max(20, 100 - avg_stress)
        
    def is_ready_for_harvest(self) -> bool:
        """Check if plant is ready for harvest"""
        return self.days_old >= self.params["days_to_harvest"] and self.health_score > 50


class GreenhouseSimulator:
    """
    Main greenhouse simulator
    """
    
    def __init__(self, crop_type: str, sowing_date: datetime, auto_control: bool = False):
        self.plant = GreenhousePlant(crop_type, sowing_date)
        self.auto_control = auto_control
        
        # Current environment state
        self.environment = {
            "temperature": 25.0,
            "humidity": 70.0,
            "soil_moisture": 65.0,
            "light_intensity": 40000.0,
            "co2_level": 400.0,
        }
        
        # Control systems
        self.heater_on = False
        self.cooler_on = False
        self.humidifier_on = False
        self.irrigation_on = False
        self.co2_injection_on = False
        
        # Resource tracking
        self.water_used = 0.0  # liters
        self.power_used = 0.0  # kWh
        self.fertilizer_used = {}  # type -> amount
        
        # History
        self.history = []
        
    def get_current_state(self) -> Dict:
        """Get current greenhouse state"""
        return {
            "environment": self.environment.copy(),
            "plant": {
                "height": round(self.plant.height, 2),
                "leaf_count": self.plant.leaf_count,
                "health_score": round(self.plant.health_score, 2),
                "days_old": self.plant.days_old,
                "ready_for_harvest": self.plant.is_ready_for_harvest()
            },
            "controls": {
                "heater_on": self.heater_on,
                "cooler_on": self.cooler_on,
                "humidifier_on": self.humidifier_on,
                "irrigation_on": self.irrigation_on,
                "co2_injection_on": self.co2_injection_on
            },
            "resources": {
                "water_used_liters": round(self.water_used, 2),
                "power_used_kwh": round(self.power_used, 2)
            }
        }
    
    def simulate_natural_changes(self, hours: float = 1.0):
        """
        Simulate natural environmental changes (without control systems)
        """
        # Temperature naturally drifts toward ambient (assume 22°C day, 18°C night)
        hour_of_day = datetime.now().hour
        if 6 <= hour_of_day <= 18:
            ambient_temp = 22 + random.gauss(0, 2)
        else:
            ambient_temp = 18 + random.gauss(0, 1.5)
        
        # Temperature drifts toward ambient
        temp_drift = (ambient_temp - self.environment["temperature"]) * 0.1 * hours
        self.environment["temperature"] += temp_drift
        
        # Humidity decreases with temperature, increases with irrigation
        humidity_change = -0.5 * hours + (2 if self.irrigation_on else 0)
        self.environment["humidity"] += humidity_change
        self.environment["humidity"] = max(30, min(95, self.environment["humidity"]))
        
        # Soil moisture decreases as plant consumes water
        moisture_decrease = self.plant.params["water_needs"] * (hours / 24)
        if self.irrigation_on:
            moisture_increase = 5 * hours
            self.environment["soil_moisture"] += (moisture_increase - moisture_decrease)
        else:
            self.environment["soil_moisture"] -= moisture_decrease
        self.environment["soil_moisture"] = max(20, min(95, self.environment["soil_moisture"]))
        
        # Light depends on time of day
        if 6 <= hour_of_day <= 18:
            # Daylight
            self.environment["light_intensity"] = 45000 + random.gauss(0, 5000)
        else:
            # Night (artificial lights if available)
            self.environment["light_intensity"] = 10000 + random.gauss(0, 2000)
        
        # CO2 naturally decreases as plant consumes it
        co2_consumption = 5 * hours
        if self.co2_injection_on:
            self.environment["co2_level"] = min(1000, self.environment["co2_level"] + 20 * hours - co2_consumption)
        else:
            self.environment["co2_level"] = max(350, self.environment["co2_level"] - co2_consumption)
    
    def apply_control(self, action: str, parameters: Dict = None):
        """
        Apply a control action
        
        Actions:
        - heat: Increase temperature
        - cool: Decrease temperature
        - humidify: Increase humidity
        - irrigate: Water the plants
        - inject_co2: Add CO2
        """
        parameters = parameters or {}
        
        if action == "heat":
            target_temp = parameters.get("target_temp", 25)
            self.heater_on = True
            self.environment["temperature"] = min(target_temp, self.environment["temperature"] + 2)
            self.power_used += 0.5  # kWh
            
        elif action == "cool":
            target_temp = parameters.get("target_temp", 25)
            self.cooler_on = True
            self.environment["temperature"] = max(target_temp, self.environment["temperature"] - 2)
            self.power_used += 0.8  # kWh
            
        elif action == "humidify":
            target_humidity = parameters.get("target_humidity", 70)
            self.humidifier_on = True
            self.environment["humidity"] = min(target_humidity, self.environment["humidity"] + 10)
            self.water_used += 0.5  # liters
            
        elif action == "irrigate":
            amount_liters = parameters.get("amount", 2)
            self.irrigation_on = True
            self.water_used += amount_liters
            moisture_increase = amount_liters * 3  # Rough conversion
            self.environment["soil_moisture"] = min(95, self.environment["soil_moisture"] + moisture_increase)
            
        elif action == "inject_co2":
            self.co2_injection_on = True
            self.environment["co2_level"] = min(1000, self.environment["co2_level"] + 100)
            
        elif action == "stop_all":
            self.heater_on = False
            self.cooler_on = False
            self.humidifier_on = False
            self.irrigation_on = False
            self.co2_injection_on = False
    
    def auto_adjust(self):
        """
        Automatically adjust environment to optimal conditions
        """
        if not self.auto_control:
            return []
        
        actions_taken = []
        opt_temp = self.plant.params["optimal_temp"]
        opt_humidity = self.plant.params["optimal_humidity"]
        opt_moisture = self.plant.params["optimal_moisture"]
        
        # Temperature control
        if self.environment["temperature"] < opt_temp[0] - 1:
            self.apply_control("heat", {"target_temp": (opt_temp[0] + opt_temp[1]) / 2})
            actions_taken.append(f"Heating to {opt_temp[0]}°C")
        elif self.environment["temperature"] > opt_temp[1] + 1:
            self.apply_control("cool", {"target_temp": (opt_temp[0] + opt_temp[1]) / 2})
            actions_taken.append(f"Cooling to {opt_temp[1]}°C")
        
        # Humidity control
        if self.environment["humidity"] < opt_humidity[0] - 5:
            self.apply_control("humidify", {"target_humidity": (opt_humidity[0] + opt_humidity[1]) / 2})
            actions_taken.append(f"Increasing humidity to {opt_humidity[0]}%")
        
        # Irrigation
        if self.environment["soil_moisture"] < opt_moisture[0] - 5:
            self.apply_control("irrigate", {"amount": 2})
            actions_taken.append("Watering plants (2L)")
        
        return actions_taken
    
    def step(self, hours: float = 1.0) -> Dict:
        """
        Run simulation for given hours
        """
        # Auto-adjust if enabled
        auto_actions = []
        if self.auto_control:
            auto_actions = self.auto_adjust()
        
        # Natural changes
        self.simulate_natural_changes(hours)
        
        # Plant growth
        days = hours / 24
        self.plant.grow(self.environment, days)
        
        # Record state
        state = self.get_current_state()
        state["auto_actions"] = auto_actions
        state["timestamp"] = datetime.now().isoformat()
        
        self.history.append(state)
        
        return state


# Tool functions for AutoGen agents

def create_greenhouse(crop_type: str, auto_control: bool = False) -> Dict:
    """Create a new greenhouse simulation"""
    sim = GreenhouseSimulator(crop_type, datetime.now(), auto_control)
    return {
        "status": "created",
        "crop": crop_type,
        "auto_control": auto_control,
        "initial_state": sim.get_current_state()
    }


def read_sensors(simulator: GreenhouseSimulator) -> Dict:
    """Read current sensor values"""
    return simulator.get_current_state()


def control_environment(simulator: GreenhouseSimulator, action: str, parameters: Dict = None) -> Dict:
    """Apply environmental control"""
    simulator.apply_control(action, parameters)
    return {
        "action": action,
        "parameters": parameters,
        "new_state": simulator.get_current_state()
    }


def simulate_hours(simulator: GreenhouseSimulator, hours: float) -> List[Dict]:
    """Simulate multiple hours and return history"""
    states = []
    for _ in range(int(hours)):
        state = simulator.step(1.0)
        states.append(state)
    return states


def get_recommendations(simulator: GreenhouseSimulator) -> List[str]:
    """Get AI recommendations for greenhouse management"""
    current = simulator.environment
    params = simulator.plant.params
    recommendations = []
    
    # Temperature check
    if current["temperature"] < params["optimal_temp"][0]:
        recommendations.append(f"⚠️ Temperature too low ({current['temperature']}°C). Increase heating.")
    elif current["temperature"] > params["optimal_temp"][1]:
        recommendations.append(f"⚠️ Temperature too high ({current['temperature']}°C). Increase cooling.")
    
    # Humidity check
    if current["humidity"] < params["optimal_humidity"][0]:
        recommendations.append(f"💧 Humidity too low ({current['humidity']}%). Use humidifier.")
    
    # Moisture check
    if current["soil_moisture"] < params["optimal_moisture"][0]:
        recommendations.append(f"🌱 Soil moisture low ({current['soil_moisture']}%). Water plants.")
    
    # Health check
    if simulator.plant.health_score < 70:
        recommendations.append(f"🔴 Plant health declining ({simulator.plant.health_score}/100). Check all conditions.")
    
    if not recommendations:
        recommendations.append("✅ All systems optimal!")
    
    return recommendations


# Tool registration
def register_greenhouse_tools():
    """Returns tool definitions for AutoGen"""
    return [
        {
            "name": "read_sensors",
            "description": "Read current greenhouse sensor values (temp, humidity, soil moisture, etc.)",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "control_environment",
            "description": "Control greenhouse environment (heat/cool/irrigate/humidify/co2)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["heat", "cool", "humidify", "irrigate", "inject_co2", "stop_all"]},
                    "parameters": {"type": "object"}
                },
                "required": ["action"]
            }
        },
        {
            "name": "get_recommendations",
            "description": "Get AI recommendations for current greenhouse conditions",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    ]


if __name__ == "__main__":
    print("=== Testing Greenhouse Simulator ===\n")
    
    # Create greenhouse
    sim = GreenhouseSimulator("tomato", datetime.now(), auto_control=True)
    print("Created greenhouse for tomato")
    print(f"Optimal conditions: Temp {sim.plant.params['optimal_temp']}, Humidity {sim.plant.params['optimal_humidity']}")
    
    # Simulate 24 hours
    print("\nSimulating 24 hours with auto-control...")
    for hour in range(24):
        state = sim.step(1.0)
        if hour % 6 == 0:  # Print every 6 hours
            print(f"\nHour {hour}:")
            print(f"  Temperature: {state['environment']['temperature']:.1f}°C")
            print(f"  Humidity: {state['environment']['humidity']:.1f}%")
            print(f"  Plant height: {state['plant']['height']:.1f}cm")
            print(f"  Health: {state['plant']['health_score']:.1f}/100")
            if state['auto_actions']:
                print(f"  Auto actions: {', '.join(state['auto_actions'])}")
    
    print(f"\nResources used:")
    print(f"  Water: {sim.water_used:.2f}L")
    print(f"  Power: {sim.power_used:.2f}kWh")
    
    # Get recommendations
    print("\nCurrent recommendations:")
    for rec in get_recommendations(sim):
        print(f"  {rec}")