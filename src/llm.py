import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()


# 替换原来的ChatNVIDIA为ChatOpenAI
r1 = ChatOpenAI(
    model=os.getenv("MODEL_NAME"), # 你可以根据需要选择合适的模型，如gpt-4o、gpt-4-turbo、gpt-3.5-turbo等
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"), 
    temperature=0.6,
    top_p=0.7,
    max_tokens=4096
)