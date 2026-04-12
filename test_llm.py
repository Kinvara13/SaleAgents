import sys
import os
sys.path.append("/Volumes/MacPro/SaleAgents/backend")
from app.services.llm_parsing_client import llm_parsing_client

text = "测试文本"
try:
    res = llm_parsing_client.extract_tender_fields(text)
    print("Result:", res)
except Exception as e:
    print("Error:", e)
