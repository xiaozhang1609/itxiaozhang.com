# 剪辑助手（video-editing-assistant）· 说明与配置

本文件是本项目（Trae + itxiaozhang.com）内该技能的**说明与配置文档**。日常使用直接说触发词（见 `SKILL.md`）即可；本文件用于查阅目录结构、执行流程、脚本契约、配置清单与版权合规信息。

本文件夹是**自包含的**：只依赖 Python + FFmpeg + faster-whisper，不依赖任何 AI 产品的专有 API。AI 只负责「理解内容、做语义判断、调用脚本」，脚本负责「实际剪辑渲染」，二者通过标准 JSON 文件交接，因此可换任意 Agent。

---

## 1. 目录结构

```
.trae/skills/
├── shared/
│   └── terminology.md       ← 术语白名单（唯一真源，与 subtitle-assistant 共用）
├── subtitle-assistant/      ← 字幕助手（另一技能）
└── video-editing-assistant/
    ├── README.md            ← 本文件：说明与配置（目录/流程/脚本契约/配置清单/合规）
    ├── SKILL.md             ← Trae Skill 入口（触发词 + 流程 + 硬性规则）
    ├── references/
    │   ├── requirements.md  ← 需求规则书：去重/语气词/静音判断细则（必读）
    │   └── ffmpeg-recipes.md← FFmpeg 命令手册（含已踩过的坑）
    └── scripts/
        ├── setup_env.py     ← 环境自检 + 自动安装依赖
        ├── fontcheck.py     ← 字体配置单点（FONT_FAMILY/FONT_DIR）+ 字体解析自检
        ├── timeline.py      ← 时间轴模型（保留区间/时间映射 + 叠化 FADE）单点
        ├── transcribe.py    ← 语音识别 → transcript.json / transcript_raw.srt
        ├── analyze.py       ← 候选发现 → cutlist_draft.json
        ├── subtitles.py     ← 双语短句字幕：split / build 两个子命令
        ├── validate.py      ← AI 交接文件校验（cutlist / cues 字段、时间、区间、字数）
        └── render.py        ← 单次编码渲染 → 成片 MP4
```

## 2. 依赖与安装

| 依赖 | 用途 | 备注 |
|---|---|---|
| Python 3.10+ | 跑脚本 | 实测 3.13 可用 |
| FFmpeg / FFprobe | 剪辑渲染 | 含 `libass`、`libx264`；`setup_env.py` 可自动装 |
| faster-whisper | 中文语音识别 + 词级时间戳 | pip 包，首次自动下载约 500MB 模型 |
| numpy | 相似度计算 | pip 包 |

一键自检（缺什么自动装什么，同时校验字幕字体：① 静态字重文件是否存在；② libass 能否正确解析到该字体、未静默回退）：

```bash
python scripts/setup_env.py
```

输出 `{"ready": true, ...}` 才继续。国内网络首次下载模型如直连失败，设置镜像：

```bash
HF_ENDPOINT=https://hf-mirror.com python scripts/transcribe.py ...
```

## 3. 完整执行流程

约定：`<DIR>` = 素材目录（里面**恰好一个**视频文件）；`<OUT>` = `<DIR>/output`；`<WORK>` = `<OUT>/work`；`<NAME>` = 视频文件名（不含扩展名）。

**原始视频永不覆盖**，所有中间产物写入 `<WORK>`，成品写入 `<OUT>`。

| 步 | 命令 / 动作 | 产出 |
|---|---|---|
| 0 | 校验：`<DIR>` 有且仅有一个视频；背景音乐文件存在且可读。不满足则**停下问用户** | — |
| 1 | `python scripts/setup_env.py` | 环境就绪 |
| 2 | `python scripts/transcribe.py "<DIR>/视频.mkv" --out "<WORK>" --model small` | `transcript.json`、`transcript_raw.srt`（已存在则自动跳过，可加 `--force` 重跑） |
| 3 | `python scripts/analyze.py "<WORK>/transcript.json" --out "<WORK>"` | `cutlist_draft.json`（仅候选） |
| 4 | **【AI 判断，不可跳过】** 通读 `transcript_raw.srt` 全文，按 `references/requirements.md` 语义复核候选，加载共享白名单 `.trae/skills/shared/terminology.md` 校对术语；写完 `python scripts/validate.py "<WORK>/cutlist.json"` | `cutlist.json`、`transcript_final.srt`、`口播文本.txt`、`剪辑记录.md` |
| 5 | `python scripts/subtitles.py split "<WORK>/transcript_final.srt" --out "<WORK>/cues_zh.json"` | `cues_zh.json` |
| 6 | **【AI 判断】** 修正断在词中间的碎片，为每条补 `en` 字段（简洁意译，术语按白名单原样）；写完 `python scripts/validate.py "<WORK>/cues_bilingual.json"` | `cues_bilingual.json` |
| 7 | `python scripts/subtitles.py build "<WORK>/cues_bilingual.json" --cutlist "<WORK>/cutlist.json" --video "<DIR>/视频.mkv" --outdir "<OUT>" --basename "<NAME>"` | `<WORK>/final.ass`、`<OUT>/<NAME>_字幕.srt` |
| 8 | `python scripts/render.py "<DIR>/视频.mkv" --cutlist "<WORK>/cutlist.json" --ass "<WORK>/final.ass" --bgm "<BGM路径>" --out "<OUT>"` | `<OUT>/<NAME>_成片.mp4` |
| 9 | 质检：抽 3~5 帧看画质与字幕、`ffprobe` 核对时长/帧率/码率、`volumedetect` 看音频峰值、抽片尾 15s 音频识别比对字幕时间轴（偏差 ≤1s） | — |
| 10 | 交付四件套，并输出「候选新词名单」（只挑最可能的少量），**用户确认后才写入白名单** | — |

