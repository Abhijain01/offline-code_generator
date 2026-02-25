import urllib.request
import json
import sys

print("Testing ngrok API check...")
try:
    with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels") as response:
        content = response.read().decode()
        print(f"Raw response: {content[:200]}...")
        data = json.loads(content)
        tunnels = data.get('tunnels', [])
        print(f"Found {len(tunnels)} tunnels")
        for tunnel in tunnels:
            print(f"Tunnel: {tunnel.get('public_url')}")
except Exception as e:
    print(f"Error: {e}")
