# 语音翻译助手

基于 Flask 的语音翻译 Web 应用，支持中英文互译、语音输入和语音朗读。

## 功能特性

- ✨ **语音输入**：使用 Sherpa-ONNX 离线语音识别，支持浏览器录音
- 🌐 **百度翻译 API**：支持中译英和英译中
- 🔊 **语音朗读**：使用 pyttsx3 本地朗读
- 📱 **响应式界面**：支持手机和电脑访问

## 项目结构

```
voice_web/
├── app.py                      # Flask 主程序
├── translation_module.py        # 翻译模块
├── voice_recognition_sherpa.py  # 语音识别模块
├── speech_synthesis_module.py   # 语音合成模块
├── templates/
│   └── index.html              # 前端页面
├── sherpa-onnx-zh-en-model/     # 语音识别模型
├── requirements.txt             # Python 依赖
├── Procfile                    # 部署配置
└── .env.example                # 环境变量示例
```

## 🚀 快速开始

### 1. 下载语音识别模型

由于模型文件较大，需要单独下载：

```bash
# 方式一：从 GitHub 下载
# 访问 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zh-en-2023-12-06.tar.bz2
# 下载后解压，将 3 个 .onnx 文件和 tokens.txt 放到 sherpa-onnx-zh-en-model/ 目录
```

或者查看 `sherpa-onnx-zh-en-model/README.md` 了解详细说明。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写你的百度翻译 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置：
```
BAIDU_TRANSLATE_APP_ID=你的APP_ID
BAIDU_TRANSLATE_SECRET_KEY=你的SECRET_KEY
```

> 获取百度翻译 API 密钥：访问 [百度翻译开放平台](https://fanyi-api.baidu.com/)

### 3. 启动服务

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问：http://localhost:5000

## ☁️ 云平台部署

### 方案一：Railway（推荐，最简单）

1. 将代码推送到 GitHub 仓库
2. 访问 [Railway](https://railway.app/) 并创建新项目
3. 连接 GitHub 仓库
4. 在 Railway 项目设置中添加环境变量：
   - `BAIDU_TRANSLATE_APP_ID`
   - `BAIDU_TRANSLATE_SECRET_KEY`
5. 部署自动完成！

### 方案二：Render

1. 将代码推送到 GitHub
2. 访问 [Render](https://render.com/) 创建 Web Service
3. 连接仓库，设置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. 添加环境变量
5. 部署！

### 方案三：Heroku

```bash
# 1. 安装 Heroku CLI
# 2. 登录
heroku login

# 3. 创建应用
heroku create 你的应用名

# 4. 设置环境变量
heroku config:set BAIDU_TRANSLATE_APP_ID=你的APP_ID
heroku config:set BAIDU_TRANSLATE_SECRET_KEY=你的SECRET_KEY

# 5. 推送代码
git push heroku main
```

## 📝 本地开发

### 调试模式

在 `.env` 文件中设置：
```
FLASK_DEBUG=true
```

## ⚠️ 注意事项

1. **语音识别模型**：确保 `sherpa-onnx-zh-en-model` 目录包含所有必需文件
2. **语音朗读**：部分云平台不支持 pyttsx3（如 Heroku），可能需要替换为云 TTS 服务
3. **安全性**：生产环境请使用 HTTPS 和密钥管理服务

## 🔧 故障排除

### 模型加载失败

确保 `sherpa-onnx-zh-en-model` 目录存在，并包含以下文件：
- tokens.txt
- encoder-epoch-99-avg-1.onnx
- decoder-epoch-99-avg-1.onnx
- joiner-epoch-99-avg-1.onnx

### 翻译失败

检查：
- 环境变量是否正确设置
- 网络连接是否正常
- 百度翻译 API 配额是否足够

### 语音识别无结果

- 确保麦克风权限已授予
- 录音环境安静
- 说话清晰
