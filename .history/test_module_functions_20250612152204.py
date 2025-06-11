"""
测试模块功能
测试三个集成模块的基本功能
"""

import os
import asyncio
from pathlib import Path

# 确保数据目录存在
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

def test_data_persistence():
    """测试数据持久化功能"""
    print("\n=== 测试数据持久化功能 ===")
    try:
        from multi_agent_system.tools.data_persistence_tools import (
            save_report_to_file, 
            read_report_from_file,
            list_saved_reports
        )
        
        # 测试保存报告
        test_content = "# 测试报告\n\n这是一个用于测试的简单报告内容。"
        file_path = save_report_to_file(test_content, "测试主题")
        print(f"保存报告成功: {file_path}")
        
        # 测试读取报告
        read_content = read_report_from_file(file_path)
        success = read_content.strip() == test_content.strip()
        print(f"读取报告成功: {success}")
        
        # 测试列出保存的报告
        reports = list_saved_reports()
        print(f"已保存的报告数量: {len(reports)}")
        
        return True
    except Exception as e:
        print(f"数据持久化功能测试失败: {e}")
        return False

def test_graph_analysis():
    """测试图分析功能"""
    print("\n=== 测试图分析功能 ===")
    try:
        from multi_agent_system.tools.graph_analysis_tools import (
            create_knowledge_graph,
            add_entities_to_graph,
            add_relationships_to_graph,
            list_knowledge_graphs
        )
        
        # 测试创建知识图谱
        graph_name = "test_graph"
        result = create_knowledge_graph(graph_name)
        print(f"创建知识图谱: {result}")
        
        # 测试添加实体
        entities = [
            {"id": "e1", "label": "Person", "properties": {"name": "测试用户"}},
            {"id": "e2", "label": "Topic", "properties": {"name": "图分析"}}
        ]
        result = add_entities_to_graph(graph_name, entities)
        print(f"添加实体: {result}")
        
        # 测试添加关系
        relations = [
            {"source": "e1", "target": "e2", "label": "INTERESTED_IN"}
        ]
        result = add_relationships_to_graph(graph_name, relations)
        print(f"添加关系: {result}")
        
        # 测试列出图谱
        graphs = list_knowledge_graphs()
        print(f"知识图谱列表: {graphs}")
        
        return True
    except Exception as e:
        print(f"图分析功能测试失败: {e}")
        return False

def test_integration_in_workflow():
    """测试在工作流中的集成"""
    print("\n=== 测试在工作流中的集成 ===")
    try:
        from multi_agent_system.workflows.deep_research_workflow import get_supervisor_tools
        
        # 获取主管工具
        tools = get_supervisor_tools()
        
        # 检查获取的工具中是否包含新增的工具
        tool_names = [tool.name for tool in tools]
        print(f"获取到的工具总数: {len(tools)}")
        
        # 检查是否包含评估工具
        has_eval_tools = any("evaluate_" in name for name in tool_names)
        print(f"包含评估工具: {has_eval_tools}")
        
        # 检查是否包含数据持久化工具
        has_data_tools = any("save_" in name or "read_" in name for name in tool_names)
        print(f"包含数据持久化工具: {has_data_tools}")
        
        # 检查是否包含图分析工具
        has_graph_tools = any("graph" in name for name in tool_names)
        print(f"包含图分析工具: {has_graph_tools}")
        
        return has_eval_tools and has_data_tools and has_graph_tools
    except Exception as e:
        print(f"工作流集成测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试三个集成模块的基本功能")
    
    persistence_test = test_data_persistence()
    graph_test = test_graph_analysis()
    integration_test = test_integration_in_workflow()
    
    print("\n=== 测试结果汇总 ===")
    print(f"数据持久化功能: {'成功' if persistence_test else '失败'}")
    print(f"图分析功能: {'成功' if graph_test else '失败'}")
    print(f"工作流集成: {'成功' if integration_test else '失败'}")
    
    if persistence_test and graph_test and integration_test:
        print("\n所有功能测试成功!")
    else:
        print("\n部分功能测试失败，请检查错误信息") 