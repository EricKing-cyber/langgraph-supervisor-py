from typing import List, Dict, Optional
from dataclasses import dataclass
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from multi_agent_system.protocols.communication import CommunicationTopology, CommunicationLink

class NetworkVisualizer:
    """网络拓扑可视化工具"""
    def __init__(self, topology: CommunicationTopology):
        self.topology = topology
        self.graph = nx.DiGraph()
        
        # 构建网络图
        self._build_graph()
        
    def _build_graph(self):
        """构建网络图"""
        # 添加节点
        for link in self.topology.links:
            self.graph.add_node(link.source)
            self.graph.add_node(link.target)
            # 添加边
            self.graph.add_edge(
                link.source, 
                link.target,
                bandwidth=link.bandwidth,
                protocol=link.protocol
            )
            
    def visualize(self, output_path: Optional[str] = None):
        """可视化网络拓扑"""
        plt.figure(figsize=(12, 8))
        
        # 布局算法
        pos = nx.spring_layout(self.graph, k=0.9, iterations=50)
        
        # 绘制节点
        nx.draw_networkx_nodes(
            self.graph, pos, 
            node_size=800, 
            node_color='lightblue',
            alpha=0.8
        )
        
        # 绘制边
        edges = self.graph.edges(data=True)
        for edge in edges:
            source, target, data = edge
            width = data['bandwidth'] * 3
            style = 'solid' if data['protocol'] == 'REST' else 'dashed'
            
            nx.draw_networkx_edges(
                self.graph, pos,
                edgelist=[(source, target)],
                width=width,
                edge_color='gray',
                style=style,
                alpha=0.7,
                arrows=True
            )
            
        # 绘制标签
        nx.draw_networkx_labels(
            self.graph, pos,
            font_size=10,
            font_family='sans-serif'
        )
        
        # 添加图例
        self._add_legend()
        
        plt.axis('off')
        if output_path:
            plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def _add_legend(self):
        """添加图例"""
        # 协议类型
        protocols = set(link.protocol for link in self.topology.links)
        legend_elements = []
        
        if 'REST' in protocols:
            legend_elements.append(Line2D([0], [0], 
                color='gray', lw=2, linestyle='solid',
                label='REST协议'))
        if 'gRPC' in protocols:
            legend_elements.append(Line2D([0], [0], 
                color='gray', lw=2, linestyle='dashed',
                label='gRPC协议'))
        
        # 带宽比例
        max_bandwidth = max(link.bandwidth for link in self.topology.links)
        bandwidth_sample = Line2D([0], [0], 
            color='gray', lw=max_bandwidth*3, linestyle='solid',
            label=f'最大带宽 {max_bandwidth:.1f}')
        legend_elements.append(bandwidth_sample)
        
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.1, 0.1))
        