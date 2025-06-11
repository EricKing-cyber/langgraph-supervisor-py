"""
图分析工具模块

提供知识图谱和复杂数据关系分析功能
"""

import re
import json
import networkx as nx
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from functools import wraps
import matplotlib.pyplot as plt
from langchain_core.tools import tool, BaseTool
import tempfile
import os

# 图数据存储路径
GRAPH_DATA_DIR = Path("data") / "graphs"
GRAPH_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 定义工具包装器，允许直接调用
def direct_tool_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # 正常工作流中的调用
            return func(*args, **kwargs)
        except AttributeError as e:
            # 处理'str' object has no attribute 'parent_run_id'错误等情况
            if "'str' object has no attribute" in str(e) or "object has no attribute" in str(e):
                # 直接执行原始函数逻辑
                if hasattr(func, '__wrapped__'):
                    return func.__wrapped__(*args, **kwargs)
                # 如果没有__wrapped__属性，可能是其他装饰器问题
                # 尝试调用原始函数
                return func(*args, **kwargs)
            raise
        except Exception as e:
            # 处理其他可能的错误
            return f"错误：图分析工具执行失败 - {str(e)}"
    return wrapper


@tool
def create_entity_graph(entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]], 
                       graph_name: str) -> str:
    """
    创建实体关系图并保存
    
    Args:
        entities: 实体列表，每个实体包含"id"和"name"等属性
        relationships: 关系列表，每个关系包含"source"、"target"和"type"等属性
        graph_name: 图的名称
        
    Returns:
        str: 保存的图文件路径
    """
    G = nx.DiGraph()
    
    # 添加实体节点
    for entity in entities:
        G.add_node(entity["id"], **entity)
    
    # 添加关系边
    for rel in relationships:
        G.add_edge(rel["source"], rel["target"], **rel)
    
    # 保存图数据
    graph_data = {
        "nodes": entities,
        "edges": relationships,
        "name": graph_name
    }
    
    # 文件名清理
    safe_name = re.sub(r'[^\w\-_]', '_', graph_name)
    filepath = GRAPH_DATA_DIR / f"{safe_name}.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    return str(filepath)


