---
title: 'HMDB离线数据库转换为Excel表格'
url: hmdb-xml-to-csv-data-conversion-solution
date: 2026-08-01T21:30:42+08:00
description: 介绍HMDB All Metabolites离线数据库转换过程，将hmdb_metabolites.xml数据转换为CSV，保留Metabolite ID、Common Name等指定字段。
categories:
  - 编程开发
tags:
  - 编程开发
  - Python
  - XML
  - CSV
  - 数据处理
  - HMDB
  - HMDB数据库
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/hmdb-xml-to-csv-data-conversion-solution/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 需求分析

HMDB（Human Metabolome Database）离线数据库提供了完整的代谢物数据，但官方数据文件采用 XML 格式存储，不适合直接进行人工查看和分析。

本项目目标是将 HMDB All Metabolites 全量 XML 数据转换为 CSV 文件，并按照需求保留指定字段，生成结构清晰、便于查询的数据表格。

输入文件为 HMDB 官方离线 XML 数据：

```text
C:\Users\Administrator\Documents\HMDB离线数据库\hmdb_metabolites\hmdb_metabolites.xml
```

输出文件为：

```text
hmdb_output.csv
```

最终 CSV 文件固定包含以下字段：

* Metabolite ID
* Common Name
* KEGG Compound ID
* Kingdom
* Super Class
* Class
* Sub Class
* Direct Parent
* Chemical Formula
* Synonyms
* Description

由于全量数据库数据量较大，转换过程需要考虑运行效率和内存占用问题。

## 实现思路

### 1. 项目结构

项目主要包含两个脚本：

```text
hmdb_xml_to_csv.py
split_csv.py
```

其中：

* `hmdb_xml_to_csv.py` 负责 XML 数据转换。
* `split_csv.py` 负责对生成后的 CSV 文件进行拆分。

整体流程：

```text
HMDB XML 文件
      ↓
XML 数据读取
      ↓
字段提取与整理
      ↓
CSV 文件生成
      ↓
大文件拆分
      ↓
最终数据表格
```

### 2. XML 数据转换

主程序负责读取 HMDB XML 文件，并完成以下工作：

* 加载输入文件。
* 按记录读取代谢物数据。
* 根据需求提取指定字段。
* 处理字段格式。
* 输出 CSV 文件。

代码框架如下：

```python
import csv
import xml.etree.ElementTree as ET


SOURCE_XML = "hmdb_metabolites.xml"
OUTPUT_CSV = "hmdb_output.csv"


def read_xml(xml_path):
    """
    读取 XML 数据
    具体解析逻辑隐藏
    """
    pass


def extract_data(record):
    """
    提取指定字段
    具体字段映射逻辑隐藏
    """
    pass


def export_csv(rows, output_path):
    """
    写入 CSV 文件
    """
    pass


def main():
    records = read_xml(SOURCE_XML)

    rows = []

    for record in records:
        rows.append(
            extract_data(record)
        )

    export_csv(rows, OUTPUT_CSV)


if __name__ == "__main__":
    main()
```

### 3. 字段处理

程序根据 HMDB XML 数据结构建立字段映射关系。

处理规则：

* 单值字段直接写入 CSV。
* 多值字段合并到同一个单元格。
* 多个结果之间使用 `; ` 分隔。
* 缺少字段时输出空值。

其中 `Synonyms` 等多值字段需要特殊处理，保证完整内容不会被拆分。

### 4. CSV 输出

导出的 CSV 文件保持固定表头顺序：

```python
FIELDS = [
    "Metabolite ID",
    "Common Name",
    "KEGG Compound ID",
    "Kingdom",
    "Super Class",
    "Class",
    "Sub Class",
    "Direct Parent",
    "Chemical Formula",
    "Synonyms",
    "Description",
]
```

输出过程中：

* 不增加额外字段。
* 不生成无关文件。
* 保持字段结构稳定。

### 5. 文件拆分

由于全量数据较大，提供 CSV 拆分工具。

运行方式：

```bash
python split_csv.py \
    --input hmdb_output.csv \
    --out-dir ./hmdb_split \
    --parts 10
```

拆分工具支持：

* 指定输入文件。
* 指定输出目录。
* 自定义拆分数量。

通过拆分降低单个文件大小，提高数据查看效率。

## 部分代码示例

CSV 拆分工具框架：

```python
import csv
import argparse


def split_file(input_file, output_dir, parts):
    """
    根据指定数量拆分 CSV 文件
    具体拆分逻辑隐藏
    """
    pass


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input")
    parser.add_argument("--out-dir")
    parser.add_argument("--parts")

    args = parser.parse_args()

    split_file(
        args.input,
        args.out_dir,
        args.parts
    )


if __name__ == "__main__":
    main()
```


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


