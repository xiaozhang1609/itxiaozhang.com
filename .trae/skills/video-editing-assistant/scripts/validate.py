#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 交接文件校验：把「字段缺失 / 时间倒挂 / 区间越界 / 字数超限」等低级错误在渲染前拦下。

背景：cutlist.json、cues_bilingual.json 由 AI 手写，格式或时间戳出错时下游可能**静默**出错
（如字幕丢失、偏移）。渲染前先跑本脚本，把问题显式暴露出来。

用法:
  python validate.py <cutlist.json>
  python validate.py <cues_bilingual.json>
  python validate.py <文件> --duration 123.4     # 覆盖/补充视频时长（秒）

类型自动识别：含 "cuts" 的对象 => 剪辑清单；数组 => 字幕 cue 列表。
退出码: 0=通过（可含警告）, 1=存在错误
"""
import argparse
import json
import sys

from subtitles import MAX_ZH, MAX_EN_CHARS        # 字幕规格单点
from timeline import kept_intervals, output_duration  # 时间轴模型（推算成片时长）


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_cutlist(data, duration_override=None):
    errors, warns = [], []
    duration = duration_override or data.get("video_duration")
    if not _num(duration) or duration <= 0:
        errors.append("缺少有效的 video_duration（可用 --duration 指定）")
        duration = None
    cuts = data.get("cuts")
    if not isinstance(cuts, list):
        errors.append("cuts 必须是数组")
        return errors, warns, {}

    for i, c in enumerate(cuts):
        if not isinstance(c, dict):
            errors.append(f"cuts[{i}] 不是对象")
            continue
        s, e = c.get("start"), c.get("end")
        if not (_num(s) and _num(e)):
            errors.append(f"cuts[{i}] start/end 缺失或非数字")
            continue
        if s >= e:
            errors.append(f"cuts[{i}] start({s}) 不小于 end({e})")
        if s < 0:
            errors.append(f"cuts[{i}] start 为负 {s}")
        if duration is not None and e > duration + 0.5:
            warns.append(f"cuts[{i}] end({e}) 超出视频时长({duration:.1f})，将被截断")
        if not c.get("type"):
            warns.append(f"cuts[{i}] 缺 type（duplicate/silence/filler）")

    info = {}
    if duration is not None:
        segs = kept_intervals(cuts, duration)
        info["原片时长"] = round(float(duration), 1)
        info["保留段数"] = len(segs)
        info["成片时长"] = round(output_duration(segs), 1)
        info["删除处数"] = len(cuts)
    return errors, warns, info


def validate_cues(data, duration_override=None):
    errors, warns = [], []
    if not isinstance(data, list):
        errors.append("cue 文件必须是数组")
        return errors, warns, {}

    prev_start = -1.0
    zh_over = en_over = 0
    for i, c in enumerate(data):
        if not isinstance(c, dict):
            errors.append(f"[{i}] 不是对象")
            continue
        s, e, zh = c.get("start"), c.get("end"), c.get("zh")
        if not (_num(s) and _num(e)):
            errors.append(f"[{i}] start/end 缺失或非数字")
            continue
        if s >= e:
            errors.append(f"[{i}] start({s}) 不小于 end({e})")
        if s < prev_start - 0.001:
            warns.append(f"[{i}] start({s}) 早于上一条 start({prev_start:.3f})，时间轴非单调")
        prev_start = s
        if not zh:
            errors.append(f"[{i}] 缺 zh 文本")
        elif len(zh) > MAX_ZH:
            zh_over += 1
        en = c.get("en", "")
        if en and len(en) > MAX_EN_CHARS:
            en_over += 1
        if duration_override and e > duration_override + 0.5:
            warns.append(f"[{i}] end({e}) 超出时长({duration_override:.1f})")

    if zh_over:
        warns.append(f"{zh_over} 条中文超过 {MAX_ZH} 字（应拆成更短句）")
    if en_over:
        warns.append(f"{en_over} 条英文超过 {MAX_EN_CHARS} 字符（渲染时会被截到词边界）")
    return errors, warns, {"条数": len(data)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--duration", type=float, help="覆盖/补充视频时长（秒）")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "cuts" in data:
        kind, (errors, warns, info) = "剪辑清单 cutlist", validate_cutlist(data, args.duration)
    elif isinstance(data, list):
        kind, (errors, warns, info) = "字幕 cue 列表", validate_cues(data, args.duration)
    else:
        print(f"无法识别文件类型（既不是含 cuts 的对象，也不是数组）: {args.file}", file=sys.stderr)
        sys.exit(1)

    print(f"校验: {args.file}  [{kind}]")
    for k, v in info.items():
        print(f"  {k}: {v}")
    for w in warns:
        print(f"  [警告] {w}")
    for e in errors:
        print(f"  [错误] {e}", file=sys.stderr)
    if errors:
        print(f"未通过：{len(errors)} 个错误（请修正后重跑）", file=sys.stderr)
        sys.exit(1)
    print(f"通过{'（%d 条警告）' % len(warns) if warns else ''}")


if __name__ == "__main__":
    main()
