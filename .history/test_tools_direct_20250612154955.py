#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具模块直接调用测试脚本
测试新集成的三个工具模块是否支持直接调用
"""

import os
import json
from pathlib import Path

# 确保数据目录存在
Path("data").mkdir(exist_ok=True)
Path("data/reports").mkdir(exist_ok=True)
Path("data/evaluations").mkdir(exist_ok=True)
Path("data/graphs").mkdir(exist_ok=True)
Path("data/cache").mkdir(exist_ok=True)

# 测试数据持久化工具
def test_persistence_tools():
    print("\n===== 测试数据持久化工具 =====")
    
    from multi_agent_system.tools.data_persistence_tools import save_report_to_file, read_report_from_file
    
    # 测试保存和读取文件
    report_content = """# 测试报告

这是一个测试报告，用于验证数据持久化工具的功能。

## 第一部分
这里是报告的第一部分内容。

## 第二部分
这里是报告的第二部分内容。
"""
    
    print("保存报告到文件...")
    filepath = save_report_to_file(report_content, "测试报告", "md")
    print(f"文件保存成功: {filepath}")
    
    print("\n读取报告内容...")
    content = read_report_from_file(filepath)
    print(f"读取成功，报告长度: {len(content)} 字符")
    
    # 测试列出报告
    from multi_agent_system.tools.data_persistence_tools import list_saved_reports
    
    print("\n列出已保存的报告...")
    reports = list_saved_reports()
    print(f"找到 {len(reports)} 个报告")
    
    # 测试缓存功能
    from multi_agent_system.tools.data_persistence_tools import cache_data, get_cached_data
    
    print("\n测试数据缓存...")
    cache_key = cache_data({"test": "数据", "number": 123}, "test_key", 60)
    print(f"缓存成功，键值: {cache_key}")
    
    cached_data = get_cached_data(cache_key)
    print(f"读取缓存成功: {cached_data}")
    
    print("数据持久化工具测试完成!")
    return True


# 测试图分析工具
def test_graph_tools():
    print("\n===== 测试图分析工具 =====")
    
    from multi_agent_system.tools.graph_analysis_tools import create_entity_graph, analyze_graph_centrality
    
    # 创建一个测试图
    entities = [
        {"id": "e1", "name": "张三", "type": "人物"},
        {"id": "e2", "name": "李四", "type": "人物"},
        {"id": "e3", "name": "王五", "type": "人物"},
        {"id": "e4", "name": "ABC公司", "type": "组织"},
        {"id": "e5", "name": "XYZ科技", "type": "组织"}
    ]
    
    relationships = [
        {"source": "e1", "target": "e4", "type": "就职于"},
        {"source": "e2", "target": "e4", "type": "就职于"},
        {"source": "e3", "target": "e5", "type": "创立了"},
        {"source": "e4", "target": "e5", "type": "合作伙伴"},
        {"source": "e2", "target": "e3", "type": "朋友"},
        {"source": "e1", "target": "e2", "type": "认识"}
    ]
    
    print("创建实体关系图...")
    graph_file = create_entity_graph(entities, relationships, "测试关系图")
    print(f"图创建成功: {graph_file}")
    
    # 分析中心性
    print("\n分析图中心性...")
    centrality = analyze_graph_centrality(graph_file)
    print(f"中心性分析结果: {len(centrality)} 项指标")
    
    # 寻找最短路径
    from multi_agent_system.tools.graph_analysis_tools import find_shortest_path
    
    print("\n寻找最短路径...")
    path = find_shortest_path(graph_file, "e1", "e5")
    print(f"路径查找结果: {path}")
    
    # 可视化图
    from multi_agent_system.tools.graph_analysis_tools import visualize_graph
    
    print("\n可视化图...")
    try:
        vis_path = visualize_graph(graph_file, "spring", "png")
        print(f"图可视化完成，保存在: {vis_path}")
    except Exception as e:
        print(f"图可视化失败: {str(e)}")
    
    print("图分析工具测试完成!")
    return True


# 测试评估工具
def test_evaluation_tools():
    print("\n===== 测试评估工具 =====")
    
    from multi_agent_system.tools.evaluation_tools import evaluate_report_quality, evaluate_reliability
    
    # 创建测试文本
    test_report = """# 大语言模型发展趋势研究

## 引言
大语言模型(LLM)是近年来人工智能领域最重要的突破之一。本报告分析大语言模型的发展趋势。

## 模型规模演化
从GPT-1的1.17亿参数到GPT-3的1750亿参数[1]，再到GPT-4的未公开参数规模(估计超过1万亿)[2]，
模型规模呈指数级增长。这一趋势可能会在未来几年继续，但也面临计算资源和训练成本的挑战。

## 多模态能力
最新的大语言模型如GPT-4V、Claude 3 Opus和Gemini等都具备多模态处理能力，可以同时理解文本和图像[3]。
根据OpenAI的研究，这种能力显著提升了模型在复杂场景中的表现。

## 推理与知识整合
虽然大语言模型在推理能力上取得了长足进步，但研究表明它们仍然存在事实混淆的问题[4]。
未来的发展方向包括知识库增强和外部工具调用。

## 结论
大语言模型正朝着规模更大、能力更全面、推理更准确的方向发展，未来将深刻改变人机交互方式。

## 参考文献
[1] Brown, T. B., et al. (2020). Language Models are Few-Shot Learners.
[2] OpenAI. (2023). GPT-4 Technical Report.
[3] Bubeck, S., et al. (2023). Sparks of Artificial General Intelligence.
[4] Mallen, A., et al. (2023). When hallucinations improve reasoning: Emergent analogical inference.
"""
    
    print("评估报告质量...")
    quality_result = evaluate_report_quality(test_report)
    print(f"质量评估结果: 平均分 {quality_result['average_score']}, 等级 {quality_result['rating']}")
    
    print("\n评估内容可靠性...")
    reliability_result = evaluate_reliability(test_report)
    print(f"可靠性评估结果: 可靠性分数 {reliability_result['reliability_score']}, 级别 {reliability_result['reliability_rating']}")
    
    # 评估内容相关性
    from multi_agent_system.tools.evaluation_tools import evaluate_content_relevance
    
    print("\n评估内容相关性...")
    relevance_result = evaluate_content_relevance(test_report, "大语言模型发展趋势", ["GPT", "模型", "AI", "参数"])
    print(f"相关性评估结果: 相关性分数 {relevance_result['relevance_score']}, 级别 {relevance_result['relevance_rating']}")
    
    # 评估连贯性
    from multi_agent_system.tools.evaluation_tools import evaluate_coherence
    
    print("\n评估连贯性...")
    coherence_result = evaluate_coherence(test_report)
    print(f"连贯性评估结果: 连贯性分数 {coherence_result['coherence_score']}, 级别 {coherence_result['coherence_rating']}")
    
    print("评估工具测试完成!")
    return True


def main():
    """主测试函数"""
    print("===== 开始工具模块直接调用测试 =====")
    
    # 测试数据持久化工具
    try:
        test_persistence_tools()
    except Exception as e:
        print(f"数据持久化工具测试失败: {str(e)}")
    
    # 测试图分析工具
    try:
        test_graph_tools()
    except Exception as e:
        print(f"图分析工具测试失败: {str(e)}")
    
    # 测试评估工具
    try:
        test_evaluation_tools()
    except Exception as e:
        print(f"评估工具测试失败: {str(e)}")
    
    print("\n===== 工具模块测试完成 =====")


if __name__ == "__main__":
    main() 