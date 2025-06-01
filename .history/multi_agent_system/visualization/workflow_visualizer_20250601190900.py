# from typing import List, Dict, Any, Optional
# from langgraph.graph.state import StateNodeSpec

# from langgraph.graph import StateGraph
# import matplotlib.pyplot as plt
# from typing import List, Dict, Any, Optional
# from langgraph.graph.state import StateNodeSpec
# import networkx as nx
# from matplotlib.lines import Line2D

# class WorkflowVisualizer:
#     """工作流程可视化工具"""
#     def __init__(self, workflow: StateGraph):
#         self.workflow = workflow
#         self.graph = nx.DiGraph()
        
#         # 构建工作流图
#         self._build_graph()
        
#     def _build_graph(self):
#         """构建工作流图"""
#         # 从工作流中提取节点和边
#         for node_name, node in self.workflow.nodes.items():
#             self.graph.add_node(
#                 node_name,
#                 type='node',
#                 data=node
#             )
            
#         # 添加边
#         for edge in self.workflow.edges:
#             # 使用元组索引访问
#             self.graph.add_edge(
#                 edge[0],  # start节点
#                 edge[1],  # end节点
#                 condition='default'  # 默认条件
#             )
                
#     def visualize(self, output_path: Optional[str] = None):
#         """可视化工作流程"""
#         plt.figure(figsize=(14, 10))
        
#         # 布局算法
#         pos = nx.spring_layout(self.graph, k=1.5, iterations=50)
        
#         # 绘制节点
#         nodes = self.graph.nodes()
#         node_colors = []
        
#         # 区分不同类型的节点
#         for node in nodes:
#             if node == 'supervisor':
#                 color = '#FFA500'  # 橙色表示主管代理
#             elif node == 'start':
#                 color = '#90EE90'  # 浅绿色表示开始节点
#             elif node == 'end':
#                 color = '#FFB6C1'  # 粉红色表示结束节点
#             else:
#                 color = '#87CEFA'  # 天蓝色表示普通代理
#             node_colors.append(color)
            
#         nx.draw_networkx_nodes(
#             self.graph, pos,
#             node_size=1000,
#             node_color='#87CEFA',  # 使用固定默认颜色
#             alpha=0.8
#         )
        
#         # 绘制边
#         edges = self.graph.edges(data=True)
#         for edge in edges:
#             source, target, data = edge
            
#             # 根据边的类型设置样式
#             if 'condition' in data:
#                 color = 'red' if data['condition'] != 'default' else 'gray'
#                 style = 'solid' if data['condition'] != 'default' else 'dashed'
#             else:
#                 color = 'gray'
#                 style = 'dashed'
                
#             nx.draw_networkx_edges(
#                 self.graph, pos,
#                 edgelist=[(source, target)],
#                 width=2,
#                 edge_color=color,
#                 style=style,
#                 arrows=True,
#                 arrowstyle='->',
#                 alpha=0.8
#             )
            
#         # 绘制标签
#         labels = {node: node for node in nodes}
#         nx.draw_networkx_labels(
#             self.graph, pos,
#             labels=labels,
#             font_size=10,
#             font_family='sans-serif'
#         )
        
#         # 添加边标签（条件）
#         edge_labels = {(u, v): d['condition'] for u, v, d in edges}
#         nx.draw_networkx_edge_labels(
#             self.graph, pos,
#             edge_labels=edge_labels,
#             font_size=8,
#             font_family='sans-serif',
#             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
#         )
        
#         plt.title('多智能体系统工作流程', fontsize=14)
#         plt.axis('off')
        
#         if output_path:
#             plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
#         plt.show()