import os
from huggingface_hub import hf_hub_download

def download_model():
    repo_id = "TheBloke/CodeLlama-7B-Instruct-GGUF"
    filename = "codellama-7b-instruct.Q4_K_M.gguf"
    
    print(f"Downloading {filename} from {repo_id}...")
    print("This may take a while depending on your internet connection (approx 1.5 - 2 GB).")
    
    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)
    
    try:
        model_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir="models",
            local_dir_use_symlinks=False
        )
        print(f"\nSuccess! Model saved to: {model_path}")
        return model_path
    except Exception as e:
        print(f"\nError downloading model: {e}")
        return None

if __name__ == "__main__":
    download_model()
