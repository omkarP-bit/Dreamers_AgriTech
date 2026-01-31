"""
Conversation Service

Manages agent conversations, stores them in database, and provides conversation history
"""

from typing import Dict, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class ConversationService:
    """
    Service for managing agent conversations
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.conversations_collection = db.agent_conversations
    
    async def save_conversation(
        self,
        season_id: str,
        farmer_message: str,
        agent_debate: List[Dict],
        final_response: str,
        active_agents: List[str],
        phase: str
    ) -> str:
        """
        Save a conversation to database
        
        Args:
            season_id: Crop season ID
            farmer_message: Message from farmer
            agent_debate: List of agent responses
            final_response: Final synthesized response
            active_agents: List of agents that participated
            phase: Current phase
            
        Returns:
            Conversation ID
        """
        conversation = {
            "season_id": season_id,
            "farmer_message": farmer_message,
            "agent_debate": agent_debate,
            "final_response": final_response,
            "active_agents": active_agents,
            "phase": phase,
            "created_at": datetime.utcnow(),
        }
        
        result = await self.conversations_collection.insert_one(conversation)
        return str(result.inserted_id)
    
    async def get_conversation_history(
        self,
        season_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get conversation history for a season
        
        Args:
            season_id: Crop season ID
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversations
        """
        cursor = self.conversations_collection.find(
            {"season_id": season_id}
        ).sort("created_at", -1).limit(limit)
        
        conversations = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for conv in conversations:
            conv["_id"] = str(conv["_id"])
            if isinstance(conv.get("created_at"), datetime):
                conv["created_at"] = conv["created_at"].isoformat()
        
        return conversations
    
    async def get_latest_conversation(self, season_id: str) -> Optional[Dict]:
        """Get the most recent conversation for a season"""
        conversation = await self.conversations_collection.find_one(
            {"season_id": season_id},
            sort=[("created_at", -1)]
        )
        
        if conversation:
            conversation["_id"] = str(conversation["_id"])
            if isinstance(conversation.get("created_at"), datetime):
                conversation["created_at"] = conversation["created_at"].isoformat()
        
        return conversation
    
    async def get_conversation_stats(self, season_id: str) -> Dict:
        """Get statistics about conversations for a season"""
        pipeline = [
            {"$match": {"season_id": season_id}},
            {"$group": {
                "_id": "$phase",
                "count": {"$sum": 1},
                "agents": {"$addToSet": "$active_agents"}
            }}
        ]
        
        result = await self.conversations_collection.aggregate(pipeline).to_list(length=None)
        
        return {
            "by_phase": result,
            "total_conversations": sum(r["count"] for r in result)
        }