from langgraph_app import app
from langchain_core.messages import HumanMessage

# 测试深度研究功能
result = app.invoke({"messages": [HumanMessage(content="请深入调研量子计算技术的最新进展及其在密码学中的应用前景。")]})

# 打印结果
print("===== 消息内容 =====")
for message in result["messages"]:
    print(f"角色: {message.type}")
    print(f"名称: {getattr(message, 'name', 'N/A')}")
    print(f"内容: {message.content}")
    print(f"工具调用: {getattr(message, 'tool_calls', [])}")
    print("-" * 50) 