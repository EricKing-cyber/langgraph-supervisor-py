import os

def run_tests(app):
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
