"""
API Routes

Main router with all endpoints organized by functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from models.database import Database
from schemas.api_schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    ChatMessage, ChatResponse, CreateSeasonRequest, SeasonResponse
)
from services.auth_service import AuthService
from agents.orchestrator import FarmingAgentOrchestrator

# Security
security = HTTPBasic()

# Main router
router = APIRouter()

# Global orchestrator instances (one per season) - PERSISTENT!
orchestrators = {}
orchestrator_contexts = {}  # Track which conversations have been loaded

async def get_orchestrator(season_id: str, db: AsyncIOMotorDatabase = None):
    """
    Get or create orchestrator instance for a season with full context loaded.
    
    IMPORTANT: Orchestrator is created ONCE per season and reused.
    Context is loaded ONCE on first creation.
    """
    if season_id not in orchestrators:
        print(f"\n📦 CREATING NEW ORCHESTRATOR for season {season_id}")
        from agents.orchestrator import FarmingAgentOrchestrator
        orchestrators[season_id] = FarmingAgentOrchestrator(
            season_id=season_id,
            current_phase="pre_sowing",
            farmer_type="normal"
        )
        orchestrator_contexts[season_id] = False  # Mark as not yet loaded
        
        # Load conversation history ONLY on first creation
        if db is not None and not orchestrator_contexts[season_id]:
            print(f"  📂 Loading conversation history for first time...")
            previous_conversations = await db.agent_conversations.find(
                {"season_id": season_id}
            ).sort("created_at", 1).to_list(100)
            
            if previous_conversations:
                print(f"  Found {len(previous_conversations)} previous messages")
                for conv in previous_conversations:
                    # Extract farmer context from the message
                    if conv.get("farmer_message"):
                        print(f"    📝 Processing: {conv['farmer_message'][:60]}...")
                        orchestrators[season_id]._extract_farmer_info(conv["farmer_message"])
                        orchestrators[season_id].logger.log("Farmer", conv["farmer_message"])
                    # Log the agent response too
                    if conv.get("final_response"):
                        orchestrators[season_id].logger.log("Agent", conv["final_response"])
                
                # Update agents with the reconstructed context
                print(f"  🔄 Updating agent system messages with farmer context...")
                orchestrators[season_id]._update_agent_contexts()
                print(f"  ✅ Context loaded! Agents now have {len(previous_conversations)} previous messages")
            else:
                print(f"  No previous conversations found - starting fresh")
            
            # Mark context as loaded for this season
            orchestrator_contexts[season_id] = True
    else:
        print(f"  ♻️  REUSING existing orchestrator for season {season_id}")
    
    return orchestrators[season_id]


# ==================== Dependency Injections ====================

async def get_db() -> AsyncIOMotorDatabase:
    """Get database connection"""
    if Database.db is None:
        await Database.connect_db()
    return Database.db


async def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get current user from basic auth credentials"""
    email = credentials.username
    password = credentials.password
    
    # Find user by email
    user = await db.users.find_one({"email": email})
    
    if not user or not AuthService.verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return str(user["_id"])


# ==================== AUTH ENDPOINTS ====================

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = AuthService.hash_password(request.password)
    user_doc = {
        "name": request.name,
        "email": request.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
    }
    
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Return response with base64 credentials
    access_token = AuthService.encode_basic_auth(request.email, request.password)
    
    return TokenResponse(
        access_token=access_token,
        token_type="basic",
        user={
            "id": user_id,
            "name": request.name,
            "email": request.email
        }
    )


