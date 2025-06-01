from langgraph_supervisor.supervisor import create_supervisor,create_top_level_supervisor


def build_supervisor_workflow(agents, model):
    """构建监督者工作流"""
    return create_supervisor(
        agents=agents,
        model=model,
        prompt="你是一个团队监督者，管理数学专家和天气专家。对于代数问题，使用algebra_expert；对于微积分问题，使用calculus_expert。",
    )

def build_top_level_supervisor(middle_supervisors, model):
    """构建顶层监督者"""
    return create_top_level_supervisor(
        middle_supervisors=middle_supervisors,
        model=model,
    )

# class EnhancedSupervisor:
#     """增强型主管代理，实现多层级决策机制"""
#     def __init__(self, base_supervisor):
#         self.base_supervisor = base_supervisor
#         self.coalition_strategy = ShapleyValueStrategy()
#         self.resource_strategy = NashEquilibriumAllocation()
#         self.communication_protocol = DynamicRoutingProtocol()
        
#     def compile(self):
#         """编译工作流图"""
#         # 直接使用base_supervisor作为StateGraph实例
#         return self.base_supervisor.compile()
        
#     def dynamic_handoff(self, task_context):
#         """动态任务调度和资源分配"""
#         # 1. 提取代理配置
#         agents = [agent for agent in self.base_supervisor.graph.nodes if agent != 'supervisor']
#         agent_profiles = [
#             AgentProfile(
#                 name=agent.name,
#                 expertise={agent.type},  # 假设代理类型作为专业领域
#                 capacity=5,              # 默认处理能力
#                 availability=1.0         # 默认可用性
#             ) for agent in self.base_supervisor.graph.nodes.values()
#         ]
        
#         # 2. 联盟形成
#         coalitions = self.coalition_strategy.form_coalitions(agent_profiles, task_context)
        
#         # 3. 资源分配
#         resources = self.resource_strategy.allocate_resources(coalitions, task_context)
        
#         # 4. 通信路由
#         communication_topology = self.communication_protocol.establish_links(
#             [agent.name for profile in coalitions for agent in profile],
#             {"complexity": task_context.complexity}
#         )
        
#         # 5. 构建增强上下文
#         enhanced_context = {
#             "messages": [{"role": "user", "content": " ".join(task_context.required_skills)}],
#             "config": {
#                 "resources": resources,
#                 "links": communication_topology.links,
#                 "efficiency": communication_topology.efficiency_score
#             }
#         }
        
#         # 6. 调用基础主管代理
#         result = self.base_supervisor.invoke(enhanced_context)
        
#         return result
    
#     def visualize_topology(self, output_path: Optional[str] = None):
#         """可视化当前通信拓扑"""
#         # 创建示例任务上下文
#         task_context = TaskContext(
#             required_skills=set(),
#             complexity=0.5,
#             urgency=0.5,
#             history=[]
#         )
        
#         # 生成通信拓扑
#         agents = [agent.name for agent in self.base_supervisor.graph.nodes.values()]
#         communication_topology = self.communication_protocol.establish_links(
#             agents,
#             {"complexity": task_context.complexity}
#         )
        
#         # 创建可视化器并显示拓扑
#         visualizer = NetworkVisualizer(communication_topology)
#         visualizer.visualize(str(output_path) if output_path else None)  # 正确调用可视化方法
        
#     def visualize_workflow(self, output_path: Optional[str] = None):
#         """可视化工作流程"""
#         # 创建工作流可视化器
#         workflow = self.base_supervisor.compile()
#         workflow_visualizer = WorkflowVisualizer(workflow)
#         workflow_visualizer.visualize(str(output_path) if output_path else None)

__all__ = ["build_supervisor_workflow",
            "build_top_level_supervisor"]