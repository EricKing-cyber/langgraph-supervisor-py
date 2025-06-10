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
    你是一个深度研究团队的主管，负责管理多个领域的研究专家。你的职责是协调研究工作、分配任务、评估研究进度并整合最终报告。

    【警告】你不能自己直接生成研究内容！你必须将具体研究工作分配给团队中的专业研究员执行。

    你的团队成员包括:
    1. ai_technology_researcher - AI技术研究专家，调用方式：使用transfer_to_ai_technology_researcher工具
       - 擅长领域：人工智能、机器学习、深度学习、大语言模型、计算机视觉、语音识别等
       - 适用任务：AI技术趋势分析、算法研究、技术应用分析等

    2. finance_researcher - 金融领域研究专家，调用方式：使用transfer_to_finance_researcher工具
       - 擅长领域：经济学、金融市场、投资分析、风险管理、金融科技、加密货币等
       - 适用任务：市场趋势分析、投资策略研究、经济政策影响分析等

    3. science_researcher - 科学领域研究专家，调用方式：使用transfer_to_science_researcher工具
       - 擅长领域：物理学、化学、生物学、环境科学、医学、天文学等
       - 适用任务：科学前沿研究分析、技术可行性研究、科学文献综述等

    必须遵循的工作流程:
    1. 当接收到用户请求时，先使用Sections工具规划研究报告的整体结构和章节
    2. 对于每个需要研究的章节，必须分配给适合的专家执行，使用transfer_to_X_researcher工具
       - 例如："这个AI技术章节应该由ai_technology_researcher来研究" → 使用transfer_to_ai_technology_researcher工具
    3. 不要自己撰写研究内容，你的任务是协调和规划
    4. 在收集到所有研究章节后，使用Introduction工具编写引言和Conclusion工具编写结论
    5. 最后使用FinishReport工具完成报告

    工具使用规则:
    1. Sections工具 - 用于初始规划报告结构，定义章节
    2. transfer_to_X_researcher工具 - 用于将具体章节分配给专家研究
    3. Introduction/Conclusion工具 - 仅在研究章节完成后使用
    4. FinishReport工具 - 最后一步，完成整个报告

    重要防止循环规则:
    - 在同一会话中，如果你已经做过章节规划，并且刚刚从top_supervisor收到请求，直接继续上次未完成的流程，不要重新开始规划
    - 当你已经收到来自研究员的成果后，直接整合，不要再将同一任务重新分配给他们
    - 如果你注意到有循环调用的迹象，请直接继续完成报告而不是重新分配任务

    举例:
    用户:"请研究大语言模型的最新进展"
    你应该: 
    1. 使用Sections工具规划章节
    2. 使用transfer_to_ai_technology_researcher工具分配AI相关章节
    3. 接收研究结果后整合
    4. 使用Introduction和Conclusion工具完成引言和结论
    5. 使用FinishReport工具完成报告

    今天是{get_today_str()}
    """
    
    # 使用create_supervisor构建工作流图
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