第 4、6 步是必须由 AI / 人完成的语义工作，脚本无法代替——这正是「内容优先于画面」原则的落点。

## 4. 中间产物数据契约（跨 Agent 复用的关键）

所有时间单位均为**秒**，除 `final.ass` 外均为 UTF-8 JSON/SRT/文本。

| 文件 | 结构 |
|---|---|
| `transcript.json` | `{"video","language","duration","segments":[{"id","start","end","text","words":[{"w","start","end"}]}]}` |
| `cutlist_draft.json` | `{"video_duration","silence_candidates":[],"filler_candidates":[],"duplicate_pairs":[]}`（候选，含 `suggest`，**不是**最终决策） |
| `cutlist.json` | `{"video_duration":123.4,"cuts":[{"start":10.0,"end":20.0,"type":"duplicate\|silence\|filler","reason":"..."}]}`（时间均指**原视频**时间轴） |
| `cues_zh.json` | `[{"start","end","zh"}]`（原视频时间轴，每条中文 ≤14 字） |
| `cues_bilingual.json` | `[{"start","end","zh","en"}]`（在上者基础上补 `en`） |
| `final.ass` | ASS 字幕，时间轴**已按剪辑清单重排到成片时间轴**，中文在上英文在下 |
| `<NAME>_字幕.srt` | 外挂双语 SRT，时间轴同成片 |

## 5. 配置清单（换机器 / 换 Agent 时改这里）

| 项目 | 当前值 | 位置 |
|---|---|---|
| 背景音乐固定路径 | `D:\IT小章\bgm\mixkit-digital-clouds-175.mp3` | `SKILL.md` 固定配置节、`references/requirements.md` 第七节；渲染时通过 `render.py --bgm` 传入 |
| 背景音乐存放 | 本机 `D:\IT小章\bgm\`，**不进仓库**（`.gitignore` 排除） | 见第 7 节授权说明 |
| 字幕字体 | `思源黑体`（Source Han Sans SC，SIL OFL 1.1） | 字体**配置单点** `scripts/fontcheck.py` 的 `FONT_FAMILY` / `FONT_DIR` / `EXPECT_PREFIX`（`subtitles.py` / `render.py` / `setup_env.py` 共用） |
| 字体静态字重目录 | `D:\IT小章\字体\SimplifiedChinese\`（`SourceHanSansSC-Bold.otf` / `SourceHanSansSC-Regular.otf`） | 同上；渲染时用 ffmpeg `fontsdir` 精确指向，**不进仓库** |
| 叠化时长 | `0.5s` | `scripts/timeline.py` 的 `FADE`（**单点**，`render.py` 与 `subtitles.py` 共用，改一处即可） |
| 识别模型 / 设备 | `small` / `auto`（有 GPU 用 GPU，否则 CPU） | `transcribe.py --model` / `--device` |
| 模型下载镜像 | `https://hf-mirror.com` | `transcribe.py` 顶部 `HF_ENDPOINT` |
| 画质 | CRF 17 / preset slow / 保持源帧率 | `render.py` 常量 |

**换机器只需**：① 安装合规字体（思源黑体静态字重：中文 Bold、英文 Regular）并把字体目录放到 `fontcheck.FONT_DIR`；② 把背景音乐放到指定路径（或改上面的配置）。二者都不在仓库内，**换机器需重建这两个目录**；其余脚本为相对路径调用，无需改动。字体配置只改 `scripts/fontcheck.py` 一处，并同步 `references/ffmpeg-recipes.md` 第 5 节。

