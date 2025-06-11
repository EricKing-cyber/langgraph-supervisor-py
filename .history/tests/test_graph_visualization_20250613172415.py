import os
import sys
import json
from pathlib import Path
import matplotlib.pyplot as plt

# 添加父级目录到系统路径，确保可以导入模块
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from multi_agent_system.tools.graph_analysis_tools import create_knowledge_graph, visualize_graph, setup_chinese_font

def test_chinese_graph_visualization():
    """测试包含中文的知识图谱可视化"""
    print("测试包含中文的知识图谱可视化...")
    
    # 创建一个包含中文的知识图谱
    entities = [
        {"id": "1", "name": "人工智能", "type": "技术领域"},
        {"id": "2", "name": "深度学习", "type": "技术分支"},
        {"id": "3", "name": "机器学习", "type": "技术分支"},
        {"id": "4", "name": "自然语言处理", "type": "应用领域"},
        {"id": "5", "name": "计算机视觉", "type": "应用领域"},
        {"id": "6", "name": "知识图谱", "type": "技术方向"},
        {"id": "7", "name": "神经网络", "type": "技术方法"},
        {"id": "8", "name": "大规模语言模型", "type": "技术产品"},
        {"id": "9", "name": "ChatGPT", "type": "产品实例"},
        {"id": "10", "name": "Claude", "type": "产品实例"}
    ]
    
    relationships = [
        {"source": "1", "target": "2", "type": "包含"},
        {"source": "1", "target": "3", "type": "包含"},
        {"source": "1", "target": "4", "type": "应用于"},
        {"source": "1", "target": "5", "type": "应用于"},
        {"source": "2", "target": "7", "type": "使用"},
        {"source": "3", "target": "7", "type": "使用"},
        {"source": "3", "target": "6", "type": "关联"},
        {"source": "4", "target": "8", "type": "使用"},
        {"source": "8", "target": "9", "type": "实例"},
        {"source": "8", "target": "10", "type": "实例"},
        {"source": "6", "target": "4", "type": "支持"}
    ]
    
    # 创建知识图谱
    graph_file = create_knowledge_graph(entities, relationships, "AI技术知识图谱")
    print(f"创建图谱文件: {graph_file}")
    
    # 测试不同布局和配色
    layouts = ["spring", "circular", "kamada_kawai"]
    themes = ["bold", "pastel", "default"]
    
    results = []
    
    for layout in layouts:
        for theme in themes:
            output_file = visualize_graph(graph_file, layout=layout, color_theme=theme)
            print(f"生成图像: {output_file} (布局: {layout}, 颜色主题: {theme})")
            results.append(output_file)
    
    return results

if __name__ == "__main__":
    # 设置字体
    setup_chinese_font()
    
    # 测试图谱可视化
    result_files = test_chinese_graph_visualization()
    
    print("\n生成的所有图像文件:")
    for file in result_files:
        print(f"- {file}") 