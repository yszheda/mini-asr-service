"""
系统资源监控模块
用于监控内存使用情况，确保在2GB内存下稳定运行
"""

import os
import psutil
from pathlib import Path


def get_available_memory_mb() -> float:
    """
    获取可用内存量（MB）

    Returns:
        可用内存量（兆字节）
    """
    try:
        mem = psutil.virtual_memory()
        return mem.available / (1024 * 1024)
    except Exception:
        # psutil 不可用时的备用方案
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemAvailable:'):
                        return float(line.split()[1]) / 1024  # 转换为MB
        except Exception:
            return None


def get_total_memory_mb() -> float:
    """
    获取总内存量（MB）

    Returns:
        总内存量（兆字节）
    """
    try:
        mem = psutil.virtual_memory()
        return mem.total / (1024 * 1024)
    except Exception:
        return None


def get_memory_usage_mb(pid: int = None) -> float:
    """
    获取当前进程的内存使用量（MB）

    Args:
        pid: 进程ID，None表示当前进程

    Returns:
        内存使用量（兆字节）
    """
    try:
        if pid is None:
            pid = os.getpid()
        process = psutil.Process(pid)
        return process.memory_info().rss / (1024 * 1024)
    except Exception:
        return None


def check_memory_sufficient(required_mb: int = 512) -> bool:
    """
    检查可用内存是否充足

    Args:
        required_mb: 所需内存（兆字节），默认512MB

    Returns:
        True表示内存充足，False表示不足
    """
    available = get_available_memory_mb()
    if available is None:
        # 无法获取内存信息，默认认为充足
        return True
    return available > required_mb


def recommend_low_memory_mode(threshold_mb: int = 1024) -> bool:
    """
    根据可用内存推荐是否启用低内存模式

    Args:
        threshold_mb: 内存阈值（兆字节），低于此值推荐启用低内存模式

    Returns:
        True表示推荐启用低内存模式
    """
    total = get_total_memory_mb()
    if total is None:
        return True  # 默认启用

    # 对于2GB以下的设备，推荐启用低内存模式
    return total < 2048


def print_memory_info():
    """打印内存信息"""
    total = get_total_memory_mb()
    available = get_available_memory_mb()
    usage = get_memory_usage_mb()

    print("=" * 50)
    print("内存使用情况")
    print("=" * 50)

    if total is not None:
        print(f"总内存: {total:.1f} MB")
    if available is not None:
        print(f"可用内存: {available:.1f} MB")
        if available < 512:
            print("警告：可用内存不足 512MB！")
    if usage is not None:
        print(f"当前进程内存使用: {usage:.1f} MB")

    low_mem = recommend_low_memory_mode()
    print(f"推荐配置: {'低内存模式' if low_mem else '标准模式'}")
    print("=" * 50)


def get_model_size_mb(model_dir: str = None) -> float:
    """
    获取模型目录大小（MB）

    Args:
        model_dir: 模型目录路径

    Returns:
        目录大小（兆字节）
    """
    try:
        if model_dir is None:
            model_dir = Path(__file__).parent.parent / "models"

        model_path = Path(model_dir)
        if not model_path.exists():
            return 0

        total_size = 0
        for file in model_path.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size

        return total_size / (1024 * 1024)
    except Exception:
        return 0


def check_system_requirements():
    """
    检查系统要求

    Returns:
        (passed, messages): passed为True表示满足要求，messages包含检查信息
    """
    messages = []
    passed = True

    # 检查可用内存
    available = get_available_memory_mb()
    if available is not None:
        messages.append(f"可用内存: {available:.1f} MB")
        if available < 512:
            messages.append("❌ 警告：可用内存不足 512MB，可能导致运行失败")
            passed = False
        elif available < 1024:
            messages.append("⚠️  警告：可用内存较少（<1GB），建议关闭其他程序")
    else:
        messages.append("无法获取内存信息")

    # 检查总内存
    total = get_total_memory_mb()
    if total is not None:
        messages.append(f"总内存: {total:.1f} MB")
        if total < 1024:
            messages.append("❌ 设备内存过小（<1GB），不推荐使用此应用")
            passed = False
    else:
        messages.append("无法获取总内存信息")

    # 检查模型大小
    model_size = get_model_size_mb()
    if model_size > 0:
        messages.append(f"模型大小: {model_size:.1f} MB")

    # 推荐配置
    low_mem = recommend_low_memory_mode()
    messages.append(f"推荐配置: {'低内存模式（单线程 + 贪婪搜索）' if low_mem else '标准模式（2线程 + 束搜索）'}")

    return passed, messages


if __name__ == "__main__":
    # 简单测试
    print_memory_info()
    print()

    passed, messages = check_system_requirements()
    for msg in messages:
        print(msg)

    print()
    if passed:
        print("✅ 系统要求检查通过")
    else:
        print("⚠️  系统要求检查未完全通过，请注意警告信息")
