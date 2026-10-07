import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["PORTKEY_API_KEY"], base_url="https://api.portkey.ai/v1")
response = client.chat.completions.create(
    model="gpt-6-luna",
    messages=[{"role": "user", "content": "Reply with exactly: Luna connectivity verified."}],
)
print(response.choices[0].message.content)
