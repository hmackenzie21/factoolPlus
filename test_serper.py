import requests

headers = {
    "X-API-KEY": "b24f68912342a989146281e1c0327a25cc6a8030"  # <- MUST be X-API-KEY
}
params = {
    "q": "OpenAI"
}

response = requests.post("https://google.serper.dev/search", headers=headers, json=params)
print("Status:", response.status_code)
print("Response:", response.text)
