import threading

# 尝试导入 pyttsx3，如果失败（云端环境）则标记为不可用
TTS_AVAILABLE = False
try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception as e:
    print(f"pyttsx3 不可用: {e}")


def speak_text(text, rate=160, volume=1.0):
    """
    语音朗读函数（在后台线程中执行，不会阻塞调用者）
    云端环境会优雅降级，返回 False 表示 TTS 不可用
    """
    if not text or not str(text).strip():
        print("无内容可朗读")
        return False
    
    if not TTS_AVAILABLE:
        print("TTS 功能不可用（可能在云端环境）")
        return False

    def _speak():
        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", rate)
            engine.setProperty("volume", volume)

            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in str(text))
            voices = engine.getProperty("voices")
            selected_voice = None

            for voice in voices:
                voice_langs = str(voice.languages).lower() if voice.languages else ""
                voice_name = voice.name.lower() if voice.name else ""

                if has_chinese:
                    if "zh" in voice_langs or "chinese" in voice_name or "mandarin" in voice_name:
                        selected_voice = voice.id
                        break
                else:
                    if "en" in voice_langs or "english" in voice_name:
                        selected_voice = voice.id
                        break

            if selected_voice:
                engine.setProperty("voice", selected_voice)
            elif voices:
                engine.setProperty("voice", voices[0].id)

            engine.say(str(text))
            engine.runAndWait()
            print("朗读完成")
        except Exception as e:
            print(f"语音朗读失败: {e}")
        finally:
            if engine:
                try:
                    engine.stop()
                except Exception:
                    pass

    # 在后台线程执行朗读，不阻塞主线程
    thread = threading.Thread(target=_speak, daemon=True)
    thread.start()
    return True


# ===== 单独测试 =====
if __name__ == "__main__":
    print("测试语音朗读模块...")

    print("\n1. 测试中文朗读:")
    success = speak_text("你好，欢迎使用语音翻译助手")
    if not success:
        print("TTS 不可用，这在云端环境是正常的")

    print("\n2. 测试英文朗读:")
    success = speak_text("Hello, welcome to voice translation tool")
    if not success:
        print("TTS 不可用，这在云端环境是正常的")

    print("\n测试完成")
