#!/usr/bin/env python3
"""
语音转文字并回答问题的完整流程

使用方法:
    python voice_to_answer.py <音频文件> [API_KEY]

示例:
    python voice_to_answer.py audio.wav
    python voice_to_answer.py audio.wav your-anthropic-api-key
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.asr_skill import ASRSkill


def main():
    if len(sys.argv) < 2:
        print("用法：python voice_to_answer.py <音频文件> [API_KEY]")
        print("示例：python voice_to_answer.py audio.wav")
        print("      python voice_to_answer.py audio.wav sk-ant-xxx")
        sys.exit(1)

    audio_file = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(audio_file):
        print(f"错误：音频文件不存在：{audio_file}")
        sys.exit(1)

    print(f"正在处理音频文件：{audio_file}")
    print("-" * 50)

    # 创建 Skill 实例
    skill = ASRSkill()

    # 转录语音并获取回答
    print("正在识别语音并获取回答...")
    result = skill.transcribe_and_respond(audio_file, api_key=api_key)

    if not result["text"]:
        print(f"识别失败：{result.get('transcription_error', '未知错误')}")
        sys.exit(1)

    question = result["text"]
    print(f"识别结果：{question}")
    print("-" * 50)

    if result["response"]:
        print(f"Claude 回答：{result['response']}")
    elif result["response_error"]:
        print(f"获取回答失败：{result['response_error']}")
    else:
        print("未获取回答（可能缺少 API Key）")

    print("-" * 50)
    print("处理完成!")


if __name__ == "__main__":
    main()