## 6. 三条核心原则（冲突时按此裁决）

1. **内容优先于画面**：讲话内容决定是否重复，严禁用画面相似度/帧重复率作为删除依据。
2. **完整优先于短小**：教程必须保留解决问题的完整过程，宁可少删不可误删。
3. **后台优先于速度**：渲染后台跑，不占前台、不接管鼠标键盘。

其余硬性规则（单次编码、字幕时间轴补偿转场重叠、全片无标点、双语单行、术语白名单只读不猜等）见 `SKILL.md`「硬性规则」与「字幕规格」两节。

## 7. 版权与合规（重要）

| 项目 | 状态 |
|---|---|
| 字幕字体 | ✅ `思源黑体`（Source Han Sans SC），SIL OFL 1.1，免费商用、允许烧录进视频与商业分发；使用本机已安装的**静态字重 OTF**，渲染时 `fontsdir` 精确指向并做解析自检 |
| 禁用字体 | ❌ 微软雅黑、等线(Deng)、宋体/黑体/楷体/仿宋等 Windows 自带字体——著作权归方正/中易，仅授权系统内显示打印，烧录进对外发布的视频需单独授权 |
| 背景音乐 | ✅ `mixkit-digital-clouds-175.mp3`，出自 **Mixkit Free License**：可免费用于视频（含商业变现），**但不得把音频文件本体单独再分发/转售**。因此该 mp3 **不随仓库携带**（`.gitignore` 排除），仅本机 `D:\IT小章\bgm\` 存放。建议保留下载页授权说明截图作为凭证 |
| 工具链 | ✅ FFmpeg(GPL)、faster-whisper/Whisper(MIT)、libass 均为本地调用，不分发软件本体，许可证不传染到成片 |
| 画面内容 | ✅ 软件界面/游戏画面用于教学评测属合理使用；不做商标性商业背书即可 |

## 8. 已知待办 / 约束

- **字体与 BGM 均不进仓库**：`思源黑体` 静态字重 OTF（`D:\IT小章\字体\SimplifiedChinese\`）与背景音乐 mp3（`D:\IT小章\bgm\`）都通过 `.gitignore` 排除，仓库零二进制。代价是**换机器需重建这两个目录**（安装字体、放回 BGM）。
- **已发布视频**：早期成片使用了雅黑，属既成事实，默认**不回溯**（如需重制可重新走一遍流程）。
- **两技能暂不串联**：`subtitle-assistant` 与 `video-editing-assistant` 目前共用白名单，但不互相调用。

## 9. 版本记录

| 版本 | 内容 |
|---|---|
| v1 | 基础流水线：转录/分析/渲染四脚本 + 术语白名单 |
| v1.1 | 术语白名单机制（唯一真源、确认后落库） |
| v2 | 画质修复（单次编码 CRF17）、双语短句 ASS 字幕 |
| v3 | 中文在上英文在下、全片无标点、双语严格单行、英文字号 75% |
| v4 | 字幕间距收紧、修复后半段音字不同步（转场重叠补偿） |
| v5 | 字体版权合规、环境自检增加字体校验、目录规整 |
| v6 | 字体自包含方案落地（`思源黑体` 静态字重 + `fontsdir` + 解析自检，配置单点 `scripts/fontcheck.py`）；BGM 更换为 Mixkit 无版权曲目并不进仓库；白名单并入共享文件 `.trae/skills/shared/terminology.md`；接入本项目 Trae Skill 体系 |
| v6.1 | 修三处：① 术语标点保护改为从共享白名单**动态读取**（`time.windows.com` / `intl.cpl` 的点不再被清）；② 新增 `scripts/timeline.py` 统一保留区间与 `FADE`，修相邻/重叠删除区字幕偏移 0.5s、并消除 FADE 双常量；③ BGM 循环改为与实现一致（`-stream_loop -1` 硬循环）。另：`transcribe.py` 加 `--device auto` 与识别进度输出 |
| v6.2 | 健壮性修复：① 渲染滤镜图改写入 `work/filter_complex.txt` 并用 `-filter_complex_script` 传入，避免长视频+多剪辑点时超出 Windows 命令行 32767 字符上限；② 所有外部命令调用显式 `encoding="utf-8"`，避免中文 Windows 下解码报错；③ `subtitles.py build` 新增 `--video`（ffprobe 实测时长），与 `render.py` 时长口径统一，消除片尾字幕偏移隐患；④ ASS 文本转义（去裸 `{ } \`，防 `\N` 误换行）；⑤ 新增 `scripts/validate.py` 在渲染前校验 AI 交接文件；⑥ `transcribe.py` 已存在结果自动跳过（`--force` 可重跑） |
