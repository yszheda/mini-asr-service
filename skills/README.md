# OpenClaw ASR Skill 接口文档

## 概述

ASR Skill 是一个用于 OpenClaw 的语音识别技能，可以将语音文件转换为文字。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载模型

```bash
python -m asr download-model
```

### 3. 使用 Skill

```python
from skills.skill_runner import run_skill

# 转录音频文件
result = run_skill("transcribe", audio_file="audio.wav")
print(result["text"])
```

## API 参考

### `run_skill(command, **kwargs)`

执行 ASR Skill 命令。

#### 参数

- `command` (str): 命令名称
  - `"transcribe"`: 转录音频文件
  - `"recognize"`: 识别音频字节数据

- `**kwargs`: 命令参数

#### 返回值

```python
{
    "success": bool,      # 是否成功
    "text": str,          # 识别结果文字
    "error": str          # 错误信息（如果有）
}
```

## 使用示例

### 示例 1: 转录 WAV 文件

```python
from skills.skill_runner import run_skill

result = run_skill("transcribe", audio_file="recording.wav")
if result["success"]:
    print(f"识别结果：{result['text']}")
else:
    print(f"识别失败：{result['error']}")
```

### 示例 2: 识别字节数据

```python
from skills.skill_runner import run_skill

with open("recording.wav", "rb") as f:
    audio_bytes = f.read()

result = run_skill("recognize", audio=audio_bytes)
if result["success"]:
    print(f"识别结果：{result['text']}")
else:
    print(f"识别失败：{result['error']}")
```

### 示例 3: 在 OpenClaw 中使用

```python
# OpenClaw 配置文件中添加：
skills:
  asr:
    path: /path/to/asr/skills/skill_runner.py
    entry_point: run_skill

# 然后在 OpenClaw 中调用：
# @asr.transcribe(audio_file="recording.wav")
```

### 示例 4: 语音转文字并回答

```python
from skills.asr_skill import ASRSkill

skill = ASRSkill()

# 转录语音
result = skill.transcribe("question.wav")
if result["success"]:
    question = result["text"]
    print(f"识别的问题：{question}")
    # 然后将问题发送给 Claude 进行回答
```

## 错误处理

| 错误类型 | 描述 | 解决方法 |
|---------|------|---------|
| `音频文件不存在` | 指定的音频文件不存在 | 检查文件路径是否正确 |
| `无法解析音频数据` | 音频格式不支持或文件损坏 | 使用支持的格式（WAV、MP3 等） |
| `模型下载失败` | 网络连接问题 | 检查网络连接，或手动下载模型 |
| `识别结果为空` | 音频中没有语音或音量太小 | 检查音频内容，增大音量 |

## 支持的音频格式

- WAV (推荐)
- MP3
- FLAC
- OGG
- M4A

**注意**: 所有音频会自动转换为 16kHz 单声道进行处理。

## 性能指标

| 指标 | 数值 |
|------|------|
| 模型大小 | ~300MB |
| 内存占用 | 300-500MB |
| 识别速度 | ~0.5x 实时 (CPU) |
| 采样率 | 16kHz |

## 故障排除

### 问题 1: 模型下载慢

可以手动下载模型：

```bash
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-multilingual-2024-04-09.tar.bz2
tar -xjf sherpa-onnx-zipformer-multilingual-2024-04-09.tar.bz2 -C models/
```

### 问题 2: 识别速度慢

- 确保音频采样率接近 16kHz
- 减少同时运行的其他程序
- 考虑使用更小的模型

### 问题 3: 识别准确率低

- 确保录音质量良好
- 减少背景噪音
- 说话速度适中
