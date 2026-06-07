import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model":"qwen3:8b",
        "prompt":"Hello",
        "stream":False
    },
    timeout=300
)

print(response.json())