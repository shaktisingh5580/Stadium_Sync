import os
import sys
from dotenv import load_dotenv

# Load the keys from .env
load_dotenv()

# Extract the keys from the GEMINI_API_KEY environment variable (since they are comma separated)
keys_str = os.getenv("GEMINI_API_KEY", "")
if not keys_str:
    keys_str = os.getenv("GEMINI_API_KEYS", "")

keys = [k.strip() for k in keys_str.split(",") if k.strip()]

nvidia_key = None
for k in keys:
    if k.startswith("nvapi-"):
        nvidia_key = k
        break

if not nvidia_key:
    print("X Could not find an NVIDIA key (starts with 'nvapi-') in your .env file!")
    sys.exit(1)

print(f"OK Found NVIDIA key starting with: {nvidia_key[:10]}...")

try:
    from openai import OpenAI
    
    print("Connecting to NVIDIA API via OpenAI client...")
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=nvidia_key
    )

    print("Sending test prompt to meta/llama-3.1-70b-instruct...")
    completion = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": "Write a haiku about a stadium."}],
        temperature=0.2,
        max_tokens=64,
    )

    print("\nSUCCESS! NVIDIA API is working. Here is the response:")
    print("-" * 40)
    print(completion.choices[0].message.content.strip())
    print("-" * 40)

except Exception as e:
    print("\nError connecting to NVIDIA API:")
    print(e)
