import os
import urllib.request
import tarfile
import tempfile
import shutil

# 可能的模型目录
MODEL_DIR = "./sherpa-onnx-zh-en-model"
ALTERNATIVE_MODEL_DIRS = [
    "./sherpa-onnx-zh-en-model",
    "./sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20"
]
# 正确的下载 URL
MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2"
REQUIRED_FILES = [
    "tokens.txt",
    "encoder-epoch-99-avg-1.onnx",
    "decoder-epoch-99-avg-1.onnx",
    "joiner-epoch-99-avg-1.onnx"
]


def find_model_dir():
    """查找包含所需模型文件的目录"""
    for dir_path in ALTERNATIVE_MODEL_DIRS:
        if os.path.isdir(dir_path):
            # 检查目录中是否有需要的文件
            has_all = True
            for f in REQUIRED_FILES:
                if not os.path.isfile(os.path.join(dir_path, f)):
                    has_all = False
                    break
            if has_all:
                print(f"✅ 找到模型目录: {dir_path}")
                return dir_path
    return None


def check_models_exist(dir_path=None):
    """检查模型文件是否都存在"""
    if dir_path is None:
        dir_path = find_model_dir()
        if dir_path is None:
            print("未找到模型目录")
            return False
    
    print(f"检查模型目录: {dir_path}")
    print(f"目录内容: {os.listdir(dir_path)}")
    
    missing = []
    for f in REQUIRED_FILES:
        filepath = os.path.join(dir_path, f)
        if not os.path.exists(filepath):
            missing.append(f)
        else:
            print(f"  ✓ 找到文件: {f} ({os.path.getsize(filepath) / 1024 / 1024:.1f}MB)")
    
    if missing:
        print(f"  ✗ 缺失文件: {missing}")
        return False
    return True


def download_and_extract_models():
    """下载并解压模型文件"""
    # 首先检查是否已经有模型
    if check_models_exist():
        print("✅ 模型文件已存在，跳过下载")
        return True

    print("开始下载模型文件...")
    
    # 清空并创建目录
    if os.path.exists(MODEL_DIR):
        shutil.rmtree(MODEL_DIR)
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    try:
        # 下载文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.bz2") as tmp_file:
            temp_path = tmp_file.name
        
        print(f"正在从 {MODEL_URL} 下载...")
        urllib.request.urlretrieve(MODEL_URL, temp_path)
        print(f"下载完成！文件大小: {os.path.getsize(temp_path) / 1024 / 1024:.1f}MB")
        
        # 解压到临时目录
        with tempfile.TemporaryDirectory() as temp_extract_dir:
            print(f"正在解压到临时目录: {temp_extract_dir}")
            with tarfile.open(temp_path, "r:bz2") as tar:
                tar.extractall(path=temp_extract_dir)
            
            # 递归查找需要的文件
            print(f"临时目录内容: {os.listdir(temp_extract_dir)}")
            for root, dirs, files in os.walk(temp_extract_dir):
                print(f"检查目录: {root}")
                for filename in files:
                    if filename in REQUIRED_FILES:
                        src = os.path.join(root, filename)
                        dst = os.path.join(MODEL_DIR, filename)
                        shutil.copy2(src, dst)
                        print(f"  复制: {filename} -> {dst}")
        
        # 清理临时文件
        try:
            os.remove(temp_path)
        except:
            pass
        
        # 检查结果
        print(f"\n最终模型目录内容: {os.listdir(MODEL_DIR)}")
        if check_models_exist():
            print("✅ 模型文件准备完成！")
            return True
        else:
            print("❌ 模型文件仍然缺失！")
            return False
        
    except Exception as e:
        print(f"下载模型失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    download_and_extract_models()
