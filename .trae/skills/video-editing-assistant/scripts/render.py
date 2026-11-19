#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""渲染（v2 单次编码）：一条 FFmpeg 命令完成 剪切+叠化转场+双语字幕烧录+背景音乐混音。
全片只编码一次（此前版本编码三次导致画质下降），保留源帧率与源分辨率，CRF 17 / preset slow。

用法:
  python render.py <视频> --cutlist <cutlist.json> --ass <final.ass> \
      --bgm "D:\\IT小章\\bgm\\mixkit-digital-clouds-175.mp3" --out <output目录>
产出: <out>/<视频名>_成片.mp4

字幕字体固定为 思源黑体，渲染时用 ffmpeg 的 fontsdir 指向静态字重目录（fontcheck.FONT_DIR）；
渲染开始前会先做一次字体解析自检（fontcheck.check），确认 libass 未静默回退到其它字体。

cutlist.json 格式（时间均指原视频时间轴）:
  {"video_duration": 123.4,
   "cuts": [{"start": 10.0, "end": 20.0, "type": "duplicate|silence|filler", "reason": "..."}]}

final.ass 由 subtitles.py build 生成，时间轴已重排为成片时间轴，直接用 ass 滤镜烧录。
"""
import argparse
import json
import os
import subprocess
import sys

from fontcheck import FONT_DIR, check as font_check  # 字体配置单点 + 解析自检
from timeline import FADE, kept_intervals            # 时间轴模型（与 subtitles.py 共用，单点）

BGM_VOL = 0.08      # 背景音乐音量（约人声 8%）
CRF = "17"          # 高保真（屏录文字画面）
PRESET = "slow"

def run(cmd, desc):
    print(f"[render] {desc} ...", flush=True)
    # encoding 显式指定：中文 Windows 默认 cp936，ffmpeg 输出含中文时会解码报错
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"失败: {desc}\n{(r.stderr or '')[-3000:]}", file=sys.stderr)
        sys.exit(1)

def probe_json(path, args_str):
    r = subprocess.run(["ffprobe", "-v", "error", *args_str, "-of", "json", path],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return json.loads(r.stdout)

def probe_video_info(path):
    j = probe_json(path, ["-show_entries", "format=duration",
                           "-select_streams", "v:0",
                           "-show_entries", "stream=width,height,avg_frame_rate"])
    st = j["streams"][0]
    dur = float(j["format"]["duration"])
    num, den = st.get("avg_frame_rate", "30/1").split("/")
    fps = float(num) / float(den) if float(den) else 30.0
    return dur, st["width"], st["height"], fps

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--cutlist", required=True)
    ap.add_argument("--ass", required=True)
    ap.add_argument("--bgm", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # 渲染前字体预检：字体解析失败（回退到雅黑等）立即中止，避免长时间渲染后才发现字体不合规
    fok, fdetail = font_check()
    if not fok:
        print(f"字体自检未通过，已中止渲染：{fdetail}", file=sys.stderr)
        sys.exit(1)
    print(f"[render] 字体自检通过：{fdetail}", flush=True)

    with open(args.cutlist, encoding="utf-8") as f:
        cl = json.load(f)

    duration, w, h, fps = probe_video_info(args.video)
    cuts = sorted(cl.get("cuts", []), key=lambda c: c["start"])
    kept = kept_intervals(cuts, duration)
    if not kept:
        print("错误：剪辑清单删除了全部内容", file=sys.stderr)
        sys.exit(1)

    base = os.path.splitext(os.path.basename(args.video))[0]
    os.makedirs(args.out, exist_ok=True)
    final_mp4 = os.path.join(args.out, f"{base}_成片.mp4")
    n = len(kept)
    durs = [e - s for s, e in kept]

    # 分辨率：>1080P 或宽高为奇数时才缩放；否则保持源分辨率
    tw, th = w, h
    if tw > 1920 or th > 1080:
        tw, th = 1920, 1080
    tw -= tw % 2; th -= th % 2
    scale = ("" if (tw, th) == (w, h) else f"scale={tw}:{th},")

    # ---- 构建单命令 filter_complex ----
    filters = []
    # 复制流给每段
    labels_v = " ".join(f"[sv{i}]" for i in range(n))
    labels_a = " ".join(f"[sa{i}]" for i in range(n))
    filters.append(f"[0:v]split={n}{labels_v}")
    filters.append(f"[0:a]asplit={n}{labels_a}")
    # 每段 trim + 规范化
    for i, (s, e) in enumerate(kept):
        filters.append(f"[sv{i}]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS,"
                       f"fps={fps:.6f},{scale}format=yuv420p[v{i}]")
        filters.append(f"[sa{i}]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]")
    # xfade / acrossfade 链
    cur_v, cur_a = "[v0]", "[a0]"
    off = 0.0
    for k in range(1, n):
        off += durs[k-1] - FADE
        cur_v2, cur_a2 = f"[xv{k}]", f"[xa{k}]"
        filters.append(f"{cur_v}[v{k}]xfade=transition=fade:duration={FADE}:offset={off:.3f}{cur_v2}")
        filters.append(f"{cur_a}[a{k}]acrossfade=d={FADE}{cur_a2}")
        cur_v, cur_a = cur_v2, cur_a2
    total = sum(durs) - FADE * (n - 1)
    # 字幕烧录（ASS 自带样式）；fontsdir 精确指向静态字重目录，避免字体静默回退
    ass_esc = os.path.abspath(args.ass).replace("\\", "/").replace(":", "\\:")
    fonts_esc = os.path.abspath(FONT_DIR).replace("\\", "/").replace(":", "\\:")
    filters.append(f"{cur_v}ass='{ass_esc}':fontsdir='{fonts_esc}',format=yuv420p[vout]")
    # 背景音乐 + 混音
    fade_out_st = max(0.0, total - 3.0)
    filters.append(f"[1:a]volume={BGM_VOL},afade=t=in:st=0:d=1.5,"
                   f"afade=t=out:st={fade_out_st:.3f}:d=3[bgm]")
    filters.append(f"{cur_a}[bgm]amix=inputs=2:duration=first:normalize=0[aout]")

    # 滤镜图写入脚本文件，用 -filter_complex_script 传入：
    # 长视频 + 多剪辑点时滤镜串会超过 Windows 命令行 32767 字符上限（保留段约 >120 段即越界），
    # 直接放在命令行会导致 CreateProcess 失败，故落盘再引用。
    work_dir = os.path.join(args.out, "work")
    os.makedirs(work_dir, exist_ok=True)
    filter_script = os.path.join(work_dir, "filter_complex.txt")
    with open(filter_script, "w", encoding="utf-8") as f:
        f.write(";\n".join(filters))

    cmd = ["ffmpeg", "-y", "-i", args.video,
           "-stream_loop", "-1", "-i", args.bgm,
           "-filter_complex_script", filter_script,
           "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-crf", CRF, "-preset", PRESET,
           "-profile:v", "high", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", "-shortest", final_mp4]
    run(cmd, f"单次编码渲染（{n} 段叠化 + 双语字幕 + 背景音乐，源 {w}x{h}@{fps:.1f}）")

    fdur = probe_json(final_mp4, ["-show_entries", "format=duration"])
    print(f"[render] 完成 -> {final_mp4}")
    print(f"[render] 成片时长 {float(fdur['format']['duration']):.1f}s（原 {duration:.1f}s）")

if __name__ == "__main__":
    main()
