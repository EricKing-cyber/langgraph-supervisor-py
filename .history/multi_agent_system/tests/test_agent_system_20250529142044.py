import os
# 创建 tests/test_agent_system.py
tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
os.makedirs(tests_dir, exist_ok=True)

test_content = '''def run_tests(app):
    """运行代理系统测试用例"""
    try:
        # 测试数学问题
        math_result = app.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": "请计算 5 和 3 的和"
                }
            ]
        })
        print("数学问题结果:", math_result)

        # 测试天气问题
        weather_result = app.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": "北京今天的天气怎么样？"
                }
            ]
        })
        print("天气问题结果:", weather_result)
    except Exception as e:
        print(f"发生错误: {e}")
        print("请确保：")
        print("1. Ollama服务已启动")
        print("2. 已下载所需的模型（例如：ollama pull llama2）")
        print("3. 环境变量配置正确")
'''

with open(os.path.join(tests_dir, 'test_agent_system.py'), 'w', encoding='utf-8') as f:
    f.write(test_content)