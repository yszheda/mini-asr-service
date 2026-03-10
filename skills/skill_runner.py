"""
Skill 运行器 - 用于 OpenClaw 调用 ASR 技能
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
        **kwargs: 命令参数

    Returns:
        执行结果
    """
    runtime = get_runtime()
    return runtime.execute(command, **kwargs)
