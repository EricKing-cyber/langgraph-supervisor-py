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
import warnings

# 图数据存储路径
GRAPH_DATA_DIR = Path("data") / "graphs"
GRAPH_DATA_DIR.mkdir(parents=True, exist_ok=True)

def setup_chinese_font():
    """
    设置支持中文显示的字体
    尝试多种方法确保中文字符正确显示
    """
    import matplotlib as mpl
    import platform
    
    # 完全屏蔽字体警告
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    
    # 尝试常见的中文字体
    system = platform.system()
    if system == "Windows":
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'FangSong', 'KaiTi']
    elif system == "Darwin":  # macOS
        chinese_fonts = ['Heiti TC', 'Heiti SC', 'STHeiti', 'STFangsong', 'Arial Unicode MS']
    else:  # Linux和其他系统
        chinese_fonts = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'Noto Sans CJK TC', 'Droid Sans Fallback']
    
    # 添加通用字体
    chinese_fonts.extend(['Microsoft Sans Serif', 'DejaVu Sans', 'Segoe UI'])
    
    # 检测可用字体
    from matplotlib.font_manager import FontManager
    fontman = FontManager()
    system_fonts = set([f.name for f in fontman.ttflist])
    
    # 尝试找到可用的中文字体
    font_found = False
    for font_name in chinese_fonts:
        if font_name in system_fonts:
            # 设置字体
            plt.rcParams['font.family'] = font_name
            plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
            mpl.rcParams['font.sans-serif'] = [font_name] + mpl.rcParams['font.sans-serif']
            print(f"使用中文字体: {font_name}")
            font_found = True
            break
    
    # 如果没有找到内置的中文字体，使用备选方案
    if not font_found:
        try:
            # 使用matplotlib自带的字体
            mpl.rcParams['font.sans-serif'] = ['DejaVu Sans'] + mpl.rcParams['font.sans-serif']
        except:
            pass
            
    # 设置通用字体属性
    mpl.rcParams['axes.unicode_minus'] = False
    
    return font_found

# 定义原始函数，之后用装饰器转换为工具
def _create_entity_graph(entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]], 
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


def _analyze_graph_centrality(graph_file: str) -> Dict[str, List[Dict[str, Any]]]:
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


def _find_shortest_path(graph_file: str, source_id: str, target_id: str) -> Dict[str, Any]:
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


def _detect_communities(graph_file: str, algorithm: str = "louvain") -> Dict[str, Any]:
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


