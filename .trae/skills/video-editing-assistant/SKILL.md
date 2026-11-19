---
name: video-editing-assistant
description: 剪辑助手——本地全自动剪辑已录制的口播教程视频。当用户说"剪辑助手，处理 <素材目录路径>"（目录内恰有一个已合成好声音/人脸/画面的视频文件），或要求对录好的教程视频做去重复、去静音、去语气词、加中英双语字幕、加转场、加背景音乐时触发。全流程本地运行（FFmpeg + faster-whisper），无需人工逐步确认，成品输出到素材目录的 output 子目录。通用入口说明见 README.md。
---

# 剪辑助手（video-editing-assistant）

本地 AI 全自动视频剪辑流水线：以**讲话内容**为剪辑依据，自动完成去重、去无效静音、去无意义语气词、中英双语字幕（含术语校对）、章节转场、背景音乐，输出 1080P 成片。

> 本文件是本项目（Trae）的 Skill 入口。完整目录结构、执行流程、脚本契约与配置清单见同目录 `README.md`；需求规则书 `references/requirements.md` 与命令手册 `references/ffmpeg-recipes.md` 为执行细则。

## 三条核心原则（最高优先级，冲突时按此裁决）

1. **内容优先于画面**：讲话内容决定是否重复，严禁用画面相似度/帧重复率作为删除依据。
2. **完整优先于短小**：教程必须保留解决问题的完整过程，宁可少删不可误删。
3. **后台优先于速度**：全流程后台运行，不占前台窗口、不接管鼠标键盘。

## 固定配置

- 背景音乐（固定路径，永远直接使用，无需询问）：
  `D:\IT小章\bgm\mixkit-digital-clouds-175.mp3`
