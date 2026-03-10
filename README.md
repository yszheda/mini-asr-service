# 端侧 ASR 语音识别项目

轻量级端侧语音转文字解决方案，使用 Sherpa-ONNX 引擎，支持纯 CPU 计算，内存占用低于 512MB。

## 功能特性

- **轻量级模型**: 模型大小约 200MB，运行时内存占用低于 512MB
- **纯 CPU 计算**: 无需 GPU，适合端侧部署
- **多语言支持**: 支持中文、英文等 100+ 语言
- **流式识别**: 支持实时语音转写
- **OpenClaw Skill 集成**: 可直接作为 Skill 调用

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
│   └── skill_config.yaml   # Skill 配置
├── tests/                  # 测试脚本
│   └── test_asr.py
├── models/                 # 模型目录 (自动创建)
├── requirements.txt        # 依赖
└── README.md              # 说明文档
```

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载模型

首次使用时需要下载模型（约 300MB）：

```bash
# 方式一：使用命令行
python -m asr download-model

# 方式二：使用 Python
python -c "from src.asr_engine import ModelDownloader, ASRConfig; ModelDownloader.download_and_extract(ASRConfig())"
```

模型会自动下载到 `models/` 目录。

## 使用方法

### 命令行使用

```bash
# 转录音频文件
python -m asr transcribe audio.wav

# 使用 Skill 模式
python -m asr skill --audio audio.wav

# 获取帮助
python -m asr --help
```

### Python API 使用

```python
from asr import create_asr_engine, recognize_speech, ASRSkill

# 方式一：使用便捷函数
result = recognize_speech("audio.wav")
print(f"识别结果：{result}")

# 方式二：使用引擎实例
engine = create_asr_engine()
result = engine.recognize_file("audio.wav")
print(f"识别结果：{result}")

# 方式三：使用 Skill
skill = ASRSkill()
result = skill.transcribe("audio.wav")
if result["success"]:
    print(f"识别结果：{result['text']}")
else:
    print(f"识别失败：{result['error']}")
```

### 作为 OpenClaw Skill 使用

```python
from skills.skill_runner import run_skill

# 转录音频文件
result = run_skill("transcribe", audio_file="audio.wav")
print(result)

# 识别音频字节数据
with open("audio.wav", "rb") as f:
    audio_bytes = f.read()
result = run_skill("recognize", audio=audio_bytes)
print(result)
```

## 技能命令

| 命令 | 描述 | 参数 |
|------|------|------|
| `transcribe` | 转录音频文件 | `audio_file`: 音频文件路径 |
| `recognize` | 识别音频字节数据 | `audio`: 音频字节数据 |

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
| 模型 | sherpa-onnx-zipformer-multilingual |
| 采样率 | 16kHz |
| 内存占用 | ~300-500MB |
| 支持语言 | 中文、英文等 100+ 语言 |
| CPU 线程 | 2 (可配置) |

## 故障排除

### 模型下载失败

如果自动下载失败，可以手动下载：

```bash
# 下载模型
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-multilingual-2024-04-09.tar.bz2

# 解压到 models 目录
tar -xjf sherpa-onnx-zipformer-multilingual-2024-04-09.tar.bz2 -C models/
```

### 识别结果为空

- 检查音频文件是否有效
- 确保音频采样率为 16kHz（会自动转换）
- 检查音频是否有声音内容

### 内存不足

如果内存不足，可以尝试：
- 关闭其他应用程序
- 使用更小的模型（如 Vosk 的小模型）

## 许可证

MIT License
