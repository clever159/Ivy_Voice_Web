from flask import Flask, render_template, request, jsonify
import os
import threading
import tempfile
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
load_dotenv()

# 检查并下载模型（在模块导入时就执行，确保 gunicorn 部署也能正常工作）
try:
    from download_models import download_and_extract_models, check_models_exist
    if not check_models_exist():
        print("模型文件缺失，正在自动下载...")
        download_success = download_and_extract_models()
        if download_success:
            print("模型下载完成！")
        else:
            print("警告：模型下载失败，请手动下载！")
except Exception as e:
    print(f"模型下载检查失败: {e}")

import translation_module
import voice_recognition_sherpa
import speech_synthesis_module

app = Flask(__name__)

# 单例模式加载模型（只加载一次）
_recognizer_instance = None
_recognizer_lock = threading.Lock()

def get_recognizer():
    global _recognizer_instance
    if _recognizer_instance is None:
        with _recognizer_lock:
            if _recognizer_instance is None:
                _recognizer_instance = voice_recognition_sherpa.Recognizer()
    return _recognizer_instance


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/translate", methods=["POST"])
def translate():
    """翻译接口 - 自动检测语言"""
    data = request.get_json()
    if not data:
        return jsonify({"result": "❌ 请求数据为空"}), 400

    text = data.get("text", "").strip()

    if not text:
        return jsonify({"result": "⚠️ 输入内容为空"}), 400

    result = translation_module.translate_text(text)
    return jsonify({"result": result})


@app.route("/voice-input", methods=["POST"])
def voice_input():
    """语音识别接口（支持上传音频文件）"""
    try:
        # 检查是否有音频文件上传
        if 'audio' in request.files:
            audio_file = request.files['audio']
            # 保存到临时文件 - 使用正确的扩展名
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                audio_path = tmp.name
                audio_file.save(audio_path)

            print(f"====== 收到音频文件: {audio_path} ======")
            try:
                recognized_text = voice_recognition_sherpa.recognize_from_file(audio_path)
            finally:
                # 删除临时文件
                if os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                    except:
                        pass
        else:
            recognized_text = "暂不支持直接从后端麦克风录音"

        return jsonify({"text": recognized_text})
    except Exception as e:
        print(f"语音识别报错: {e}")
        return jsonify({"text": f"语音识别后端报错: {e}"}), 500


@app.route("/speak", methods=["POST"])
def speak():
    """语音朗读接口"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "请求数据为空"}), 400

    text = data.get("text", "").strip()
    if not text:
        return jsonify({"success": False, "error": "没有内容可朗读"}), 400

    # 朗读已在后台线程执行，立即返回
    try:
        success = speech_synthesis_module.speak_text(text)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "语音朗读功能在当前环境不可用"}), 501
    except Exception as e:
        print(f"朗读报错: {e}")
        return jsonify({"success": False, "error": f"朗读失败: {e}"}), 500


if __name__ == "__main__":
    # 获取端口，默认5000
    port = int(os.environ.get("PORT", 5000))
    # 预加载模型
    try:
        print("正在预加载模型...")
        get_recognizer()
        print("模型预加载完成！")
    except Exception as e:
        print(f"警告：模型预加载失败：{e}")
    # threaded=True 让 Flask 支持异步并发，debug=False 生产环境
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, threaded=True, host="0.0.0.0", port=port)
