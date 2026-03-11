"""
ASR 语音识别核心模块
使用 Sherpa-ONNX 引擎实现轻量级语音转文字
"""

import os
import shutil
import typing
import urllib.request
import hashlib
from pathlib import Path

import sherpa_onnx

from .audio_processor import AudioProcessor, AudioInput


class ASRConfig:
    """ASR 配置类"""

    # 模型下载配置 - 使用小的中英文双语模型（内存占用更小）
    MODEL_NAME = "sherpa-onnx-streaming-zipformer-small-bilingual-zh-en-2023-02-16"
    MODEL_URL = f"https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{MODEL_NAME}.tar.bz2"

    # 模型文件哈希验证
    MODEL_HASH = None  # 暂不验证

    # 推荐配置（针对 2GB 内存以下设备）
    RECOMMENDED_CONFIG = {
        "num_threads": 1,           # 单线程运行（节省内存）
        "max_active_paths": 2,       # 减少搜索路径
        "decoding_method": "greedy_search",  # 贪婪搜索（最省内存）
    }

    def __init__(self, model_dir: str = None, low_memory_mode: bool = True):
        """
        初始化配置

        Args:
            model_dir: 模型目录路径
            low_memory_mode: 是否启用低内存模式（针对 2GB 以下设备）
        """
        self.model_dir = Path(model_dir) if model_dir else Path(__file__).parent.parent / "models"
        self.model_path = self.model_dir / self.MODEL_NAME
        self.low_memory_mode = low_memory_mode

    def get_model_path(self) -> Path:
        """获取模型路径"""
        return self.model_path


