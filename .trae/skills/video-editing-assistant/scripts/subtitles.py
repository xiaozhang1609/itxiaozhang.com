#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""双语字幕工具。

子命令:
  split  <in.srt> --out <cues_zh.json>
        把整句 SRT 按标点/语义拆成短句 cue（每条中文 ≤ MAX_ZH 字），时间按字数比例分配。
        产出 JSON: [{"start":s,"end":e,"zh":"..."}]（原视频时间轴）。
        之后由 AI 为每条补 "en" 字段（简洁意译，术语按白名单原样），得到 cues_bilingual.json。

  build  <cues_bilingual.json> --cutlist <cutlist.json> --video <源视频> --outdir <素材output目录> --basename <视频名>
        按剪辑清单把 cue 时间重排到成片时间轴，落在被删区间内的 cue 丢弃。
        字幕规范: 中文在上(64号/白字黑边) 英文在下(48号=中文75%/浅灰) 双语均单行
        全部标点符号清除(停顿用空格) 技术术语(sfc /scannow ncpa.cpl 等)受保护原样保留
        字体固定 思源黑体 (Source Han Sans SC, SIL OFL 1.1 免费商用; 字体配置单点在 fontcheck.py), 禁用微软雅黑
        产出: <outdir>/work/final.ass（烧录用）
              <outdir>/<basename>_字幕.srt（外挂双语 SRT，上行中文下行英文）
