import os
os.chdir('/Volumes/MacPro/SaleAgents/backend-v2')

import sqlite3
from openai import OpenAI

# Read config from DB
conn = sqlite3.connect('sale_agents_v2.db')
cursor = conn.cursor()
cursor.execute("SELECT provider, model, base_url, api_key FROM ai_configs WHERE is_active=1")
row = cursor.fetchone()
conn.close()

if not row:
    print("ERROR: No active LLM config found")
    exit(1)

provider, model, base_url, api_key = row
print(f"Config: provider={provider}, model={model}, base_url={base_url}")
print(f"API key prefix: {api_key[:15]}...")

client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0)

# Test 1: Simple ping
print("\n--- Test 1: Simple completion (small text) ---")
try:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Say hello in one word."}],
        max_tokens=10,
    )
    print(f"SUCCESS: {resp.choices[0].message.content}")
    print(f"Model used: {resp.model}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")

# Test 2: Medium text (~5000 chars)  
print("\n--- Test 2: Medium text (~5000 chars) ---")
try:
    text = "请提取以下招标信息中的项目名称。\n" * 500
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": text[:5000]}],
        max_tokens=50,
    )
    print(f"SUCCESS: response length={len(resp.choices[0].message.content)}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")

# Test 3: Large text (~28000 chars, similar to actual)
print("\n--- Test 3: Large text (~28000 chars) ---")
try:
    text = "请提取以下招标信息中的关键字段。\n" * 2000
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": text[:28000]}],
        max_tokens=100,
    )
    print(f"SUCCESS: response length={len(resp.choices[0].message.content)}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")

print("\n--- Done ---")
