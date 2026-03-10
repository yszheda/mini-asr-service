#!/usr/bin/env python3
"""
语音转文字并回答问题的完整流程演示
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.asr_skill import ASRSkill


def main():
    if len(sys.argv) < 2:
        print("用法：python voice_to_answer.py <音频文件> [是否回答问题]")
        print("示例：python voice_to_answer.py audio.wav")
        sys.exit(1)

    audio_file = sys.argv[1]

    if not os.path.exists(audio_file):
        print(f"错误：音频文件不存在：{audio_file}")
        sys.exit(1)

    print(f"正在处理音频文件：{audio_file}")
    print("-" * 50)

    # 创建 Skill 实例
    skill = ASRSkill()

    # 转录语音
    print("正在转录语音...")
    result = skill.transcribe(audio_file)

    if not result["success"]:
        print(f"转录失败：{result['error']}")
        sys.exit(1)

    question = result["text"]
    print(f"识别结果：{question}")
    print("-" * 50)

    if not question:
        print("识别结果为空，可能是静音或无效的音频")
        sys.exit(0)

    print("语音转文字完成!")


if __name__ == "__main__":
    main()