@auth_router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Login user"""
    # Find user by email
    user = await db.users.find_one({"email": request.email})
    
    if not user or not AuthService.verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user_id = str(user["_id"])
    
    # Return base64 encoded credentials
    access_token = AuthService.encode_basic_auth(request.email, request.password)
    
    return TokenResponse(
        access_token=access_token,
        token_type="basic",
        user={
            "id": user_id,
            "name": user["name"],
            "email": user["email"]
        }
    )


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(user_id: str = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get current user info"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user.get("created_at")
    )


# ==================== CHAT ENDPOINTS ====================

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


@chat_router.post("/", response_model=ChatResponse)
async def chat_message(
    request: ChatMessage,
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send message to chatbot using AI agents"""
    
    # Validate user exists
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get or create season if season_id not provided
    if not request.season_id:
        print(f"  ⚠️  No season_id provided - creating NEW season")
        # Create default season for user
        season_doc = {
            "farmer_id": user_id,
            "crop_type": "unknown",
            "farmer_type": "normal",
            "current_phase": "pre_sowing",
            "status": "active",
            "created_at": datetime.utcnow()
        }
        result = await db.crop_seasons.insert_one(season_doc)
        season_id = str(result.inserted_id)
        print(f"  📦 Created season: {season_id}")
    else:
        season_id = request.season_id
        print(f"  ♻️  Using provided season_id: {season_id}")
    
    # Get orchestrator and process message with AI agents
    bot_response = None
    active_agents = []
    agent_debate = []
    
    try:
        print(f"\n{'='*60}")
        print(f"Chat endpoint: Processing message for user {user_id}")
        print(f"Message: {request.message[:100]}")
        print(f"Season ID: {season_id}")
        print(f"{'='*60}")
        
        orchestrator = await get_orchestrator(season_id, db)
        print(f"✓ Orchestrator ready for season {season_id}")
        
        # Load previous conversation history to rebuild context
        print(f"→ Loading previous conversation history...")
        previous_conversations = await db.agent_conversations.find(
            {"season_id": season_id}
        ).sort("created_at", 1).to_list(100)
        
        # Reconstruct farmer context from previous messages
        if previous_conversations:
            print(f"  Found {len(previous_conversations)} previous messages")
            for conv in previous_conversations:
                # Process farmer message to extract context
                if conv.get("farmer_message"):
                    orchestrator._extract_farmer_info(conv["farmer_message"])
                # Log previous conversation to memory
                orchestrator.logger.log("Farmer", conv.get("farmer_message", ""))
                orchestrator.logger.log("Agent", conv.get("final_response", ""))
            
            # Update agent contexts with historical farmer info
            orchestrator._update_agent_contexts()
            print(f"  ✓ Loaded context from {len(previous_conversations)} previous messages")
        
        # Process message through agent team
        print(f"→ Calling orchestrator.process_message()...")
        agent_result = await orchestrator.process_message(request.message)
        print(f"✓ Agent result received: {type(agent_result)}")
        
        bot_response = agent_result.get("final_response", "")
        active_agents = agent_result.get("active_agents", [])
        agent_debate = agent_result.get("agent_debate", [])
        
        print(f"✓ Response from agents ({len(bot_response)} chars)")
        print(f"  Active agents: {active_agents}")
        
    except Exception as e:
        print(f"\n❌ ERROR in orchestrator:")
        print(f"  Type: {type(e).__name__}")
        print(f"  Message: {str(e)}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        print(f"{'='*60}\n")
        
        # Fallback response if agent fails
        bot_response = f"I'm analyzing your question about farming. To give you the best advice, could you share: your location, soil type, and what crops you're interested in?"
        active_agents = []
        agent_debate = []
    
    # Ensure we have a response
    if not bot_response:
        bot_response = "Thank you for sharing that information. Can you tell me more about what specific farming challenge you'd like help with?"
    
    # Save conversation with agent details
    conversation_doc = {
        "season_id": season_id,
        "farmer_id": user_id,
        "farmer_message": request.message,
        "agent_debate": agent_debate,
        "final_response": bot_response,
        "active_agents": active_agents,
        "phase": "pre_sowing",
        "created_at": datetime.utcnow()
    }
    
    result = await db.agent_conversations.insert_one(conversation_doc)
    conversation_id = str(result.inserted_id)
    
    return ChatResponse(
        success=True,
        response=bot_response,
        conversation_id=conversation_id,
        message_id=conversation_id
    )


@chat_router.get("/history")
async def get_chat_history(
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get chat history for user"""
    
    # Get all conversations for user's seasons
    conversations = await db.agent_conversations.find(
        {"farmer_id": user_id}
    ).sort("created_at", -1).to_list(50)
    
    return {
        "success": True,
        "conversations": [
            {
                "id": str(conv["_id"]),
                "message": conv.get("farmer_message", ""),
                "response": conv.get("final_response", ""),
                "created_at": conv.get("created_at"),
                "season_id": conv.get("season_id")
            }
            for conv in conversations
        ]
    }


# ==================== SEASON ENDPOINTS ====================

season_router = APIRouter(prefix="/seasons", tags=["Seasons"])


@season_router.post("/", response_model=SeasonResponse)
async def create_season(
    request: CreateSeasonRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new crop season"""
    
    season_doc = {
        "farmer_id": user_id,
        "crop_type": request.crop_type,
        "variety": request.variety,
        "farmer_type": request.farmer_type,
        "soil_type": request.soil_type,
        "previous_crop": request.previous_crop,
        "current_phase": "pre_sowing",
        "status": "active",
        "created_at": datetime.utcnow()
    }
    
    result = await db.crop_seasons.insert_one(season_doc)
    
    return SeasonResponse(
        id=str(result.inserted_id),
        farmer_id=user_id,
        crop_type=request.crop_type,
        current_phase="pre_sowing",
        status="active",
        created_at=datetime.utcnow()
    )


@season_router.get("/")
async def get_seasons(
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all seasons for user"""
    
    seasons = await db.crop_seasons.find(
        {"farmer_id": user_id}
    ).to_list(100)
    
    return {
        "success": True,
        "seasons": [
            {
                "id": str(s["_id"]),
                "crop_type": s.get("crop_type"),
                "current_phase": s.get("current_phase"),
                "status": s.get("status"),
                "created_at": s.get("created_at")
            }
            for s in seasons
        ]
    }


# ==================== CROP ENDPOINTS ====================

crop_router = APIRouter(prefix="/crop", tags=["Crop"])


@crop_router.get("/current-season")
async def current_season(user_id: str = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get current season for user"""
    season = await db.crop_seasons.find_one(
        {"farmer_id": user_id, "status": "active"},
        sort=[("created_at", -1)]
    )
    
    if not season:
        return {"success": False, "season": None}
    
    return {
        "success": True,
        "season": {
            "id": str(season["_id"]),
            "crop_type": season.get("crop_type"),
            "phase": season.get("current_phase"),
            "status": season.get("status")
        }
    }


# ==================== PLACEHOLDER ENDPOINTS ====================

task_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@task_router.get("/")
async def get_tasks(user_id: str = Depends(get_current_user)):
    """Get tasks for user"""
    return {"success": True, "tasks": []}


greenhouse_router = APIRouter(prefix="/greenhouse", tags=["Greenhouse"])


@greenhouse_router.get("/sensors")
async def greenhouse_sensors(user_id: str = Depends(get_current_user)):
    """Get greenhouse sensor data"""
    return {"success": True, "sensors": {}}


market_router = APIRouter(prefix="/market", tags=["Market"])


@market_router.get("/prices")
async def market_prices(user_id: str = Depends(get_current_user)):
    """Get market prices"""
    return {"success": True, "prices": {}}


weather_router = APIRouter(prefix="/weather", tags=["Weather"])


@weather_router.get("/{location}")
async def weather(location: str, user_id: str = Depends(get_current_user)):
    """Get weather information"""
    return {"success": True, "location": location, "forecast": {}}


# ==================== Include all routers ====================

router.include_router(auth_router)
router.include_router(chat_router)
router.include_router(season_router)
router.include_router(crop_router)
router.include_router(task_router)
router.include_router(greenhouse_router)
router.include_router(market_router)
router.include_router(weather_router)
