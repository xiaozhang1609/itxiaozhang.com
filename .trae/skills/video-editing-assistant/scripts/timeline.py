#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""时间轴工具：剪辑清单 -> 保留区间，以及「原时间轴 -> 成片时间轴」映射。

render.py（切段/拼接）与 subtitles.py（字幕时间轴重排）共用本模块，确保两处使用
**同一套**时间轴模型：先把删除清单合并成保留区间，再据此推算拼接点。这样就不会再出现
「渲染按合并后的段数、字幕按原始删除条数各算一套」而导致的偏移。

成片时间轴模型：保留段依次首尾相接，每两段之间叠化 FADE 秒（xfade/acrossfade），
因此每处拼接使成片时间比「保留总时长」少 FADE 秒。

改动叠化时长只改本文件的 FADE 一处（原 render.py 的 FADE 与 subtitles.py 的 XFADE 已合并到此）。
"""

FADE = 0.5       # 叠化时长（秒），渲染与字幕重排共用（单点）
_MIN_GAP = 0.05  # 小于该值的空隙视为噪声，不单独成段（并入删除区）


def kept_intervals(cuts, duration):
    """删除清单 -> 保留区间 [(start, end), ...]（升序、互不相邻、间隔 >= _MIN_GAP）。
    cuts: [{"start":..,"end":..}, ...]（原视频时间轴）；duration: 原视频总时长（秒）。"""
    cs = sorted((max(0.0, float(c["start"])), min(float(duration), float(c["end"])))
                for c in cuts)
    kept, cur = [], 0.0
    for s, e in cs:
        if s > cur + _MIN_GAP:
            kept.append((cur, s))
        cur = max(cur, e)
    if cur < float(duration) - _MIN_GAP:
        kept.append((cur, float(duration)))
    return kept


def output_duration(kept):
    """成片总时长 = 保留总长 - FADE × 拼接点数。"""
    if not kept:
        return 0.0
    return sum(e - s for s, e in kept) - FADE * (len(kept) - 1)


def map_time(t, kept):
    """原时间轴时刻 -> 成片时间轴时刻；落在删除区（无保留内容）返回 None。
    按「第 i 段之前有 i 个拼接点」累积扣减 FADE，天然处理开头/结尾的整段删除。"""
    cum = 0.0
    for s, e in kept:
        if s <= t <= e:
            return cum + (t - s)
        cum += (e - s) - FADE
    return None