class ModelDownloader:
    """模型下载器"""

    @staticmethod
    def download_and_extract(config: ASRConfig) -> bool:
        """
        下载并解压模型

        Args:
            config: ASR 配置

        Returns:
            是否成功
        """
        import ssl

        model_dir = config.model_dir
        model_path = config.get_model_path()

        if model_path.exists():
            print(f"模型已存在：{model_path}")
            return True

        # 创建模型目录
        model_dir.mkdir(parents=True, exist_ok=True)

        tar_path = model_dir / f"{config.MODEL_NAME}.tar.bz2"

        try:
            print(f"正在下载模型：{config.MODEL_URL}")

            # 创建不验证 SSL 的上下文（解决证书问题）
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            # 使用 urlopen 下载
            with urllib.request.urlopen(config.MODEL_URL, context=ctx) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(tar_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            print(f'下载进度：{downloaded * 100 // total_size}%', end='\r')

            print(f'\n模型下载完成：{tar_path}')

            # 解压
            print("正在解压模型...")
            shutil.unpack_archive(tar_path, model_dir)

            # 删除压缩包
            tar_path.unlink()

            print(f"模型已解压到：{model_path}")
            return True

        except Exception as e:
            print(f"模型下载/解压失败：{e}")
            # 清理失败的文件
            if tar_path.exists():
                tar_path.unlink()
            return False


class ASREngine:
    """ASR 识别引擎"""

    def __init__(self, model_dir: str = None, language: str = "zh", low_memory_mode: bool = True):
        """
        初始化 ASR 引擎

        Args:
            model_dir: 模型目录
            language: 主要识别语言 ('zh' 或 'en')
            low_memory_mode: 是否启用低内存模式（针对 2GB 以下设备）
        """
        self.config = ASRConfig(model_dir, low_memory_mode=low_memory_mode)
        self.audio_processor = AudioProcessor()
        self.language = language
        self.recognizer = None
        self._initialize()

    def _initialize(self):
        """初始化识别器"""
        model_path = self.config.get_model_path()

        # 如果模型不存在，下载
        if not model_path.exists():
            if not ModelDownloader.download_and_extract(self.config):
                raise RuntimeError("模型下载失败")

        # 优先使用 INT8 量化模型（减少48%内存占用）
        encoder_path = model_path / "encoder-epoch-99-avg-1.int8.onnx"
        decoder_path = model_path / "decoder-epoch-99-avg-1.int8.onnx"
        joiner_path = model_path / "joiner-epoch-99-avg-1.int8.onnx"

        # 如果量化模型不存在，降级使用 FP32 模型
        if not encoder_path.exists():
            encoder_path = model_path / "encoder-epoch-99-avg-1.onnx"
            decoder_path = model_path / "decoder-epoch-99-avg-1.onnx"
            joiner_path = model_path / "joiner-epoch-99-avg-1.onnx"
            print("警告：使用 FP32 模型（内存占用更大）")
        else:
            print("使用 INT8 量化模型（节省 48% 内存）")

        # 根据内存模式配置参数
        if self.config.low_memory_mode:
            num_threads = 1
            max_active_paths = 2
            decoding_method = "greedy_search"  # 最省内存
            print("启用低内存模式：单线程 + 贪婪搜索")
        else:
            num_threads = 2
            max_active_paths = 4
            decoding_method = "modified_beam_search"

        # 使用 from_transducer 方法创建识别器
        self.recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=str(model_path / "tokens.txt"),
            encoder=str(encoder_path),
            decoder=str(decoder_path),
            joiner=str(joiner_path),
            num_threads=num_threads,
            sample_rate=16000,
            feature_dim=80,
            decoding_method=decoding_method,
            max_active_paths=max_active_paths,
            provider="cpu",
        )

        print(f"ASR 引擎初始化完成，模型：{model_path}")

    def recognize(self, audio_input: AudioInput) -> str:
        """
        识别语音

        Args:
            audio_input: 音频文件路径或字节数据

        Returns:
            识别的文字结果
        """
        # 处理音频（包含归一化）
        audio_data = self.audio_processor.process_audio(audio_input)

        # 标准化音量（提高识别准确率）
        audio_data = self.audio_processor.normalize_audio(audio_data)

        # 创建流式识别器
        stream = self.recognizer.create_stream()

        # 分块处理音频 (模拟流式)
        chunk_size = int(16000 * 0.1)  # 100ms  chunks
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            stream.accept_waveform(16000, chunk)

        # 输入尾部
        tail_paddings = 8000  # 0.5 秒的静音
        stream.accept_waveform(16000, [0.0] * tail_paddings)

        # 识别
        while self.recognizer.is_ready(stream):
            self.recognizer.decode_stream(stream)

        result = self.recognizer.get_result(stream)

        # 释放流对象
        del stream

        return result.text.strip()

    def recognize_file(self, audio_path: str) -> str:
        """
        识别音频文件

        Args:
            audio_path: 音频文件路径

        Returns:
            识别结果
        """
        return self.recognize(audio_path)

    def recognize_bytes(self, audio_bytes: bytes) -> str:
        """
        识别音频字节数据

        Args:
            audio_bytes: 音频字节数据

        Returns:
            识别结果
        """
        return self.recognize(audio_bytes)


# 便捷函数
def create_asr_engine(model_dir: str = None, language: str = "zh", low_memory_mode: bool = True) -> ASREngine:
    """
    创建 ASR 引擎实例

    Args:
        model_dir: 模型目录
        language: 主要识别语言
        low_memory_mode: 是否启用低内存模式（针对 2GB 以下设备）

    Returns:
        ASREngine 实例
    """
    return ASREngine(model_dir=model_dir, language=language, low_memory_mode=low_memory_mode)


def recognize_speech(audio_input: AudioInput, model_dir: str = None, low_memory_mode: bool = True) -> str:
    """
    便捷函数：识别语音

    Args:
        audio_input: 音频文件路径或字节数据
        model_dir: 模型目录
        low_memory_mode: 是否启用低内存模式

    Returns:
        识别结果
    """
    engine = create_asr_engine(model_dir=model_dir, low_memory_mode=low_memory_mode)
    return engine.recognize(audio_input)
