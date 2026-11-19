#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""字体解析自检：确认 libass 能把指定字体族解析到期望的字体文件，而不是静默回退。

原理：让 ffmpeg 用一段最小 ASS 渲染 1 帧（-v verbose），从日志里的
      `fontselect: (字体族, 字重, 0) -> 实际字体文件` 行判断真正选中了哪个字体。
背景：libass 找不到 ASS 里指定的字体时**不报错**，而是静默回退到系统默认字体
      （实测可能回退到 Arial / 微软雅黑，后者带字体版权风险），所以必须显式校验。

被 setup_env.py（环境自检）与 render.py（渲染前预检）共同调用。
用法: python scripts/fontcheck.py
退出码: 0=解析到期望字体, 1=解析异常或发生回退
"""
import json
import os
import re
import subprocess
import sys
import tempfile

# 以下两项必须与 subtitles.py 的 FONT_FAMILY、render.py 的 FONT_DIR 保持一致
FONT_FAMILY = "思源黑体"                              # 字体族名（思源黑体 / Source Han Sans SC）
FONT_DIR = r"D:\IT小章\字体\SimplifiedChinese"        # 静态字重 OTF 所在目录
EXPECT_PREFIX = "SourceHanSansSC"                    # 期望命中的字体文件族前缀

_TMP_ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: 320
PlayResY: 100
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: BOLD,{family},40,&H00FFFFFF,&H000000,&H80000000,-1,2,0,2,10,10,10,1
Style: REG,{family},40,&H00FFFFFF,&H000000,&H80000000,0,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:00.05,BOLD,,0,0,0,,字体自检
Dialogue: 0,0:00:00.00,0:00:00.05,REG,,0,0,0,,font check
"""


def _escape_filter_path(path):
    """ffmpeg 滤镜参数里的路径：反斜杠转正斜杠、冒号转义，外层由调用方加单引号。"""
    return path.replace("\\", "/").replace(":", "\\:")


def selected_fonts(font_family=FONT_FAMILY, font_dir=FONT_DIR, ffmpeg="ffmpeg"):
    """用最小 ASS 探测 libass 实际选中的字体。
    返回 [(字重:int, 实际字体名:str), ...]；无法解析时返回 None。"""
    ass_path = os.path.join(tempfile.gettempdir(), "fontcheck_probe.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(_TMP_ASS.format(family=font_family))

    vf = f"ass='{_escape_filter_path(ass_path)}'"
    if font_dir:
        vf += f":fontsdir='{_escape_filter_path(font_dir)}'"
    cmd = [ffmpeg, "-hide_banner", "-v", "verbose", "-f", "lavfi",
           "-i", "color=c=black:s=320x100:d=0.1", "-vf", vf,
           "-frames:v", "1", "-f", "null", "-"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except OSError:
        return None
    out = (r.stdout or "") + (r.stderr or "")
    picks = re.findall(r"fontselect:\s*\([^,]+,\s*(\d+),\s*\d+\)\s*->\s*([^,\r\n]+)", out)
    if not picks:
        return None
    return [(int(w), name.strip()) for w, name in picks]


def check(font_family=FONT_FAMILY, font_dir=FONT_DIR,
          expect_prefix=EXPECT_PREFIX, ffmpeg="ffmpeg"):
    """返回 (ok:bool, detail:str)。"""
    picks = selected_fonts(font_family, font_dir, ffmpeg)
    if picks is None:
        return False, (f"无法获取字体选择日志（未出现 fontselect 行）；"
                       f"请确认 ffmpeg 可用、字体族名「{font_family}」与目录 {font_dir} 是否正确")
    detail = "；".join(f"字重{w} -> {n}" for w, n in picks)
    bad = [(w, n) for w, n in picks if expect_prefix.lower() not in n.lower()]
    if bad:
        return False, (f"字体解析自检失败：期望命中 {expect_prefix} 系列，实际为 {detail}。"
                       f"libass 很可能已静默回退到其它字体（含版权风险），"
                       f"请检查字体是否安装、字体族名是否为「{font_family}」、目录 {font_dir} 是否存在")
    return True, detail


if __name__ == "__main__":
    ok, detail = check()
    print(json.dumps({"font_ok": ok, "detail": detail}, ensure_ascii=False, indent=2))
    sys.exit(0 if ok else 1)
