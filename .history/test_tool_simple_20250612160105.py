#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版工具测试脚本
直接导入函数而不是工具类
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

def test_data_persistence():
    """测试数据持久化工具的底层函数"""
    print("\n===== 测试数据持久化模块 =====")
    
    # 导入原始函数而非工具
    from multi_agent_system.tools.data_persistence_tools import (
        save_report_to_file, read_report_from_file, 
        list_saved_reports, cache_data, get_cached_data
    )
    
    # 查看函数的包装情况
    import inspect
    print(f"save_report_to_file.__wrapped__ 存在: {hasattr(save_report_to_file, '__wrapped__')}")
    
    # 找到原始函数
    if hasattr(save_report_to_file, '__wrapped__'):
        original_save = save_report_to_file.__wrapped__
    else:
        original_save = save_report_to_file
        
    # 手动调用原始函数
    report_content = """# 测试报告

这是一个测试报告，用于验证数据持久化工具的功能。

## 第一部分
这里是报告的第一部分内容。
"""
    
    print("\n保存报告...")
    filepath = original_save(report_content, "测试报告简化", "md")
    print(f"保存成功: {filepath}")
    
    if hasattr(read_report_from_file, '__wrapped__'):
        original_read = read_report_from_file.__wrapped__
    else:
        original_read = read_report_from_file
        
    print("\n读取报告...")
    content = original_read(filepath)
    print(f"读取成功，内容长度: {len(content)} 字符")
    
    return True

def test_graph_analysis():
    """测试图分析工具的底层函数"""
    print("\n===== 测试图分析模块 =====")
    
    # 导入原始函数
    from multi_agent_system.tools.graph_analysis_tools import (
        create_entity_graph, analyze_graph_centrality,
        find_shortest_path, visualize_graph
    )
    
    # 获取原始函数
    if hasattr(create_entity_graph, '__wrapped__'):
        orig_create_graph = create_entity_graph.__wrapped__
    else:
        orig_create_graph = create_entity_graph
    
    # 创建测试数据
    entities = [
        {"id": "e1", "name": "张三", "type": "人物"},
        {"id": "e2", "name": "李四", "type": "人物"},
        {"id": "e3", "name": "王五", "type": "人物"}
    ]
    
    relationships = [
        {"source": "e1", "target": "e2", "type": "认识"},
        {"source": "e2", "target": "e3", "type": "朋友"},
    ]
    
    print("\n创建图...")
    graph_file = orig_create_graph(entities, relationships, "简单测试图")
    print(f"图创建成功: {graph_file}")
    
    # 获取原始中心性分析函数
    if hasattr(analyze_graph_centrality, '__wrapped__'):
        orig_analyze = analyze_graph_centrality.__wrapped__
    else:
        orig_analyze = analyze_graph_centrality
    
    print("\n分析中心性...")
    centrality = orig_analyze(graph_file)
    print(f"中心性分析包含: {len(centrality)} 种指标")
    
    return True

def test_evaluation():
    """测试评估工具的底层函数"""
    print("\n===== 测试评估模块 =====")
    
    # 导入原始函数
    from multi_agent_system.tools.evaluation_tools import (
        evaluate_report_quality, evaluate_reliability,
        evaluate_content_relevance, evaluate_coherence
    )
    
    # 获取原始函数
    if hasattr(evaluate_report_quality, '__wrapped__'):
        orig_eval_quality = evaluate_report_quality.__wrapped__
    else:
        orig_eval_quality = evaluate_report_quality
    
    # 创建测试数据
    test_report = """# 测试报告

## 引言
这是一个测试报告的引言部分。

## 主体部分
这里是主体内容，包含一些分析和结论。

## 结论
测试报告到此结束。
"""
    
    print("\n评估报告质量...")
    quality_result = orig_eval_quality(test_report)
    print(f"质量评估结果: 平均分 {quality_result['average_score']}, 等级: {quality_result['rating']}")
    
    return True

def main():
    """主函数"""
    print("===== 开始简化工具测试 =====")
    
    try:
        test_data_persistence()
    except Exception as e:
        print(f"数据持久化测试失败: {str(e)}")
    
    try:
        test_graph_analysis()
    except Exception as e:
        print(f"图分析测试失败: {str(e)}")
    
    try:
        test_evaluation()
    except Exception as e:
        print(f"评估测试失败: {str(e)}")
    
    print("\n===== 简化工具测试完成 =====")

if __name__ == "__main__":
    main() 