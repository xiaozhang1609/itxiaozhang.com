# 术语白名单（唯一真源）

本文件是 **subtitle-assistant（字幕助手）** 与 **video-editing-assistant（剪辑助手）** 共用的唯一真源。两个技能产出的所有文本（字幕 / 口播稿 / 博客正文）都按本文件校对，**不允许任一技能各自维护副本**。

## ① 标准写法清单

清单中的字符串必须原样出现：不改写、不翻译、不缩写、不改大小写；脚本 / 命令类连空格和斜杠都照原样写。

```
WeGame
章九工具箱
Geek Uninstaller
Edge浏览器
sfc /scannow
ipconfig /flushdns
ncpa.cpl
IPv4
IPv6
DNS
小章
IT小章
穿越火线
CFData
CFSystem
Personal
Windows 安全中心
regedit
time.windows.com
intl.cpl
Trae
Skill
ChatGPT
万兴喵影
FocuSee
鲁棒性
```

## ② 常见误识别对照

右列仅举例、非穷举。判断标准不是「右列有没有出现过这个错法」，而是「该词的读音 / 语境是否指向左列标准写法」；命中即改为左列标准写法。

| 标准写法 | 常见误识别 |
| --- | --- |
| 小章 | 小张 |
| IT小章 | IT小张 |
| 穿越火线 | 穿越火线s 等带杂字的写法 |
| WeGame | Vgame、wegame、Wgame |
| sfc /scannow | scnnuw、sfc scannow |
| ipconfig /flushdns | rpconfig /flushdns、ipconfig flushdns |
| ncpa.cpl | ncpa.cp、ncpc.cpl |
| IPv4 / IPv6 | IPv四、IPV4 / IPV6 |
| DNS | dns、D N S |
| CFData | CF date、CFDATA |
| CFSystem | CF system、CFSYSTEM |
| Personal | personel、Personnal |
| Windows 安全中心 | windows安全中心 等大小写错误 |
| regedit | regedit.exe（视上下文判断） |
| time.windows.com | time.windows.con、time windows com |
| intl.cpl | intel.cpl、intl cp |
| Trae | Tree、Tray |
| Skill | scale、skil |
| ChatGPT | chatgpt、Chat GTP |
| 万兴喵影 | 万兴妙影、喵影 |
| FocuSee | focus、focu see |
| 鲁棒性 | 鲁棒行、鲁帮性 |
| 章九工具箱 | 章九工具 |
| Geek Uninstaller | Geek Uninstall、极客卸载 |
| Edge浏览器 | edge浏览器 |

## ③ 使用规则

1. **唯一真源**：以标准写法清单为准，识别结果与之不一致时改为标准写法。
2. **按读音 / 语境判断**：不局限于右列已列出的错法。
3. **只读不猜**：未登记的词按合理写法处理并输出，不擅自入库；在交付时整理「建议新增白名单」清单提醒用户。
4. **确认后落库**：用户明确确认（如「登记 1、3」或「全部登记」）后，才把新词条写入本文件；防止一次性误判固化成长期规则。
5. **双端一致**：两个技能（字幕助手 / 剪辑助手）使用同一份白名单同步校对。
6. **只增不改**：原则上只新增不删改；确需修改已有词条时，先征得用户同意。

## ④ 白名单积累机制（两个技能统一使用）

1. **先照常处理**：本次按合理写法校正并照常输出，**不因缺词而阻塞流程**。
2. **交付时列出建议**：在处理结束的说明中附加一份「建议新增白名单」，格式固定为：

```
【建议新增白名单】
- 标准写法：DISM    （来源：字幕第 68 条）
- 标准写法：ncpa.cpl（来源：剪辑记录 12:05）
```

3. **必须等用户确认**：仅挑最可能的少量词条；用户确认后才写入本文件「① 标准写法清单」，必要时同步补入「② 常见误识别对照」。**未经确认不得自行追加。**
