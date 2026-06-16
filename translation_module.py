import os
import random
import hashlib
import requests


def translate_text(text, direction):
    """
    百度翻译函数
    支持中译英 (direction="1") 和英译中 (direction="2")
    """
    if not text or text.strip() == "":
        return "⚠️ 输入内容为空"

    if direction not in ["1", "2"]:
        return "⚠️ 翻译方向错误"

    # 从环境变量读取百度翻译配置
    APP_ID = os.environ.get("BAIDU_TRANSLATE_APP_ID")
    SECRET_KEY = os.environ.get("BAIDU_TRANSLATE_SECRET_KEY")

    if not APP_ID or not SECRET_KEY:
        return "❌ 翻译配置缺失，请设置 BAIDU_TRANSLATE_APP_ID 和 BAIDU_TRANSLATE_SECRET_KEY 环境变量"

    URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    if direction == "1":
        from_lang = "zh"
        to_lang = "en"
    else:
        from_lang = "en"
        to_lang = "zh"

    try:
        salt = str(random.randint(32768, 65536))
        sign_str = APP_ID + text + salt + SECRET_KEY
        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()

        payload = {
            "q": text,
            "from": from_lang,
            "to": to_lang,
            "appid": APP_ID,
            "salt": salt,
            "sign": sign,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(URL, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        result_json = response.json()

        if "trans_result" in result_json:
            dst_list = [item["dst"] for item in result_json["trans_result"]]
            return "\n".join(dst_list)
        elif "error_code" in result_json:
            return f"❌ 百度翻译错误 (代码 {result_json['error_code']})：{result_json.get('error_msg', '未知错误')}"
        else:
            return "❌ 翻译失败：未收到有效的翻译结果"

    except requests.exceptions.Timeout:
        return "❌ 翻译失败：请求超时，请检查网络连接"
    except requests.exceptions.ConnectionError:
        return "❌ 翻译失败：网络连接错误"
    except requests.exceptions.RequestException as e:
        return f"❌ 翻译请求异常：{e}"
    except Exception as e:
        return f"❌ 翻译失败：{e}"


# ===== 单独测试 =====
if __name__ == "__main__":
    print("测试翻译模块...")

    # 测试中文转英文
    result1 = translate_text("你好，欢迎使用语音翻译助手", "1")
    print(f"中译英: {result1}")

    # 测试英文转中文
    result2 = translate_text("Hello, welcome to voice translation tool", "2")
    print(f"英译中: {result2}")

    print("测试完成")
