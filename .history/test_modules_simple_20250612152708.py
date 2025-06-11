"""
简化版功能模块测试脚本
独立测试三个功能模块的基本功能
"""

from pathlib import Path
import json

# 确保数据目录存在
data_dirs = ["data", "data/reports", "data/cache", "data/evaluations", "data/graph_data"]
for dir_name in data_dirs:
    Path(dir_name).mkdir(parents=True, exist_ok=True)

def test_data_persistence_module():
    """测试数据持久化模块的基本功能"""
    print("\n=== 测试数据持久化模块 ===")
    
    # 导入模块
    from multi_agent_system.tools.data_persistence_tools import save_report_to_file, read_report_from_file
    
    # 创建测试内容
    test_content = "# 测试报告\n\n这是一个简单的测试报告。"
    
    # 保存到文件
    filepath = save_report_to_file(test_content, "测试主题")
    print(f"报告已保存到: {filepath}")
    
    # 读取文件内容
    read_content = read_report_from_file(filepath)
    print(f"内容读取成功: {read_content == test_content}")
    
    return filepath

def test_graph_analysis_module():
    """测试图分析模块的基本功能"""
    print("\n=== 测试图分析模块 ===")
    
    # 导入模块
    from multi_agent_system.tools.graph_analysis_tools import (
        create_knowledge_graph,
        add_entities_to_graph,
        list_knowledge_graphs
    )
    
    # 创建图谱
    graph_name = "test_graph"
    result = create_knowledge_graph(graph_name)
    print(f"图谱创建结果: {result}")
    
    # 添加实体
    entities = [
        {"id": "e1", "label": "Person", "properties": {"name": "测试用户"}}
    ]
    result = add_entities_to_graph(graph_name, entities)
    print(f"添加实体结果: {result}")
    
    # 列出图谱
    graphs = list_knowledge_graphs()
    print(f"图谱列表: {graphs}")
    
    return graph_name

def test_evaluation_setup():
    """测试评估模块的环境设置"""
    print("\n=== 测试评估模块环境 ===")
    
    # 导入类
    try:
        from open_deep_research.tests.evals.evaluators import (
            OverallQualityScore,
            RelevanceScore, 
            StructureScore,
            GroundednessScore
        )
        print("评估模块类导入成功")
        
        # 导入函数
        from multi_agent_system.tools.evaluation_tools import (
            get_evaluation_criteria,
            get_evaluation_tools
        )
        
        # 获取评估标准
        criteria = get_evaluation_criteria()
        print(f"获取到的评估标准数: {len(criteria)}")
        
        # 获取评估工具
        tools = get_evaluation_tools()
        print(f"评估工具数量: {len(tools)}")
        
        return len(tools) > 0
    except Exception as e:
        print(f"评估模块环境测试失败: {e}")
        return False

def test_workflow_tools_integration():
    """测试工作流工具集成"""
    print("\n=== 测试工作流工具集成 ===")
    
    try:
        from multi_agent_system.workflows.deep_research_workflow import get_supervisor_tools
        
        # 获取所有工具
        all_tools = get_supervisor_tools()
        
        # 按类型统计工具数量
        tool_names = [tool.name for tool in all_tools]
        print(f"工具总数: {len(all_tools)}")
        
        # 计算每种类型的工具数量
        base_tools_count = sum(1 for name in tool_names if name in ["sections", "introduction", "conclusion", "finishReport", "question"])
        eval_tools_count = sum(1 for name in tool_names if "evaluate_" in name.lower())
        persistence_tools_count = sum(1 for name in tool_names if "save_" in name.lower() or "read_" in name.lower() or "list_" in name.lower())
        graph_tools_count = sum(1 for name in tool_names if "graph" in name.lower() or "entit" in name.lower())
        
        print(f"基础工具数: {base_tools_count}")
        print(f"评估工具数: {eval_tools_count}")
        print(f"数据持久化工具数: {persistence_tools_count}")
        print(f"图分析工具数: {graph_tools_count}")
        
        return all([base_tools_count, eval_tools_count, persistence_tools_count, graph_tools_count])
    except Exception as e:
        print(f"工作流工具集成测试失败: {e}")
        return False

def save_test_results(results):
    """保存测试结果到文件"""
    result_file = Path("test_results.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试结果已保存到: {result_file}")

if __name__ == "__main__":
    print("开始运行功能模块测试...")
    
    # 测试数据持久化
    try:
        data_test_result = test_data_persistence_module()
        data_test_success = bool(data_test_result)
    except Exception as e:
        print(f"数据持久化测试异常: {e}")
        data_test_success = False
    
    # 测试图分析
    try:
        graph_test_result = test_graph_analysis_module()
        graph_test_success = bool(graph_test_result)
    except Exception as e:
        print(f"图分析测试异常: {e}")
        graph_test_success = False
    
    # 测试评估模块
    try:
        eval_test_success = test_evaluation_setup()
    except Exception as e:
        print(f"评估模块测试异常: {e}")
        eval_test_success = False
    
    # 测试工作流集成
    try:
        workflow_test_success = test_workflow_tools_integration()
    except Exception as e:
        print(f"工作流集成测试异常: {e}")
        workflow_test_success = False
    
    # 汇总结果
    results = {
        "data_persistence": data_test_success,
        "graph_analysis": graph_test_success,
        "evaluation": eval_test_success,
        "workflow_integration": workflow_test_success,
        "overall_success": all([data_test_success, graph_test_success, eval_test_success, workflow_test_success])
    }
    
    # 打印结果
    print("\n=== 测试结果汇总 ===")
    print(f"数据持久化模块: {'成功' if results['data_persistence'] else '失败'}")
    print(f"图分析模块: {'成功' if results['graph_analysis'] else '失败'}")
    print(f"评估模块: {'成功' if results['evaluation'] else '失败'}")
    print(f"工作流集成: {'成功' if results['workflow_integration'] else '失败'}")
    print(f"\n总体结果: {'全部成功' if results['overall_success'] else '部分失败'}")
    
    # 保存结果
    save_test_results(results) 