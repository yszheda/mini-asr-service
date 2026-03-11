"""
OpenClaw 集成模块 - 语音转文字并回答

使用方法：
1. 在 OpenClaw 中导入此模块
2. 配置 Anthropic API Key
3. 向 OpenClaw 发送语音消息，自动转文字并回答

示例：
    from skills.openclaw_integration import VoiceAssistant

    # 创建助手
    assistant = VoiceAssistant(api_key="your-api-key")

    # 处理语音文件
    result = assistant.process_voice("question.wav")
    print(f"识别：{result['text']}")
    print(f"回答：{result['response']}")

    # 或者处理字节数据
    with open("question.wav", "rb") as f:
        result = assistant.process_voice(f.read())
"""

import os
import sys
import typing
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.asr_skill import ASRSkill

AudioInput = typing.Union[str, bytes]


class VoiceAssistant:
    """
    语音助手 - 集成 ASR 和 Claude API

    流程：语音 -> ASR 转文字 -> Claude 回答
    """

    def __init__(self, api_key: str = None, model: str = None):
        """
        初始化语音助手

        Args:
            api_key: Anthropic API Key，默认从 ANTHROPIC_API_KEY 环境变量读取
            model: Claude 模型名称，默认使用 claude-3-5-sonnet-20241022
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or "claude-3-5-sonnet-20241022"  # 更新为最新模型
        self.asr_skill = ASRSkill()
        self._claude_client = None

    @property
    def claude_client(self):
        """懒加载 Claude 客户端"""
        if self._claude_client is None:
            try:
                from anthropic import Anthropic
                self._claude_client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("请安装 anthropic 包：pip install anthropic")
        return self._claude_client

    def process_voice(self, audio_input: AudioInput, system_prompt: str = None) -> dict:
        """
        处理语音输入：转文字 + Claude 回答

        Args:
            audio_input: 音频文件路径或字节数据
            system_prompt: 系统提示词（可选）

        Returns:
            包含识别和回答结果的字典：
            {
                "success": bool,
                "text": str,           # 识别的文字
                "response": str,       # Claude 的回答
                "transcription_error": str,
                "response_error": str
            }
        """
        # 步骤 1: ASR 转录语音
        transcription = self.asr_skill.transcribe(audio_input)

        if not transcription["success"]:
            return {
                "success": False,
                "transcription_error": transcription["error"],
                "text": "",
                "response": ""
            }

        question = transcription["text"]

        if not question.strip():
            return {
                "success": False,
                "transcription_error": "识别结果为空，可能是静音或无效音频",
                "text": "",
                "response": ""
            }

        # 步骤 2: 使用 Claude 回答
        try:
            messages = [{"role": "user", "content": question}]
            if system_prompt:
                response = self.claude_client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=messages
                )
            else:
                response = self.claude_client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=messages
                )

            answer = response.content[0].text

            return {
                "success": True,
                "text": question,
                "response": answer,
                "transcription_error": "",
                "response_error": ""
            }

        except Exception as e:
            return {
                "success": True,  # 转录成功，但回答失败
                "text": question,
                "response": "",
                "transcription_error": "",
                "response_error": f"Claude API 调用失败：{e}"
            }

    def transcribe_only(self, audio_input: AudioInput) -> dict:
        """
        仅转录语音，不回答

        Args:
            audio_input: 音频文件路径或字节数据

        Returns:
            转录结果
        """
        return self.asr_skill.transcribe(audio_input)

    def respond_to_text(self, text: str, system_prompt: str = None) -> dict:
        """
        对文字内容进行回答

        Args:
            text: 用户输入的文字
            system_prompt: 系统提示词（可选）

        Returns:
            回答结果
        """
        try:
            messages = [{"role": "user", "content": text}]
            if system_prompt:
                response = self.claude_client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=messages
                )
            else:
                response = self.claude_client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=messages
                )

            return {
                "success": True,
                "text": text,
                "response": response.content[0].text,
                "error": ""
            }
        except Exception as e:
            return {
                "success": False,
                "text": text,
                "response": "",
                "error": str(e)
            }


# OpenClaw Skill 接口函数
_assistant = None


def get_assistant(api_key: str = None) -> VoiceAssistant:
    """获取或创建语音助手实例"""
    global _assistant
    if _assistant is None:
        _assistant = VoiceAssistant(api_key=api_key)
    return _assistant


def process_voice_message(audio_input: AudioInput, api_key: str = None) -> dict:
    """
    OpenClaw Skill 入口：处理语音消息

    Args:
        audio_input: 音频文件路径或字节数据
        api_key: API Key（可选）

    Returns:
        处理结果
    """
    assistant = get_assistant(api_key)
    return assistant.process_voice(audio_input)


def transcribe_message(audio_input: AudioInput) -> dict:
    """
    OpenClaw Skill 入口：仅转录语音

    Args:
        audio_input: 音频文件路径或字节数据

    Returns:
        转录结果
    """
    assistant = get_assistant()
    return assistant.transcribe_only(audio_input)


# CLI 测试
def main():
    """命令行测试入口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw ASR 集成 - 语音转文字并回答")
    parser.add_argument("audio_file", nargs="?", help="音频文件路径")
    parser.add_argument("--api-key", type=str, help="Anthropic API Key")
    parser.add_argument("--transcribe-only", action="store_true", help="仅转录，不回答")
    parser.add_argument("--system-prompt", type=str, help="系统提示词")

    args = parser.parse_args()

    if not args.audio_file:
        print("用法：python -m skills.openclaw_integration <音频文件> [选项]")
        print("选项:")
        print("  --api-key XXX       设置 API Key")
        print("  --transcribe-only   仅转录，不回答")
        print("  --system-prompt X   设置系统提示词")
        return

    print(f"处理音频：{args.audio_file}")
    print("-" * 50)

    assistant = VoiceAssistant(api_key=args.api_key)

    if args.transcribe_only:
        result = assistant.transcribe_only(args.audio_file)
        if result["success"]:
            print(f"识别结果：{result['text']}")
        else:
            print(f"识别失败：{result['error']}")
    else:
        result = assistant.process_voice(args.audio_file, system_prompt=args.system_prompt)

        if result["success"]:
            print(f"识别结果：{result['text']}")
            print("-" * 50)
            if result["response"]:
                print(f"Claude 回答：{result['response']}")
            elif result["response_error"]:
                print(f"回答失败：{result['response_error']}")
        else:
            print(f"处理失败：{result['transcription_error']}")


if __name__ == "__main__":
    main()
