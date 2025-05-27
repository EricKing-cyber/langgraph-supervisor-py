# main.py
from multi_agent_system.model_utils import create_model

def main():
    try:
        model=create_model()
        print(model,"model created successfully")
    except:
        print(Exception)

    

if __name__=="__main__":
    main()