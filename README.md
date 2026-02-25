# 💻 Offline Code Generator

An incredibly fast, completely offline, and private AI code generator built with Python and Streamlit. It uses local LLMs (like CodeLlama 7B) and executes directly on your hardware without needing an internet connection.

🚀 **Special Feature**: This project is optimized to run on **AMD Radeon GPUs** (via Vulkan support) using a standalone hyper-optimized `llama.cpp` backend, bypassing Python compilation errors entirely!

---

## ⚡ Features
- **100% Offline & Private:** Your code never leaves your computer.
- **AMD GPU Acceleration:** Automatically downloads and utilizes the official `llama.cpp` Vulkan backend for lightning-fast token generation on AMD hardware.
- **Premium UI:** A beautiful, dark-themed Streamlit interface resembling modern AI chatbots.
- **Streaming Generation:** Watch the code generate word-by-word in real time.
- **Automatic Fallback:** Gracefully falls back to CPU inference if a GPU backend isn't available.

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/Abhijain01/offline-code_generator.git
cd offline-code_generator
```

2. **Install Python Dependencies**
Ensure you have Python 3.9+ installed, then run:
```bash
pip install -r requirements.txt
# Alternatively, manually install: pip install flask streamlit
```

3. **Download the AI Model**
Run the built-in downloader script to fetch the `CodeLlama-7B-Instruct` model in GGUF format (~4GB):
```bash
python model_downloader.py
```
*(The model will be saved to the `models/` directory)*

4. **Install the High-Performance Backend (For AMD / Windows Users)**
Run this script to automatically download the pre-compiled `llama.cpp` Vulkan executable. This is necessary to unlock massive speedups on AMD GPUs without struggling with C++ build tools.
```bash
python download_backend.py
```

## 🎮 Usage

Start the Streamlit application:
```bash
streamlit run streamlit_app.py
```
> The web interface will automatically open in your browser (usually at `http://localhost:8501`).

When you submit a prompt, the application will transparently spin up the high-performance local AI server, load the model into VRAM, and stream the generated code back to the UI!

## 📁 Project Structure
- `streamlit_app.py` - The main beautiful Streamlit user interface.
- `engine.py` - The core logic that bridges the UI to the local AI backend via HTTP streaming.
- `download_backend.py` - Script to install the standalone Vulkan AI executable.
- `model_downloader.py` - Script to fetch the 7 Billion parameter CodeLlama model. 
- `main.py` & `app.py` - Alternative lightweight CLI and Flask interfaces.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Abhijain01/offline-code_generator/issues).
