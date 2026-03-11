#!/usr/bin/env python3
"""
ASR 语音识别示例 - 语音转文字并回答

使用方法:
    python example_usage.py <音频文件> [API_KEY]

示例:
    python example_usage.py recording.wav
    python example_usage.py recording.wav sk-ant-xxx
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.asr_skill import ASRSkill
from skills.openclaw_integration import VoiceAssistant


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    audio_file = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(audio_file):
        print(f"错误：音频文件不存在：{audio_file}")
        sys.exit(1)

    print_header("ASR 语音识别示例")

    print(f"音频文件：{audio_file}")
    print(f"文件大小：{os.path.getsize(audio_file) / 1024:.1f} KB")

    # 方式一：使用 ASRSkill
    print_header("方式 1: 仅语音转文字 (ASRSkill)")
    print("正在加载 ASR 技能...")
    skill = ASRSkill()
    print("正在识别语音...")
    result = skill.transcribe(audio_file)

    if result["success"]:
        print(f"识别结果：{result['text']}")
    else:
        print(f"识别失败：{result['error']}")

    # 方式二：使用 VoiceAssistant (带回答)
    if api_key:
        print_header("方式 2: 语音转文字并回答 (VoiceAssistant)")
        assistant = VoiceAssistant(api_key=api_key)
        result = assistant.process_voice(audio_file)

        if result["success"]:
            print(f"识别结果：{result['text']}")
            if result["response"]:
                print(f"\nClaude 回答：{result['response']}")
            elif result["response_error"]:
                print(f"\n回答失败：{result['response_error']}")
        else:
            print(f"处理失败：{result.get('transcription_error', '未知错误')}")
    else:
        print_header("提示")
        print("提供 API Key 可以获取 Claude 回答")
        print(f"用法：python example_usage.py {audio_file} <your-api-key>")

    print_header("完成")


if __name__ == "__main__":
    main()
