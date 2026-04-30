import os
os.chdir('/Volumes/MacPro/SaleAgents/backend-v2')
from openai import OpenAI

client = OpenAI(
    api_key='sk-kimi-L8j73bgDWMYUtdWOUzh8KqidiEM8iY4oXiLOewUvvUu95jx2Q6HvEbe9Aaf782l1',
    base_url='https://api.kimi.com/coding/v1',
    timeout=30.0,
)

for model in ['kimi-k2.6', 'kimi-k2', 'kimi-moonshot-v1-8k']:
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10,
        )
        print(f"{model}: OK - {resp.choices[0].message.content}")
    except Exception as e:
        err = str(e)
        print(f"{model}: FAILED - {err[:120]}")
