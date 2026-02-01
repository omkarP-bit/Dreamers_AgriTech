"""
API Request/Response schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== Auth Schemas ====================

class RegisterRequest(BaseModel):
    """User registration request"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    """User response (without password)"""
    id: str = Field(alias="_id")
    name: str
    email: str
    created_at: datetime

    class Config:
        populate_by_name = True


# ==================== Chat Schemas ====================

class ChatMessage(BaseModel):
    """Chat message request"""
    message: str = Field(..., min_length=1)
    season_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response from bot"""
    success: bool
    response: str
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None


class ConversationHistory(BaseModel):
    """Conversation history item"""
    id: str = Field(alias="_id")
    farmer_message: str
    final_response: str
    created_at: datetime

    class Config:
        populate_by_name = True


# ==================== Season Schemas ====================

class CreateSeasonRequest(BaseModel):
    """Create new crop season"""
    crop_type: str
    variety: Optional[str] = None
    farmer_type: str = Field(..., description="greenhouse or normal")
    soil_type: Optional[str] = None
    previous_crop: Optional[str] = None


class SeasonResponse(BaseModel):
    """Season response"""
    id: str = Field(alias="_id")
    farmer_id: str
    crop_type: str
    current_phase: str
    status: str
    created_at: datetime

    class Config:
        populate_by_name = True


# ==================== Task Schemas ====================

class TaskResponse(BaseModel):
    """Task response"""
    id: str = Field(alias="_id")
    task_name: str
    description: Optional[str] = None
    planned_action: str
    status: str
    priority: str
    phase: str
    created_at: datetime

    class Config:
        populate_by_name = True


# ==================== Market/Weather Schemas ====================

class MarketPriceResponse(BaseModel):
    """Market price response"""
    crop: str
    current_price: float
    trend: str
    location: Optional[str] = None


class WeatherResponse(BaseModel):
    """Weather response"""
    location: str
    temperature: float
    humidity: float
    condition: str
    forecast: List[Dict[str, Any]]
