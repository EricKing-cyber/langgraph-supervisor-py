from langgraph_supervisor.supervisor import create_supervisor
from multi_agent_system.strategies.game_theory import ShapleyValueStrategy, NashEquilibriumAllocation
from multi_agent_system.protocols.communication import DynamicRoutingProtocol, CommunicationTopology
from multi_agent_system.strategies import AgentProfile  # 导入AgentProfile类


def build_supervisor_workflow(agents, model):
    """构建监督者工作流"""
    return create_supervisor(
        agents=agents,
        model=model,
        prompt="你是一个团队监督者，管理数学专家和天气专家。对于数学问题，使用math_expert；对于天气问题，使用weather_expert。"
    )


class EnhancedSupervisor:
    """增强型主管代理，实现多层级决策机制"""
    def __init__(self, base_supervisor):
        self.base_supervisor = base_supervisor
        self.coalition_strategy = ShapleyValueStrategy()
        self.resource_strategy = NashEquilibriumAllocation()
        self.communication_protocol = DynamicRoutingProtocol()

    def compile(self):
        """编译工作流图"""
        return self.base_supervisor.graph.compile()
        
    def dynamic_handoff(self, task_context):
        """动态任务调度和资源分配"""
        # 1. 提取代理配置
        agents = [agent for agent in self.base_supervisor.graph.nodes if agent != 'supervisor']
        agent_profiles = [
            AgentProfile(
                name=agent.name,
                expertise={agent.type},  # 假设代理类型作为专业领域
                capacity=5,              # 默认处理能力
                availability=1.0         # 默认可用性
            ) for agent in self.base_supervisor.graph.nodes.values()
        ]
        
        # 2. 联盟形成
        coalitions = self.coalition_strategy.form_coalitions(agent_profiles, task_context)
        
        # 3. 资源分配
        resources = self.resource_strategy.allocate_resources(coalitions, task_context)
        
        # 4. 通信路由
        communication_topology = self.communication_protocol.establish_links(
            [agent.name for profile in coalitions for agent in profile],
            {"complexity": task_context.complexity}
        )
        
        # 5. 构建增强上下文
        enhanced_context = {
            "messages": [{"role": "user", "content": " ".join(task_context.required_skills)}],
            "config": {
                "resources": resources,
                "links": communication_topology.links,
                "efficiency": communication_topology.efficiency_score
            }
        }
        
        # 6. 调用基础主管代理
        result = self.base_supervisor.invoke(enhanced_context)
        
        return result


__all__ = ["build_supervisor_workflow",
            "EnhancedSupervisor"]