import requests
import json
import sys

url = "http://127.0.0.1:5001/generate"
payload = {"prompt": "def add(a, b):"}

print(f"Sending request to {url}...")
try:
    with requests.post(url, json=payload, stream=True) as r:
        print(f"Status Code: {r.status_code}")
        if r.status_code != 200:
            print(r.text)
            sys.exit(1)
            
        print("--- Start Stream ---")
        for chunk in r.iter_content(chunk_size=None):
            if chunk:
                print(chunk.decode('utf-8'), end='', flush=True)
        print("\n--- End Stream ---")
except Exception as e:
    print(f"Error: {e}")
