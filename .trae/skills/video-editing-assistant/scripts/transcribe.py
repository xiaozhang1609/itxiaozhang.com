#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语音识别：faster-whisper 转录视频语音，产出词级时间戳 JSON 和原始 SRT。
用法: python transcribe.py <视频路径> --out <输出目录> [--model small]
产出: <out>/transcript.json, <out>/transcript_raw.srt
"""
import argparse
import json
import os
import subprocess
import sys

# 国内网络直连 HuggingFace 常 502，默认走镜像（已缓存模型则不会触发下载）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

def extract_audio(video, wav_path):
    cmd = ["ffmpeg", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000",
           "-c:a", "pcm_s16le", wav_path]
    # encoding 显式指定：中文 Windows 默认 cp936，ffmpeg 输出含中文时会解码报错
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("ffmpeg 提取音频失败:", (r.stderr or "")[-2000:], file=sys.stderr)
        sys.exit(1)

def fmt_ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

def load_wav_float32(wav_path):
    """用标准库 wave 读取 16kHz 单声道 pcm_s16le，返回 float32 numpy 数组。
    绕过 PyAV 版本兼容问题（faster-whisper 的 decode_audio 依赖 av）。"""
    import wave
    import numpy as np
    with wave.open(wav_path, "rb") as w:
        assert w.getsampwidth() == 2 and w.getnchannels() == 1, "需要 16bit 单声道 wav"
        frames = w.readframes(w.getnframes())
    return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="small", help="whisper 模型: tiny/base/small/medium，默认 small")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"],
                    help="推理设备：auto=有可用 GPU 就用否则 CPU（默认），cpu 最稳，cuda 强制 GPU")
    ap.add_argument("--force", action="store_true",
                    help="即使已有转录结果也重新识别（默认存在则跳过，避免重复跑几分钟）")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    jpath = os.path.join(args.out, "transcript.json")
    spath = os.path.join(args.out, "transcript_raw.srt")
    if os.path.exists(jpath) and os.path.exists(spath) and not args.force:
        print(f"已存在转录结果，跳过识别（如需重跑加 --force）:\n  -> {jpath}\n  -> {spath}")
        return

    wav = os.path.join(args.out, "audio_16k.wav")
    print(f"[1/2] 提取音频 -> {wav}")
    extract_audio(args.video, wav)

    print(f"[2/2] faster-whisper 识别（模型 {args.model}，设备 {args.device}，首次运行自动下载约 500MB）...")
    from faster_whisper import WhisperModel
    compute_type = "int8" if args.device == "cpu" else "auto"
    try:
        model = WhisperModel(args.model, device=args.device, compute_type=compute_type)
    except Exception as e:
        if args.device == "auto":
            print(f"设备 auto 初始化失败（{e}），回退 CPU int8", file=sys.stderr)
            model = WhisperModel(args.model, device="cpu", compute_type="int8")
        else:
            raise
    audio = load_wav_float32(wav)
    segments_iter, info = model.transcribe(
        audio, language="zh", word_timestamps=True,
        vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500),
        beam_size=5)

    segments = []
    for seg in segments_iter:
        segments.append({
            "id": len(segments),
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "words": [{"w": w.word, "start": round(w.start, 3), "end": round(w.end, 3)}
                      for w in (seg.words or [])],
        })
        if len(segments) % 20 == 0:
            print(f"  已识别 {len(segments)} 段，进度 {seg.end:.0f}s / {info.duration:.0f}s", flush=True)

    data = {"video": os.path.abspath(args.video), "language": info.language,
            "duration": round(info.duration, 3), "segments": segments}
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(spath, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"{seg['id']+1}\n{fmt_ts(seg['start'])} --> {fmt_ts(seg['end'])}\n{seg['text']}\n\n")

    print(f"完成: {len(segments)} 段, 时长 {info.duration:.1f}s")
    print(f"  -> {jpath}")
    print(f"  -> {spath}")

if __name__ == "__main__":
    main()
