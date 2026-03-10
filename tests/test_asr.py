"""
测试脚本
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.audio_processor import AudioProcessor
from src.asr_engine import create_asr_engine, ModelDownloader, ASRConfig
from skills.asr_skill import ASRSkill


def test_audio_processor():
    """测试音频处理器"""
    print("=" * 50)
    print("测试音频处理器")
    print("=" * 50)

    processor = AudioProcessor()
    print(f"目标采样率：{processor.TARGET_SAMPLE_RATE}")
    print("音频处理器初始化完成")

    # 测试文件读取（如果有测试文件）
    test_files = ["test.wav", "test.mp3", "test.flac"]
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"测试读取：{test_file}")
            try:
                audio_data, sample_rate = processor.read_audio(test_file)
                print(f"  采样率：{sample_rate}, 数据形状：{audio_data.shape}")
            except Exception as e:
                print(f"  失败：{e}")


def test_model_download():
    """测试模型下载"""
    print("=" * 50)
    print("测试模型下载")
    print("=" * 50)

    config = ASRConfig()
    print(f"模型名称：{config.MODEL_NAME}")
    print(f"模型路径：{config.get_model_path()}")

    if config.get_model_path().exists():
        print("模型已存在")
    else:
        print("模型不存在，需要下载")
        # 实际下载可能需要较长时间，这里仅做演示
        # success = ModelDownloader.download_and_extract(config)
        # print(f"下载结果：{'成功' if success else '失败'}")


def test_asr_engine():
    """测试 ASR 引擎"""
    print("=" * 50)
    print("测试 ASR 引擎")
    print("=" * 50)

    try:
        engine = create_asr_engine()
        print("ASR 引擎初始化完成")

        # 测试识别（如果有测试文件）
        test_files = ["test.wav", "test_audio.wav"]
        for test_file in test_files:
            if Path(test_file).exists():
                print(f"测试识别：{test_file}")
                result = engine.recognize_file(test_file)
                print(f"  识别结果：{result}")

    except Exception as e:
        print(f"ASR 引擎测试失败：{e}")


def test_skill():
    """测试 Skill"""
    print("=" * 50)
    print("测试 ASR Skill")
    print("=" * 50)

    skill = ASRSkill()
    print("Skill 初始化完成")

    # 测试转录（如果有测试文件）
    test_files = ["test.wav", "test_audio.wav"]
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"测试转录：{test_file}")
            result = skill.transcribe(test_file)
            if result["success"]:
                print(f"  识别结果：{result['text']}")
            else:
                print(f"  失败：{result['error']}")


def main():
    """运行所有测试"""
    print("ASR 项目测试")
    print("=" * 50)

    test_audio_processor()
    print()

    test_model_download()
    print()

    test_asr_engine()
    print()

    test_skill()

    print("=" * 50)
    print("测试完成")


if __name__ == "__main__":
    main()
