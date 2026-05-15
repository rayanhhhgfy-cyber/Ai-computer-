import os
import requests
import sys

def download_model(url, save_path):
    if os.path.exists(save_path):
        print(f"Model already exists at {save_path}")
        return True

    print(f"Downloading model from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
        return True
    except Exception as e:
        print(f"Error downloading model: {e}")
        return False

def get_best_model_for_specs():
    """
    Logic to select the best model based on 8GB RAM.
    Returns (llm_url, vision_url)
    """
    # Optimized GGUF for 8GB RAM (Phi-3 Mini)
    llm_url = "https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct-Q4_K_M.gguf"
    # Valid Community Moondream2 GGUF
    vision_url = "https://huggingface.co/bartowski/moondream2-GGUF/resolve/main/moondream2-q4_k_m.gguf"
    return llm_url, vision_url

if __name__ == "__main__":
    llm, vision = get_best_model_for_specs()
    os.makedirs("data/models", exist_ok=True)
    download_model(llm, "data/models/phi3.gguf")
    download_model(vision, "data/models/moondream.gguf")
