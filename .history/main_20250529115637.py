# main.py
from multi_agent_system.model_utils import create_model

def main():
    """主函数，用于演示模型创建流程"""
    try:
        model = create_model()
        print("✅ 模型已成功创建！")
        # 可以在这里添加更多测试代码
    except Exception as e:
        print(f"❌ 创建模型时出错：{e}")

if __name__ == "__main__":
    main()