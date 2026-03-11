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

    def __init__(self, model_dir: str = None, low_memory_mode: bool = True):
        """
        初始化技能

        Args:
            model_dir: 模型目录路径
            low_memory_mode: 是否启用低内存模式（针对 2GB 以下设备）
        """
        self.model_dir = model_dir
        self.low_memory_mode = low_memory_mode
        self._engine = None

    @property
    def engine(self):
        """懒加载 ASR 引擎"""
        if self._engine is None:
            self._engine = create_asr_engine(model_dir=self.model_dir, low_memory_mode=self.low_memory_mode)
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

    def transcribe_and_respond(self, audio_input: AudioInput, api_key: str = None, model: str = None) -> dict:
        """
        转录语音并使用 Claude 回答

        Args:
            audio_input: 音频文件路径或字节数据
            api_key: Anthropic API Key (可选，默认从环境变量读取)
            model: Claude 模型名称 (可选)

        Returns:
            包含转录和回答结果的字典
        """
        import os

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

        # 获取 API Key
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return {
                "success": True,  # 转录成功，但无法回答
                "text": question,
                "response": "",
                "transcription_error": "",
                "response_error": "缺少 API Key，请设置 ANTHROPIC_API_KEY 环境变量或传入 api_key 参数"
            }

        # 导入 Claude 客户端
        try:
            from anthropic import Anthropic, APIError, APITimeoutError, RateLimitError
        except ImportError:
            return {
                "success": True,
                "text": question,
                "response": "",
                "transcription_error": "",
                "response_error": "请安装 anthropic 包：pip install anthropic"
            }

        # 获取回答（带重试和超时）
        try:
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model or "claude-3-5-sonnet-20241022",  # 更新为最新模型
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": question}
                ],
                timeout=30.0  # 30秒超时
            )
            answer = response.content[0].text

            return {
                "success": True,
                "text": question,
                "response": answer,
                "transcription_error": "",
                "response_error": ""
            }

        except (RateLimitError, APITimeoutError) as e:
            return {
                "success": True,  # 转录成功
                "text": question,
                "response": "",
                "transcription_error": "",
                "response_error": f"API 限制或超时：{e}。请稍后重试。"
            }

        except APIError as e:
            return {
                "success": True,  # 转录成功
                "text": question,
                "response": "",
                "transcription_error": "",
                "response_error": f"Claude API 错误：{e}"
            }

        except Exception as e:
            return {
                "success": True,  # 转录成功
                "text": question,
                "response": "",
                "transcription_error": "",
                "response_error": f"未知错误：{type(e).__name__}: {e}"
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
