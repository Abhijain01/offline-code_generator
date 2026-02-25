from engine import CodeGenerator
import sys

print("Loading model...")
gen = CodeGenerator("models/codellama-7b-instruct.Q4_K_M.gguf")

print("Generating response...")
try:
    stream = gen.generate_response("Write a python loop from 1 to 5")
    for chunk in stream:
        print(chunk, end="", flush=True)
    print("\nDone")
except Exception as e:
    print(f"FAILED: {e}")
