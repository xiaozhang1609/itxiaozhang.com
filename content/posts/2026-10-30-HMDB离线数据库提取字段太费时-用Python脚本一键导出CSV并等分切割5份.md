---
title: 'HMDB离线数据库提取字段太费时 用Python脚本一键导出CSV并等分切割5份'
url: hmdb-xml-export-csv-and-split-5-parts
date: 2026-10-30T19:11:00+08:00
description: 手动翻查 HMDB 离线数据库提取代谢物字段效率低，需要把二十多万条 XML 记录整理成 CSV，并等分成 5 份便于查看和分发，同时自动校验行数、HMDB ID 唯一性和各列空值比例。
categories:
  - 编程开发
tags:
  - python
  - xml-parsing
  - 数据处理
  - HMDB数据库
  - 脚本工具
---

> 原文地址：<https://itxiaozhang.com/hmdb-xml-export-csv-and-split-5-parts/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 需求说明

HMDB（Human Metabolome Database）离线数据库以 XML 格式存储，单文件体积较大，二十多万条代谢物记录无法直接查看和筛选。

本次需求是把离线 XML 中需要的字段一次性提取出来，整理成 CSV 表格，并等分成 5 份，方便逐份查看、传输和交付。具体目标如下：

1. 从 `hmdb_metabolites.xml` 中读取每一条代谢物记录。
2. 提取固定的 12 个字段，包含标识、结构信息和分类信息。
3. 导出 UTF-8-SIG 编码的 CSV，保证 Windows 下 Excel 直接打开不乱码。
4. 把主 CSV 等分成 5 份，每份行数尽量接近。
5. 导出完成后自动自检，输出行数、唯一性和空值统计。

最终 CSV 固定包含以下字段：

```text
HMDB ID
代谢物名称
分子式
分子量
SMILES 结构
KEGG ID
PubChem CID
InChIKey
所属通路
来源
同义词
超类
```

其中「分子量」优先取单同位素分子量，缺失时回退到平均分子量；「所属通路」「来源」「同义词」属于多值字段，需要合并到同一个单元格。

## 程序设计

整体流程分为三步：解析 XML 导出主 CSV → 等分切割 5 份 → 自检并输出报告。

### 一、流式解析 XML

HMDB XML 体积较大，直接整体加载会占用大量内存。程序采用 `iterparse` 流式解析，逐条处理 `metabolite` 节点，处理完立即释放节点：

```python
def iter_rows(xml_path, limit):
    context = ET.iterparse(xml_path, events=("start", "end"))
    context = iter(context)
    _, root = next(context)

    for event, elem in context:
        if event != "end" or elem.tag != "{http://www.hmdb.ca}metabolite":
            continue

        mono_mass = text_or_empty(elem.find("h:monisotopic_molecular_weight", NS))
        avg_mass = text_or_empty(elem.find("h:average_molecular_weight", NS))

        yield {
            "HMDB ID": text_or_empty(elem.find("h:accession", NS)),
            "代谢物名称": text_or_empty(elem.find("h:name", NS)),
            "分子量": mono_mass if mono_mass else avg_mass,
            # 其余字段按同一方式提取
        }

        elem.clear()
        root.clear()
```

### 二、多值字段去重合并

「所属通路」「来源」「同义词」这类字段在原始数据中可能重复，直接拼接会产生冗余内容。程序统一做去重处理，再以 `|` 分隔写入同一个单元格：

```python
def join_unique(items, sep):
    seen = set()
    unique_items = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            unique_items.append(item)
    return sep.join(unique_items)
```

其中「来源」字段并非直接读取，而是需要按 HMDB 本体层级定位。程序先找到 `Disposition` 根节点，再逐层匹配 `Source`，最后收集其下所有子节点名称：

```python
DISPOSITION_TERM = "Disposition"
SOURCE_TERM = "Source"

def extract_source(metabolite_elem):
    terms = []
    for root in metabolite_elem.findall("h:ontology/h:root", NS):
        if text_or_empty(root.find("h:term", NS)) != DISPOSITION_TERM:
            continue
        for level2 in root.findall("h:descendants/h:descendant", NS):
            if text_or_empty(level2.find("h:term", NS)) != SOURCE_TERM:
                continue
            for node in level2.findall("h:descendants/h:descendant/h:term", NS):
                terms.append(text_or_empty(node))
    return join_unique(terms, VALUE_SEP)
```

### 三、等分切割

切割前先统计主 CSV 的数据行数，用 `divmod` 计算每份的基础行数和余数，余数从第一份开始依次分配，保证 5 份行数差距不超过 1 行：

```python
base, extra = divmod(total_rows, parts)

target_rows = base + (1 if part_index <= extra else 0)
```

分片文件命名为 `hmdb_selected_fields.part0001.csv` 这类形式，写入到 `splits_5` 目录，每份都带完整表头。

### 四、自检报告

程序在导出和切割完成后自动校验，主要检查项包括：

* 主 CSV 表头是否与预期一致，每行列数是否正确。
* 5 份分片行数合计是否等于主 CSV 行数。
* 分片表头是否与主 CSV 一致。
* HMDB ID 是否存在重复。
* 每一列的空值数量与占比。

## 安全机制

考虑到脚本涉及文件写入和批量切割，加入了以下保护设计：

1. **默认不覆盖**：输出文件已存在时直接报错并终止，必须在命令行显式加上 `--force` 参数才会覆盖，避免误删已有结果。
2. **抽样试跑**：提供 `--limit` 参数，可以只处理前 N 条记录，先验证字段提取是否正确，再执行全量导出。
3. **输入校验**：启动时检查源 XML 是否存在，不存在时直接抛出 `FileNotFoundError`；切割前检查主 CSV 是否有数据行、行数是否少于切割份数。
4. **一致性校验**：自检阶段逐项核对行数、表头和 ID 唯一性，一旦发现问题会打印明细并通过 `sys.exit(1)` 退出，便于在自动化流程中捕获失败。

## 使用方法与运行结果

脚本的源 XML 路径、输出路径和切割份数均在代码中固定，无需配置参数，普通用户只需运行：

```bash
python hmdb_export.py
```

首次使用或想先验证字段是否正确，建议先抽样试跑：

```bash
python hmdb_export.py --force --limit 2000
```

其中：

* `--limit` 指定只处理前 N 条记录，`0` 表示全量。
* `--force` 表示允许覆盖已存在的产出文件。

运行过程中会按进度打印处理条数，结束后输出自检报告：

```text
开始解析：your_path\hmdb_metabolites\hmdb_metabolites.xml
  已处理 20000 条代谢物记录...
导出完成：220945 条记录 -> hmdb_selected_fields.csv
切割完成：5 份 -> splits_5

=== 自检报告 ===
[通过] 列数 = 12
[通过] 主 CSV 数据行 = 220945
[通过] 分片 5 份，行数合计 = 220945
[通过] HMDB ID 唯一数 = 220945

分片大小：
  hmdb_selected_fields.part0001.csv  ...
各列空值数：
  HMDB ID: 0 (0.0%)
  ...

全部检查通过。
```

（上方行数为结构示意，实际以本机数据库为准。）

## 实现效果

脚本把原本需要人工反复翻查的字段提取工作压缩成一条命令：一次运行即可完成 XML 解析、12 个字段导出、5 份等分切割和全套自检。输出 CSV 可直接用 Excel 打开，分片后的文件体积适中，方便分发和比对。

对于代谢物数据整理、离线数据库转换、大批量字段提取等场景，这类固定口径的脚本可以减少重复劳动，同时通过自检报告保证结果可信。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)
