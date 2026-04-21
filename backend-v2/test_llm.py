import sys
import os
sys.path.append("/Volumes/MacPro/SaleAgents/backend")
from app.services.llm_parsing_client import llm_parsing_client

text = "测试文本"
print("Client:", llm_parsing_client.client)
print("Key:", repr(llm_parsing_client.api_key)[:10])
print("Model:", llm_parsing_client.model_name)
try:
    res = llm_parsing_client.extract_tender_fields(text)
    print("Result:", res)
except Exception as e:
    print("Error:", e)
