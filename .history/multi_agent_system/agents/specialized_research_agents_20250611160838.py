"""
专业研究代理模块
定义特定领域研究代理实现
"""

from typing import List, Dict, Any, Optional
from langchain_core.language_models import LanguageModelLike
from langgraph.pregel import Pregel

from multi_agent_system.agents.research_agent import SpecialtyResearchAgent, create_research_agent
from multi_agent_system.model_utils import create_model


def create_legal_research_agent(model_name: str = "default_model", search_api: str = "tavily") -> Pregel:
    """创建法律研究代理
    
    专注于法律条文检索、案例分析、合规性审查、合同条款审查等法律专业研究
    
    Args:
        model_name: 模型名称
        search_api: 搜索API类型，默认使用tavily（更稳定的选择）
    """
    return create_research_agent("legal", model_name, search_api)


def create_medical_research_agent(model_name: str = "default_model", search_api: str = "tavily") -> Pregel:
    """创建医疗健康研究代理
    
    专注于医学文献检索、临床试验分析、药物研发等医疗健康领域研究
    
    Args:
        model_name: 模型名称
        search_api: 搜索API类型，默认使用tavily（更稳定的选择）
    """
    return create_research_agent("medical", model_name, search_api)


def create_engineering_research_agent(model_name: str = "default_model", search_api: str = "tavily") -> Pregel:
    """创建工程技术研究代理
    
    专注于技术标准查询、专利分析、工程方案优化等工程技术领域研究
    
    Args:
        model_name: 模型名称
        search_api: 搜索API类型，默认使用tavily（更稳定的选择）
    """
    return create_research_agent("engineering", model_name, search_api)


def create_socialscience_research_agent(model_name: str = "default_model", search_api: str = "tavily") -> Pregel:
    """创建社会科学研究代理
    
    专注于社会调查数据分析、政策影响评估等社会科学领域研究
    
    Args:
        model_name: 模型名称
        search_api: 搜索API类型，默认使用tavily（更稳定的选择）
    """
    return create_research_agent("socialscience", model_name, search_api)


def create_climate_research_agent(model_name: str = "default_model", search_api: str = "tavily") -> Pregel:
    """创建气候科学研究代理
    
    专注于气候模型分析、环境数据挖掘等气候科学领域研究
    
    Args:
        model_name: 模型名称
        search_api: 搜索API类型，默认使用tavily（更稳定的选择）
    """
    return create_research_agent("climate", model_name, search_api)


# 创建多搜索源研究代理的工厂函数
def create_multisource_research_agent(
    specialty: str,
    model_name: str = "default_model",
    search_apis: List[str] = ["tavily", "duckduckgo"]
) -> Pregel:
    """创建具有多搜索源能力的研究代理
    
    Args:
        specialty: 研究专业领域
        model_name: 模型名称
        search_apis: 搜索API列表，默认组合使用tavily和duckduckgo（最稳定的组合）
    """
    # 保证安全的搜索API组合
    safe_apis = []
    for api in search_apis:
        if api.lower() in ["tavily", "duckduckgo"]:
            # 这些是最稳定的API，总是允许
            safe_apis.append(api.lower())
    
    # 确保至少有一个搜索API
    if not safe_apis:
        safe_apis = ["tavily"]
        
    return create_research_agent(specialty, model_name, safe_apis)


__all__ = [
    "create_legal_research_agent",
    "create_medical_research_agent", 
    "create_engineering_research_agent",
    "create_socialscience_research_agent",
    "create_climate_research_agent",
    "create_multisource_research_agent"
] 