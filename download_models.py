import os
import urllib.request
import tarfile
import tempfile

MODEL_DIR = "./sherpa-onnx-zh-en-model"
MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zh-en-2023-12-06.tar.bz2"
REQUIRED_FILES = [
    "tokens.txt",
    "encoder-epoch-99-avg-1.onnx",
    "decoder-epoch-99-avg-1.onnx",
    "joiner-epoch-99-avg-1.onnx"
]


def check_models_exist():
    """检查模型文件是否都存在"""
    if not os.path.isdir(MODEL_DIR):
        return False
    for f in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(MODEL_DIR, f)):
            return False
    return True


def download_and_extract_models():
    """下载并解压模型文件"""
    if check_models_exist():
        print("模型文件已存在，跳过下载")
        return True

    print("开始下载模型文件...")
    
    # 创建目录
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 下载到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.bz2") as tmp_file:
        temp_path = tmp_file.name
    
    try:
        print(f"正在从 {MODEL_URL} 下载...")
        urllib.request.urlretrieve(MODEL_URL, temp_path)
        
        print("下载完成，正在解压...")
        with tarfile.open(temp_path, "r:bz2") as tar:
            # 只提取需要的文件
            for member in tar.getmembers():
                if member.isfile() and member.name.split("/")[-1] in REQUIRED_FILES:
                    # 提取到正确的目录
                    member.name = os.path.basename(member.name)
                    tar.extract(member, path=MODEL_DIR)
        
        print("模型文件解压完成！")
        return True
        
    except Exception as e:
        print(f"下载模型失败: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


if __name__ == "__main__":
    download_and_extract_models()
