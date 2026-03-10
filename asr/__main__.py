"""
ASR 包入口
"""

from src.asr_engine import create_asr_engine, recognize_speech, ASREngine
from src.audio_processor import AudioProcessor
from skills.asr_skill import ASRSkill

__all__ = [
    "create_asr_engine",
    "recognize_speech",
    "ASREngine",
    "AudioProcessor",
    "ASRSkill",
]

__version__ = "1.0.0"
