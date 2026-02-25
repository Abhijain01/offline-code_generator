import urllib.request
import zipfile
import io
import os

def download_llama_server():
    download_url = "https://github.com/ggerganov/llama.cpp/releases/download/b4855/llama-b4855-bin-win-vulkan-x64.zip"
    print(f"Downloading Vulkan backend from: {download_url}")
    print("This is a ~60MB download...")
    
    try:
        req = urllib.request.Request(download_url)
        req.add_header('User-Agent', 'Python script')
        with urllib.request.urlopen(req) as response:
            zip_data = response.read()
            
        print("Extracting llama-server.exe and DLLs...")
        out_dir = os.path.join(os.path.dirname(__file__), 'llama_backend')
        os.makedirs(out_dir, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            for file_info in z.infolist():
                if file_info.filename.endswith('.exe') or file_info.filename.endswith('.dll'):
                    file_info.filename = os.path.basename(file_info.filename)
                    z.extract(file_info, out_dir)
        
        print("Successfully installed offline Vulkan backend!")
        return True
    except Exception as e:
        print(f"Download or extraction failed: {e}")
        return False

if __name__ == '__main__':
    download_llama_server()
