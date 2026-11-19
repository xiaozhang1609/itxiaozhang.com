#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""剪辑助手环境自检：检查并自动安装 FFmpeg / faster-whisper / numpy，并校验字幕字体。
字体校验分两步：① 静态字重文件是否存在；② libass 能否解析到该字体（未静默回退）。
用法: python setup_env.py
退出码: 0=就绪, 1=存在无法自动修复的缺失（信息打印到 stdout）
"""
import json
import os
import shutil
import subprocess
import sys

from fontcheck import FONT_DIR, FONT_FAMILY, check as font_check

# 中文用 Bold、英文用 Regular，缺任意一个都无法正常出字幕（须与 fontcheck.FONT_DIR 同一目录）
FONT_FILES = ["SourceHanSansSC-Bold.otf", "SourceHanSansSC-Regular.otf"]


def run(cmd, timeout=600):
    # encoding 显式指定：中文 Windows 默认 cp936，外部命令输出含中文时会解码报错
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def check_ffmpeg():
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def install_ffmpeg():
    # 优先 winget（Windows）
    if shutil.which("winget"):
        r = run(["winget", "install", "--id", "Gyan.FFmpeg", "-e",
                 "--accept-source-agreements", "--accept-package-agreements",
                 "--disable-interactivity"], timeout=1800)
        if r.returncode == 0 and check_ffmpeg():
            return True
        # winget 装完可能需刷新 PATH；提示新开会话生效
        if r.returncode == 0:
            return "reopen"
    return False


def check_pip_pkg(import_name):
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def has_font_files():
    """静态字重 OTF 是否齐备。"""
    return all(os.path.isfile(os.path.join(FONT_DIR, n)) for n in FONT_FILES)


def install_pip_pkg(pkg):
    r = run([sys.executable, "-m", "pip", "install", "--quiet", pkg], timeout=1800)
    return r.returncode == 0


def main():
    status = {"ffmpeg": "ok", "numpy": "ok", "faster_whisper": "ok", "font": "ok", "notes": []}

    # 1. FFmpeg
    if not check_ffmpeg():
        res = install_ffmpeg()
        if res is True:
            status["ffmpeg"] = "installed"
        elif res == "reopen":
            status["ffmpeg"] = "installed_needs_new_shell"
            status["notes"].append("FFmpeg 已安装，但当前会话 PATH 未刷新；请重开终端或将 FFmpeg bin 目录加入 PATH 后重试")
        else:
            status["ffmpeg"] = "missing"
            status["notes"].append("FFmpeg 自动安装失败；请手动安装（winget install Gyan.FFmpeg 或下载 gyan.dev 构建版）")

    # 2. 字幕字体：先查静态字重文件，再用 ffmpeg 做解析自检（防 libass 静默回退）
    if not has_font_files():
        status["font"] = "missing"
        status["notes"].append(
            f"未找到字幕字体文件：需在 {FONT_DIR} 下放置 " + "、".join(FONT_FILES) +
            f"（{FONT_FAMILY}，SIL OFL 1.1 免费商用）。"
            "字体缺失时 libass 会静默回退到其它字体（可能带版权风险），不可放行。")
    elif status["ffmpeg"] not in ("ok", "installed"):
        status["font"] = "unchecked"
        status["notes"].append("字体文件已存在，但 FFmpeg 未就绪，暂无法做字体解析自检；FFmpeg 可用后请重跑本脚本")
    else:
        fok, fdetail = font_check()
        if fok:
            status["notes"].append(f"字体解析自检通过：{fdetail}")
        else:
            status["font"] = "fallback"
            status["notes"].append(fdetail)

    # 3. Python 依赖
    for pkg, imp in [("numpy", "numpy"), ("faster-whisper", "faster_whisper")]:
        if not check_pip_pkg(imp):
            if install_pip_pkg(pkg) and check_pip_pkg(imp):
                status[imp] = "installed"
            else:
                status[imp] = "missing"
                status["notes"].append(f"pip 安装 {pkg} 失败")

    # faster-whisper 首次运行会自动下载模型（约 500MB，small 模型），此处不预下载
    ok = status["ffmpeg"] in ("ok", "installed") and status["numpy"] in ("ok", "installed") \
         and status["faster_whisper"] in ("ok", "installed") and status["font"] == "ok"
    print(json.dumps({"ready": ok, **status}, ensure_ascii=False, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
