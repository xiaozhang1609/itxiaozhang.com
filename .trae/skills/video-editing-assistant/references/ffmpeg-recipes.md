# FFmpeg 命令手册（剪辑助手专用）

平台：Windows。所有命令默认在素材目录执行。路径含中文/空格时务必加引号。

## 1. 探测素材信息

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of json "input.mp4"
```

## 2. 提取 16kHz 单声道音频（供 whisper 识别）

```bash
ffmpeg -y -i "input.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le "audio_16k.wav"
```

## 3. 静音检测（辅助 analyze.py）

```bash
ffmpeg -i "input.mp4" -af silencedetect=noise=-35dB:d=3 -f null - 2>&1 | grep silence
```

## 4. 单次编码渲染（render.py 的实现思路，务必遵守）

**核心原则：全片只编码一次。** 分步（切段→拼接→烧字幕）会导致 2~3 代有损编码，屏录文字画面会明显糊掉。

一条命令内完成：split 复制流 → 每段 trim/atrim → xfade/acrossfade 链 → ass 烧字幕 → bgm 混音。

```bash
ffmpeg -y -i "input.mkv" -stream_loop -1 -i "bgm.mp3" -filter_complex "\
[0:v]split=3[sv0][sv1][sv2];\
[0:a]asplit=3[sa0][sa1][sa2];\
[sv0]trim=start=0:end=100,setpts=PTS-STARTPTS,fps=30,format=yuv420p[v0];\
[sa0]atrim=start=0:end=100,asetpts=PTS-STARTPTS[a0];\
[sv1]trim=start=105:end=200,setpts=PTS-STARTPTS,fps=30,format=yuv420p[v1];\
[sa1]atrim=start=105:end=200,asetpts=PTS-STARTPTS[a1];\
[sv2]trim=start=205:end=300,setpts=PTS-STARTPTS,fps=30,format=yuv420p[v2];\
[sa2]atrim=start=205:end=300,asetpts=PTS-STARTPTS[a2];\
[v0][v1]xfade=transition=fade:duration=0.5:offset=99.5[xv1];\
[a0][a1]acrossfade=d=0.5[xa1];\
[xv1][v2]xfade=transition=fade:duration=0.5:offset=199[xv2];\
[xa1][a2]acrossfade=d=0.5[xa2];\
[xv2]ass='final.ass':fontsdir='D\:/IT小章/字体/SimplifiedChinese',format=yuv420p[vout];\
[1:a]volume=0.08,afade=t=in:st=0:d=1.5,afade=t=out:st=297:d=3[bgm];\
[xa2][bgm]amix=inputs=2:duration=first:normalize=0[aout]" \
-map "[vout]" -map "[aout]" -c:v libx264 -crf 17 -preset slow -c:a aac -b:a 192k \
-movflags +faststart -shortest "final.mp4"
```

关键点：
- xfade 的 offset = `前 k 段总时长 - k × 0.5`；成片总时长 = `Σ段长 - 0.5×(段数-1)`
- 叠化时长 `FADE` **单点在 `scripts/timeline.py`**（render.py 与 subtitles.py 共用）；字幕时间轴映射也用该模块的 `map_time`，两处不会再各算一套
- 每段必须 `fps=<源帧率>,format=yuv420p` 归一化，否则 xfade 会报参数不匹配
- **坑 1**：滤镜参数之间漏逗号会报 `Error applying option '30.000000format' to filter 'fps'`
- **坑 2**：ass 滤镜输出可能是 4:4:4，直接接 libx264 会报 `high profile doesn't support 4:4:4` → 必须在 ass 后补 `,format=yuv420p`
- 质量参数：CRF 17 + preset slow（屏录文字画面），不要用 CRF 20 以下或 veryfast
- 字幕用 ASS（`ass=` 滤镜）而非 SRT，才能做双语不同字号
- **坑 3**：`ass` 滤镜的 `fontsdir` 指向中文路径时，路径要转成正斜杠、盘符冒号转义为 `\:`，并用单引号包裹整段（如 `fontsdir='D\:/IT小章/字体/SimplifiedChinese'`）；否则报 `Error parsing filterchain`。此转义在 `fontcheck.py` 的 `_escape_filter_path` 与 `render.py` 中统一处理
- **坑 4**：libass 找不到指定字体时会**静默回退**到其它字体（如微软雅黑），画面看不出异常但已带版权风险 → 渲染前必须做字体解析自检（`fontcheck.check`，用 `-v verbose` 抓 `fontselect` 行）

