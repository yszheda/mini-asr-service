# 端侧 ASR 语音识别系统

轻量级端侧语音转文字解决方案，使用 Sherpa-ONNX 引擎，支持纯 CPU 计算，内存占用低于 500MB。

## 功能特性

- **轻量级模型**: 模型大小约 300MB，运行时内存占用低于 500MB
- **纯 CPU 计算**: 无需 GPU，适合端侧部署
- **多语言支持**: 支持中文、英文等 100+ 语言
- **流式识别**: 支持实时语音转写
- **OpenClaw Skill 集成**: 可直接作为 Skill 调用
- **语音问答**: 支持语音转文字后使用 Claude 回答问题

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载模型

首次使用前需要下载 ASR 模型（约 300MB）：

```bash
python3 -m asr download-model
```

### 3. 测试安装

```bash
python3 example_usage.py test.wav
```

### 4. 使用方法

#### 方法一：仅语音转文字

```bash
# 命令行
python3 -m asr transcribe audio.wav

# Python API
from asr import recognize_speech
result = recognize_speech("audio.wav")
print(result)
```

#### 方法二：语音转文字并回答

```bash
# 命令行
python3 voice_to_answer.py audio.wav YOUR_API_KEY

# 或使用环境变量
export ANTHROPIC_API_KEY=sk-ant-xxx
python3 voice_to_answer.py audio.wav
```

#### 方法三：OpenClaw Skill

```python
from skills.skill_runner import run_skill

# 仅转录
result = run_skill("transcribe", audio_file="audio.wav")
print(result["text"])

# 转录并回答
result = run_skill("ask", audio_file="question.wav", api_key="sk-ant-xxx")
print(f"识别：{result['text']}")
print(f"回答：{result['response']}")
```

## 系统要求

- Python 3.10+
- 内存：至少 512MB 可用内存
- 存储：至少 500MB 可用空间（用于模型）
- CPU：支持 AVX 指令集

## OpenClaw 集成

### 基本使用

```python
from skills.openclaw_integration import VoiceAssistant

# 创建助手
assistant = VoiceAssistant(api_key="sk-ant-xxx")

# 处理语音文件
result = assistant.process_voice("question.wav")
print(f"识别：{result['text']}")
print(f"回答：{result['response']}")

# 处理字节数据（适合从网络接收的音频）
with open("question.wav", "rb") as f:
    result = assistant.process_voice(f.read())
```

### 完整流程示例

```python
from skills.openclaw_integration import VoiceAssistant

# 初始化助手
assistant = VoiceAssistant(api_key="your-api-key")

# 向 OpenClaw 发送语音，自动转文字并回答
def handle_voice_message(audio_path):
    result = assistant.process_voice(audio_path)
    if result["success"]:
        return {
            "question": result["text"],
            "answer": result["response"]
        }
    else:
        return {"error": result.get("transcription_error", "识别失败")}
```

## 项目结构

```
asr/
├── asr/                    # 包入口
│   ├── __init__.py
│   └── __main__.py
├── src/                    # 核心模块
│   ├── __init__.py
│   ├── audio_processor.py  # 音频处理
│   └── asr_engine.py       # ASR 引擎
├── skills/                 # Skill 模块
│   ├── __init__.py
│   ├── asr_skill.py        # ASR Skill 实现
│   ├── skill_runner.py     # Skill 运行器
│   ├── openclaw_integration.py  # OpenClaw 集成
│   └── skill_config.yaml   # Skill 配置
├── tests/                  # 测试脚本
│   └── test_asr.py
├── models/                 # 模型目录 (自动创建)
├── requirements.txt        # 依赖
└── README.md              # 说明文档
```

## 技能命令

| 命令 | 描述 | 参数 |
|------|------|------|
| `transcribe` | 转录音频文件 | `audio_file`: 音频文件路径 |
| `recognize` | 识别音频字节数据 | `audio`: 音频字节数据 |
| `ask` | 语音转文字并使用 Claude 回答 | `audio_file`/`audio`, `api_key` |

## 支持的音频格式

支持 FFmpeg/SoundFile 支持的所有格式，包括：
- WAV
- MP3
- FLAC
- OGG
- M4A
- 等

## 技术规格

| 项目 | 规格 |
|------|------|
| ASR 引擎 | Sherpa-ONNX |
| 模型 | sherpa-onnx-streaming-zipformer-bilingual-zh-en |
| 采样率 | 16kHz |
| 内存占用 | ~300-500MB |
| 支持语言 | 中文、英文等 100+ 语言 |
| CPU 线程 | 2 (可配置) |

## 常见问题

**Q: 模型下载失败？**
A: 可以手动下载模型并解压到 `models/` 目录。

**Q: 识别结果为空？**
A: 检查音频文件是否有效，确保有语音内容。

**Q: 内存不足？**
A: 关闭其他应用程序，模型运行时占用约 300-500MB 内存。

**Q: 如何获取 API Key？**
A: 访问 https://console.anthropic.com/ 创建 API Key。

## 许可证

MIT License
