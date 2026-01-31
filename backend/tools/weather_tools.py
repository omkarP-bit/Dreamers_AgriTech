"""
Weather data fetching using OpenWeatherMap API
Free tier provides: 5-day forecast, current weather
"""
import requests
from typing import Dict, Optional
from config.settings import settings
from datetime import datetime


class WeatherTools:
    """OpenWeatherMap API integration"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    @staticmethod
    def get_current_weather(location: str) -> Optional[Dict]:
        """
        Get current weather for a location
        
        Args:
            location: City name (e.g., "Ludhiana, Punjab" or "Ludhiana,IN")
        
        Returns:
            Dict with current weather data or None if failed
        """
        if settings.MOCK_APIS:
            return WeatherTools._mock_current_weather()
        
        try:
            url = f"{WeatherTools.BASE_URL}/weather"
            params = {
                "q": location,
                "appid": settings.OPENWEATHER_API_KEY,
                "units": "metric"  # Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "location": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "weather": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "clouds": data["clouds"]["all"],
                "timestamp": datetime.fromtimestamp(data["dt"]).isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching current weather: {e}")
            return None
        except KeyError as e:
            print(f"❌ Error parsing weather data: {e}")
            return None
    
    @staticmethod
    def get_5day_forecast(location: str) -> Optional[Dict]:
        """
        Get 5-day weather forecast (3-hour intervals)
        
        Args:
            location: City name
        
        Returns:
            Dict with forecast data or None if failed
        """
        if settings.MOCK_APIS:
            return WeatherTools._mock_5day_forecast()
        
        try:
            url = f"{WeatherTools.BASE_URL}/forecast"
            params = {
                "q": location,
                "appid": settings.OPENWEATHER_API_KEY,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse forecast data
            forecast_list = []
            for item in data["list"]:
                forecast_list.append({
                    "datetime": datetime.fromtimestamp(item["dt"]).isoformat(),
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "weather": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "wind_speed": item["wind"]["speed"],
                    "rain_probability": item.get("pop", 0) * 100,  # Probability of precipitation
                    "rain_volume": item.get("rain", {}).get("3h", 0)  # Rain volume in last 3h
                })
            
            # Calculate daily summaries
            daily_summary = WeatherTools._calculate_daily_summary(forecast_list)
            
            return {
                "location": data["city"]["name"],
                "country": data["city"]["country"],
                "forecast_3hourly": forecast_list,
                "daily_summary": daily_summary,
                "total_forecasts": len(forecast_list)
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching 5-day forecast: {e}")
            return None
        except KeyError as e:
            print(f"❌ Error parsing forecast data: {e}")
            return None
    
    @staticmethod
    def _calculate_daily_summary(forecast_list: list) -> list:
        """Calculate daily summaries from 3-hourly data"""
        daily_data = {}
        
        for item in forecast_list:
            date = item["datetime"].split("T")[0]
            
            if date not in daily_data:
                daily_data[date] = {
                    "date": date,
                    "temps": [],
                    "humidity": [],
                    "rain_prob": [],
                    "rain_volume": [],
                    "weather_conditions": []
                }
            
            daily_data[date]["temps"].append(item["temperature"])
            daily_data[date]["humidity"].append(item["humidity"])
            daily_data[date]["rain_prob"].append(item["rain_probability"])
            daily_data[date]["rain_volume"].append(item["rain_volume"])
            daily_data[date]["weather_conditions"].append(item["weather"])
        
        # Create summaries
        summaries = []
        for date, data in daily_data.items():
            summary = {
                "date": date,
                "temp_min": min(data["temps"]),
                "temp_max": max(data["temps"]),
                "temp_avg": sum(data["temps"]) / len(data["temps"]),
                "humidity_avg": sum(data["humidity"]) / len(data["humidity"]),
                "rain_probability": max(data["rain_prob"]),
                "total_rain_mm": sum(data["rain_volume"]),
                "dominant_weather": max(set(data["weather_conditions"]), 
                                       key=data["weather_conditions"].count)
            }
            summaries.append(summary)
        
        return summaries
    
    @staticmethod
    def get_weather_analysis(location: str) -> Dict:
        """
        Get comprehensive weather analysis combining current and forecast
        
        Args:
            location: City name
        
        Returns:
            Dict with current weather, 5-day forecast, and agricultural insights
        """
        current = WeatherTools.get_current_weather(location)
        forecast = WeatherTools.get_5day_forecast(location)
        
        if not current or not forecast:
            return {
                "success": False,
                "error": "Failed to fetch weather data"
            }
        
        # Agricultural insights based on weather
        insights = WeatherTools._generate_agricultural_insights(current, forecast)
        
        return {
            "success": True,
            "current_weather": current,
            "forecast_5day": forecast,
            "agricultural_insights": insights
        }
    
    @staticmethod
    def _generate_agricultural_insights(current: Dict, forecast: Dict) -> Dict:
        """Generate agriculture-specific weather insights"""
        daily = forecast["daily_summary"]
        
        # Calculate total expected rainfall
        total_rain = sum(day["total_rain_mm"] for day in daily)
        
        # Count rainy days
        rainy_days = sum(1 for day in daily if day["rain_probability"] > 50)
        
        # Temperature analysis
        avg_temp = sum(day["temp_avg"] for day in daily) / len(daily)
        max_temp = max(day["temp_max"] for day in daily)
        min_temp = min(day["temp_min"] for day in daily)
        
        # Humidity analysis
        avg_humidity = sum(day["humidity_avg"] for day in daily) / len(daily)
        
        return {
            "total_expected_rainfall_mm": round(total_rain, 2),
            "rainy_days_count": rainy_days,
            "average_temperature": round(avg_temp, 1),
            "temperature_range": {
                "min": round(min_temp, 1),
                "max": round(max_temp, 1)
            },
            "average_humidity": round(avg_humidity, 1),
            "is_monsoon_like": rainy_days >= 3 and total_rain > 20,
            "suitable_for_sowing": current["temperature"] > 15 and rainy_days > 0,
            "irrigation_needed": total_rain < 10,
            "high_temperature_warning": max_temp > 38,
            "frost_warning": min_temp < 5
        }
    
    # Mock data for testing without API key
    @staticmethod
    def _mock_current_weather() -> Dict:
        """Mock current weather data"""
        return {
            "location": "Ludhiana",
            "country": "IN",
            "temperature": 28.5,
            "feels_like": 30.2,
            "humidity": 65,
            "pressure": 1013,
            "weather": "Clouds",
            "description": "scattered clouds",
            "wind_speed": 3.5,
            "clouds": 40,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _mock_5day_forecast() -> Dict:
        """Mock 5-day forecast data"""
        import random
        from datetime import timedelta
        
        forecast_list = []
        base_date = datetime.utcnow()
        
        for i in range(40):  # 5 days * 8 intervals (3-hour each)
            dt = base_date + timedelta(hours=3*i)
            forecast_list.append({
                "datetime": dt.isoformat(),
                "temperature": random.uniform(22, 35),
                "feels_like": random.uniform(23, 36),
                "humidity": random.uniform(50, 80),
                "weather": random.choice(["Clear", "Clouds", "Rain"]),
                "description": "mock weather",
                "wind_speed": random.uniform(2, 8),
                "rain_probability": random.uniform(0, 80),
                "rain_volume": random.uniform(0, 5)
            })
        
        daily_summary = WeatherTools._calculate_daily_summary(forecast_list)
        
        return {
            "location": "Ludhiana",
            "country": "IN",
            "forecast_3hourly": forecast_list,
            "daily_summary": daily_summary,
            "total_forecasts": len(forecast_list)
        }
# Module-level functions for orchestrator compatibility
def get_weather_forecast(location: str, forecast_days: int = 7, historical_years: int = 3) -> Dict:
    """
    Module-level wrapper for orchestrator compatibility
    """
    analysis = WeatherTools.get_weather_analysis(location)
    return analysis if analysis.get("success") else {"error": "Failed to fetch weather"}


def register_weather_tools() -> Dict:
    """Register weather tools"""
    return {
        "get_weather_forecast": get_weather_forecast
    }