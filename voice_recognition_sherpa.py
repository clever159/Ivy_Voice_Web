import os
import queue
import sherpa_onnx
import time
import numpy as np
import wave
# sounddevice 只在本地录音时需要，云端不会用到，所以不在这里导入

MODEL_DIR = "./sherpa-onnx-zh-en-model"  # 模型目录


class Recognizer:
    """单例模式的识别器，避免重复加载模型"""
    _instance = None
    _lock = None

    def __init__(self):
        self.recognizer = None
        self.sample_rate = 16000
        self._load_model()

    def _load_model(self):
        """加载模型（内部调用）"""
        if self.recognizer is not None:
            return
        
        if not os.path.isdir(MODEL_DIR):
            raise Exception(f"模型目录不存在: {MODEL_DIR}")

        required_files = ["tokens.txt", "encoder-epoch-99-avg-1.onnx", "decoder-epoch-99-avg-1.onnx", "joiner-epoch-99-avg-1.onnx"]
        missing_files = [f for f in required_files if not os.path.isfile(os.path.join(MODEL_DIR, f))]
        if missing_files:
            raise Exception(f"模型文件缺失: {', '.join(missing_files)}")

        print("正在加载模型...")
        try:
            self.recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
                tokens=f"{MODEL_DIR}/tokens.txt",
                encoder=f"{MODEL_DIR}/encoder-epoch-99-avg-1.onnx",
                decoder=f"{MODEL_DIR}/decoder-epoch-99-avg-1.onnx",
                joiner=f"{MODEL_DIR}/joiner-epoch-99-avg-1.onnx",
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
        return f"音频识别出错: {e}"


def speech_recognize(
    model_dir=MODEL_DIR,
    sample_rate=16000,
    max_utterance_length=20.0,
    rule1_silence=1.5,
    rule2_silence=0.8,
    rule3_min_utterance_length=20.0,
    timeout=30.0,
):
    """直接从麦克风录音识别（仅本地开发使用）"""
    # 延迟导入，避免云端导入失败
    try:
        import sounddevice as sd
    except Exception as e:
        return f"本地录音功能不可用: {e}"
    
    full_text = ""

    if not os.path.isdir(model_dir):
        return f"模型目录不存在: {model_dir}，请检查路径是否正确"

    required_files = ["tokens.txt", "encoder-epoch-99-avg-1.onnx", "decoder-epoch-99-avg-1.onnx", "joiner-epoch-99-avg-1.onnx"]
    missing_files = [f for f in required_files if not os.path.isfile(os.path.join(model_dir, f))]
    if missing_files:
        return f"模型文件缺失: {', '.join(missing_files)}"

    print("正在加载模型...")
    try:
        recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=f"{model_dir}/tokens.txt",
            encoder=f"{model_dir}/encoder-epoch-99-avg-1.onnx",
            decoder=f"{model_dir}/decoder-epoch-99-avg-1.onnx",
            joiner=f"{model_dir}/joiner-epoch-99-avg-1.onnx",
            num_threads=4,
            sample_rate=sample_rate,
            decoding_method="modified_beam_search",
            max_active_paths=4,
            enable_endpoint_detection=True,
            rule1_min_trailing_silence=rule1_silence,
            rule2_min_trailing_silence=rule2_silence,
            rule3_min_utterance_length=rule3_min_utterance_length,
            provider="cpu",
        )
    except Exception as e:
        print(f"模型加载失败: {e}")
        return f"模型加载失败: {e}"

    print("模型加载完成!\n")

    stream = recognizer.create_stream()
    audio_queue = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            print(f"音频状态: {status}")
        audio_queue.put(indata.copy().flatten())

    print("录音中... 请说话, 说完后安静1.5秒自动结束，或按 Ctrl+C 退出\n")

    start_time = time.time()
    audio_received = False
    last_status_print = 0
    try:
        with sd.InputStream(
            samplerate=sample_rate, channels=1, dtype="float32", callback=callback
        ):
            print(f"音频流已启动，采样率: {sample_rate}Hz")
            while True:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    print(f"\n超时（{timeout}秒），停止录音")
                    break

                try:
                    samples = audio_queue.get_nowait()
                    audio_received = True
                    stream.accept_waveform(sample_rate, samples)
                except queue.Empty:
                    pass
                else:
                    while recognizer.is_ready(stream):
                        recognizer.decode_stream(stream)

                    is_endpoint = recognizer.is_endpoint(stream)
                    result = recognizer.get_result(stream)

                    if is_endpoint and result.strip():
                        print(f"识别结果: {result}")
                        full_text += result + "."
                        recognizer.reset(stream)
                        while not audio_queue.empty():
                            audio_queue.get()

                if elapsed > timeout and not full_text:
                    break

                if audio_received and int(elapsed) - last_status_print >= 5:
                    last_status_print = int(elapsed)
                    result = recognizer.get_result(stream)
                    if result:
                        print(f"当前识别: {result}")
                    else:
                        print(f"当前状态: 等待语音输入... ({int(elapsed)}秒)")

    except KeyboardInterrupt:
        print("\n\n用户中断识别")
    except Exception as e:
        print(f"\n录音过程出错: {e}")
        return f"录音过程出错: {e}"

    final_text = full_text.rstrip(".")
    print(f"\n识别结束! 最终结果: {final_text}")
    return final_text if final_text else "（未识别到语音）"


if __name__ == "__main__":
    print("测试语音识别模块...")
    text = speech_recognize()
    print(f"\n最终识别文本: {text}")