"""
import argparse
import json
import os
import re
import subprocess
import sys

from fontcheck import FONT_FAMILY  # 字体配置单点（FONT_FAMILY / FONT_DIR / 解析自检）
from timeline import kept_intervals, map_time  # 时间轴模型（与 render.py 共用，FADE 单点）

MAX_ZH = 14          # 每条中文字幕最多字数
ZH_FS, EN_FS = 64, 48  # ASS 字号（PlayResY=1080 下即像素），英文为中文 75%（主流双语规范）
MAX_EN_CHARS = 66    # 英文单行硬上限（估算宽度不超过画面；超出时截到词边界）

# 字体：思源黑体（Source Han Sans SC），SIL OFL 1.1 开源、免费商用，
# 允许烧录进视频/商业变现/嵌入分发。字体**配置单点**在 fontcheck.py
# （FONT_FAMILY + FONT_DIR + 解析自检），subtitles.py / render.py / setup_env.py 均引用它，
# 避免多处常量漂移。
# 禁用 Microsoft YaHei（微软雅黑）：雅黑著作权归北大方正，微软仅购买 Windows 内显示+打印授权，
# 把字形烧进公开发布的视频属于复制/发行，需方正单独授权（维权赔偿案例常见）。
# 也不要用系统自带 NotoSansSC-VF.ttf：它是可变字体，请求 Bold 会落到 Thin、
# 字体名稍不精确会被静默回退到雅黑，把版权风险重新带回来。

# 需要清除的标点（中英文），停顿语义由空格承担
_PUNCT_ZH = "，。、！？；：·…—～“”‘’（）()《》【】"
_PUNCT_EN = ",.?!;:\"'"
_ALL_PUNCT = set(_PUNCT_ZH) | set(_PUNCT_EN)

# 英文缩写：撇号属于单词的一部分，需原样保留（与术语无关，固定清单）
_CONTRACTIONS = [
    "I'm", "i'm", "don't", "Don't", "can't", "Can't", "won't", "it's", "It's",
    "that's", "you're", "You're", "we're", "We're", "let's", "Let's", "what's",
    "doesn't", "didn't", "isn't", "aren't", "wasn't", "weren't", "haven't",
    "hasn't", "couldn't", "shouldn't", "wouldn't", "there's", "here's",
]

# 共享白名单（唯一真源，与 subtitle-assistant 共用）
_SHARED_TERMINOLOGY = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "shared", "terminology.md"))

# 兜底：万一共享白名单读不到，至少保护这些「含标点的命令术语」，避免其标点被误清
_FALLBACK_TERMS = ["sfc /scannow", "ipconfig /flushdns", "ncpa.cpl",
                   "time.windows.com", "intl.cpl"]


def load_whitelist_terms(path=_SHARED_TERMINOLOGY):
    """读取共享白名单「① 标准写法清单」代码块，返回词条列表；读不到返回 None。"""
    try:
        with open(path, encoding="utf-8") as f:
            md = f.read()
    except OSError:
        return None
    sec = re.search(r"①.*?(?=##\s*②)", md, re.S)
    block = re.search(r"```(.*?)```", sec.group(0), re.S) if sec else None
    if not block:
        return None
    return [ln.strip() for ln in block.group(1).splitlines() if ln.strip()]


def _build_protected_terms():
    """需原样保留标点的术语 = 共享白名单里含标点的词条 + 英文缩写撇号；长词优先替换。"""
    terms = load_whitelist_terms()
    if terms is None:
        terms = _FALLBACK_TERMS
        print(f"[subtitles] 警告：未读到共享白名单 {_SHARED_TERMINOLOGY}，"
              f"已用内置兜底术语清单保护标点", file=sys.stderr)
    punct_terms = [t for t in terms if any(c in _ALL_PUNCT for c in t)]
    return sorted(set(punct_terms) | set(_CONTRACTIONS), key=len, reverse=True)


# 技术术语保护清单：这些子串内的标点（如 sfc /scannow 的空格与斜杠、time.windows.com 的点）
# 是术语的一部分，必须原样保留。唯一真源 = 共享白名单，不在本文件另行硬编码，避免漂移。
PROTECTED_TERMS = _build_protected_terms()

def strip_punct(s):
    """清除全部标点，词边界标点替换为空格；术语先保护再还原。"""
    if not s:
        return s.strip()
    placeholders = {}
    for i, term in enumerate(PROTECTED_TERMS):
        key = f"\x00{i}\x00"
        if term in s:
            s = s.replace(term, key)
            placeholders[key] = term
    out = []
    for ch in s:
        if ch in _PUNCT_ZH or ch in _PUNCT_EN:
            out.append(" ")
        else:
            out.append(ch)
    s = "".join(out)
    for key, term in placeholders.items():
        s = s.replace(key, term)
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s

def clip_en(text, max_chars=MAX_EN_CHARS):
    """英文强制单行：超出宽度上限时截到最近的词边界（是否截断由调用方统计并提示，不静默）。"""
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rfind(" ")
    return text[:cut].rstrip() if cut > 0 else text[:max_chars].rstrip()

def escape_ass(text):
    """ASS 文本转义：`{}` 是特效块定界符，`\\` 后接 n/N/h 会被 libass 当换行/硬空格。
    字幕应为纯文本，正常术语（sfc /scannow、time.windows.com 等）只用正斜杠与点，
    故把裸 `{` `}` 与反斜杠直接去除，避免误触发换行/特效（不改动其它字符）。"""
    return text.replace("\\", "").replace("{", "").replace("}", "")

def probe_duration(video):
    """用 ffprobe 取容器实际时长，与 render.py 的时长口径一致；失败返回 None。"""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", video],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return None

def parse_srt_ts(ts):
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

def fmt_srt_ts(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1)*1000):03d}"

def fmt_ass_ts(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{int(s):02d}.{int((s % 1)*100):02d}"

def parse_srt(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    cues = []
    for b in re.split(r"\n\s*\n", content.strip()):
        lines = b.strip().splitlines()
        if len(lines) < 3:
            continue
        m = re.match(r"(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)", lines[1])
        if not m:
            continue
        text = "".join(lines[2:]).strip()
        cues.append((parse_srt_ts(m.group(1)), parse_srt_ts(m.group(2)), text))
    return cues

def split_text(text, max_len=MAX_ZH):
    parts = [p.strip() for p in re.findall(r"[^，。、！？；：]+[，。、！？；：]?", text) if p.strip()]
    chunks, cur = [], ""
    for p in parts:
        if len(p) > max_len:
            if cur:
                chunks.append(cur); cur = ""
            while len(p) > max_len:
                chunks.append(p[:max_len].rstrip("，。、"))
                p = p[max_len:].lstrip("，。、")
            cur = p
        elif len(cur) + len(p) <= max_len:
            cur += p
        else:
            if cur:
                chunks.append(cur)
            cur = p
    if cur:
        chunks.append(cur)
    return [c for c in chunks if c]

def cmd_split(args):
    cues = parse_srt(args.infile)
    out = []
    for st, ed, text in cues:
        chunks = split_text(text)
        if not chunks:
            continue
        n = sum(len(c) for c in chunks)
        t = st
        for c in chunks:
            d = (ed - st) * len(c) / n
            out.append({"start": round(t, 3), "end": round(t + d, 3), "zh": c})
            t += d
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"拆分完成: {len(cues)} 句 -> {len(out)} 条短句 -> {args.out}")
    print("下一步: AI 为每条补 en 字段 -> cues_bilingual.json, 然后 build")

ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ZH,{FONT_FAMILY},{ZH_FS},&H00FFFFFF,&H000000,&H80000000,-1,3,0,2,60,60,108,1
Style: EN,{FONT_FAMILY},{EN_FS},&H00D8D8D8,&H000000,&H80000000,0,2,0,2,60,60,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def cmd_build(args):
    with open(args.infile, encoding="utf-8") as f:
        cues = json.load(f)
    with open(args.cutlist, encoding="utf-8") as f:
        cl = json.load(f)
    cuts = cl.get("cuts", [])
    # 时长口径必须与 render.py 一致：优先用 ffprobe 实测（--video），其次 cutlist，最后 cues 末值。
    # 否则两脚本的保留区间右边界会差零点几秒，片尾字幕可能偏移/丢失。
    duration = probe_duration(args.video) if args.video else None
    if not duration:
        duration = cl.get("video_duration")
    if not duration:
        duration = max((c["end"] for c in cues), default=0.0)

    # 与 render.py 共用同一套保留区间模型，字幕时间轴才与成片严格一致
    segs = kept_intervals(cuts, duration)

    kept, truncated = [], 0
    for c in cues:
        st, ed = map_time(c["start"], segs), map_time(c["end"], segs)
        if st is None or ed is None or ed <= st:
            continue
        zh = escape_ass(strip_punct(c["zh"]))
        raw_en = escape_ass(strip_punct(c.get("en", "")))
        en = clip_en(raw_en)
        if len(raw_en) > MAX_EN_CHARS:
            truncated += 1
        if not zh and not en:
            continue
        kept.append({"start": st, "end": ed, "zh": zh, "en": en})

    os.makedirs(os.path.join(args.outdir, "work"), exist_ok=True)
    ass_path = os.path.join(args.outdir, "work", "final.ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        for c in kept:
            f.write(f"Dialogue: 0,{fmt_ass_ts(c['start'])},{fmt_ass_ts(c['end'])},ZH,,0,0,0,,{c['zh']}\n")
            if c["en"]:
                f.write(f"Dialogue: 0,{fmt_ass_ts(c['start'])},{fmt_ass_ts(c['end'])},EN,,0,0,0,,{c['en']}\n")

    srt_path = os.path.join(args.outdir, f"{args.basename}_字幕.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, c in enumerate(kept, 1):
            en_line = f"\n{c['en']}" if c["en"] else ""
            f.write(f"{i}\n{fmt_srt_ts(c['start'])} --> {fmt_srt_ts(c['end'])}\n{c['zh']}{en_line}\n\n")

    print(f"双语字幕完成: {len(kept)} 条")
    if truncated:
        print(f"  注意: {truncated} 条英文超 {MAX_EN_CHARS} 字符已截到词边界，建议精简该条 en 译文")
    print(f"  烧录用 ASS -> {ass_path}")
    print(f"  外挂双语 SRT -> {srt_path}")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("split")
    p1.add_argument("infile")
    p1.add_argument("--out", required=True)
    p1.set_defaults(func=cmd_split)

    p2 = sub.add_parser("build")
    p2.add_argument("infile")
    p2.add_argument("--cutlist", required=True)
    p2.add_argument("--video", help="源视频路径：用 ffprobe 实测时长，确保与 render.py 口径一致（强烈建议传）")
    p2.add_argument("--outdir", required=True)
    p2.add_argument("--basename", required=True)
    p2.set_defaults(func=cmd_build)

    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
