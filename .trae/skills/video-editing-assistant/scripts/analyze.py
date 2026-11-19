#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""内容分析：基于转录结果产出候选剪辑草案（供 AI 语义复核后生成最终 cutlist.json）。
用法: python analyze.py <transcript.json> --out <输出目录>
产出: <out>/cutlist_draft.json  （候选：长静音 / 无效语气词 / 疑似重复对）

注意：本脚本只做"候选发现"。重复段落的最终删除决策必须由 AI 通读全文后做出
（内容优先于画面；拿不准一律保留）。最终清单文件名为 cutlist.json，格式：
{
  "video_duration": 123.4,
  "cuts": [{"start": 10.0, "end": 20.0, "type": "duplicate|silence|filler", "reason": "..."}]
}
"""
import argparse
import json
import os
import re
import sys

FILLER_CHARS = set("嗯呃啊哦噢额哼唉")
FILLER_WORDS = {"那个", "就是", "然后呢", "这个", "就是说"}

def ngrams(text, n=3):
    t = re.sub(r"[\s，。！？、,.!?;；：:\"'\"'（）()【】\[\]]", "", text)
    return {t[i:i+n] for i in range(max(0, len(t)-n+1))} or ({t} if t else set())

def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def is_filler_only(text):
    t = re.sub(r"[\s，。！？、,.!?]", "", text)
    if not t:
        return True
    if all(c in FILLER_CHARS for c in t):
        return True
    return t in FILLER_WORDS

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--out", required=True)
    ap.add_argument("--silence-threshold", type=float, default=3.0, help="长静音阈值秒，默认 3")
    args = ap.parse_args()

    with open(args.transcript, encoding="utf-8") as f:
        data = json.load(f)
    segs = data["segments"]
    duration = data.get("duration", segs[-1]["end"] if segs else 0)

    draft = {"video_duration": duration,
             "silence_candidates": [], "filler_candidates": [], "duplicate_pairs": []}

    # 1. 段间长静音（候选缩短；是否删除需结合画面内容判断：安装/扫描/修复过程保留）
    for a, b in zip(segs, segs[1:]):
        gap = b["start"] - a["end"]
        if gap >= args.silence_threshold:
            draft["silence_candidates"].append({
                "start": round(a["end"] + 0.3, 3), "end": round(b["start"] - 0.3, 3),
                "duration": round(gap, 3),
                "note": f"段间静音 {gap:.1f}s；若是系统启动/安装/扫描/修复过程请保留"
            })

    # 2. 无效语气词（整段只是语气词，或语气词+长停顿）
    for s in segs:
        if is_filler_only(s["text"]):
            dur = s["end"] - s["start"]
            prev_end = segs[s["id"]-1]["end"] if s["id"] > 0 else 0
            next_start = segs[s["id"]+1]["start"] if s["id"]+1 < len(segs) else duration
            ctx_gap = max(s["start"] - prev_end, next_start - s["end"])
            draft["filler_candidates"].append({
                "start": s["start"], "end": s["end"], "text": s["text"],
                "duration": round(dur, 3), "context_gap": round(ctx_gap, 3),
                "suggest": "delete" if (dur > 1.5 or ctx_gap > 2.0) else "keep",
                "note": "流畅讲述中的少量语气词应保留；长停顿夹无效语气词才删"
            })

    # 3. 疑似重复对（文本相似度候选，最终由 AI 语义复核：一般删前留后，但前面有独有信息则保留）
    grams = [ngrams(s["text"]) for s in segs]
    n = len(segs)
    for i in range(n):
        if len(segs[i]["text"]) < 6:
            continue
        for j in range(i+1, n):
            if len(segs[j]["text"]) < 6:
                continue
            sim = jaccard(grams[i], grams[j])
            if sim >= 0.65:
                draft["duplicate_pairs"].append({
                    "earlier": {"start": segs[i]["start"], "end": segs[i]["end"], "text": segs[i]["text"]},
                    "later":   {"start": segs[j]["start"], "end": segs[j]["end"], "text": segs[j]["text"]},
                    "similarity": round(sim, 3),
                    "suggest": "delete_earlier",
                    "note": "复核：后段是否更完整准确？前段是否有独有信息？拿不准则都保留"
                })

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "cutlist_draft.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)

    print(f"候选分析完成 -> {path}")
    print(f"  长静音候选: {len(draft['silence_candidates'])}")
    print(f"  语气词候选: {len(draft['filler_candidates'])} (建议删 {sum(1 for x in draft['filler_candidates'] if x['suggest']=='delete')})")
    print(f"  疑似重复对: {len(draft['duplicate_pairs'])}")
    print("下一步：AI 通读全文语义复核，产出最终 cutlist.json / transcript_final.srt / 口播文本.txt")

if __name__ == "__main__":
    main()
