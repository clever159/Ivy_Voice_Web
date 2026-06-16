# 语音识别模型

由于模型文件体积较大（超过 100MB），无法直接提交到 GitHub。

## 下载模型

请从以下地址下载模型文件，并放置到此目录：

- [sherpa-onnx-zh-en-2023-12-06](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zh-en-2023-12-06.tar.bz2)

## 需要的文件

确保此目录包含以下文件：

```
sherpa-onnx-zh-en-model/
├── README.md
├── tokens.txt
├── encoder-epoch-99-avg-1.onnx
├── decoder-epoch-99-avg-1.onnx
└── joiner-epoch-99-avg-1.onnx
```

## 下载步骤

1. 下载 `sherpa-onnx-zh-en-2023-12-06.tar.bz2`
2. 解压该文件
3. 将解压后的模型文件（3个 .onnx 文件和 tokens.txt）复制到此目录
