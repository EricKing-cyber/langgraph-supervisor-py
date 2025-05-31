from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

@dataclass
class AgentProfile:
    """专业代理的特征描述"""
    name: str
    expertise: Set[str]  # 专业领域
    capacity: int        # 处理能力等级
    availability: float  # 可用性评分

@dataclass
class TaskContext:
    """任务上下文信息"""
    required_skills: Set[str]  # 所需技能
    complexity: float          # 任务复杂度
    urgency: float             # 紧急程度
    history: List[str]         # 任务历史记录