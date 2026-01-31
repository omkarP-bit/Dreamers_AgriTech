"""
Task Service

Manages tasks (instructions from agents) and tracks their completion
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class TaskService:
    """
    Service for managing agricultural tasks
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.tasks_collection = db.tasks
        self.completions_collection = db.task_completions
    
    async def create_task(
        self,
        season_id: str,
        task_name: str,
        description: str,
        planned_action: str,
        scheduled_date: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        priority: str = "medium",
        created_by_agent: str = "system",
        phase: str = "growth"
    ) -> str:
        """
        Create a new task
        
        Args:
            season_id: Crop season ID
            task_name: Name of the task
            description: Detailed description
            planned_action: What the agent instructed
            scheduled_date: When task should be done
            due_date: Latest date to complete
            priority: low/medium/high/critical
            created_by_agent: Which agent created this task
            phase: Which phase this task belongs to
            
        Returns:
            Task ID
        """
        task = {
            "season_id": season_id,
            "task_name": task_name,
            "description": description,
            "planned_action": planned_action,
            "scheduled_date": scheduled_date or datetime.utcnow(),
            "due_date": due_date or (datetime.utcnow() + timedelta(days=7)),
            "status": "pending",
            "priority": priority,
            "created_by_agent": created_by_agent,
            "phase": phase,
            "created_at": datetime.utcnow(),
        }
        
        result = await self.tasks_collection.insert_one(task)
        return str(result.inserted_id)
    
    async def get_pending_tasks(self, season_id: str) -> List[Dict]:
        """Get all pending tasks for a season"""
        cursor = self.tasks_collection.find(
            {"season_id": season_id, "status": "pending"}
        ).sort("due_date", 1)
        
        tasks = await cursor.to_list(length=None)
        
        # Convert ObjectId to string
        for task in tasks:
            task["_id"] = str(task["_id"])
            if isinstance(task.get("scheduled_date"), datetime):
                task["scheduled_date"] = task["scheduled_date"].isoformat()
            if isinstance(task.get("due_date"), datetime):
                task["due_date"] = task["due_date"].isoformat()
            if isinstance(task.get("created_at"), datetime):
                task["created_at"] = task["created_at"].isoformat()
        
        return tasks
    
    async def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a specific task"""
        task = await self.tasks_collection.find_one({"_id": ObjectId(task_id)})
        
        if task:
            task["_id"] = str(task["_id"])
            if isinstance(task.get("scheduled_date"), datetime):
                task["scheduled_date"] = task["scheduled_date"].isoformat()
            if isinstance(task.get("due_date"), datetime):
                task["due_date"] = task["due_date"].isoformat()
            if isinstance(task.get("created_at"), datetime):
                task["created_at"] = task["created_at"].isoformat()
        
        return task
    
    async def complete_task(
        self,
        task_id: str,
        farmer_response: str,
        actual_action: str,
        is_deviation: bool = False,
        agent_analysis: Optional[str] = None
    ) -> Dict:
        """
        Mark a task as completed with farmer's feedback
        
        Args:
            task_id: Task ID
            farmer_response: Natural language response from farmer
            actual_action: Parsed action that farmer took
            is_deviation: Whether farmer deviated from plan
            agent_analysis: Agent's analysis of the deviation
            
        Returns:
            Completion record
        """
        # Update task status
        await self.tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": "completed" if not is_deviation else "modified"}}
        )
        
        # Create completion record
        completion = {
            "task_id": task_id,
            "farmer_response": farmer_response,
            "actual_action": actual_action,
            "is_deviation": is_deviation,
            "agent_analysis": agent_analysis,
            "completion_date": datetime.utcnow(),
        }
        
        result = await self.completions_collection.insert_one(completion)
        completion["_id"] = str(result.inserted_id)
        
        return completion
    
    async def get_task_completion(self, task_id: str) -> Optional[Dict]:
        """Get completion record for a task"""
        completion = await self.completions_collection.find_one({"task_id": task_id})
        
        if completion:
            completion["_id"] = str(completion["_id"])
            if isinstance(completion.get("completion_date"), datetime):
                completion["completion_date"] = completion["completion_date"].isoformat()
        
        return completion
    
    async def get_overdue_tasks(self, season_id: str) -> List[Dict]:
        """Get tasks that are past their due date"""
        cursor = self.tasks_collection.find({
            "season_id": season_id,
            "status": "pending",
            "due_date": {"$lt": datetime.utcnow()}
        }).sort("due_date", 1)
        
        tasks = await cursor.to_list(length=None)
        
        for task in tasks:
            task["_id"] = str(task["_id"])
            if isinstance(task.get("due_date"), datetime):
                task["due_date"] = task["due_date"].isoformat()
        
        return tasks
    
    async def update_task(self, task_id: str, updates: Dict) -> bool:
        """Update a task"""
        result = await self.tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": updates}
        )
        
        return result.modified_count > 0
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        result = await self.tasks_collection.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0
    
    async def get_task_statistics(self, season_id: str) -> Dict:
        """Get task statistics for a season"""
        pipeline = [
            {"$match": {"season_id": season_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        result = await self.tasks_collection.aggregate(pipeline).to_list(length=None)
        
        stats = {status["_id"]: status["count"] for status in result}
        stats["total"] = sum(stats.values())
        
        return stats