from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from multi_agent_system.model_config import ModelConfig
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_anthropic import ChatAnthropic
from langchain.chat_models.ollama import ChatOllama
from typing import List, Dict, Any, Optional, Union, Callable
import re
import os

def create_model(model_name: str = None):
    """创建语言模型实例，支持多种模型类型并提供工具调用适配"""
    #=================================
    # Cogito模型（使用适配器支持工具调用）
    #=================================
    if model_name and model_name.startswith("cogito:"):
        model = ChatOllama(
            model=model_name,
            temperature=0.1,
            format="json",  # 启用JSON格式
            tool_system_prompt="使用工具时必须使用JSON格式，format={'name': 'tool_name', 'arguments': {}}。工具调用必须使用JSON格式，不能用文本描述。"
        )
        return CogitoToolAdapter(model)  # 使用适配器包装
    
    #=================================
    # OpenAI模型
    #=================================
    elif model_name == "gpt-4.1-2025-04-14" or model_name == "qwen3-32b":
        if not ModelConfig.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in the environment variables.")
            
        return ChatOpenAI(
            model=model_name,
            base_url=ModelConfig.OPENAI_BASE_URL,
            api_key=SecretStr(ModelConfig.OPENAI_API_KEY)
        )
    
    #=================================
    # 本地模型（使用OpenAI兼容接口）
    #=================================
    elif model_name in ["qwen3:8b", "granite3.3:8b"]:
        return ChatOpenAI(
            model=model_name,
            base_url=ModelConfig.LOCAL_MODEL_URL,
            api_key=SecretStr("no-need")
        )
    
    #=================================
    # Anthropic模型
    #=================================
    elif model_name and (model_name.startswith("claude-3") or model_name.startswith("claude:")):
        api_key = os.environ.get('ANTHROPIC_API_KEY', 'your_api_key')
        model = ChatAnthropic(
            temperature=0,
            model_name=model_name,
            anthropic_api_key=api_key,
        )
        return model
    
    #=================================
    # 默认模型
    #=================================
    else:
        # 默认使用 cogito:8b 模型并应用工具调用适配器
        model = ChatOllama(
            model="cogito:8b",
            temperature=0.1,
            format="json",  # 启用JSON格式 
            tool_system_prompt="使用工具时必须使用JSON格式，format={'name': 'tool_name', 'arguments': {}}。工具调用必须使用JSON格式，不能用文本描述。"
        )
        return CogitoToolAdapter(model)

class CogitoToolAdapter:
    """Cogito模型的工具调用适配器，处理文本描述的工具调用"""
    
    def __init__(self, model: ChatOllama):
        self.model = model
        # 编译正则表达式用于匹配描述中的工具调用
        self.tool_pattern = re.compile(r"调用(?:工具)?[\s]*(transfer_to_\w+)[\s]*(?:工具)?")
    
    def bind_tools(self, tools: List[BaseTool], **kwargs):
        """绑定工具到模型，并创建一个带工具支持的新适配器"""
        # 原始模型绑定工具
        modified_model = self.model.bind_tools(tools, **kwargs)
        # 创建新适配器
        adapter = CogitoToolAdapter(modified_model)
        # 保存工具名称映射，用于后续识别
        adapter.tool_names = {tool.name: tool for tool in tools}
        return adapter
    
    def _extract_tool_calls(self, message_content: str):
        """从消息内容中提取工具调用"""
        tool_calls = []
        # 匹配所有工具调用
        matches = self.tool_pattern.findall(message_content)
        
        for idx, tool_name in enumerate(matches):
            if hasattr(self, 'tool_names') and tool_name in self.tool_names:
                tool_calls.append({
                    'id': f'call_{idx}',
                    'name': tool_name,
                    'args': {},
                    'type': 'tool_call'
                })
        
        return tool_calls
    
    def invoke(self, messages, **kwargs):
        """调用模型并处理响应，将文本描述的工具调用转换为实际工具调用"""
        response = self.model.invoke(messages, **kwargs)
        
        # 检查是否已有工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            return response
            
        # 提取文本中描述的工具调用
        content = response.content
        tool_calls = self._extract_tool_calls(content)
        
        # 如果找到工具调用，修改响应
        if tool_calls:
            # 设置AI消息的工具调用
            response.tool_calls = tool_calls
            # 修改内容为空，让工具调用更明显
            response.content = ""
            # 设置元数据以表明处理了工具调用
            if not hasattr(response, 'response_metadata'):
                response.response_metadata = {}
            response.response_metadata['finish_reason'] = 'tool_calls'
            response.additional_kwargs['tool_calls'] = tool_calls
        
        return response
    
    async def ainvoke(self, messages, **kwargs):
        """异步调用模型并处理响应，将文本描述的工具调用转换为实际工具调用"""
        response = await self.model.ainvoke(messages, **kwargs)
        
        # 检查是否已有工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            return response
            
        # 提取文本中描述的工具调用
        content = response.content
        tool_calls = self._extract_tool_calls(content)
        
        # 如果找到工具调用，修改响应
        if tool_calls:
            # 设置AI消息的工具调用
            response.tool_calls = tool_calls
            # 修改内容为空，让工具调用更明显
            response.content = ""
            # 设置元数据以表明处理了工具调用
            if not hasattr(response, 'response_metadata'):
                response.response_metadata = {}
            response.response_metadata['finish_reason'] = 'tool_calls'
            response.additional_kwargs['tool_calls'] = tool_calls
        
        return response

__all__ = ["create_model"]