@tool
def analyze_graph_centrality(graph_file: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    分析图中的中心性度量
    
    Args:
        graph_file: 图数据文件路径
        
    Returns:
        Dict: 包含不同中心性指标的分析结果
    """
    # 加载图数据
    try:
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        return {"error": f"文件不存在: {graph_file}"}
    
    # 创建图
    G = nx.DiGraph()
    
    # 添加节点和边
    for node in graph_data["nodes"]:
        G.add_node(node["id"], **node)
    
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)
    
    # 计算中心性指标
    degree_centrality = nx.degree_centrality(G)
    in_degree_centrality = nx.in_degree_centrality(G)
    out_degree_centrality = nx.out_degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    
    # 尝试计算特征向量中心性，对于某些图可能会失败
    try:
        eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
    except:
        eigenvector_centrality = {}
    
    # 组织结果
    results = {
        "degree_centrality": sorted(
            [{"entity_id": n, "name": G.nodes[n].get("name", n), "score": score} 
             for n, score in degree_centrality.items()],
            key=lambda x: x["score"], 
            reverse=True
        ),
        "in_degree_centrality": sorted(
            [{"entity_id": n, "name": G.nodes[n].get("name", n), "score": score} 
             for n, score in in_degree_centrality.items()],
            key=lambda x: x["score"], 
            reverse=True
        ),
        "out_degree_centrality": sorted(
            [{"entity_id": n, "name": G.nodes[n].get("name", n), "score": score} 
             for n, score in out_degree_centrality.items()],
            key=lambda x: x["score"], 
            reverse=True
        ),
        "betweenness_centrality": sorted(
            [{"entity_id": n, "name": G.nodes[n].get("name", n), "score": score} 
             for n, score in betweenness_centrality.items()],
            key=lambda x: x["score"], 
            reverse=True
        ),
    }
    
    # 如果特征向量中心性计算成功，加入结果
    if eigenvector_centrality:
        results["eigenvector_centrality"] = sorted(
            [{"entity_id": n, "name": G.nodes[n].get("name", n), "score": score} 
             for n, score in eigenvector_centrality.items()],
            key=lambda x: x["score"], 
            reverse=True
        )
    
    return results


@tool
def find_shortest_path(graph_file: str, source_id: str, target_id: str) -> Dict[str, Any]:
    """
    找到两个实体之间的最短路径
    
    Args:
        graph_file: 图数据文件路径
        source_id: 起始实体ID
        target_id: 目标实体ID
        
    Returns:
        Dict: 包含路径信息的结果
    """
    # 加载图数据
    try:
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        return {"error": f"文件不存在: {graph_file}"}
    
    # 创建图
    G = nx.DiGraph()
    
    # 添加节点和边
    for node in graph_data["nodes"]:
        G.add_node(node["id"], **node)
    
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)
    
    # 检查节点是否存在
    if source_id not in G:
        return {"error": f"起始实体ID不存在: {source_id}"}
    if target_id not in G:
        return {"error": f"目标实体ID不存在: {target_id}"}
    
    # 尝试找到最短路径
    try:
        path = nx.shortest_path(G, source=source_id, target=target_id)
        
        # 获取路径上的实体名称
        path_names = []
        for node_id in path:
            node_data = G.nodes[node_id]
            path_names.append(node_data.get("name", node_id))
        
        # 获取路径上的边关系
        edge_types = []
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            edge_data = G.edges[source, target]
            edge_types.append(edge_data.get("type", "关联"))
        
        return {
            "path": path,
            "path_names": path_names,
            "edge_types": edge_types,
            "path_length": len(path) - 1,
            "path_description": " -> ".join(path_names)
        }
    except nx.NetworkXNoPath:
        return {"error": f"未找到从 {source_id} 到 {target_id} 的路径"}


@tool
def detect_communities(graph_file: str, algorithm: str = "louvain") -> Dict[str, Any]:
    """
    检测图中的社区结构
    
    Args:
        graph_file: 图数据文件路径
        algorithm: 社区检测算法，可选值为"louvain"、"girvan_newman"
        
    Returns:
        Dict: 社区结构分析结果
    """
    # 加载图数据
    try:
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        return {"error": f"文件不存在: {graph_file}"}
    
    # 创建无向图（社区检测通常基于无向图）
    G = nx.Graph()
    
    # 添加节点和边
    for node in graph_data["nodes"]:
        G.add_node(node["id"], **node)
    
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)
    
    communities = []
    
    # 使用指定的算法检测社区
    if algorithm.lower() == "louvain":
        try:
            import community as community_louvain
            partition = community_louvain.best_partition(G)
            
            # 组织社区结果
            community_dict = {}
            for node, comm_id in partition.items():
                if comm_id not in community_dict:
                    community_dict[comm_id] = []
                node_name = G.nodes[node].get("name", node)
                community_dict[comm_id].append({"id": node, "name": node_name})
            
            # 转换为列表格式
            for comm_id, members in community_dict.items():
                communities.append({
                    "community_id": comm_id,
                    "size": len(members),
                    "members": members
                })
                
        except ImportError:
            return {"error": "需要安装python-louvain包: pip install python-louvain"}
            
    elif algorithm.lower() == "girvan_newman":
        try:
            # Girvan-Newman算法计算较慢，限制迭代次数
            comp = nx.community.girvan_newman(G)
            # 取前几层的结果
            for i, community_set in enumerate(comp):
                if i >= 3:  # 只取前3层
                    break
                    
                level_communities = []
                for j, community in enumerate(community_set):
                    members = []
                    for node in community:
                        node_name = G.nodes[node].get("name", node)
                        members.append({"id": node, "name": node_name})
                    
                    level_communities.append({
                        "community_id": f"level{i}_group{j}",
                        "size": len(members),
                        "members": members
                    })
                    
                communities = level_communities
                        
        except Exception as e:
            return {"error": f"Girvan-Newman算法执行失败: {str(e)}"}
            
    else:
        return {"error": f"不支持的算法: {algorithm}，请使用'louvain'或'girvan_newman'"}
    
    # 按社区大小排序
    communities.sort(key=lambda x: x["size"], reverse=True)
    
    return {
        "algorithm": algorithm,
        "num_communities": len(communities),
        "communities": communities
    }


@tool
def visualize_graph(graph_file: str, layout: str = "spring", output_format: str = "png") -> str:
    """
    可视化图结构并保存为图片
    
    Args:
        graph_file: 图数据文件路径
        layout: 布局算法，可选值为"spring"、"circular"、"kamada_kawai"、"random"
        output_format: 输出格式，可选值为"png"、"svg"
        
    Returns:
        str: 生成的图片文件路径
    """
    # 加载图数据
    try:
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        return f"错误：文件不存在: {graph_file}"
    
    # 创建图
    G = nx.DiGraph()
    
    # 添加节点和边
    for node in graph_data["nodes"]:
        G.add_node(node["id"], **node)
    
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)
    
    # 创建图形和轴
    plt.figure(figsize=(12, 10))
    
    # 获取节点标签
    node_labels = {node: G.nodes[node].get("name", node) for node in G.nodes()}
    
    # 选择布局
    if layout == "spring":
        pos = nx.spring_layout(G, seed=42)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "kamada_kawai":
        try:
            pos = nx.kamada_kawai_layout(G)
        except:
            pos = nx.spring_layout(G, seed=42)
    elif layout == "random":
        pos = nx.random_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)
    
    # 绘制节点
    nx.draw_networkx_nodes(G, pos, alpha=0.7, node_size=700)
    
    # 绘制边
    nx.draw_networkx_edges(G, pos, alpha=0.5, arrows=True)
    
    # 绘制标签
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)
    
    # 设置图表
    plt.title(f"图: {graph_data.get('name', 'Unknown')}")
    plt.axis("off")
    
    # 保存图片
    graph_name = Path(graph_file).stem
    vis_dir = GRAPH_DATA_DIR / "visualization"
    vis_dir.mkdir(exist_ok=True)
    
    output_path = vis_dir / f"{graph_name}_{layout}.{output_format}"
    plt.savefig(output_path, format=output_format, bbox_inches="tight", dpi=300)
    plt.close()
    
    return str(output_path)


@tool
def graph_similarity_analysis(graph_file1: str, graph_file2: str) -> Dict[str, Any]:
    """
    比较两个图的相似度
    
    Args:
        graph_file1: 第一个图的文件路径
        graph_file2: 第二个图的文件路径
        
    Returns:
        Dict: 包含相似度指标的结果
    """
    # 加载第一个图
    try:
        with open(graph_file1, 'r', encoding='utf-8') as f:
            graph_data1 = json.load(f)
    except FileNotFoundError:
        return {"error": f"文件不存在: {graph_file1}"}
    
    # 加载第二个图
    try:
        with open(graph_file2, 'r', encoding='utf-8') as f:
            graph_data2 = json.load(f)
    except FileNotFoundError:
        return {"error": f"文件不存在: {graph_file2}"}
    
    # 创建图
    G1 = nx.DiGraph()
    G2 = nx.DiGraph()
    
    # 添加节点和边到第一个图
    for node in graph_data1["nodes"]:
        G1.add_node(node["id"], **node)
    for edge in graph_data1["edges"]:
        G1.add_edge(edge["source"], edge["target"], **edge)
    
    # 添加节点和边到第二个图
    for node in graph_data2["nodes"]:
        G2.add_node(node["id"], **node)
    for edge in graph_data2["edges"]:
        G2.add_edge(edge["source"], edge["target"], **edge)
    
    # 计算节点重叠
    nodes1 = set(G1.nodes())
    nodes2 = set(G2.nodes())
    common_nodes = nodes1.intersection(nodes2)
    
    # 计算边重叠
    edges1 = set(G1.edges())
    edges2 = set(G2.edges())
    common_edges = edges1.intersection(edges2)
    
    # 计算Jaccard相似度
    node_jaccard = len(common_nodes) / len(nodes1.union(nodes2)) if nodes1 or nodes2 else 0
    edge_jaccard = len(common_edges) / len(edges1.union(edges2)) if edges1 or edges2 else 0
    
    # 比较网络特性
    avg_degree1 = sum(dict(G1.degree()).values()) / G1.number_of_nodes() if G1.number_of_nodes() > 0 else 0
    avg_degree2 = sum(dict(G2.degree()).values()) / G2.number_of_nodes() if G2.number_of_nodes() > 0 else 0
    
    density1 = nx.density(G1)
    density2 = nx.density(G2)
    
    try:
        avg_clustering1 = nx.average_clustering(G1.to_undirected())
    except:
        avg_clustering1 = 0
        
    try:
        avg_clustering2 = nx.average_clustering(G2.to_undirected())
    except:
        avg_clustering2 = 0
    
    # 计算特性差异的归一化距离
    feature_diffs = {
        "avg_degree_diff": abs(avg_degree1 - avg_degree2) / max(avg_degree1, avg_degree2) if max(avg_degree1, avg_degree2) > 0 else 0,
        "density_diff": abs(density1 - density2) / max(density1, density2) if max(density1, density2) > 0 else 0,
        "clustering_diff": abs(avg_clustering1 - avg_clustering2) / max(avg_clustering1, avg_clustering2) if max(avg_clustering1, avg_clustering2) > 0 else 0
    }
    
    # 计算综合相似度分数 (简化版本)
    similarity_score = (node_jaccard + edge_jaccard) / 2
    
    return {
        "node_overlap": {
            "common_nodes": len(common_nodes),
            "nodes_in_graph1": len(nodes1),
            "nodes_in_graph2": len(nodes2),
            "jaccard_similarity": node_jaccard
        },
        "edge_overlap": {
            "common_edges": len(common_edges),
            "edges_in_graph1": len(edges1),
            "edges_in_graph2": len(edges2),
            "jaccard_similarity": edge_jaccard
        },
        "graph_features": {
            "graph1": {
                "avg_degree": avg_degree1,
                "density": density1,
                "avg_clustering": avg_clustering1
            },
            "graph2": {
                "avg_degree": avg_degree2,
                "density": density2,
                "avg_clustering": avg_clustering2
            },
            "feature_differences": feature_diffs
        },
        "similarity_score": similarity_score
    }


@tool
def extract_subgraph(graph_file: str, central_node_id: str, distance: int = 2) -> str:
    """
    从图中提取以指定节点为中心的子图
    
    Args:
        graph_file: 图数据文件路径
        central_node_id: 中心节点ID
        distance: 与中心节点的最大距离
        
    Returns:
        str: 子图文件路径
    """
    # 加载图数据
    try:
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        return f"错误：文件不存在: {graph_file}"
    
    # 创建图
    G = nx.DiGraph()
    
    # 添加节点和边
    for node in graph_data["nodes"]:
        G.add_node(node["id"], **node)
    
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)
    
    # 确认中心节点存在
    if central_node_id not in G:
        return f"错误：节点不存在: {central_node_id}"
    
    # 获取中心节点信息
    central_node_name = G.nodes[central_node_id].get("name", central_node_id)
    
    # 提取指定距离内的节点
    nodes = set()
    current_layer = {central_node_id}
    nodes.add(central_node_id)
    
    # 广度优先搜索
    for _ in range(distance):
        next_layer = set()
        for node in current_layer:
            # 获取所有相邻节点(输入和输出)
            neighbors = set(G.predecessors(node)).union(set(G.successors(node)))
            for neighbor in neighbors:
                if neighbor not in nodes:
                    next_layer.add(neighbor)
                    nodes.add(neighbor)
        current_layer = next_layer
    
    # 创建子图
    subgraph = G.subgraph(nodes).copy()
    
    # 转换为格式化数据
    subgraph_nodes = []
    for node in subgraph.nodes():
        node_data = dict(subgraph.nodes[node])
        node_data["id"] = node
        subgraph_nodes.append(node_data)
    
    subgraph_edges = []
    for u, v in subgraph.edges():
        edge_data = dict(subgraph.edges[u, v])
        edge_data["source"] = u
        edge_data["target"] = v
        subgraph_edges.append(edge_data)
    
    # 保存子图
    graph_name = Path(graph_file).stem
    subgraph_data = {
        "nodes": subgraph_nodes,
        "edges": subgraph_edges,
        "name": f"{graph_name}_sub_{central_node_name}_{distance}hop"
    }
    
    # 生成文件名
    filepath = GRAPH_DATA_DIR / f"{graph_name}_sub_{central_node_id}_{distance}hop.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(subgraph_data, f, ensure_ascii=False, indent=2)
    
    return str(filepath)


# 应用包装器到各个工具
create_entity_graph = direct_tool_wrapper(create_entity_graph)
analyze_graph_centrality = direct_tool_wrapper(analyze_graph_centrality)
find_shortest_path = direct_tool_wrapper(find_shortest_path)
detect_communities = direct_tool_wrapper(detect_communities)
visualize_graph = direct_tool_wrapper(visualize_graph)
graph_similarity_analysis = direct_tool_wrapper(graph_similarity_analysis)
extract_subgraph = direct_tool_wrapper(extract_subgraph)


# 获取所有图分析工具
def get_graph_analysis_tools() -> List[BaseTool]:
    """
    获取所有图分析工具
    
    Returns:
        List[BaseTool]: 图分析工具列表
    """
    return [
        create_entity_graph,
        analyze_graph_centrality,
        find_shortest_path,
        detect_communities,
        visualize_graph,
        graph_similarity_analysis, 
        extract_subgraph
    ] 