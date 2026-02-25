import os
import sys
from engine import CodeGenerator
import glob

def get_model_path():
    # Look for any .gguf file in the models directory
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    if not os.path.exists(models_dir):
        return None
    
    files = glob.glob(os.path.join(models_dir, "*.gguf"))
    if files:
        return files[0] # Return the first one found
    return None

def main():
    print("--- Offline Code Generator ---")
    model_path = get_model_path()
    
    if not model_path:
        print("Error: No model file found in 'models' directory.")
        print("Please run 'python model_downloader.py' first.")
        return

    generator = CodeGenerator(model_path)
    
    print("\nReady! Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ('exit', 'quit'):
                break
            
            print("\nGenerating...", end="", flush=True)
            
            # Stream the response
            stream = generator.generate_response(user_input)
            
            # Helper to clear "Generating..."
            print("\r", end="")
            
            full_response = ""
            for chunk in stream:
                # Clean up potential tokenizer artifacts
                text_chunk = chunk.replace('Ġ', ' ').replace('Ċ', '\n').replace('<|im_end|>', '')
                print(text_chunk, end="", flush=True)
                full_response += text_chunk
            
            print() # Newline at end
            
        except KeyboardInterrupt:
            print("\nType 'exit' to quit.")
            continue
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
