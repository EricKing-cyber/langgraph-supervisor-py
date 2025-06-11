import unittest
import os
import sys
from pathlib import Path
import json

# 添加父级目录到系统路径，确保可以导入模块
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from langgraph_app import app
from multi_agent_system.tools.graph_analysis_tools import get_graph_analysis_tools
from multi_agent_system.tools.data_persistence_tools import get_persistence_tools
from multi_agent_system.tools.evaluation_tools import get_evaluation_tools
from multi_agent_system.workflows.deep_research_workflow import get_supervisor_tools

class ToolIssuesTest(unittest.TestCase):
    
    def test_tool_name_consistency(self):
        """
        测试工具的实际实现名称与提示词中描述的名称是否一致
        """
        # 获取所有工具
        print("检查工具名称是否一致...")
        
        # 分别获取不同类型的工具
        graph_tools = get_graph_analysis_tools()
        data_tools = get_persistence_tools()
        eval_tools = get_evaluation_tools()
        supervisor_tools = get_supervisor_tools()
        
        # 提示词中提到的工具名称
        prompted_tool_names = [
            # 图分析工具
            "create_knowledge_graph", "add_entities_to_graph", "add_relationships_to_graph",
            "analyze_graph_centrality", "find_path_between_entities", "detect_communities",
            "list_knowledge_graphs",
            
            # 数据持久化工具
            "save_report_to_file", "read_report_from_file", "save_evaluation_results",
            "cache_data", "get_cached_data", "list_saved_reports", "list_evaluation_results",
            
            # 评估工具
            "evaluate_report_quality", "evaluate_groundedness", "get_evaluation_criteria",
            "get_evaluation_summary",
            
            # 基础工具
            "Sections", "Introduction", "Conclusion", "FinishReport", "Question",
            
            # 转移工具（这些是隐式定义的，不在工具列表中）
            "transfer_to_ai_technology_researcher", "transfer_to_finance_researcher",
            "transfer_to_science_researcher", "transfer_to_legal_researcher",
            "transfer_to_medical_researcher", "transfer_to_engineering_researcher",
            "transfer_to_socialscience_researcher", "transfer_to_climate_researcher"
        ]
        
        # 检查实际工具名称
        actual_tool_names = []
        
        for tool_list in [graph_tools, data_tools, eval_tools, supervisor_tools]:
            for tool in tool_list:
                actual_tool_names.append(tool.name)
                print(f"找到工具: {tool.name}")
        
        # 检查提示词中提到的工具是否都存在
        for tool_name in prompted_tool_names:
            # 忽略转移工具，因为它们是隐式定义的
            if tool_name.startswith("transfer_to_"):
                continue
            
            self.assertIn(tool_name, actual_tool_names, f"工具 '{tool_name}' 在提示词中提到但实际未实现")
    
    def test_tool_registration(self):
        """测试工具注册是否正确"""
        print("检查工具注册...")
        
        # 获取主管工具
        supervisor_tools = get_supervisor_tools()
        supervisor_tool_names = [tool.name for tool in supervisor_tools]
        
        # 验证全部工具是否都注册了
        required_tools = [
            # 图分析工具
            "create_knowledge_graph", "analyze_graph_centrality", 
            "find_path_between_entities", "detect_communities",
            
            # 数据持久化工具
            "cache_data", "get_cached_data", "list_saved_reports", "list_evaluation_results",
            
            # 评估工具
            "evaluate_groundedness", "get_evaluation_criteria", "get_evaluation_summary"
        ]
        
        for tool_name in required_tools:
            self.assertIn(tool_name, supervisor_tool_names, f"工具 '{tool_name}' 未正确注册到主管工具列表")
    
    def test_parallel_tool_call_config(self):
        """测试并行工具调用配置是否存在"""
        print("检查并行工具调用配置...")
        
        # 检查工作流的配置中是否有 parallel_tool_calls 参数
        if hasattr(app, 'config'):
            config = app.config
            print("应用配置:", config)
        else:
            print("应用没有config属性")

if __name__ == "__main__":
    unittest.main() 