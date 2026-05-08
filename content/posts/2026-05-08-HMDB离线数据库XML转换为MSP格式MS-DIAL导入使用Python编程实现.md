---
title: 'HMDB离线数据库XML转换为MSP格式MS DIAL导入使用Python编程实现'
url: hmdb-xml-to-msp-msdial-python-conversion-guide
date: 2026-05-08T19:32:00+08:00
description: 本文介绍如何使用Python将HMDB离线XML及MS/MS谱图转换为MSP格式谱库，实现MS-DIAL可导入使用，并解决大文件解析与内存占用问题，同时支持完整与分割谱库输出。
categories:
  - 编程开发
tags:
  - Python
  - HMDB
  - MS-DIAL
  - XML
  - MSP
  - 谱库构建
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/posts/hmdb-xml-to-msp-msdial-python-conversion-guide/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 



## 需求梳理

客户手头有 HMDB 离线数据库（XML）与 HMDB 实验 MS/MS 谱图包（zip）。目标是做成 MS-DIAL 可识别的谱库（MSP）。
核心约束与验收点：

1. **输入数据**
   - HMDB 离线代谢物 XML（例如 serum metabolites 的 XML）
   - HMDB 实验 MS/MS 谱图压缩包（包含大量 *_experimental.xml 的谱图条目）
2. **输出结果**
   - 每次执行脚本同时生成：
     - 1 个**完整 MSP**（便于高性能机器一次导入）
     - 5 个**平均分割 MSP**（放在一个新的子文件夹中，便于 MS-DIAL/低配置机器分批导入）
3. **谱图筛选策略**
   - 只输出 **包含 MS/MS 峰列表**的记录
   - 没有峰列表的记录直接 **跳过**
4. **字段要求（MS-DIAL 识别优先）**
   - 每条 MSP 记录至少包含：Name、Num Peaks、峰列表（m/z intensity）
   - Ion mode、Precursor type 缺失时填 **Unknown**
5. **性能与稳定性**
   - XML 体量大，不允许一次性整树加载导致内存爆炸
   - 需要流式处理、增量写出

## 实现思路

我把问题拆成三个稳定的模块，让脚本既能跑得动大文件，又能保证 MS-DIAL 兼容性。

1. **流式解析 HMDB 代谢物 XML（低内存）**
   - 使用 iterparse 按 metabolite 结点逐条处理
   - 每处理完一条就 clear，避免堆积
2. **按谱图 ID 从 zip 中按需读取 MS/MS 谱图（避免解压全量文件）**
   - zip 里文件数非常多（数万级），不能逐个解压落盘
   - 采用“需要哪条读哪条”的随机读取策略
3. **一遍输出同时写两套结果**
   - 完整 MSP：顺序追加写入
   - 分割 MSP：根据总记录数计算五等分目标，边写边切换输出句柄

为什么不做“先生成完整 MSP 再二次切割”？

- 二次切割会多一次 I/O 扫描，文件越大越慢；  
- 更重要的是，MSP 是“记录块”结构，简单按行切割容易切坏；  
- 直接在生成阶段做“按记录计数的切割”最稳。

## 部分代码

```python
import xml.etree.ElementTree as ET

NS = {"h": "http://www.hmdb.ca"}

def _text(node):
    return node.text.strip() if node is not None and node.text else ""

def iter_metabolites(xml_path: str):
    ctx = ET.iterparse(xml_path, events=("start", "end"))
    ctx = iter(ctx)
    _, root = next(ctx)

    for event, elem in ctx:
        if event != "end":
            continue
        if not elem.tag.endswith("metabolite"):
            continue

        hmdb_id = _text(elem.find("h:accession", NS))
        name = _text(elem.find("h:name", NS))
        formula = _text(elem.find("h:chemical_formula", NS))
        smiles = _text(elem.find("h:smiles", NS))
        inchikey = _text(elem.find("h:inchikey", NS))

        msms_ids = []
        for sp in elem.findall("h:spectra/h:spectrum", NS):
            sp_type = _text(sp.find("h:type", NS))
            if sp_type != "Specdb::MsMs":
                continue
            sid = _text(sp.find("h:spectrum_id", NS))
            if sid:
                msms_ids.append(sid)

        yield {
            "id": hmdb_id,
            "name": name,
            "formula": formula,
            "smiles": smiles,
            "inchikey": inchikey,
            "msms_ids": msms_ids,
        }

        elem.clear()
        root.clear()
```


## 最终效果

脚本每次运行会生成：

1. 项目根目录下 1 个完整谱库：
   - `xxx.msp`
2. 一个新的子文件夹，内含 5 个平均分割谱库：
   - `xxx_split_5/xxx_part001.msp`
   - `xxx_split_5/xxx_part002.msp`
   - `xxx_split_5/xxx_part003.msp`
   - `xxx_split_5/xxx_part004.msp`
   - `xxx_split_5/xxx_part005.msp`

并且严格遵守：
- 只有存在 MS/MS 峰列表的谱图才输出为 MSP 记录（否则跳过）
- Ion mode / Precursor type 缺失时统一写 Unknown



## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


