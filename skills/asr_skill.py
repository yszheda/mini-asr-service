"""
ASR Skill - OpenClaw 语音识别技能
将语音转换为文字，并传递给 Claude 进行回答
"""

import os
import sys
import typing
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.asr_engine import create_asr_engine, recognize_speech

AudioInput = typing.Union[str, bytes]


class ASRSkill:
    """ASR 语音识别技能"""

    def __init__(self, model_dir: str = None):
        """
        初始化技能

        Args:
            model_dir: 模型目录路径
        """
        self.model_dir = model_dir
        self._engine = None

    @property
    def engine(self):
        """懒加载 ASR 引擎"""
        if self._engine is None:
            self._engine = create_asr_engine(model_dir=self.model_dir)
        return self._engine

    def transcribe(self, audio_input: AudioInput) -> dict:
        """
        转录语音为文字

        Args:
            audio_input: 音频文件路径或字节数据

        Returns:
            包含转录结果的字典
        """
        try:
            if isinstance(audio_input, str):
                # 文件路径
                if not os.path.exists(audio_input):
                    return {
                        "success": False,
                        "error": f"音频文件不存在：{audio_input}",
                        "text": ""
                    }
                result = self.engine.recognize_file(audio_input)
            else:
                # 字节数据
                result = self.engine.recognize_bytes(audio_input)

            return {
                "success": True,
                "text": result,
                "error": ""
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }

    def transcribe_and_respond(self, audio_input: AudioInput, claude_client=None) -> dict:
        """
        转录语音并使用 Claude 回答

        Args:
            audio_input: 音频文件路径或字节数据
            claude_client: Claude API 客户端 (可选)

        Returns:
            包含转录和回答结果的字典
        """
        # 先转录语音
        transcription = self.transcribe(audio_input)

        if not transcription["success"]:
            return {
                "success": False,
                "transcription_error": transcription["error"],
                "text": "",
                "response": ""
            }

        question = transcription["text"]

        if not question:
            return {
                "success": False,
                "transcription_error": "识别结果为空",
                "text": "",
                "response": ""
            }

        # 如果有 Claude 客户端，获取回答
        if claude_client:
            try:
                response = claude_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=[
                        {"role": "user", "content": question}
                    ]
                )
                answer = response.content[0].text
            except Exception as e:
                answer = f"获取回答失败：{e}"
                return {
                    "success": False,
                    "transcription_error": "",
                    "text": question,
                    "response": answer,
                    "response_error": str(e)
                }
        else:
            answer = None

        return {
            "success": True,
            "text": question,
            "response": answer,
            "transcription_error": "",
            "response_error": ""
        }


# 命令行接口
def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="ASR 语音识别技能")
    parser.add_argument("audio_file", nargs="?", help="音频文件路径")
    parser.add_argument("--model-dir", type=str, help="模型目录")
    parser.add_argument("--test", action="store_true", help="运行测试")

    args = parser.parse_args()

    if args.test:
        # 运行测试
        print("运行 ASR 技能测试...")
        skill = ASRSkill(model_dir=args.model_dir)
        print("ASR 技能初始化完成")
        print("请提供一个音频文件进行测试")
        return

    if not args.audio_file:
        print("用法：python -m skills.asr_skill <音频文件> [--model-dir <模型目录>]")
        print("或：python -m skills.asr_skill --test")
        return

    skill = ASRSkill(model_dir=args.model_dir)
    result = skill.transcribe(args.audio_file)

    if result["success"]:
        print(f"识别结果：{result['text']}")
    else:
        print(f"识别失败：{result['error']}")


if __name__ == "__main__":
    main()
