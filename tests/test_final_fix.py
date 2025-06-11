import unittest
import os
import sys
from pathlib import Path
import json

# 添加父级目录到系统路径，确保可以导入模块
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from multi_agent_system.tools.graph_analysis_tools import get_graph_analysis_tools
from multi_agent_system.tools.data_persistence_tools import get_persistence_tools
from multi_agent_system.tools.evaluation_tools import get_evaluation_tools
from multi_agent_system.workflows.deep_research_workflow import get_supervisor_tools
from multi_agent_system.workflows.deep_research_workflow import build_deep_research_workflow
from multi_agent_system.model_utils import create_model
from multi_agent_system.agents import create_research_agent
from multi_agent_system.config.deep_research_config import create_research_config

class FinalFixTest(unittest.TestCase):
    
    def test_graph_tools_name_fix(self):
        """测试图分析工具名称修复"""
        print("\n测试图分析工具名称修复...")
        
        graph_tools = get_graph_analysis_tools()
        tool_names = [tool.name for tool in graph_tools]
        
        required_tools = [
            "create_knowledge_graph",
            "add_entities_to_graph", 
            "add_relationships_to_graph",
            "analyze_graph_centrality", 
            "find_path_between_entities", 
            "detect_communities",
            "list_knowledge_graphs"
        ]
        
        for tool_name in required_tools:
            self.assertIn(tool_name, tool_names, f"工具 '{tool_name}' 未在图分析工具列表中找到")
        
        print("图分析工具名称已正确修复!")
    
    def test_parallel_tool_calls_config(self):
        """测试并行工具调用配置传递"""
        print("\n测试并行工具调用配置传递...")
        
        # 创建语言模型
        model = create_model("gpt-4.1-2025-04-14")
        
        # 创建研究代理
        ai_research_agent = create_research_agent("ai_technology", "gpt-4.1-2025-04-14", search_api="tavily")
        
        # 创建研究配置并添加并行工具调用
        research_config = create_research_config(
            search_api="tavily",
            parallel_tool_calls=True  # 启用并行工具调用
        )
        
        # 构建深度研究工作流
        graph = build_deep_research_workflow(
            [ai_research_agent],
            model,
            research_config
        )
        
        # 验证配置是否被正确保存
        self.assertTrue(hasattr(build_deep_research_workflow, 'config'), 
                       "工作流未保存配置")
        
        if hasattr(build_deep_research_workflow, 'config'):
            config = build_deep_research_workflow.config
            self.assertIn('configurable', config, 
                         "配置中缺少configurable键")
            
            if 'configurable' in config:
                self.assertIn('parallel_tool_calls', config['configurable'], 
                             "配置中缺少parallel_tool_calls设置")
                
                self.assertTrue(config['configurable']['parallel_tool_calls'], 
                              "parallel_tool_calls未被启用")
        
        print("并行工具调用配置已正确传递!")
    
    def test_supervisor_tool_registration(self):
        """测试主管工具注册"""
        print("\n测试主管工具注册...")
        
        supervisor_tools = get_supervisor_tools()
        supervisor_tool_names = [tool.name for tool in supervisor_tools]
        
        # 工具分类
        graph_tools = [
            "create_knowledge_graph", "add_entities_to_graph", "add_relationships_to_graph",
            "analyze_graph_centrality", "find_path_between_entities", "detect_communities",
            "list_knowledge_graphs"
        ]
        
        persistence_tools = [
            "save_report_to_file", "read_report_from_file", "save_evaluation_results",
            "cache_data", "get_cached_data", "list_saved_reports", "list_evaluation_results"
        ]
        
        evaluation_tools = [
            "evaluate_report_quality", "evaluate_groundedness", "get_evaluation_criteria",
            "get_evaluation_summary"
        ]
        
        base_tools = [
            "Sections", "Introduction", "Conclusion", "FinishReport", "Question"
        ]
        
        # 检查所有工具是否已注册到主管工具列表中
        all_required_tools = graph_tools + persistence_tools + evaluation_tools + base_tools
        
        for tool_name in all_required_tools:
            # 由于工具名称可能有前缀下划线，我们检查工具名称的结尾
            matched = False
            for actual_name in supervisor_tool_names:
                if actual_name == tool_name or actual_name.endswith("_" + tool_name):
                    matched = True
                    break
            
            # 如果没有匹配，检查是否有别名
            if not matched:
                self.fail(f"工具 '{tool_name}' 未在主管工具列表中找到")
        
        print("主管工具注册已正确配置!")

if __name__ == "__main__":
    unittest.main() 