def _visualize_graph(graph_file: str, layout: str = "spring", color_theme: str = "bold") -> str:
    """
    可视化图结构并保存为图片
    
    Args:
        graph_file: 图数据文件路径
        layout: 布局算法，可选值为"spring"、"circular"、"kamada_kawai"、"random"
        color_theme: 颜色主题，可选值为"bold"、"pastel"、"default"
        
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
    
    # 配置中文字体支持
    setup_chinese_font()
        
    # 创建图形和轴
    plt.figure(figsize=(15, 12), facecolor='#f9f9f9')
    
    # 获取节点标签
    node_labels = {node: G.nodes[node].get("name", node) for node in G.nodes()}
    
    # 选择布局
    if layout == "spring":
        pos = nx.spring_layout(G, k=0.3, seed=42)  # k参数调整节点间距
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "kamada_kawai":
        try:
            pos = nx.kamada_kawai_layout(G)
        except:
            pos = nx.spring_layout(G, k=0.3, seed=42)
    elif layout == "random":
        pos = nx.random_layout(G)
    else:
        pos = nx.spring_layout(G, k=0.3, seed=42)
    
    # 计算节点中心度并用于调整节点大小
    degrees = dict(G.degree())
    if not degrees:  # 防止空图
        degrees = {node: 1 for node in G.nodes()}
    
    # 归一化节点大小 (在500到2000之间)
    if len(degrees) > 1:
        min_degree = min(degrees.values())
        max_degree = max(degrees.values())
        if max_degree > min_degree:
            node_sizes = {node: 500 + 1500 * (degrees[node] - min_degree) / (max_degree - min_degree) for node in G.nodes()}
        else:
            node_sizes = {node: 1000 for node in G.nodes()}
    else:
        node_sizes = {node: 1000 for node in G.nodes()}
    
    # 设置节点颜色 - 使用漂亮的配色方案
    # 尝试从节点属性中获取类型或分组信息
    node_types = {}
    for node in G.nodes():
        node_type = G.nodes[node].get("type", G.nodes[node].get("category", "default"))
        node_types[node] = node_type
    
    # 获取所有不同的节点类型
    unique_types = list(set(node_types.values()))
    
    # 使用漂亮的颜色方案
    color_palettes = {
        "default": ['#3498db', '#1abc9c', '#9b59b6', '#f39c12', '#e74c3c', '#2ecc71', '#34495e', '#16a085', '#8e44ad', '#d35400'],
        "pastel": ['#a3d9e9', '#a8d8b9', '#e6c1c5', '#f3d0a5', '#d5c0dd', '#d4e9c1', '#ceeaf6', '#fed4ae', '#e0bbd1', '#bedec2'],
        "bold": ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    }
    
    # 选择颜色方案（默认使用bold配色）
    if color_theme not in color_palettes:
        print(f"警告: 未知的颜色主题 '{color_theme}'，使用默认主题 'bold'")
        color_theme = "bold"
        
    color_scheme = color_palettes[color_theme]
    
    # 如果节点类型太多，循环使用颜色
    node_colors = {node: color_scheme[unique_types.index(node_type) % len(color_scheme)] for node, node_type in node_types.items()}
    
    # 为边创建不同宽度和样式
    edge_types = {}
    for u, v, data in G.edges(data=True):
        edge_type = data.get("type", "default")
        edge_types[(u, v)] = edge_type
    
    unique_edge_types = list(set(edge_types.values()))
    
    # 边的宽度和样式 - 默认为实线箭头
    edge_widths = {(u, v): 1.5 for u, v in G.edges()}
    edge_styles = {(u, v): 'solid' for u, v in G.edges()}
    edge_colors = {(u, v): '#636363' for u, v in G.edges()}  # 默认灰色
    
    # 绘制节点
    for node_type in unique_types:
        nodes_of_type = [node for node, ntype in node_types.items() if ntype == node_type]
        if not nodes_of_type:
            continue
            
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=nodes_of_type,
            node_size=[node_sizes[node] for node in nodes_of_type],
            node_color=[node_colors[node] for node in nodes_of_type],
            alpha=0.85,
            edgecolors='white',
            linewidths=1.5,
            label=f"类型: {node_type}" if node_type != "default" else "节点"
        )
    
    # 绘制边
    for edge_type in unique_edge_types:
        edges_of_type = [(u, v) for (u, v), etype in edge_types.items() if etype == edge_type]
        if not edges_of_type:
            continue
            
        nx.draw_networkx_edges(
            G, pos,
            edgelist=edges_of_type,
            width=[edge_widths[(u, v)] for u, v in edges_of_type],
            alpha=0.7,
            edge_color=[edge_colors[(u, v)] for u, v in edges_of_type],
            style=[edge_styles[(u, v)] for u, v in edges_of_type],
            arrows=True,
            arrowsize=15,
            arrowstyle='-|>',
            connectionstyle='arc3,rad=0.1'
        )
    
    # 绘制标签，为避免拥挤，可以只对重要节点显示标签
    important_nodes = [node for node in G.nodes() if node_sizes[node] > 800]  # 只为较大的节点添加标签
    
    if len(G.nodes()) <= 20:  # 节点较少时显示所有标签
        important_nodes = list(G.nodes())
    
    if important_nodes:
        # 使用白色背景增加可见性
        label_options = {
            "font_size": 10,
            "font_weight": 'bold',
            "bbox": {
                "boxstyle": "round,pad=0.3",
                "fc": "white",
                "ec": "none",
                "alpha": 0.85
            },
            "horizontalalignment": 'center',
            "verticalalignment": 'center'
        }
        
        # 单独绘制每个标签以增强可见性
        for node in important_nodes:
            x, y = pos[node]
            label = node_labels[node]
            plt.text(x, y, label, **label_options)
    
    # 添加图例
    if len(unique_types) > 1 and "default" not in unique_types:
        legend_handles = []
        for node_type in unique_types:
            type_color = color_scheme[unique_types.index(node_type) % len(color_scheme)]
            legend_handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=type_color, 
                                    markersize=10, label=node_type))
        plt.legend(handles=legend_handles, loc='upper right', title="节点类型")
    
    # 设置图表样式
    plt.title(f"知识图谱: {graph_data.get('name', 'Untitled')}", fontsize=16, pad=20)
    plt.axis("off")
    
    # 添加边框和背景
    plt.gca().set_facecolor('#f9f9f9')  # 设置背景色为淡灰色
    
    # 保存图片
    graph_name = Path(graph_file).stem
    vis_dir = GRAPH_DATA_DIR / "visualization"
    vis_dir.mkdir(exist_ok=True)
    
    output_path = vis_dir / f"{graph_name}_{layout}_{color_theme}.png"
    plt.savefig(output_path, format="png", bbox_inches="tight", dpi=300, facecolor='#f9f9f9')
    plt.close()
    
    return str(output_path)


def _graph_similarity_analysis(graph_file1: str, graph_file2: str) -> Dict[str, Any]:
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


def _extract_subgraph(graph_file: str, central_node_id: str, distance: int = 2) -> str:
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


# 定义工具，确保名称与提示词中描述的一致
@tool
def create_knowledge_graph(entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]], graph_name: str) -> str:
    """
    创建知识图谱
    
    Args:
        entities: 实体列表，每个实体包含"id"和"name"等属性
        relationships: 关系列表，每个关系包含"source"、"target"和"type"等属性
        graph_name: 图的名称
        
    Returns:
        str: 保存的图文件路径
    """
    return _create_entity_graph(entities, relationships, graph_name)

@tool
def add_entities_to_graph(entities: List[Dict[str, Any]], graph_name: str) -> str:
    """
    向图谱添加实体
    
    Args:
        entities: 实体列表
        graph_name: 图的名称
        
    Returns:
        str: 操作结果
    """
    # 简单实现 - 创建只有实体的图谱
    return _create_entity_graph(entities, [], graph_name)

@tool
def add_relationships_to_graph(relationships: List[Dict[str, Any]], graph_name: str) -> str:
    """
    向图谱添加关系
    
    Args:
        relationships: 关系列表
        graph_name: 图的名称
        
    Returns:
        str: 操作结果
    """
    # 简单实现 - 创建只有关系的图谱
    return _create_entity_graph([], relationships, graph_name)

@tool
def analyze_graph_centrality(graph_file: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    分析中心节点
    
    Args:
        graph_file: 图谱文件路径
        
    Returns:
        Dict: 中心性分析结果
    """
    return _analyze_graph_centrality(graph_file)

