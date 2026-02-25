from flask import Flask, render_template, request, Response, stream_with_context
from engine import CodeGenerator
import os
import glob
import sys

# Initialize Flask app
app = Flask(__name__)

# Initialize Generator Global Variable
generator = None

def load_generator():
    global generator
    # Look for model
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    files = glob.glob(os.path.join(models_dir, "*.gguf"))
    
    if not files:
        print("No model found! Please run model_downloader.py")
        sys.exit(1)
        
    model_path = files[0] 
    print(f"Initializing engine with {model_path}...")
    generator = CodeGenerator(model_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        print("Received empty prompt")
        return Response("No prompt provided", status=400)
    
    print(f"Received prompt: {prompt}")

    def generate_stream():
        try:
            # Stream the response from the engine
            if generator is None:
                yield "Error: Generator not initialized"
                return

            print("Starting generation...")
            stream = generator.generate_response(prompt)
            for chunk in stream:
                # Clean artifacts just in case
                clean_chunk = chunk.replace('Ġ', ' ').replace('Ċ', '\n').replace('<|im_end|>', '')
                print(f"Yielding chunk: {clean_chunk!r}")
                yield clean_chunk
            print("Generation finished.")
        except Exception as e: 
            print(f"Error during generation: {e}")
            yield f"\n[Error: {str(e)}]"

    return Response(stream_with_context(generate_stream()), mimetype='text/plain')

if __name__ == '__main__':
    # Attempt to print Ngrok URL first
    try:
        print(" * Checking for ngrok tunnel...")
        sys.stdout.flush()
        import urllib.request
        import json
        with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels") as response:
            data = json.loads(response.read().decode())
            for tunnel in data.get('tunnels', []):
                if tunnel.get('proto') == 'https':
                    print(f" * Public URL: {tunnel['public_url']}")
                    sys.stdout.flush()
                    break
    except Exception as e:
        print(f" * Could not fetch ngrok URL: {e}")
        print(" * Ensure ngrok is running (http://127.0.0.1:4040)")
        sys.stdout.flush()

    load_generator()
    print("Starting Web Server at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
