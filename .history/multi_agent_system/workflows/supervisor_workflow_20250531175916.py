from langgraph_supervisor.supervisor import create_supervisor
from multi_agent_system.strategies.game_theory import ShapleyValueStrategy, NashEquilibriumAllocation
from multi_agent_system.protocols.communication import DynamicRoutingProtocol, CommunicationTopology
from multi_agent_system.strategies import AgentProfile
from multi_agent_system.strategies import TaskContext
from multi_agent_system.visualization.network_visualizer import NetworkVisualizer
from multi_agent_system.visualization.workflow_visualizer import WorkflowVisualizer
from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.runnables import RunnableConfig

def build_supervisor_workflow(agents, model):
    """构建监督者工作流"""
    # 创建基础工作流
    workflow = StateGraph(state_schema=AgentState)
    
    # 添加代理节点
    for agent in agents:
        workflow.add_node(agent.name, agent)
    
    # 创建主管代理
    supervisor = create_supervisor(
        agents=agents,
        model=model,
        state_schema=AgentState,
        prompt="你是一个团队监督者，管理数学专家和天气专家。对于数学问题，使用math_expert；对于天气问题，使用weather_expert。"
    )
    
    # 添加主管节点
    workflow.add_node("supervisor", supervisor)
    
    # 设置边
    for agent in agents:
        workflow.add_edge("supervisor", agent.name)
        workflow.add_edge(agent.name, "supervisor")
    
    # 编译工作流
    return workflow.compile()

class EnhancedSupervisor:
    """增强型主管代理，实现多层级决策机制"""
    def __init__(self, base_workflow):
        self.workflow = base_workflow
        self.coalition_strategy = ShapleyValueStrategy()
        self.resource_strategy = NashEquilibriumAllocation()
        self.communication_protocol = DynamicRoutingProtocol()
        
    def compile(self):
        """编译工作流图"""
        return self.workflow
        
    def dynamic_handoff(self, task_context):
        """动态任务调度和资源分配"""
        # 1. 提取代理配置
        agents = [node for node in self.workflow.nodes if node != 'supervisor']
        agent_profiles = [
            AgentProfile(
                name=agent,
                expertise={self.workflow.nodes[agent].type if hasattr(self.workflow.nodes[agent], 'type') else 'general'},
                capacity=5,
                availability=1.0
            ) for agent in agents
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
        
        return enhanced_context
    
    def visualize_topology(self, output_path: Optional[str] = None):
        """可视化当前通信拓扑"""
        # 创建示例任务上下文
        task_context = TaskContext(
            required_skills=set(),
            complexity=0.5,
            urgency=0.5,
            history=[]
        )
        
        # 生成通信拓扑
        agents = [node for node in self.workflow.nodes if node != 'supervisor']
        communication_topology = self.communication_protocol.establish_links(
            agents,
            {"complexity": task_context.complexity}
        )
        
        # 创建可视化器并显示拓扑
        visualizer = NetworkVisualizer(communication_topology)
        visualizer.visualize(str(output_path) if output_path else None)
        
    def visualize_workflow(self, output_path: Optional[str] = None):
        """可视化工作流程"""
        workflow_visualizer = WorkflowVisualizer(self.workflow)
        workflow_visualizer.visualize(str(output_path) if output_path else None)

__all__ = ["build_supervisor_workflow", "EnhancedSupervisor"]