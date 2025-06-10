from langchain_openai import ChatOpenAI
from pydantic import SecretStr, Field
from multi_agent_system.model_config import ModelConfig
from langchain_core.language_models import BaseChatModel, LanguageModelLike
from langchain_core.tools import BaseTool
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models.ollama import ChatOllama
from langchain_groq import ChatGroq
from typing import List, Dict, Any, Optional, Union, Callable
import re
import os
from langchain_core.messages import BaseMessage
from langchain_core.callbacks import CallbackManagerForLLMRun
import json

# 全局模型缓存，避免重复创建相同模型
_MODEL_CACHE = {}

def create_model(model_name: str = None, **kwargs) -> LanguageModelLike:
    """
    根据模型名称创建模型实例
    
    Args:
        model_name: 模型名称，格式为 "提供商:模型名称"，如 "openai:gpt-4"
        **kwargs: 传递给模型构造函数的其他参数
    
    Returns:
        创建的模型实例
    """
    # 使用默认模型
    if model_name is None or model_name == "default_model":
        # 环境变量中有默认模型则使用环境变量
        env_model = os.environ.get("DEFAULT_MODEL")
        if env_model:
            model_name = env_model
        else:
            # 默认使用 OpenAI 的 gpt-3.5-turbo
            model_name = "openai:gpt-3.5-turbo"
    
    # 构建缓存键 - 包含模型名称和所有关键参数
    cache_key = model_name
    for k, v in sorted(kwargs.items()):
        cache_key += f"_{k}:{v}"
        
    # 检查模型是否已存在于缓存中
    if cache_key in _MODEL_CACHE:
        print(f"使用缓存的模型实例: {cache_key}")
        return _MODEL_CACHE[cache_key]
    
    # 解析模型提供商和模型名称
    parts = model_name.split(":", 1)
    if len(parts) == 2:
        provider, model = parts
    else:
        # 如果没有提供商前缀，默认为 OpenAI
        provider = "openai"
        model = model_name
    
    # 根据提供商创建对应的模型
    try:
        if provider.lower() == "openai":
            model_instance = ChatOpenAI(model=model, **kwargs)
        elif provider.lower() == "anthropic":
            model_instance = ChatAnthropic(model=model, **kwargs)
        elif provider.lower() == "groq":
            model_instance = ChatGroq(model=model, **kwargs)
        elif provider.lower() in ["qwen", "qwen3"]:
            # 使用Ollama的Qwen模型
            from langchain_community.chat_models import ChatOllama
            # 为Ollama模型添加默认参数，减少并发负载
            ollama_kwargs = {
                "num_ctx": 4096,  # 减小上下文窗口
                "timeout": 120,   # 增加超时时间
                "temperature": 0.7,
            }
            # 用户提供的参数会覆盖默认参数
            ollama_kwargs.update(kwargs)
            model_instance = ChatOllama(model=model, **ollama_kwargs)
        else:
            # 不支持的提供商，尝试使用OpenAI
            print(f"不支持的模型提供商: {provider}，使用OpenAI作为备选")
            model_instance = ChatOpenAI(model="gpt-3.5-turbo", **kwargs)
    except Exception as e:
        # 如果模型创建失败，回退到Tavily的T5模型
        print(f"模型 {model_name} 创建失败: {str(e)}，使用OpenAI作为备选")
        model_instance = ChatOpenAI(model="gpt-3.5-turbo", **kwargs)
    
    # 将模型实例保存到缓存
    _MODEL_CACHE[cache_key] = model_instance
    return model_instance

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