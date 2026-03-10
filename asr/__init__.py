"""
ASR 项目主入口
提供命令行接口和 API 接口
"""

import sys
import argparse
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.asr_engine import create_asr_engine, recognize_speech, ASREngine
from skills.asr_skill import ASRSkill


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="端侧 ASR 语音识别系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转录音频文件
  python -m asr transcribe audio.wav

  # 使用技能模式
  python -m asr skill --audio audio.wav

  # 下载模型
  python -m asr download-model
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # transcribe 命令
    transcribe_parser = subparsers.add_parser("transcribe", help="转录音频文件")
    transcribe_parser.add_argument("audio_file", type=str, help="音频文件路径")
    transcribe_parser.add_argument("--model-dir", type=str, help="模型目录")

    # skill 命令
    skill_parser = subparsers.add_parser("skill", help="使用 ASR 技能")
    skill_parser.add_argument("--audio", type=str, help="音频文件路径")
    skill_parser.add_argument("--model-dir", type=str, help="模型目录")
    skill_parser.add_argument("--respond", action="store_true", help="使用 Claude 回答问题")

    # download-model 命令
    download_parser = subparsers.add_parser("download-model", help="下载 ASR 模型")
    download_parser.add_argument("--model-dir", type=str, help="模型目录")

    args = parser.parse_args()

    if args.command == "transcribe":
        # 转录音频文件
        print(f"正在转录：{args.audio_file}")
        result = recognize_speech(args.audio_file, model_dir=args.model_dir)
        print(f"识别结果：{result}")

    elif args.command == "skill":
        # 使用技能
        skill = ASRSkill(model_dir=args.model_dir)

        if args.audio:
            result = skill.transcribe(args.audio)
            if result["success"]:
                print(f"识别结果：{result['text']}")
            else:
                print(f"识别失败：{result['error']}")
        else:
            print("技能已加载，请提供 --audio 参数指定音频文件")

    elif args.command == "download-model":
        # 下载模型
        from src.asr_engine import ASRConfig, ModelDownloader
        config = ASRConfig(model_dir=args.model_dir)
        success = ModelDownloader.download_and_extract(config)
        if success:
            print("模型下载完成")
        else:
            print("模型下载失败")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