## 5. 字幕样式（ASS，双语）

**字体合规（硬性）**：统一 `思源黑体`（Source Han Sans SC，Adobe/Google 出品，SIL OFL 1.1，免费商用、允许烧录进视频与商业分发）。
使用本机已安装的**静态字重 OTF**（`D:\IT小章\字体\SimplifiedChinese\`：`SourceHanSansSC-Bold.otf` 用于中文、`SourceHanSansSC-Regular.otf` 用于英文），字体族名实测为 `思源黑体`。
**字体配置单点在 `scripts/fontcheck.py`**（`FONT_FAMILY` / `FONT_DIR` / `EXPECT_PREFIX`），`subtitles.py` / `render.py` / `setup_env.py` 均引用它；渲染时用 `ass` 滤镜的 `fontsdir` 精确指向该目录（路径转义见第 4 节「坑 3」），渲染前由 `fontcheck.check` 做解析自检，未解析到 `SourceHanSansSC` 系列即中止（防 libass 静默回退）。
**禁止使用 Microsoft YaHei（微软雅黑）/ 等线（Deng）**：著作权归北大方正，微软仅购得 Windows 内「显示 + 打印」授权，把字形烧进对外发布的视频属复制/发行，需方正单独授权（维权赔偿案例常见）。
**不要用系统自带 `NotoSansSC-VF.ttf`**：它是可变字体，libass 请求 Bold(700) 会落到 `NotoSansSC-Thin` 实例（笔画偏细）；且字体名稍不精确会被 DirectWrite 静默回退到 `MicrosoftYaHeiUI-Bold`，把版权风险带回来。改用静态字重 + `fontsdir` + 自检兜底。

```ass
Style: ZH,思源黑体,64,&H00FFFFFF,&H000000,&H80000000,-1,3,0,2,60,60,108,1
Style: EN,思源黑体,48,&H00D8D8D8,&H000000,&H80000000,0,2,0,2,60,60,50,1
```
- 中文在上：64 号白字 + 3px 黑边，MarginV=108
- 英文在下：48 号浅灰（约中文 75%，主流双语规范），MarginV=50；两行间距约 10px，紧凑不重叠
- 同一时间码写两条 Dialogue（一条 ZH、一条 EN），不要用 \N 拼在同一事件里
- 双语均严格单行：中文 ≤14 字；英文 ≤66 字符（超宽截到词边界）；`WrapStyle: 2` 禁止自动换行
- 字幕内不出现任何标点符号，停顿用空格；**术语自带的标点必须原样保留**（如 `sfc /scannow`、`ncpa.cpl`、`time.windows.com`、`intl.cpl`），保护清单由 `subtitles.py` 从共享白名单动态读取；英文缩写撇号（I'm）原样保留

## 6. 背景音乐：循环 + 压低音量 + 结尾淡出

在单命令渲染中直接合入（见第 4 节），关键滤镜：

```
[1:a]volume=0.08,afade=t=in:st=0:d=1.5,afade=t=out:st=<总时长-3>:d=3[bgm];
[人声][bgm]amix=inputs=2:duration=first:normalize=0[aout]
```

`-stream_loop -1` 让音乐循环铺满；`normalize=0` 避免 amix 自动衰减人声。

## 7. 抽帧抽查（渲染后质检）

```bash
ffmpeg -ss <秒> -i "final.mp4" -frames:v 1 -q:v 2 "check_<秒>.jpg"
```

## 8. 输出规格

- 视频：H.264 (libx264)，**CRF 17**，**preset slow**，保持源分辨率（>1080P 才缩到 1080P），yuv420p
- 音频：AAC 192k
- 容器：MP4（`-movflags +faststart` 便于网络播放）
- 交付前核对：`ffprobe` 看时长/帧率/码率是否合理，`volumedetect` 看峰值是否在 -3dB 以下不削波
