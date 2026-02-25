import os
import sys
import subprocess
import urllib.request
import json
import time
import atexit

class CodeGenerator:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please run model_downloader.py first.")
        
        print(f"Loading model from {model_path}...")
        self.port = 8080
        backend_dir = os.path.join(os.path.dirname(__file__), 'llama_backend')
        server_exe = os.path.join(backend_dir, 'llama-server.exe')
        
        if os.path.exists(server_exe):
            print("Using dedicated local AMD Vulkan server backend!")
            # Start the server as a background process
            self.process = subprocess.Popen(
                [server_exe, "-m", model_path, "-c", "4096", "--host", "127.0.0.1", "--port", str(self.port)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            atexit.register(self.process.kill)
            
            # Wait for server to be ready
            print("Waiting for AMD GPU Server to spin up... (this takes ~10 seconds)")
            ready = False
            for _ in range(30):
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=1)
                    ready = True
                    break
                except:
                    time.sleep(1)
                    
            if not ready:
                print("Warning: GPU Server taking too long to start, but will keep trying.")
        else:
            raise FileNotFoundError("Could not find llama_backend/llama-server.exe. Please download it first.")
            
        print("Model loaded successfully!")

    def generate_response(self, prompt, stream=True):
        formatted_prompt = f"[INST] Write code to solve the following problem:\n{prompt}\n[/INST]\n"
        
        req_data = {
            "prompt": formatted_prompt,
            "n_predict": 1024,
            "temperature": 0.3,
            "top_k": 40,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "stream": stream
        }
        
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/completion", 
            data=json.dumps(req_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                if stream:
                    for line in response:
                        if line:
                            decoded_line = line.decode('utf-8').strip()
                            if decoded_line.startswith('data: '):
                                json_str = decoded_line[6:]
                                try:
                                    data = json.loads(json_str)
                                    # Output stream chunk
                                    yield data.get('content', '')
                                except json.JSONDecodeError:
                                    pass
                else:
                    result = json.loads(response.read().decode('utf-8'))
                    return result.get('content', '')
        except Exception as e:
            yield f"\n[Error connecting to backend: {e}]"
