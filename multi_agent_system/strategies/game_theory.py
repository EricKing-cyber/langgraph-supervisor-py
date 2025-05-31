from . import AgentProfile, TaskContext
from collections import defaultdict
from typing import List, Dict
import math

class CoalitionFormationStrategy:
    """联盟形成策略基类"""
    def form_coalitions(self, agents: List[AgentProfile], task: TaskContext) -> List[List[AgentProfile]]:
        raise NotImplementedError()
        
class ResourceAllocationStrategy:
    """资源分配策略基类"""
    def allocate_resources(self, coalitions: List[List[AgentProfile]], task: TaskContext) -> Dict[str, float]:
        raise NotImplementedError()
        
class ShapleyValueStrategy(CoalitionFormationStrategy):
    """基于夏普利值的联盟形成策略"""
    def form_coalitions(self, agents: List[AgentProfile], task: TaskContext) -> List[List[AgentProfile]]:
        # 实现夏普利值计算逻辑
        # 简化版：按专业领域匹配度分组
        skill_match = {}
        
        # 按技能匹配度分组
        for agent in agents:
            match_score = len(set(agent.expertise) & task.required_skills)
            if match_score > 0:
                group_key = f"skill_{match_score}"
                if group_key not in skill_match:
                    skill_match[group_key] = []
                skill_match[group_key].append(agent)
                
        # 返回分组结果
        return list(skill_match.values())
        
class NashEquilibriumAllocation(ResourceAllocationStrategy):
    """基于纳什均衡的资源分配策略"""
    def allocate_resources(self, coalitions: List[List[AgentProfile]], task: TaskContext) -> Dict[str, float]:
        allocation = {}
        total_capacity = sum(
            sum(agent.capacity for agent in coalition) 
            for coalition in coalitions
        )
        
        for coalition in coalitions:
            coalition_capacity = sum(agent.capacity for agent in coalition)
            coalition_share = coalition_capacity / total_capacity if total_capacity > 0 else 0
            
            for agent in coalition:
                base_share = agent.capacity / coalition_capacity if coalition_capacity > 0 else 0
                urgency_factor = 1 + task.urgency * 0.5
                availability_factor = agent.availability
                
                final_share = base_share * coalition_share * urgency_factor * availability_factor
                allocation[agent.name] = final_share
                
        return allocation