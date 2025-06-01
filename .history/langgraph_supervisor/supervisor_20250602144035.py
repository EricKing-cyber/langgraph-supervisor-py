#=============================
# description 
# 用于构建多代理系统中的主管代理（Supervisor），它负责协调多个子代理之间的任务分配和消息流转。
# 它是整个多代理系统的核心控制器。
#=============================
import inspect
from typing import Any, Callable, Literal, Optional, Sequence, Type, Union, cast, get_args
from uuid import UUID, uuid5

from langchain_core.language_models import BaseChatModel, LanguageModelLike
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt.chat_agent_executor import (
    AgentState,
    AgentStateWithStructuredResponse,
    Prompt,
    StateSchemaType,
    StructuredResponseSchema,
    _should_bind_tools,
    create_react_agent,
)
from langgraph.pregel import Pregel
from langgraph.pregel.remote import RemoteGraph
from langgraph.utils.config import patch_configurable
from langgraph.utils.runnable import RunnableCallable

from langgraph_supervisor.agent_name import AgentNameMode, with_agent_name
from langgraph_supervisor.handoff import (
    METADATA_KEY_HANDOFF_DESTINATION,
    _normalize_agent_name,
    create_handoff_back_messages,
    create_handoff_tool,
)
from langgraph_supervisor.wrapper import NamedStateGraph

OutputMode = Literal["full_history", "last_message"]
"""Mode for adding agent outputs to the message history in the multi-agent workflow

- `full_history`: add the entire agent message history
- `last_message`: add only the last message
"""


MODELS_NO_PARALLEL_TOOL_CALLS = {"o3-mini", "o3", "o4-mini"}


def _supports_disable_parallel_tool_calls(model: LanguageModelLike) -> bool:
    if not isinstance(model, BaseChatModel):
        return False

    if getattr(model, "model_name", None) in MODELS_NO_PARALLEL_TOOL_CALLS:
        return False

    if not hasattr(model, "bind_tools"):
        return False

    if "parallel_tool_calls" not in inspect.signature(model.bind_tools).parameters:
        return False

    return True


def _make_call_agent(
    agent: Pregel,
    output_mode: OutputMode,
    add_handoff_back_messages: bool,
    supervisor_name: str,
) -> Callable[[dict], dict] | RunnableCallable:
    if output_mode not in get_args(OutputMode):
        raise ValueError(
            f"Invalid agent output mode: {output_mode}. Needs to be one of {get_args(OutputMode)}"
        )

    def _process_output(output: dict) -> dict:
        messages = output["messages"]
        if output_mode == "full_history":
            pass
        elif output_mode == "last_message":
            messages = messages[-1:]

        else:
            raise ValueError(
                f"Invalid agent output mode: {output_mode}. "
                f"Needs to be one of {OutputMode.__args__}"
            )

        if add_handoff_back_messages:
            messages.extend(create_handoff_back_messages(agent.name, supervisor_name))

        return {
            **output,
            "messages": messages,
        }

    def call_agent(state: dict, config: RunnableConfig) -> dict:
        thread_id = config.get("configurable", {}).get("thread_id")
        output = agent.invoke(
            state,
            patch_configurable(
                config,
                {"thread_id": str(uuid5(UUID(str(thread_id)), agent.name)) if thread_id else None},
            )
            if isinstance(agent, RemoteGraph)
            else config,
        )
        return _process_output(output)

    async def acall_agent(state: dict, config: RunnableConfig) -> dict:
        thread_id = config.get("configurable", {}).get("thread_id")
        output = await agent.ainvoke(
            state,
            patch_configurable(
                config,
                {"thread_id": str(uuid5(UUID(str(thread_id)), agent.name)) if thread_id else None},
            )
            if isinstance(agent, RemoteGraph)
            else config,
        )
        return _process_output(output)

    return RunnableCallable(call_agent, acall_agent)


