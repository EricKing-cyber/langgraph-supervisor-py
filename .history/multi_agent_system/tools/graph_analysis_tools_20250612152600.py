"""
图分析工具模块

提供基于图神经网络的高级数据分析能力
"""

import os
import json
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import networkx as nx
from langchain_core.tools import tool, BaseTool
from langchain_core.language_models import BaseChatModel

# 这里我们假设需要导入图神经网络相关的功能
# 由于代码中没有看到完整的graph.py文件，需要根据片段推断创建必要的函数

# 图数据存储路径
GRAPH_DATA_DIR = Path("data/graph_data")
GRAPH_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 定义图分析数据结构
class GraphNode:
    """表示图中的一个节点"""
    def __init__(self, id: str, label: str, properties: Optional[Dict[str, Any]] = None):
        self.id = id
        self.label = label
        self.properties = properties or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "properties": self.properties
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GraphNode':
        return GraphNode(
            id=data["id"],
            label=data["label"],
            properties=data.get("properties", {})
        )


class GraphEdge:
    """表示图中的一条边"""
    def __init__(self, source: str, target: str, label: str, weight: float = 1.0, properties: Optional[Dict[str, Any]] = None):
        self.source = source
        self.target = target
        self.label = label
        self.weight = weight
        self.properties = properties or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "label": self.label,
            "weight": self.weight,
            "properties": self.properties
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GraphEdge':
        return GraphEdge(
            source=data["source"],
            target=data["target"],
            label=data["label"],
            weight=data.get("weight", 1.0),
            properties=data.get("properties", {})
        )


