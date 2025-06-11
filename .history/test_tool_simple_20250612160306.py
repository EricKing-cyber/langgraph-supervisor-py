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
    
    # 查看函数的原始引用情况
    print(f"save_report_to_file._original 存在: {hasattr(save_report_to_file, '_original')}")
    
    # 找到原始函数
    if hasattr(save_report_to_file, '_original'):
        original_save = save_report_to_file._original
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
    
    if hasattr(read_report_from_file, '_original'):
        original_read = read_report_from_file._original
    else:
        original_read = read_report_from_file
        
    print("\n读取报告...")
    content = original_read(filepath)
    print(f"读取成功，内容长度: {len(content)} 字符")
    
    # 测试缓存
    if hasattr(cache_data, '_original'):
        original_cache = cache_data._original
    else:
        original_cache = cache_data
        
    print("\n缓存数据...")
    cache_key = original_cache({"test": "数据", "number": 123}, "test_key", 60)
    print(f"缓存成功: {cache_key}")
    
    if hasattr(get_cached_data, '_original'):
        original_get_cache = get_cached_data._original
    else:
        original_get_cache = get_cached_data
        
    print("\n获取缓存数据...")
    data = original_get_cache(cache_key)
    print(f"获取成功: {data}")
    
    return True

def test_graph_analysis():
    """测试图分析工具的底层函数"""
    print("\n===== 测试图分析模块 =====")
    
    # 导入函数
    from multi_agent_system.tools.graph_analysis_tools import (
        create_entity_graph, analyze_graph_centrality,
        find_shortest_path, visualize_graph
    )
    
    # 修改graph_analysis_tools.py使用相同的方式导出函数
    print("\n注意: 对图分析模块的测试将在更新graph_analysis_tools.py后进行")
    
    return True

def test_evaluation():
    """测试评估工具的底层函数"""
    print("\n===== 测试评估模块 =====")
    
    # 导入函数
    from multi_agent_system.tools.evaluation_tools import (
        evaluate_report_quality, evaluate_reliability,
        evaluate_content_relevance, evaluate_coherence
    )
    
    # 修改evaluation_tools.py使用相同的方式导出函数
    print("\n注意: 对评估模块的测试将在更新evaluation_tools.py后进行")
    
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