from langgraph_supervisor.supervisor import create_supervisor
from multi_agent_system.strategies.game_theory import ShapleyValueStrategy, NashEquilibriumAllocation
from multi_agent_system.protocols.communication import DynamicRoutingProtocol, CommunicationTopology
from multi_agent_system.strategies import AgentProfile  # 导入AgentProfile类
from multi_agent_system.strategies import TaskContext  # 添加缺失的导入
from multi_agent_system.visualization.network_visualizer import NetworkVisualizer
from multi_agent_system.visualization.workflow_visualizer import WorkflowVisualizer
from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage


def build_supervisor_workflow(agents, model):
    """构建多层级主管工作流"""
    # 创建基础工作流
    workflow = StateGraph(state_schema=AgentState)
    
    # 定义基础主管节点处理函数
    def base_supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state.get("messages", [])
        if not messages:
            return {"next": "__end__"}
            
        last_message = messages[-1]
        content = last_message.content.lower()
        
        # 基础任务分发逻辑
        if "math" in content:
            return {"next": "math_expert"}
        elif "weather" in content:
            return {"next": "weather_forecast"}
        return {"next": "advanced_supervisor"}
    
    # 定义高级主管节点处理函数
    def advanced_supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state.get("messages", [])
        if not messages:
            return {"next": "__end__"}
            
        last_message = messages[-1]
        content = last_message.content.lower()
        
        # 高级任务分发逻辑
        if "complex" in content or "difficult" in content:
            # 对于复杂任务，可能需要多个代理协作
            return {
                "next": "math_expert",
                "messages": messages + [AIMessage(content="这是一个复杂任务，需要多个代理协作。")]
            }
        elif "urgent" in content or "priority" in content:
            # 对于紧急任务，直接分配给最合适的代理
            if "math" in content:
                return {"next": "math_expert"}
            elif "weather" in content:
                return {"next": "weather_forecast"}
        
        return {"next": "__end__"}
    
    # 添加主管节点
    workflow.add_node("base_supervisor", base_supervisor_node)
    workflow.add_node("advanced_supervisor", advanced_supervisor_node)
    
    # 添加代理节点
    for agent in agents:
        workflow.add_node(agent.name, agent)
    
    # 设置边
    workflow.add_edge("__start__", "base_supervisor")
    workflow.add_edge("base_supervisor", "advanced_supervisor")
    
    # 添加代理边
    for agent in agents:
        # 从基础主管到代理
        workflow.add_edge("base_supervisor", agent.name)
        # 从高级主管到代理
        workflow.add_edge("advanced_supervisor", agent.name)
        # 从代理回到基础主管
        workflow.add_edge(agent.name, "base_supervisor")
    
    # 添加结束边
    workflow.add_edge("base_supervisor", "__end__")
    workflow.add_edge("advanced_supervisor", "__end__")
    
    # 为每个代理添加结束边
    for agent in agents:
        workflow.add_edge(agent.name, "__end__")
    
    return workflow


class EnhancedSupervisor:
    """增强型主管代理，实现多层级决策机制"""
    def __init__(self, base_supervisor):
        self.base_supervisor = base_supervisor
        self.coalition_strategy = ShapleyValueStrategy()
        self.resource_strategy = NashEquilibriumAllocation()
        self.communication_protocol = DynamicRoutingProtocol()
        
    def compile(self):
        """编译工作流图"""
        # 直接使用base_supervisor作为StateGraph实例
        return self.base_supervisor.compile()
        
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
        agents = [agent.name for agent in self.base_supervisor.graph.nodes.values()]
        communication_topology = self.communication_protocol.establish_links(
            agents,
            {"complexity": task_context.complexity}
        )
        
        # 创建可视化器并显示拓扑
        visualizer = NetworkVisualizer(communication_topology)
        visualizer.visualize(str(output_path) if output_path else None)  # 正确调用可视化方法
        
    def visualize_workflow(self, output_path: Optional[str] = None):
        """可视化工作流程"""
        # 创建工作流可视化器
        workflow = self.base_supervisor.compile()
        workflow_visualizer = WorkflowVisualizer(workflow)
        workflow_visualizer.visualize(str(output_path) if output_path else None)

__all__ = ["build_supervisor_workflow",
            "EnhancedSupervisor"]