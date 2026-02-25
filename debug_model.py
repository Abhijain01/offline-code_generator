from engine import CodeGenerator
import os
import glob
import time

def get_model_path():
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    files = glob.glob(os.path.join(models_dir, "*.gguf"))
    if files:
        return files[0]
    return None

def main():
    print("Finding model...")
    model_path = get_model_path()
    if not model_path:
        print("No model found!")
        return

    print(f"Loading model from {model_path}...")
    try:
        generator = CodeGenerator(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    prompt = "Write a python function to add two numbers."
    print(f"Generating for prompt: {prompt}")
    
    start_time = time.time()
    try:
        stream = generator.generate_response(prompt, stream=True)
        count = 0
        print("--- Start Output ---")
        for chunk in stream:
            print(f"Chunk: '{chunk}'")
            count += 1
        print("--- End Output ---")
        print(f"Total chunks: {count}")
    except Exception as e:
        print(f"Error generating: {e}")
    
    print(f"Time taken: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    main()
