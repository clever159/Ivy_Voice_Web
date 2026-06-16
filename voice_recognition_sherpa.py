import os
import sherpa_onnx
import numpy as np
import wave

# 可能的模型目录
ALTERNATIVE_MODEL_DIRS = [
    "./sherpa-onnx-zh-en-model",
    "./sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20"
]
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


class Recognizer:
    """单例模式的识别器，避免重复加载模型"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.recognizer = None
            cls._instance.sample_rate = 16000
            cls._instance.model_dir = None
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """加载模型（内部调用）"""
        if self.recognizer is not None:
            return
        
        self.model_dir = find_model_dir()
        if self.model_dir is None:
            raise Exception(f"未找到模型目录，请检查: {ALTERNATIVE_MODEL_DIRS}")

        print("正在加载模型...")
        try:
            self.recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
                tokens=f"{self.model_dir}/tokens.txt",
                encoder=f"{self.model_dir}/encoder-epoch-99-avg-1.onnx",
                decoder=f"{self.model_dir}/decoder-epoch-99-avg-1.onnx",
                joiner=f"{self.model_dir}/joiner-epoch-99-avg-1.onnx",
                num_threads=4,
                sample_rate=self.sample_rate,
                provider="cpu",
            )
            print("模型加载完成！")
        except Exception as e:
            raise Exception(f"模型加载失败: {e}")


def recognize_from_file(audio_path, sample_rate=16000):
    """从音频文件识别语音（支持 WAV 格式）"""
    try:
        # 读取 WAV 文件
        with wave.open(audio_path, 'rb') as wf:
            if wf.getnchannels() != 1:
                return "音频必须是单声道"
            if wf.getframerate() != sample_rate:
                return f"音频采样率必须是 {sample_rate}Hz，当前 {wf.getframerate()}Hz"
            frames = wf.readframes(wf.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

        print(f"音频数据长度: {len(audio_data)} 样本 ({len(audio_data)/sample_rate:.2f}秒)")

        # 获取单例识别器
        rec = Recognizer()

        # 创建流并输入音频
        stream = rec.recognizer.create_stream()
        stream.accept_waveform(sample_rate, audio_data)

        while rec.recognizer.is_ready(stream):
            rec.recognizer.decode_stream(stream)

        result = rec.recognizer.get_result(stream)
        print(f"识别结果: {result}")

        return result if result else "（未识别到语音）"

    except Exception as e:
        print(f"音频识别出错: {e}")
        import traceback
        traceback.print_exc()
        return f"音频识别出错: {e}"


if __name__ == "__main__":
    print("测试语音识别模块...")
    print("注意: 麦克风录音功能在云端不可用")
