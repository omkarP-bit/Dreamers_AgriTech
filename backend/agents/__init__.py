"""
Agents Module

Multi-agent system for agricultural guidance
AutoGen 0.7.5 compatible
"""

# CRITICAL: Import groq_wrapper BEFORE orchestrator
# orchestrator.py depends on groq_wrapper.py
from .groq_wrapper import GroqChatCompletionClient

# Base configuration and utilities
from .base_agent import (
    AgentConfig,
    ToolExecutor,
    ConversationLogger,
    GROQ_API_KEY,
    GROQ_MODEL
)

# Individual agents
from .pre_sowing_agent import PreSowingAgent, create_pre_sowing_agent
from .growth_agent import GrowthAgent, create_growth_agent
from .harvest_agent import HarvestAgent, create_harvest_agent

# Orchestrator (import AFTER groq_wrapper)
from .orchestrator import FarmingAgentOrchestrator, create_orchestrator

__all__ = [
    # Groq wrapper
    "GroqChatCompletionClient",
    
    # Base configuration and utilities
    "AgentConfig",
    "ToolExecutor",
    "ConversationLogger",
    "GROQ_API_KEY",
    "GROQ_MODEL",
    
    # Agent classes
    "PreSowingAgent",
    "GrowthAgent",
    "HarvestAgent",
    
    # Factory functions
    "create_pre_sowing_agent",
    "create_growth_agent",
    "create_harvest_agent",
    
    # Orchestrator
    "FarmingAgentOrchestrator",
    "create_orchestrator"
]