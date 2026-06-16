import os
import urllib.request
import tarfile
import tempfile
import shutil

MODEL_DIR = "./sherpa-onnx-zh-en-model"
# 使用更稳定的中英文模型
MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-12-06.tar.bz2"
REQUIRED_FILES = [
    "tokens.txt",
    "encoder-epoch-99-avg-1.onnx",
    "decoder-epoch-99-avg-1.onnx",
    "joiner-epoch-99-avg-1.onnx"
]


def check_models_exist():
    """检查模型文件是否都存在"""
    if not os.path.isdir(MODEL_DIR):
        print(f"模型目录不存在: {MODEL_DIR}")
        return False
    
    print(f"检查模型目录内容: {os.listdir(MODEL_DIR)}")
    
    missing = []
    for f in REQUIRED_FILES:
        filepath = os.path.join(MODEL_DIR, f)
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
