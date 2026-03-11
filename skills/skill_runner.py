"""
Skill 运行器 - 用于 OpenClaw 调用 ASR 技能

使用方法：
    from skills.skill_runner import run_skill

    # 转录音频文件
    result = run_skill("transcribe", audio_file="audio.wav")

    # 识别音频字节
    result = run_skill("recognize", audio=audio_bytes)

    # 语音转文字并回答（需要 API Key）
    result = run_skill("ask", audio_file="question.wav", api_key="xxx")
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.asr_skill import ASRSkill


class SkillRuntime:
    """Skill 运行时"""

    def __init__(self):
        self.skill = ASRSkill()

    def execute(self, command: str, **kwargs) -> dict:
        """
        执行技能命令

        Args:
            command: 命令名称
            **kwargs: 命令参数

        Returns:
            执行结果
        """
        if command == "transcribe":
            audio_file = kwargs.get("audio_file")
            if not audio_file:
                return {"success": False, "error": "缺少 audio_file 参数"}
            return self.skill.transcribe(audio_file)

        elif command == "recognize":
            audio = kwargs.get("audio")
            if not audio:
                return {"success": False, "error": "缺少 audio 参数"}
            return self.skill.transcribe(audio)

        elif command == "ask":
            # 语音转文字并回答
            audio_input = kwargs.get("audio_file") or kwargs.get("audio")
            if not audio_input:
                return {"success": False, "error": "缺少 audio_file 或 audio 参数"}
            api_key = kwargs.get("api_key")
            model = kwargs.get("model")
            return self.skill.transcribe_and_respond(audio_input, api_key=api_key, model=model)

        else:
            return {"success": False, "error": f"未知命令：{command}"}


# 全局运行器实例
_runtime = None


def get_runtime() -> SkillRuntime:
    """获取运行时实例"""
    global _runtime
    if _runtime is None:
        _runtime = SkillRuntime()
    return _runtime


# OpenClaw Skill 接口
def run_skill(command: str, **kwargs) -> dict:
    """
    OpenClaw Skill 入口函数

    Args:
        command: 命令名称
          - "transcribe": 转录音频文件
          - "recognize": 识别音频字节数据
          - "ask": 语音转文字并使用 Claude 回答
        **kwargs: 命令参数
          - audio_file: 音频文件路径（用于 transcribe/ask）
          - audio: 音频字节数据（用于 recognize/ask）
          - api_key: Anthropic API Key（用于 ask）

    Returns:
        执行结果字典
    """
    runtime = get_runtime()
    return runtime.execute(command, **kwargs)