def _get_handoff_destinations(tools: Sequence[BaseTool | Callable]) -> list[str]:
    """Extract handoff destinations from provided tools.
    Args:
        tools: List of tools to inspect.
    Returns:
        List of agent names that are handoff destinations.
    """
    return [
        tool.metadata[METADATA_KEY_HANDOFF_DESTINATION]
        for tool in tools
        if isinstance(tool, BaseTool)
        and tool.metadata is not None
        and METADATA_KEY_HANDOFF_DESTINATION in tool.metadata
    ]


def _prepare_tool_node(
    tools: list[BaseTool | Callable] | ToolNode | None,
    handoff_tool_prefix: Optional[str],
    add_handoff_messages: bool,
    agent_names: set[str],
) -> ToolNode:
    """Prepare the ToolNode to use in supervisor agent."""
    if isinstance(tools, ToolNode):
        input_tool_node = tools
        tool_classes = list(tools.tools_by_name.values())
    elif tools:
        input_tool_node = ToolNode(tools)
        # get the tool functions wrapped in a tool class from the ToolNode
        tool_classes = list(input_tool_node.tools_by_name.values())
    else:
        input_tool_node = None
        tool_classes = []

    handoff_destinations = _get_handoff_destinations(tool_classes)
    if handoff_destinations:
        if missing_handoff_destinations := set(agent_names) - set(handoff_destinations):
            raise ValueError(
                "When providing custom handoff tools, you must provide them for all subagents. "
                f"Missing handoff tools for agents '{missing_handoff_destinations}'."
            )

        # Handoff tools should be already provided here
        tool_node = cast(ToolNode, input_tool_node)
    else:
        handoff_tools = [
            create_handoff_tool(
                agent_name=agent_name,
                name=(
                    None
                    if handoff_tool_prefix is None
                    else f"{handoff_tool_prefix}{_normalize_agent_name(agent_name)}"
                ),
                add_handoff_messages=add_handoff_messages,
            )
            for agent_name in agent_names
        ]
        all_tools = tool_classes + list(handoff_tools)

        # re-wrap the combined tools in a ToolNode
        # if the original input was a ToolNode, apply the same params
        if input_tool_node is not None:
            tool_node = ToolNode(
                all_tools,
                name=input_tool_node.name,
                tags=list(input_tool_node.tags) if input_tool_node.tags else None,
                handle_tool_errors=input_tool_node.handle_tool_errors,
                messages_key=input_tool_node.messages_key,
            )
        else:
            tool_node = ToolNode(all_tools)

    return tool_node