- 字幕字体（固定，禁止更换）：`思源黑体`（Source Han Sans SC，SIL OFL 1.1）
  - 静态字重文件目录（渲染时用 ffmpeg `fontsdir` 精确指向）：
    `D:\IT小章\字体\SimplifiedChinese\`
  - 中文用 Bold（700）、英文用 Regular（400）
- 输出分辨率：1080P（源不足 1080P 时保持源分辨率，不强行放大）
- 输入素材目录约定：目录内**恰好一个**视频文件（mp4/mov/mkv/avi 等）

## 触发与输入校验

当用户说"剪辑助手，处理 <目录路径>"（或类似表述）时执行：

1. 校验目录存在，且其中**恰好一个**视频文件。
   - **目录内不含视频、或视频不止一个 → 立即停下询问用户**，不要猜测、不要继续（避免与 `subtitle-assistant` 的字幕任务混淆触发）。
2. 校验固定背景音乐文件存在且可读。
3. 以上任一不满足：**暂停并直接询问用户**，不要猜测、不要继续。
4. 全部满足：**立即开工，全程不再向用户提问**（剪辑清单不需要用户确认，直接渲染）。
5. 运行 `scripts/setup_env.py` 自检环境（缺 FFmpeg / faster-whisper / numpy 时自动安装；首次需下载约 500MB 识别模型；并校验字幕字体存在、且能被 libass 正确解析到指定字体，未回退）。

## 工作流程

详细规则见 `references/requirements.md`，FFmpeg 命令细节见 `references/ffmpeg-recipes.md`。脚本位于 `scripts/`，均可用 `python scripts/xxx.py --help` 查看参数。

1. **环境自检**：`python scripts/setup_env.py`
2. **语音识别**：`python scripts/transcribe.py <视频> --out <素材目录>/output/work`
   - 产出 `transcript.json`（词级时间戳）、`transcript_raw.srt`
3. **AI 语义分析**：先运行 `python scripts/analyze.py <素材目录>/output/work/transcript.json --out <素材目录>/output/work` 产出候选 `cutlist_draft.json`（静音/语气词/文本相似重复），然后**亲自通读转录全文**，用语义判断修正草案：
   - 前后两段话高度相似 → 保留**后面**更完整准确的版本，删前面
   - 前面有独有信息 → 保留前面
   - 语气词分级：流畅讲述中的少量语气词、自然停顿保留；长停顿夹无效语气词、明显重复语气词删除
   - 长静音删除；但系统启动/安装/扫描/修复等过程画面保留（不因静音整段删除）
   - 修正错别字与电脑专业术语：**必须先加载共享术语白名单 `.trae/skills/shared/terminology.md`**，按其规则校对（唯一真源、按读音/语境判断、只读不猜）；字幕和口播稿用同一份白名单，保证双端一致
   - 写出最终 `cutlist.json`、`transcript_final.srt`（校对后的中文整句字幕，作为字幕拆分的输入）、`口播文本.txt`
   - 写完先校验：`python scripts/validate.py <.../cutlist.json>`（字段/时间/区间检查，未通过不得进入下一步）
4. **双语短句字幕**：
   - `python scripts/subtitles.py split <.../transcript_final.srt> --out <.../cues_zh.json>` —— 按标点拆成短句（每条中文 ≤14 字），时间按字数比例分配
   - 检查拆分结果，**修正断在词中间的碎片**（如"命令行窗/口""文件/夹"）：合并碎片并重新按字数比例分配这一句的时间
   - AI 为每条补 `en` 字段（简洁意译，不逐字硬译；术语按白名单原样保留），写成 `cues_bilingual.json`
   - 写完先校验：`python scripts/validate.py <.../cues_bilingual.json>`
   - `python scripts/subtitles.py build <.../cues_bilingual.json> --cutlist <.../cutlist.json> --video <视频> --outdir <素材目录>/output --basename <视频名>` —— 按剪辑清单重排时间轴，产出烧录用 `work/final.ass` 与外挂双语 SRT
     - `--video` 必传：由 ffprobe 实测时长，确保与 `render.py` 的时长口径完全一致（否则片尾字幕可能偏移）
5. **后台渲染**：`python scripts/render.py <视频> --cutlist <.../cutlist.json> --ass <.../work/final.ass> --bgm "D:\IT小章\bgm\mixkit-digital-clouds-175.mp3" --out <素材目录>/output`
   - **单次编码**：一条命令完成剪切+叠化+字幕烧录+混音，全片只压缩一次（多代编码会导致画质明显下降）
   - 保留源分辨率与源帧率，CRF 17 / preset slow（屏录文字画面需高保真）
   - 用后台方式运行（run_in_background），不阻塞前台
   - 渲染完成后抽查成片：抽 3~5 帧看画质与字幕、ffprobe 核对时长/帧率/码率、volumedetect 确认音频正常
6. **交付**：输出到 `<素材目录>/output/`，通知用户并给出成品路径
7. **白名单积累**：交付时按共享白名单文件 `.trae/skills/shared/terminology.md` 的「④ 白名单积累机制」，额外输出一份「建议新增白名单」——本次任务中识别异常或不确定、但白名单未登记的词，只挑最可能的（少量），格式示例：
   ```
   【建议新增白名单】
   - 标准写法：DISM    （来源：剪辑记录 12:05）
   ```
   仅在用户明确确认（如"登记 1、3"/"全部登记"）后，才把词条追加进共享白名单文件；用户未确认前不得写入。

## 字幕规格（固定）

- **字体（版权硬性）**：统一 `思源黑体`（Source Han Sans SC，Adobe/Google 出品，SIL OFL 1.1，免费商用、允许烧录进视频与商业分发）。字体配置**单点**在 `scripts/fontcheck.py`（`FONT_FAMILY` / `FONT_DIR` / `EXPECT_PREFIX`），`subtitles.py`、`render.py`、`setup_env.py` 均引用它；渲染时用 ffmpeg `fontsdir` 指向静态字重目录 `D:\IT小章\字体\SimplifiedChinese\`，并做**字体解析自检**（确认 libass 实际选中 SourceHanSansSC 系列字体，未静默回退）。**严禁改回 Microsoft YaHei（微软雅黑）、等线（Deng）等系统自带但需商用授权的字库**：雅黑著作权归北大方正，微软仅购得 Windows 内「显示+打印」授权，把字形烧进对外发布的视频属于复制/发行，需方正单独授权（字体维权赔偿案例常见）。
  - 为什么不用系统自带 `NotoSansSC-VF.ttf`：它是可变字体，libass 请求 Bold 会落到 Thin 实例（笔画偏细），且字体名稍不精确会被 DirectWrite **静默回退到微软雅黑**，会把版权风险重新带回来。改用本机已安装的**静态字重 OTF**，并用 `fontsdir` 精确指向 + 自检兜底。
- **双语**：中文为主、英文为辅；中文正常字号（ASS 64），英文按主流双语规范约为中文 75%（ASS 48），浅灰 #D8D8D8
- 布局：**中文在上、英文在下**，底部居中，中文白字黑边
- **每条中文不超过 14 字**，到逗号/句号即换条，禁止整句满行长条
- **全标点零出现**：中英文字幕内不得出现任何标点符号（，。、！？："" 以及 , . ? ! ; : " ' 等），停顿语义用空格表达；**技术术语的标点属于术语本身、必须原样保留**（如 `sfc /scannow` 的空格斜杠、`ncpa.cpl` / `time.windows.com` / `intl.cpl` 的点），保护清单由 `subtitles.py` 从共享白名单 `.trae/skills/shared/terminology.md` 动态读取（含标点的词条自动纳入，不另行硬编码）；英文缩写撇号（I'm、don't）属于单词一部分，保留
- **双语均严格单行**：中文 ≤14 字；英文意译精简，单行硬上限 66 字符（subtitles.py 的 clip_en 截到词边界），WrapStyle: 2 禁止自动换行，任何情况不得折成两行、不得溢出画面

## 输出物（四件套，均在 output/ 下）

| 文件 | 内容 |
|---|---|
| `<视频名>_成片.mp4` | 1080P，双语字幕已烧录，含转场与背景音乐 |
| `<视频名>_字幕.srt` | 外挂双语字幕（上行中文、下行英文，已校对术语） |
| `<视频名>_剪辑记录.md` | 每处删改的时间段 + 原因（去重/静音/语气词分类标注）+ 术语校对表 |
| `<视频名>_口播文本.txt` | 最终保留内容的纯文本口播稿（校对后） |

## 硬性规则

- **原始视频永不覆盖**：所有中间产物写入 `output/work/`，成品写入 `output/`。
- **字幕字体必须可免费商用**：固定 `思源黑体`（SIL OFL 1.1）。更换字体前必须先核实其授权允许「烧录进视频并对外发布」，且必须修改字体**配置单点** `scripts/fontcheck.py`（`FONT_FAMILY` / `FONT_DIR` / `EXPECT_PREFIX`），并同步更新 `references/ffmpeg-recipes.md` 第 5 节。
- **全片只编码一次**：所有处理在一条 FFmpeg 命令内完成；严禁分步多次重编码（画质会明显劣化）。
- 保持源分辨率与源帧率，不得强制降帧。
- 术语校对遵循共享白名单 `.trae/skills/shared/terminology.md`（唯一真源；只读不猜；用户确认后才入库）。
- 背景音乐：`-stream_loop -1` 循环铺满全片、音量约为原人声 10% 以下、结尾 3 秒淡出（硬循环接缝在低音量下基本不可闻，如遇爆音可更换循环更友好的曲目）。
- 转场：仅在删减造成的拼接点加 0.5s 叠化（xfade），正常讲述不打断，不过度使用动效。
- **字幕时间轴必须与成片严格一致**：`render.py` 与 `subtitles.py` 共用 `scripts/timeline.py` 的保留区间模型与 `FADE` 常量；字幕时间轴由 `timeline.map_time` 按「同一套保留段 + 每处拼接扣 `FADE`」换算（`t` 落在删除区返回 None）。**叠化时长单点在 `timeline.py` 的 `FADE`，改一处即可**，不要在 render/subtitles 各自另存常量——否则相邻/重叠删除区会被两处各算一套，导致字幕偏移。
- 交付前必须做**后半段对齐实测**：抽取片尾前 15s 音频重新识别，比对词级时间戳与 ASS 字幕时间轴，偏差应 ≤1s。
- 全程本地处理，视频与音频不上传任何外部服务。
