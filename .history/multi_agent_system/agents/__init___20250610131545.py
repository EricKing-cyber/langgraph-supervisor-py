# agents/__init__.py
from .math_agent import create_math_agent
from .weather_agent import create_weather_agent
from .research_agent import create_research_agent

__all__ = [
    "create_math_agent",
    "create_weather_agent",
    "create_research_agent"
]