def create_supervisor(
    agents: list[Union[Pregel, NamedStateGraph]],
    *,
    model: LanguageModelLike,
    tools: list[BaseTool | Callable] | ToolNode | None = None,
    prompt: Prompt | None = None,
    response_format: Optional[
        Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]
    ] = None,
    parallel_tool_calls: bool = False,
    state_schema: StateSchemaType | None = None,
    config_schema: Type[Any] | None = None,
    output_mode: OutputMode = "last_message",
    add_handoff_messages: bool = True,
    handoff_tool_prefix: Optional[str] = None,
    add_handoff_back_messages: Optional[bool] = None,
    supervisor_name: str = "supervisor",
    include_agent_name: AgentNameMode | None = None,
) -> StateGraph:
    """Create a multi-agent supervisor.

    Args:
        agents: List of agents to manage.
            An agent can be a LangGraph [CompiledStateGraph](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.state.CompiledStateGraph),
            a functional API [workflow](https://langchain-ai.github.io/langgraph/reference/func/#langgraph.func.entrypoint),
            or any other [Pregel](https://langchain-ai.github.io/langgraph/reference/pregel/#langgraph.pregel.Pregel) object.
        model: Language model to use for the supervisor
        tools: Tools to use for the supervisor
        prompt: Optional prompt to use for the supervisor. Can be one of:

            - str: This is converted to a SystemMessage and added to the beginning of the list of messages in state["messages"].
            - SystemMessage: this is added to the beginning of the list of messages in state["messages"].
            - Callable: This function should take in full graph state and the output is then passed to the language model.
            - Runnable: This runnable should take in full graph state and the output is then passed to the language model.
        response_format: An optional schema for the final supervisor output.

            If provided, output will be formatted to match the given schema and returned in the 'structured_response' state key.
            If not provided, `structured_response` will not be present in the output state.
            Can be passed in as:

                - an OpenAI function/tool schema,
                - a JSON Schema,
                - a TypedDict class,
                - or a Pydantic class.
                - a tuple (prompt, schema), where schema is one of the above.
                    The prompt will be used together with the model that is being used to generate the structured response.

            !!! Important
                `response_format` requires the model to support `.with_structured_output`

            !!! Note
                `response_format` requires `structured_response` key in your state schema.
                You can use the prebuilt `langgraph.prebuilt.chat_agent_executor.AgentStateWithStructuredResponse`.
        parallel_tool_calls: Whether to allow the supervisor LLM to call tools in parallel (only OpenAI and Anthropic).
            Use this to control whether the supervisor can hand off to multiple agents at once.
            If True, will enable parallel tool calls.
            If False, will disable parallel tool calls (default).

            !!! Important
                This is currently supported only by OpenAI and Anthropic models.
                To control parallel tool calling for other providers, add explicit instructions for tool use to the system prompt.
        state_schema: State schema to use for the supervisor graph.
        config_schema: An optional schema for configuration.
            Use this to expose configurable parameters via `supervisor.config_specs`.
        output_mode: Mode for adding managed agents' outputs to the message history in the multi-agent workflow.
            Can be one of:

            - `full_history`: add the entire agent message history
            - `last_message`: add only the last message (default)
        add_handoff_messages: Whether to add a pair of (AIMessage, ToolMessage) to the message history
            when a handoff occurs.
        handoff_tool_prefix: Optional prefix for the handoff tools (e.g., "delegate_to_" or "transfer_to_")
            If provided, the handoff tools will be named `handoff_tool_prefix_agent_name`.
            If not provided, the handoff tools will be named `transfer_to_agent_name`.
        add_handoff_back_messages: Whether to add a pair of (AIMessage, ToolMessage) to the message history
            when returning control to the supervisor to indicate that a handoff has occurred.
        supervisor_name: Name of the supervisor node.
        include_agent_name: Use to specify how to expose the agent name to the underlying supervisor LLM.

            - None: Relies on the LLM provider using the name attribute on the AI message. Currently, only OpenAI supports this.
            - `"inline"`: Add the agent name directly into the content field of the AI message using XML-style tags.
                Example: `"How can I help you"` -> `"<name>agent_name</name><content>How can I help you?</content>"`

    Example:
        ```python
        from langchain_openai import ChatOpenAI

        from langgraph_supervisor import create_supervisor
        from langgraph.prebuilt import create_react_agent

        # Create specialized agents

        def add(a: float, b: float) -> float:
            '''Add two numbers.'''
            return a + b

        def web_search(query: str) -> str:
            '''Search the web for information.'''
            return 'Here are the headcounts for each of the FAANG companies in 2024...'

        math_agent = create_react_agent(
            model="openai:gpt-4o",
            tools=[add],
            name="math_expert",
        )

        research_agent = create_react_agent(
            model="openai:gpt-4o",
            tools=[web_search],
            name="research_expert",
        )

        # Create supervisor workflow
        workflow = create_supervisor(
            [research_agent, math_agent],
            model=ChatOpenAI(model="gpt-4o"),
        )

        # Compile and run
        app = workflow.compile()
        result = app.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": "what's the combined headcount of the FAANG companies in 2024?"
                }
            ]
        })
        ```
    """
    if add_handoff_back_messages is None:
        add_handoff_back_messages = add_handoff_messages

    if state_schema is None:
        state_schema = (
            AgentStateWithStructuredResponse if response_format is not None else AgentState
        )

    agent_names = set()
    for agent in agents:
        if agent.name is None or agent.name == "LangGraph":
            raise ValueError(
                "Please specify a name when you create your agent, either via `create_react_agent(..., name=agent_name)` "
                "or via `graph.compile(name=name)`."
            )

        if agent.name in agent_names:
            raise ValueError(
                f"Agent with name '{agent.name}' already exists. Agent names must be unique."
            )

        agent_names.add(agent.name)

    tool_node = _prepare_tool_node(
        tools,
        handoff_tool_prefix,
        add_handoff_messages,
        agent_names,
    )
    all_tools = list(tool_node.tools_by_name.values())

    if _should_bind_tools(model, all_tools):
        if _supports_disable_parallel_tool_calls(model):
            model = cast(BaseChatModel, model).bind_tools(
                all_tools, parallel_tool_calls=parallel_tool_calls
            )
        else:
            model = cast(BaseChatModel, model).bind_tools(all_tools)

    if include_agent_name:
        model = with_agent_name(model, include_agent_name)

    supervisor_agent = create_react_agent(
        name=supervisor_name,
        model=model,
        tools=tool_node,
        prompt=prompt,
        state_schema=state_schema,
        response_format=response_format,
    )

    builder = StateGraph(state_schema, config_schema=config_schema)
    builder.add_node(supervisor_agent, destinations=tuple(agent_names) + (END,))
    builder.add_edge(START, supervisor_agent.name)
    for agent in agents:
        builder.add_node(
            agent.name,
            _make_call_agent(
                agent,
                output_mode,
                add_handoff_back_messages=add_handoff_back_messages,
                supervisor_name=supervisor_name,
            ),
        )
        builder.add_edge(agent.name, supervisor_agent.name)

    return builder


