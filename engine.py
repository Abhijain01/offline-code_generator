import os
import sys
import subprocess
import urllib.request
import json
import time
import atexit

class CodeGenerator:
    def __init__(self, model_path, api_key=None):
        self.mode = "local"
        self.port = 8080
        self.api_key = api_key
        
        backend_dir = os.path.join(os.path.dirname(__file__), 'llama_backend')
        server_exe = os.path.join(backend_dir, 'llama-server.exe')
        
        # Determine if we can run locally
        if os.path.exists(model_path) and os.path.exists(server_exe):
            print(f"Loading local model from {model_path}...")
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
            print("Local model loaded successfully!")
            
        else:
            self.mode = "cloud"
            print("Local model or backend not found. Falling back to Cloud Mode (Gemini).")
            # We don't initialize the Gemini client here because the API key
            # might be provided dynamically per-request from the Streamlit UI.

    def generate_response(self, prompt, stream=True, api_key=None):
        if self.mode == "cloud":
            # Use dynamically passed key, or the one from initialization
            active_key = api_key or self.api_key or os.environ.get("GEMINI_API_KEY")
            
            if not active_key:
                yield "Error: No Gemini API Key provided. Please enter one in the sidebar to use Cloud Mode."
                return
                
            try:
                from google import genai
                client = genai.Client(api_key=active_key)
                system_instruction = "You are an expert coding assistant. Respond only with the requested code and minimal, concise explanations."
                
                if stream:
                    response_stream = client.models.generate_content_stream(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=genai.types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.3
                        )
                    )
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                else:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=genai.types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.3
                        )
                    )
                    return response.text
            except ImportError:
                yield "Error: google-genai library is not installed."
                return
            except Exception as e:
                yield f"Cloud API Error: {str(e)}"
                return

        elif self.mode == "local":
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
                                        yield data.get('content', '')
                                    except json.JSONDecodeError:
                                        pass
                    else:
                        result = json.loads(response.read().decode('utf-8'))
                        return result.get('content', '')
            except Exception as e:
                yield f"\n[Error connecting to local backend: {e}]"
