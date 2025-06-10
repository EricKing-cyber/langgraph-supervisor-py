# agents/__init__.py
from .math_agent import create_math_agent
from .weather_agent import create_weather_agent
from .research_agent import create_research_agent
from .specialized_research_agents import (
    create_legal_research_agent,
    create_medical_research_agent,
    create_engineering_research_agent,
    create_socialscience_research_agent,
    create_climate_research_agent,
    create_multisource_research_agent
)

__all__ = [
    "create_math_agent",
    "create_weather_agent",
    "create_research_agent",
    "create_legal_research_agent",
    "create_medical_research_agent",
    "create_engineering_research_agent",
    "create_socialscience_research_agent",
    "create_climate_research_agent",
    "create_multisource_research_agent"
]