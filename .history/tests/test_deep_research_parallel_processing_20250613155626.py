"""
测试深度研究工作流中的并行处理功能。

主要测试点：
1. 并行处理功能 - initiate_final_section_writing 函数在 langgraph studio 中是否正常工作
2. 图分析工具 - 是否正确处理中文字体、错误处理和正确处理工具名称
3. 数据持久化模块 - 数据缓存系统是否正常工作，包括数据过期机制
"""

import os
import tempfile
import json
from pathlib import Path
import pytest
import matplotlib.pyplot as plt

from open_deep_research.state import Section, ReportState
from open_deep_research.graph import initiate_final_section_writing, graph
from multi_agent_system.tools.graph_analysis_tools import (
    _create_entity_graph, 
    _visualize_graph,
    get_graph_analysis_tools
)
from multi_agent_system.tools.data_persistence_tools import (
    cache_data,
    get_cached_data,
    get_persistence_tools
)
from langgraph.constants import Send

class TestParallelProcessing:
    """测试深度研究工作流的并行处理功能"""
    
    @pytest.fixture
    def test_graph_data(self):
        """创建测试用的图数据"""
        entities = [
            {"id": "e1", "name": "实体1", "type": "person"},
            {"id": "e2", "name": "实体2", "type": "organization"},
            {"id": "e3", "name": "实体3", "type": "place"},
            {"id": "e4", "name": "实体4", "type": "concept"},
            {"id": "e5", "name": "实体5中文测试", "type": "person"}
        ]
        relationships = [
            {"source": "e1", "target": "e2", "type": "works_for"},
            {"source": "e2", "target": "e3", "type": "located_in"},
            {"source": "e1", "target": "e4", "type": "created"},
            {"source": "e5", "target": "e3", "type": "visited"},
            {"source": "e5", "target": "e1", "type": "knows"}
        ]
        
        return {"entities": entities, "relationships": relationships, "name": "测试图谱"}
    
    def test_section_content_field(self):
        """测试 Section 类是否正确包含 content 字段"""
        # 创建带有内容的 Section
        section = Section(
            name="测试章节",
            description="这是一个测试章节的描述",
            research=True,
            content="这是章节内容"
        )
        
        # 验证 content 字段正确设置
        assert section.content == "这是章节内容"
        
        # 测试更新 content 字段
        section.content = "更新后的内容"
        assert section.content == "更新后的内容"

    def test_initiate_final_section_writing(self):
        """测试 initiate_final_section_writing 函数是否能正确创建并行任务"""
        # 创建测试所需的 ReportState
        sections = [
            Section(name="引言", description="报告引言", research=False, content=""),
            Section(name="方法论", description="研究方法论", research=True, content=""),
            Section(name="结果", description="研究结果", research=True, content=""),
            Section(name="结论", description="报告结论", research=False, content="")
        ]
        
        state = {
            "topic": "测试主题",
            "sections": sections,
            "completed_sections": [],
            "report_sections_from_research": "已完成的研究章节: 方法论和结果",
            "final_report": "",
            "feedback_on_report_plan": [],
            "source_str": ""
        }
        
        # 调用函数
        result = initiate_final_section_writing(state)
        
        # 验证结果是否返回了 Send 对象列表
        assert isinstance(result, list)
        assert len(result) == 2, "应该有两个不需要研究的章节"
        
        # 验证 Send 对象是否正确
        for send_obj in result:
            assert isinstance(send_obj, Send)
            
            # 检查 Send 对象的 node 参数，这应该是 "write_final_sections"
            assert send_obj.node == "write_final_sections"
            
            # 检查 Send 对象的 arg 参数，这应该包含所需的状态信息
            assert "topic" in send_obj.arg
            assert "section" in send_obj.arg
            assert "report_sections_from_research" in send_obj.arg

    def test_graph_analysis_tools(self):
        """测试图分析工具是否正常工作，包括工具名称是否正确"""
        # 获取工具列表
        tools = get_graph_analysis_tools()
        
        # 提取工具名称
        tool_names = [tool.name for tool in tools]
        print(f"实际工具名称: {tool_names}")
        
        # 验证所有工具是否存在
        assert "_create_entity_graph" in tool_names, "缺少创建知识图谱工具"
        assert "_analyze_graph_centrality" in tool_names, "缺少中心性分析工具"
        assert "_find_shortest_path" in tool_names, "缺少路径查找工具"
        assert "_detect_communities" in tool_names, "缺少社区检测工具"
        assert "_visualize_graph" in tool_names, "缺少可视化图谱工具"
        assert "_graph_similarity_analysis" in tool_names, "缺少图谱相似度分析工具"
        assert "_extract_subgraph" in tool_names, "缺少子图提取工具"
    
    def test_create_entity_graph(self, test_graph_data):
        """测试创建实体图谱功能"""
        entities = test_graph_data["entities"]
        relationships = test_graph_data["relationships"]
        name = test_graph_data["name"]
        
        # 创建图谱
        graph_file = _create_entity_graph(entities, relationships, name)
        
        # 验证图谱文件是否创建
        assert Path(graph_file).exists()
        
        # 验证图谱内容
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        assert graph_data["name"] == name
        assert len(graph_data["nodes"]) == len(entities)
        assert len(graph_data["edges"]) == len(relationships)
    
    def test_visualize_graph(self, test_graph_data):
        """测试图谱可视化功能，包括中文字体支持"""
        # 首先创建一个图谱文件
        entities = test_graph_data["entities"]
        relationships = test_graph_data["relationships"]
        name = test_graph_data["name"]
        
        # 创建图谱
        graph_file = _create_entity_graph(entities, relationships, name)
        
        # 测试可视化
        image_file = _visualize_graph(graph_file, layout="spring", output_format="png")
        
        # 验证图片是否创建
        assert Path(image_file).exists()
        
        # 清理文件
        Path(image_file).unlink(missing_ok=True)
    
    def test_data_persistence(self):
        """测试数据持久化功能，包括缓存过期机制"""
        # 测试数据缓存
        key = "test_key"
        value = {"data": "测试数据", "timestamp": 123456789}
        
        # 缓存数据 - 正确的参数顺序是 data, key, ttl
        cache_data.invoke({"data": value, "key": key, "ttl": 1})  # 1秒过期
        
        # 立即获取
        cached = get_cached_data.invoke({"key": key})
        assert cached == value
        
        # 导入时间模块以等待
        import time
        
        # 等待缓存过期
        time.sleep(1.5)
        
        # 获取过期数据
        expired = get_cached_data.invoke({"key": key})
        assert expired is None or isinstance(expired, str), "缓存应该已经过期"
        
        # 测试获取工具
        tools = get_persistence_tools()
        assert len(tools) > 0, "应该返回多个持久化工具"


def test():
    """运行所有测试"""
    test_parallel = TestParallelProcessing()
    
    # 测试 Section 类的 content 字段
    test_parallel.test_section_content_field()
    
    # 测试并行处理功能
    test_parallel.test_initiate_final_section_writing()
    
    # 测试图分析工具
    test_parallel.test_graph_analysis_tools()
    
    # 准备测试图数据
    graph_data = {
        "entities": [
            {"id": "e1", "name": "实体1", "type": "person"},
            {"id": "e2", "name": "实体2", "type": "organization"},
            {"id": "e3", "name": "实体3", "type": "place"},
        ],
        "relationships": [
            {"source": "e1", "target": "e2", "type": "works_for"},
            {"source": "e2", "target": "e3", "type": "located_in"},
        ],
        "name": "简单测试图谱"
    }
    
    # 测试创建实体图谱
    test_parallel.test_create_entity_graph(graph_data)
    
    # 测试图谱可视化
    test_parallel.test_visualize_graph(graph_data)
    
    # 测试数据持久化
    test_parallel.test_data_persistence()
    
    print("所有测试通过！")


if __name__ == "__main__":
    test() 