class KnowledgeGraph:
    """知识图谱类，封装对图的操作"""
    def __init__(self, name: str = "default"):
        self.name = name
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
    
    def add_node(self, node: GraphNode) -> None:
        """添加节点"""
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.to_dict())
    
    def add_edge(self, edge: GraphEdge) -> None:
        """添加边"""
        self.edges.append(edge)
        self.graph.add_edge(edge.source, edge.target, **edge.to_dict())
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """获取节点"""
        return self.nodes.get(node_id)
    
    def get_connected_nodes(self, node_id: str) -> List[GraphNode]:
        """获取与指定节点相连的所有节点"""
        if node_id not in self.graph:
            return []
        
        connected_ids = list(self.graph.successors(node_id)) + list(self.graph.predecessors(node_id))
        return [self.nodes[nid] for nid in connected_ids if nid in self.nodes]
    
    def find_shortest_path(self, source_id: str, target_id: str) -> List[str]:
        """查找最短路径"""
        if source_id not in self.graph or target_id not in self.graph:
            return []
        
        try:
            path = nx.shortest_path(self.graph, source=source_id, target=target_id, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return []
    
    def get_central_nodes(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """获取中心性最高的节点"""
        if len(self.graph) == 0:
            return []
        
        # 计算PageRank中心性
        pagerank = nx.pagerank(self.graph, weight='weight')
        sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_nodes[:top_n]
    
    def get_communities(self) -> Dict[int, List[str]]:
        """检测社区结构"""
        if len(self.graph) == 0:
            return {}
        
        # 转换为无向图进行社区检测
        undirected_graph = self.graph.to_undirected()
        communities = nx.community.greedy_modularity_communities(undirected_graph)
        
        result = {}
        for i, community in enumerate(communities):
            result[i] = list(community)
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "name": self.name,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges]
        }
    
    def save(self, filepath: Optional[str] = None) -> str:
        """保存图数据到文件"""
        if not filepath:
            filepath = str(GRAPH_DATA_DIR / f"{self.name}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        
        return filepath
    
    @staticmethod
    def load(filepath: str) -> 'KnowledgeGraph':
        """从文件加载图数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        graph = KnowledgeGraph(name=data.get("name", "loaded_graph"))
        
        for node_data in data.get("nodes", []):
            node = GraphNode.from_dict(node_data)
            graph.add_node(node)
        
        for edge_data in data.get("edges", []):
            edge = GraphEdge.from_dict(edge_data)
            graph.add_edge(edge)
        
        return graph


# 工具函数
def extract_entities_and_relationships(text: str, model: BaseChatModel) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """从文本中提取实体和关系"""
    # 这里简化实现，实际应用中应该使用NLP模型进行实体和关系提取
    # 由于没有看到原始的graph.py中的相关代码，这里提供一个简单的实现
    
    prompt = f"""
    请从以下文本中提取实体和实体之间的关系:

    {text}
    
    以JSON格式返回，格式如下:
    {{
        "entities": [
            {{"id": "entity1", "label": "Person", "name": "实体名称1"}},
            {{"id": "entity2", "label": "Organization", "name": "实体名称2"}}
        ],
        "relationships": [
            {{"source": "entity1", "target": "entity2", "label": "WORKS_FOR", "description": "关系描述"}}
        ]
    }}
    """
    
    result = model.invoke(prompt)
    
    try:
        # 尝试解析JSON响应
        import re
        json_match = re.search(r'```json\n(.*?)\n```', result.content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            data = json.loads(result.content)
        
        return data.get("entities", []), data.get("relationships", [])
    except Exception as e:
        print(f"解析实体和关系时出错: {e}")
        return [], []


# 图分析工具
@tool
def create_knowledge_graph(name: str) -> str:
    """
    创建新的知识图谱
    
    Args:
        name: 知识图谱名称
        
    Returns:
        str: 成功创建的消息
    """
    graph = KnowledgeGraph(name=name)
    filepath = graph.save()
    
    return f"成功创建知识图谱 '{name}', 保存在 {filepath}"


@tool
def add_entities_to_graph(graph_name: str, entities: List[Dict[str, Any]]) -> str:
    """
    向知识图谱添加实体
    
    Args:
        graph_name: 知识图谱名称
        entities: 实体列表，每个实体是一个字典，包含id, label和properties
        
    Returns:
        str: 成功添加的消息
    """
    filepath = str(GRAPH_DATA_DIR / f"{graph_name}.json")
    if not os.path.exists(filepath):
        return f"错误：找不到名为'{graph_name}'的知识图谱"
    
    graph = KnowledgeGraph.load(filepath)
    
    for entity_data in entities:
        node = GraphNode(
            id=entity_data["id"],
            label=entity_data["label"],
            properties=entity_data.get("properties", {})
        )
        graph.add_node(node)
    
    graph.save(filepath)
    
    return f"成功向知识图谱'{graph_name}'添加了{len(entities)}个实体"


@tool
def add_relationships_to_graph(graph_name: str, relationships: List[Dict[str, Any]]) -> str:
    """
    向知识图谱添加关系
    
    Args:
        graph_name: 知识图谱名称
        relationships: 关系列表，每个关系是一个字典，包含source, target, label和weight
        
    Returns:
        str: 成功添加的消息
    """
    filepath = str(GRAPH_DATA_DIR / f"{graph_name}.json")
    if not os.path.exists(filepath):
        return f"错误：找不到名为'{graph_name}'的知识图谱"
    
    graph = KnowledgeGraph.load(filepath)
    
    added_count = 0
    for rel_data in relationships:
        if rel_data["source"] not in graph.nodes or rel_data["target"] not in graph.nodes:
            continue
            
        edge = GraphEdge(
            source=rel_data["source"],
            target=rel_data["target"],
            label=rel_data["label"],
            weight=rel_data.get("weight", 1.0),
            properties=rel_data.get("properties", {})
        )
        graph.add_edge(edge)
        added_count += 1
    
    graph.save(filepath)
    
    return f"成功向知识图谱'{graph_name}'添加了{added_count}个关系"


@tool
def analyze_graph_centrality(graph_name: str, top_n: int = 5) -> Dict[str, Any]:
    """
    分析知识图谱中的中心节点
    
    Args:
        graph_name: 知识图谱名称
        top_n: 返回的顶部节点数量
        
    Returns:
        Dict[str, Any]: 中心节点分析结果
    """
    filepath = str(GRAPH_DATA_DIR / f"{graph_name}.json")
    if not os.path.exists(filepath):
        return {"error": f"找不到名为'{graph_name}'的知识图谱"}
    
    graph = KnowledgeGraph.load(filepath)
    central_nodes = graph.get_central_nodes(top_n=top_n)
    
    result = {
        "graph_name": graph_name,
        "central_nodes": [
            {
                "id": node_id,
                "centrality": float(centrality),
                "label": graph.get_node(node_id).label if node_id in graph.nodes else "Unknown",
                "properties": graph.get_node(node_id).properties if node_id in graph.nodes else {}
            }
            for node_id, centrality in central_nodes
        ]
    }
    
    return result


@tool
def find_path_between_entities(graph_name: str, source_id: str, target_id: str) -> Dict[str, Any]:
    """
    在知识图谱中查找两个实体之间的路径
    
    Args:
        graph_name: 知识图谱名称
        source_id: 源实体ID
        target_id: 目标实体ID
        
    Returns:
        Dict[str, Any]: 路径查询结果
    """
    filepath = str(GRAPH_DATA_DIR / f"{graph_name}.json")
    if not os.path.exists(filepath):
        return {"error": f"找不到名为'{graph_name}'的知识图谱"}
    
    graph = KnowledgeGraph.load(filepath)
    
    if source_id not in graph.nodes:
        return {"error": f"找不到ID为'{source_id}'的源实体"}
    
    if target_id not in graph.nodes:
        return {"error": f"找不到ID为'{target_id}'的目标实体"}
    
    path = graph.find_shortest_path(source_id, target_id)
    
    if not path:
        return {
            "source": source_id,
            "target": target_id,
            "path_exists": False,
            "message": "未找到连接路径"
        }
    
    path_with_details = []
    for i in range(len(path) - 1):
        source = path[i]
        target = path[i + 1]
        source_node = graph.get_node(source)
        
        path_with_details.append({
            "id": source,
            "label": source_node.label if source_node else "Unknown",
            "properties": source_node.properties if source_node else {}
        })
        
        # 添加边信息
        for edge in graph.edges:
            if edge.source == source and edge.target == target:
                path_with_details.append({
                    "relation": edge.label,
                    "properties": edge.properties
                })
                break
    
    # 添加最后一个节点
    last_node = graph.get_node(path[-1])
    path_with_details.append({
        "id": path[-1],
        "label": last_node.label if last_node else "Unknown",
        "properties": last_node.properties if last_node else {}
    })
    
    return {
        "source": source_id,
        "target": target_id,
        "path_exists": True,
        "path_length": len(path) - 1,
        "path": path_with_details
    }


@tool
def detect_communities(graph_name: str) -> Dict[str, Any]:
    """
    在知识图谱中检测社区结构
    
    Args:
        graph_name: 知识图谱名称
        
    Returns:
        Dict[str, Any]: 社区检测结果
    """
    filepath = str(GRAPH_DATA_DIR / f"{graph_name}.json")
    if not os.path.exists(filepath):
        return {"error": f"找不到名为'{graph_name}'的知识图谱"}
    
    graph = KnowledgeGraph.load(filepath)
    communities = graph.get_communities()
    
    result = {
        "graph_name": graph_name,
        "community_count": len(communities),
        "communities": {}
    }
    
    for community_id, node_ids in communities.items():
        community_nodes = []
        for node_id in node_ids:
            node = graph.get_node(node_id)
            if node:
                community_nodes.append({
                    "id": node_id,
                    "label": node.label,
                    "properties": node.properties
                })
        
        result["communities"][str(community_id)] = {
            "size": len(node_ids),
            "nodes": community_nodes
        }
    
    return result


@tool
def list_knowledge_graphs() -> List[Dict[str, Any]]:
    """
    列出所有知识图谱
    
    Returns:
        List[Dict[str, Any]]: 知识图谱列表
    """
    graphs = []
    
    for filepath in GRAPH_DATA_DIR.glob("*.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            graph_name = data.get("name", filepath.stem)
            node_count = len(data.get("nodes", []))
            edge_count = len(data.get("edges", []))
            
            graphs.append({
                "name": graph_name,
                "filepath": str(filepath),
                "node_count": node_count,
                "edge_count": edge_count
            })
        except Exception as e:
            print(f"读取图数据时出错 {filepath}: {e}")
    
    return graphs


# 获取所有图分析工具
def get_graph_analysis_tools() -> List[BaseTool]:
    """
    获取所有图分析工具
    
    Returns:
        List[BaseTool]: 图分析工具列表
    """
    return [
        create_knowledge_graph,
        add_entities_to_graph,
        add_relationships_to_graph,
        analyze_graph_centrality,
        find_path_between_entities,
        detect_communities,
        list_knowledge_graphs
    ] 