@tool
def find_path_between_entities(graph_file: str, source_id: str, target_id: str) -> Dict[str, Any]:
    """
    查找实体间路径
    
    Args:
        graph_file: 图谱文件路径
        source_id: 起始实体ID
        target_id: 目标实体ID
        
    Returns:
        Dict: 路径信息
    """
    return _find_shortest_path(graph_file, source_id, target_id)

@tool
def detect_communities(graph_file: str, algorithm: str = "louvain") -> Dict[str, Any]:
    """
    检测社区结构
    
    Args:
        graph_file: 图谱文件路径
        algorithm: 算法类型，支持"louvain", "girvan_newman", "label_propagation"
        
    Returns:
        Dict: 社区检测结果
    """
    return _detect_communities(graph_file, algorithm)

@tool
def visualize_graph(graph_file: str, layout: str = "spring", color_theme: str = "bold") -> str:
    """
    可视化图谱
    
    Args:
        graph_file: 图谱文件路径
        layout: 布局算法，可选值为"spring"、"circular"、"kamada_kawai"、"random"
        color_theme: 颜色主题，可选值为"bold"、"pastel"、"default"
        
    Returns:
        str: 图像文件路径
    """
    return _visualize_graph(graph_file, layout, color_theme=color_theme)

@tool
def list_knowledge_graphs() -> List[str]:
    """
    列出所有保存的知识图谱文件
    
    Returns:
        List[str]: 图谱文件路径列表
    """
    return [str(p) for p in GRAPH_DATA_DIR.glob("*.json")]


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
        visualize_graph,
        list_knowledge_graphs
    ] 