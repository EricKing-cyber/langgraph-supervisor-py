from langgraph_supervisor import create_supervisor
import os

def build_supervisor_workflow(agents, model):
    """构建监督者工作流"""
    return create_supervisor(
        agents=agents,
        model=model,
        prompt="你是一个团队监督者，管理数学专家和天气专家。对于数学问题，使用math_expert；对于天气问题，使用weather_expert。"
    )

__all__ = ["build_supervisor_workflow"]