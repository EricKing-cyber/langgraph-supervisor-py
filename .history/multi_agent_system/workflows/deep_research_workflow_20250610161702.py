from langgraph_supervisor.supervisor import create_supervisor
from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import tool, BaseTool
from typing import List, Dict, Any, Callable
from langchain_core.runnables import RunnableConfig
from functools import wraps

# 导入open_deep_research中的相关模块
from open_deep_research.src.open_deep_research.multi_agent import (
    supervisor, 
    Sections, 
    Introduction, 
    Conclusion, 
    FinishReport, 
    Question
)
from open_deep_research.src.open_deep_research.prompts import SUPERVISOR_INSTRUCTIONS
from open_deep_research.src.open_deep_research.utils import get_today_str
from open_deep_research.src.open_deep_research.configuration import Configuration

# 导入配置工具
from multi_agent_system.config.deep_research_config import config_to_runnable_config

def get_supervisor_tools() -> list[BaseTool]:
    """获取主管代理工具"""
    tools = [
        tool(Sections), 
        tool(Introduction), 
        tool(Conclusion), 
        tool(FinishReport),
        tool(Question)
    ]
    return tools

def with_config_injection(graph_func):
    """装饰器：向图的调用中注入配置"""
    @wraps(graph_func)
    def wrapper(state, config=None):
        # 如果配置存在，使用它
        if hasattr(build_deep_research_workflow, 'config') and build_deep_research_workflow.config:
            # 合并传入的配置和存储的配置
            stored_config = config_to_runnable_config(build_deep_research_workflow.config)
            if config:
                merged_config = config.copy() if config else {}
                if 'configurable' in stored_config and 'configurable' in merged_config:
                    merged_config['configurable'].update(stored_config['configurable'])
                else:
                    merged_config.update(stored_config)
                return graph_func(state, merged_config)
            else:
                return graph_func(state, stored_config)
        else:
            # 如果没有存储配置，使用传入的配置
            return graph_func(state, config)
    
    return wrapper

def build_deep_research_workflow(research_agents: list, model: LanguageModelLike, config: Dict[str, Any] = None):
    """
    构建深度研究工作流，集成open_deep_research的主管代理架构
    
    Args:
        research_agents: 研究员代理列表
        model: 语言模型
        config: 配置信息，用于设置deep_research的行为（将通过后续调用时的config传递）
    
    Returns:
        构建好的主管工作流图
    """
    # 初始化配置 - 保存为类变量供后续使用
    if config is None:
        config = {}
    
    # 保存配置以便后续使用
    build_deep_research_workflow.config = config
    
    # 获取主管工具
    supervisor_tools = get_supervisor_tools()
    
    # 创建增强的提示词，明确指导研究主管如何分配任务给不同领域的研究员
    enhanced_supervisor_prompt = f"""
    你是一个深度研究团队的主管，负责管理多个领域的研究专家。你的职责是协调研究工作、分配任务、监督研究进度并整合最终报告。

    你的团队成员包括:
    1. ai_technology_researcher - AI技术研究专家
       - 擅长领域：人工智能、机器学习、深度学习、大语言模型、计算机视觉、语音识别等
       - 适用任务：AI技术趋势分析、算法研究、技术应用分析等

    2. finance_researcher - 金融领域研究专家
       - 擅长领域：经济学、金融市场、投资分析、风险管理、金融科技、加密货币等
       - 适用任务：市场趋势分析、投资策略研究、经济政策影响分析等

    3. science_researcher - 科学领域研究专家
       - 擅长领域：物理学、化学、生物学、环境科学、医学、天文学等
       - 适用任务：科学前沿研究分析、技术可行性研究、科学文献综述等

    工作流程:
    1. 根据用户提供的研究主题，确定需要哪些专业领域的研究
    2. 使用 Sections 工具规划研究报告的结构，划分适当的章节
    3. 将各个研究章节分配给最合适的专家进行深入研究
    4. 监督研究进度，必要时提供指导或要求补充研究
    5. 当所有章节完成后，使用 Introduction 和 Conclusion 工具完成引言和结论
    6. 整合所有内容，生成最终的完整研究报告

    如何分配任务:
    - 对于跨领域的研究主题，可以将不同章节分配给不同专家
    - 确保每个章节分配给最专业的研究员
    - 例如：对于"AI在金融领域的应用"，可以让AI专家研究技术部分，金融专家研究应用场景部分

    今天是{get_today_str()}
    """
    
    # 使用create_supervisor构建工作流图，不传递config参数
    graph = create_supervisor(
        agents=research_agents,
        model=model,
        prompt=enhanced_supervisor_prompt,
        tools=supervisor_tools
    )
    
    # 为图的invoke和ainvoke方法添加配置注入装饰器
    original_invoke = (graph.compile()).invoke
    original_ainvoke = (graph.compile()).ainvoke
    
    graph.invoke = with_config_injection(original_invoke)
    graph.ainvoke = with_config_injection(original_ainvoke)
    
    return graph

__all__ = ["build_deep_research_workflow"] 