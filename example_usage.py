#!/usr/bin/env python3
"""
语音转文字并回答问题的完整示例

使用方法:
    python example_usage.py <音频文件>

示例:
    python example_usage.py recording.wav
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.asr_skill import ASRSkill


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

    if not os.path.exists(audio_file):
        print(f"错误：音频文件不存在：{audio_file}")
        sys.exit(1)

    print_header("ASR 语音识别示例")

    print(f"音频文件：{audio_file}")
    print(f"文件大小：{os.path.getsize(audio_file) / 1024:.1f} KB")

    # 创建 Skill 实例
    print_header("步骤 1: 初始化 ASR 引擎")
    print("正在加载 ASR 技能...")
    skill = ASRSkill()
    print("ASR 技能加载完成")

    # 转录语音
    print_header("步骤 2: 转录语音")
    print("正在识别语音...")
    result = skill.transcribe(audio_file)

    if not result["success"]:
        print(f"转录失败：{result['error']}")
        sys.exit(1)

    question = result["text"]
    print(f"识别结果：{question}")

    if not question:
        print("\n识别结果为空，可能是静音或无效的音频")
        sys.exit(0)

    print_header("完成")
    print("语音转文字成功!")
    print(f"\n识别的文字内容：{question}")


if __name__ == "__main__":
    main()
