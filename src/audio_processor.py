"""
音频处理模块
负责音频文件读取、格式转换、重采样等
"""

import io
import wave
import typing
import numpy as np
import soundfile as sf
import resampy

# Python 3.6 兼容类型注解
try:
    # Python 3.10+
    pass
except:
    pass

AudioInput = typing.Union[str, bytes]


class AudioProcessor:
    """音频处理器"""

    TARGET_SAMPLE_RATE = 16000  # ASR 模型期望的采样率

    @staticmethod
    def read_audio(audio_path: str) -> typing.Tuple[np.ndarray, int]:
        """
        读取音频文件

        Args:
            audio_path: 音频文件路径

        Returns:
            (audio_data, sample_rate): 音频数据和原始采样率
        """
        audio_data, sample_rate = sf.read(audio_path)

        # 如果是立体声，转换为单声道
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)

        return audio_data.astype(np.float32), sample_rate

    @staticmethod
    def read_audio_bytes(audio_bytes: bytes) -> typing.Tuple[np.ndarray, int]:
        """
        从字节数据读取音频

        Args:
            audio_bytes: 音频文件的字节数据

        Returns:
            (audio_data, sample_rate): 音频数据和采样率
        """
        # 尝试使用 soundfile 读取
        try:
            audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            return audio_data.astype(np.float32), sample_rate
        except Exception:
            # 如果是 WAV 格式，尝试用 wave 模块解析
            pass

        # 尝试解析 WAV 格式
        try:
            with wave.open(io.BytesIO(audio_bytes), 'rb') as wav_file:
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()

                raw_data = wav_file.readframes(n_frames)

                # 根据采样宽度转换数据
                if sample_width == 1:
                    dtype = np.uint8
                elif sample_width == 2:
                    dtype = np.int16
                elif sample_width == 4:
                    dtype = np.int32
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")

                audio_data = np.frombuffer(raw_data, dtype=dtype)

                # 转换为浮点数
                if dtype == np.uint8:
                    audio_data = (audio_data.astype(np.float32) - 128) / 128.0
                elif dtype == np.int16:
                    audio_data = audio_data.astype(np.float32) / 32768.0
                elif dtype == np.int32:
                    audio_data = audio_data.astype(np.float32) / 2147483648.0

                # 如果是多声道，转换为单声道
                if n_channels > 1:
                    audio_data = audio_data.reshape(-1, n_channels)
                    audio_data = np.mean(audio_data, axis=1)

                return audio_data.astype(np.float32), frame_rate

        except Exception as e:
            raise ValueError(f"无法解析音频数据：{e}")

    @staticmethod
    def resample(audio_data: np.ndarray, orig_sr: int, target_sr: int = TARGET_SAMPLE_RATE) -> np.ndarray:
        """
        重采样音频到目标采样率

        Args:
            audio_data: 音频数据
            orig_sr: 原始采样率
            target_sr: 目标采样率 (默认 16000)

        Returns:
            重采样后的音频数据
        """
        if orig_sr == target_sr:
            return audio_data

        return resampy.resample(audio_data, orig_sr, target_sr).astype(np.float32)

    @staticmethod
    def process_audio(audio_input: AudioInput) -> np.ndarray:
        """
        处理音频输入，返回模型可用的音频数据

        Args:
            audio_input: 音频文件路径或字节数据

        Returns:
            处理后的音频数据 (16kHz, 单声道，float32)
        """
        if isinstance(audio_input, bytes):
            audio_data, sample_rate = AudioProcessor.read_audio_bytes(audio_input)
        else:
            audio_data, sample_rate = AudioProcessor.read_audio(audio_input)

        # 重采样到 16kHz
        audio_data = AudioProcessor.resample(audio_data, sample_rate)

        return audio_data

    @staticmethod
    def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
        """
        标准化音频音量

        Args:
            audio_data: 音频数据

        Returns:
            标准化后的音频数据
        """
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
        return audio_data
