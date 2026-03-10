# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 下载模型

首次使用前需要下载 ASR 模型（约 300MB）：

```bash
python3 -m asr download-model
```

或者手动下载：

```bash
cd models
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-multilingual-2024-04-09.tar.bz2
tar -xjf sherpa-onnx-zipformer-multilingual-2024-04-09.tar.bz2
```

## 3. 测试安装

```bash
python3 example_usage.py test.wav
```

## 4. 使用方法

### 方法一：命令行

```bash
# 转录音频文件
python3 -m asr transcribe audio.wav

# 使用 Skill
python3 -m asr skill --audio audio.wav
```

### 方法二：Python API

```python
from asr import recognize_speech

# 简单使用
result = recognize_speech("audio.wav")
print(result)
```

### 方法三：Skill 接口

```python
from skills.skill_runner import run_skill

# 转录文件
result = run_skill("transcribe", audio_file="audio.wav")
print(result["text"])

# 识别字节数据
with open("audio.wav", "rb") as f:
    result = run_skill("recognize", audio=f.read())
print(result["text"])
```

## 5. 集成到 OpenClaw

在 OpenClaw 中配置 Skill：

```python
# 导入 Skill
from skills.skill_runner import run_skill

# 处理语音消息
def handle_voice_message(audio_path):
    result = run_skill("transcribe", audio_file=audio_path)
    if result["success"]:
        return result["text"]
    else:
        return f"识别失败：{result['error']}"
```

## 系统要求

- Python 3.6+
- 内存：至少 512MB 可用内存
- 存储：至少 500MB 可用空间（用于模型）
- CPU：支持 AVX 指令集

## 常见问题

**Q: 模型下载失败？**
A: 可以手动下载模型文件并解压到 `models/` 目录。

**Q: 识别结果为空？**
A: 检查音频文件是否有效，确保有语音内容。

**Q: 内存不足？**
A: 关闭其他应用程序，或考虑使用更小的模型。