def create_top_level_supervisor(
    middle_supervisors: list[NamedStateGraph],
    model: LanguageModelLike,
    prompt: Optional[Prompt] = None,
    tools: list[BaseTool | Callable] | ToolNode | None = None,
    response_format: Optional[Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]] = None,
    parallel_tool_calls: bool = False,
    state_schema: StateSchemaType | None = None,
    config_schema: Type[Any] | None = None,
    output_mode: OutputMode = "last_message",
    add_handoff_messages: bool = True,
    handoff_tool_prefix: Optional[str] = None,
    supervisor_name: str = "top_supervisor",
    include_agent_name: AgentNameMode | None = None,
) -> StateGraph:
    """创建多层级监督者系统

    Args:
        middle_supervisors: 中间层监督者列表
        model: 语言模型
        prompt: 系统提示词
        tools: 工具列表
        response_format: 响应格式
        parallel_tool_calls: 是否允许并行工具调用
        state_schema: 状态模型
        config_schema: 配置模型
        output_mode: 输出模式
        add_handoff_messages: 是否添加交接消息
        handoff_tool_prefix: 交接工具前缀
        supervisor_name: 顶层监督者名称
        include_agent_name: 是否包含代理名称

    Returns:
        StateGraph: 构建好的状态图
    """
    if not middle_supervisors:
        raise ValueError("必须提供至少一个中间层监督者")

    agent_names = {sv.name for sv in middle_supervisors}
    if len(agent_names) != len(middle_supervisors):
        raise ValueError("中间层监督者名称必须唯一")

    # 创建基础监督者
    base_supervisor = create_supervisor(
        agents=middle_supervisors,  # 这里传入的是 NamedStateGraph 列表
        model=model,
        tools=tools,
        prompt=prompt,
        response_format=response_format,
        parallel_tool_calls=parallel_tool_calls,
        state_schema=state_schema,
        config_schema=config_schema,
        output_mode=output_mode,
        add_handoff_messages=add_handoff_messages,
        handoff_tool_prefix=handoff_tool_prefix,
        supervisor_name=supervisor_name,
        include_agent_name=include_agent_name
    )

    builder = StateGraph(base_supervisor.schema)

    # 添加中间层监督者节点
    for sv in middle_supervisors:
        builder.add_node(sv.name, sv.graph)  # 使用包装器中的 graph 实例

    # 添加基础监督者节点
    builder.add_node("supervisor", base_supervisor.compile())

    # 添加边
    builder.add_edge("__start__", "supervisor")
    builder.add_edge("supervisor", "__end__")

    return builder
