from langchain_openai import ChatOpenAI
from pydantic import SecretStr, Field
from multi_agent_system.model_config import ModelConfig
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models.ollama import ChatOllama
from typing import List, Dict, Any, Optional, Union, Callable
import re
import os
from langchain_core.messages import BaseMessage
from langchain_core.callbacks import CallbackManagerForLLMRun
import json

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
        return CogitoToolAdapter(llm=model)  # 使用适配器包装
    
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
        # 默认使用 qwen3:8b 模型并应用工具调用适配器
        model = ChatOllama(
            model="qwen3:8b",
            temperature=0.1,
            format="json",  # 启用JSON格式 
            tool_system_prompt="使用工具时必须使用JSON格式，format={'name': 'tool_name', 'arguments': {}}。工具调用必须使用JSON格式，不能用文本描述。"
        )
        return CogitoToolAdapter(llm=model)

class CogitoToolAdapter(BaseChatModel):
    """Cogito模型的工具调用适配器，处理文本描述的工具调用"""
    
    # 定义pydantic字段
    llm: ChatOllama = Field(description="底层语言模型")
    tools_list: List[BaseTool] = Field(default_factory=list, description="绑定的工具列表")
    tool_names_dict: Dict[str, BaseTool] = Field(default_factory=dict, description="工具名称映射")
    tool_pattern: Any = Field(default=None, description="工具调用模式匹配")
    
    def __init__(self, llm: ChatOllama, **kwargs):
        """初始化适配器
        
        Args:
            llm: 底层模型
        """
        # 编译正则表达式用于匹配描述中的工具调用
        tool_pattern = re.compile(r"调用(?:工具)?[\s]*(transfer_to_\w+)[\s]*(?:工具)?")
        # 调用父类初始化
        super().__init__(llm=llm, tool_pattern=tool_pattern, **kwargs)
        
    @property
    def _llm_type(self) -> str:
        """返回LLM类型"""
        return f"cogito-tool-adapter"
    
    def bind_tools(self, tools: List[BaseTool], **kwargs):
        """绑定工具到模型，LangGraph会调用此方法"""
        # 保存工具列表，供后续使用
        self.tools_list = tools
        # 创建工具名称映射，用于后续识别
        self.tool_names_dict = {tool.name: tool for tool in tools}
        
        # 正确实现bind_tools以避免NotImplementedError
        # 返回自己的实例
        return self
    
    def _extract_tool_calls(self, message_content: str):
        """从消息内容中提取工具调用"""
        if not message_content:
            return []
            
        tool_calls = []
        
        # 尝试从JSON格式中提取工具调用（Cogito在format=json时可能会输出这种格式）
        try:
            # 查找可能的JSON工具调用格式
            json_matches = re.findall(r'\{"name":\s*"([^"]+)",\s*"arguments":\s*({[^}]*})\}', message_content)
            if json_matches:
                for idx, (tool_name, args_str) in enumerate(json_matches):
                    if tool_name in self.tool_names_dict:
                        args = {}
                        try:
                            args = json.loads(args_str)
                        except:
                            pass  # 如果解析失败，使用空字典
                            
                        tool_calls.append({
                            'id': f'json_call_{idx}',
                            'name': tool_name,
                            'args': args,
                            'type': 'tool_call'
                        })
                return tool_calls
        except:
            pass  # 如果解析失败，继续尝试正则表达式方法
            
        # 使用正则表达式匹配文本描述的工具调用
        matches = self.tool_pattern.findall(message_content)
        
        for idx, tool_name in enumerate(matches):
            if tool_name in self.tool_names_dict:
                tool_calls.append({
                    'id': f'text_call_{idx}',
                    'name': tool_name,
                    'args': {},
                    'type': 'tool_call'
                })
        
        return tool_calls
    
    def _generate(
        self, messages: List[BaseMessage], stop: List[str] = None, run_manager: CallbackManagerForLLMRun = None, **kwargs
    ) -> Dict[str, Any]:
        """处理生成回复"""
        original_response = self.llm._generate(messages, stop, run_manager, **kwargs)
        
        # 获取原始内容
        generation = original_response.generations[0]
        content = generation.text
        
        # 提取工具调用
        tool_calls = self._extract_tool_calls(content)
        
        # 如果找到工具调用，修改响应
        if tool_calls:
            # 设置AI消息的工具调用
            generation.message.tool_calls = tool_calls
            # 修改内容为空，让工具调用更明显
            generation.message.content = ""
            # 设置元数据
            generation.message.additional_kwargs['tool_calls'] = tool_calls
            return original_response
        
        return original_response
    
    async def _agenerate(
        self, messages: List[BaseMessage], stop: List[str] = None, run_manager: CallbackManagerForLLMRun = None, **kwargs
    ) -> Dict[str, Any]:
        """处理异步生成回复"""
        original_response = await self.llm._agenerate(messages, stop, run_manager, **kwargs)
        
        # 获取原始内容
        generation = original_response.generations[0]
        content = generation.text
        
        # 提取工具调用
        tool_calls = self._extract_tool_calls(content)
        
        # 如果找到工具调用，修改响应
        if tool_calls:
            # 设置AI消息的工具调用
            generation.message.tool_calls = tool_calls
            # 修改内容为空，让工具调用更明显
            generation.message.content = ""
            # 设置元数据
            generation.message.additional_kwargs['tool_calls'] = tool_calls
            return original_response
        
        return original_response
        
    def invoke(self, input, config=None, **kwargs):
        """调用模型并处理响应，将文本描述的工具调用转换为实际工具调用"""
        response = self.llm.invoke(input, config, **kwargs)
        
        # 检查是否已有工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            return response
            
        # 提取文本中描述的工具调用
        content = response.content if hasattr(response, 'content') else ""
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
    
    async def ainvoke(self, input, config=None, **kwargs):
        """异步调用模型并处理响应，将文本描述的工具调用转换为实际工具调用"""
        response = await self.llm.ainvoke(input, config, **kwargs)
        
        # 检查是否已有工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            return response
            
        # 提取文本中描述的工具调用
        content = response.content if hasattr(response, 'content') else ""
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