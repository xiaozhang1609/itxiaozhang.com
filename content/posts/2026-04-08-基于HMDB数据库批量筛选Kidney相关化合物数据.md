---
title: '基于HMDB数据库批量筛选Kidney相关化合物数据'
url: filter-kidney-related-compounds-from-hmdb-dataset
date: 2026-04-08T21:13:18+08:00
description: 从 HMDB XML 构建 Kidney 相关 HMDB ID 命中集合，再批量过滤 Excel（.xlsx）并导出 CSV，保持原有列结构与顺序不变，同时输出统计与未命中列表。
categories:
  - 编程开发
tags:
  - Python
  - 数据处理
  - 数据筛选
  - 数据可视化
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/filter-kidney-related-compounds-from-hmdb-dataset>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 背景与目标


目标是把 Excel 里“与肾脏相关（Kidney）”的化合物筛出来，要求：

- 只删除行，不改任何列结构与列顺序
- 支持一个目录下批量处理多个 `.xlsx`
- 输出可追溯（统计信息、未命中列表、汇总文件）

## 核心思路

这类任务最容易踩坑的点是：Excel 行数可能很大，而 XML 也很大，如果每一行都去 XML 里“现查现找”，性能会非常差。

更高效的做法是两步走：

1. **流式解析 XML**：扫描每个 metabolite 的 `tissue_locations` 和 `ontology`，只要文本里包含 `kidney`（大小写不敏感），就把该 metabolite 的主 accession 与 secondary accessions 统一归一化后放进一个 `kidney_hit_set`
2. **过滤 Excel**：遍历每个工作表的每一行，读取 HMDB ID 并做归一化，如果在 `kidney_hit_set` 里就写入 CSV，否则跳过，从而实现“保留命中、删除未命中”

## 代码要点

- **ID 归一化**：支持严格/宽松两种匹配，最终统一成 `HMDB0000123` 这种 7 位格式，避免因为前导 0 或大小写导致误判
- **XML 流式解析**：使用 `lxml.etree.iterparse` 按需扫描并 `elem.clear()` 释放节点，适合超大 XML
- **命中范围更全**：同时检查 `biological_properties/tissue_locations` 里的 tissue 与 `ontology` 的 term
- **保持列结构**：读取 Excel 行时保留原列数，写 CSV 时对齐长度，不会打乱列顺序或丢列
- **批量与多工作表**：同一 `.xlsx` 多个 sheet 会分别输出 CSV（文件名带 sheet 序号和安全化名称）
- **输出可追溯**：会生成 `stats.txt`、`unmatched_hmid.txt` 与目录级 `summary.txt`，方便核对筛选比例和排查漏筛


常用参数：

- `--xlsx-out-suffix .kidney`：输出文件名后缀
- `--xlsx-only a.xlsx,b.xlsx`：只处理指定文件（逗号分隔）
- `--progress-every 5000`：XML 扫描进度输出间隔
- `--xlsx-progress-every 50000`：Excel 行处理进度输出间隔
- `--strict / --no-strict`：严格/宽松 HMDB ID 匹配

## 输出说明

- `*.csv`：过滤后的结果（保留表头 + 命中行），列顺序与原表一致
- `*.unmatched_hmid.txt`：当前文件中出现但未命中的 HMDB ID（去重并排序）
- `*.stats.txt`：行数统计（输入/输出/删除数量、命中/未命中/无效 ID 数量）
- `kidney_filter_summary*.txt`：目录级汇总，便于快速对比每个文件的筛选情况

## 部分代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HMDB Kidney 代谢物筛选工具
作者：IT小章
时间：2026年4月8日
网站：itxiaozhang.com

功能：从HMDB XML数据库中筛选与肾脏相关的代谢物，并过滤Excel文件
"""

import argparse
import csv
import os
import re
import time
from lxml import etree

# 默认XML路径
DEFAULT_XML_PATH = r"C:\Users\Administrator\Documents\HMDB离线数据库\hmdb_metabolites\hmdb_metabolites.xml"


def normalize_hmdb_id(raw: str) -> str | None:
    """标准化HMDB ID格式为 HMDB0000001"""
    if not raw:
        return None
    s = raw.strip().upper()
    m = re.match(r"^HMDB(\d+)$", s)
    if not m:
        return None
    return "HMDB" + m.group(1).zfill(7)


def detect_namespace(xml_file: str) -> str:
    """检测XML命名空间"""
    with open(xml_file, "rb") as f:
        context = etree.iterparse(f, events=("start",))
        _, root = next(context)
        if "}" in root.tag:
            return root.tag.split("}", 1)[0][1:]
        return ""


def has_kidney_keyword(elem, ns: str) -> bool:
    """检查代谢物是否包含kidney关键词"""
    tag = lambda local: f"{{{ns}}}{local}" if ns else local
    
    # 检查组织位置
    bio = elem.find(tag("biological_properties"))
    if bio is not None:
        tissues = bio.find(tag("tissue_locations"))
        if tissues is not None:
            for t in tissues.findall(tag("tissue")):
                if "kidney" in (t.text or "").lower():
                    return True
    
    # 检查本体论
    ontology = elem.find(tag("ontology"))
    if ontology is not None:
        for t in ontology.iter(tag=tag("term")):
            if "kidney" in (t.text or "").lower():
                return True
    return False


def build_kidney_set(xml_file: str) -> set[str]:
    """构建肾脏相关代谢物ID集合"""
    print(f"正在解析 XML: {xml_file}")
    ns = detect_namespace(xml_file)
    tag = lambda local: f"{{{ns}}}{local}" if ns else local
    
    kidney_ids = set()
    count = 0
    start = time.time()
    
    context = etree.iterparse(xml_file, events=("end",), tag=tag("metabolite"))
    
    for _, elem in context:
        count += 1
        if count % 5000 == 0:
            rate = count / (time.time() - start)
            print(f"  已扫描 {count} 条，命中 {len(kidney_ids)} 条 ({rate:.0f} 条/秒)")
        
        if has_kidney_keyword(elem, ns):
            # 提取主ID
            acc = elem.find(tag("accession"))
            if acc is not None and acc.text:
                if (nid := normalize_hmdb_id(acc.text)):
                    kidney_ids.add(nid)
            # 提取次要ID
            sec = elem.find(tag("secondary_accessions"))
            if sec is not None:
                for a in sec.findall(tag("accession")):
                    if (nid := normalize_hmdb_id(a.text)):
                        kidney_ids.add(nid)
        
        # 释放内存
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    
    print(f"XML解析完成: 共 {count} 条代谢物，{len(kidney_ids)} 条与肾脏相关")
    return kidney_ids


def find_hmdb_column(headers: list) -> int:
    """查找HMDB ID所在列索引（从1开始）"""
    norm = lambda x: str(x).lower().replace("_", " ").replace("-", " ")
    candidates = {"hmdb id", "hmdbid", "compound id", "compoundid"}
    
    for i, h in enumerate(headers, 1):
        if norm(h) in candidates:
            return i
    return 2  # 默认第2列


def filter_excel(src_path: str, out_path: str, kidney_set: set) -> dict:
    """过滤Excel文件，只保留肾脏相关行"""
    import openpyxl
    
    wb = openpyxl.load_workbook(src_path, read_only=True, data_only=False)
    stats = {"in": 0, "out": 0, "removed": 0}
    
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            hmdb_col = find_hmdb_column([c.value for c in next(ws.iter_rows(max_row=1))])
            max_col = ws.max_column or 0
            
            print(f"  处理工作表 '{sheet}' (HMDB列: {hmdb_col})")
            
            for i, row in enumerate(ws.iter_rows(values_only=False)):
                stats["in"] += 1
                
                # 保留表头
                if i == 0:
                    writer.writerow([c.value for c in row])
                    stats["out"] += 1
                    continue
                
                # 检查HMDB ID
                try:
                    raw_id = row[hmdb_col - 1].value
                except IndexError:
                    raw_id = None
                
                nid = normalize_hmdb_id(str(raw_id)) if raw_id else None
                
                # 匹配则保留，否则跳过
                if nid and nid in kidney_set:
                    writer.writerow([c.value for c in row])
                    stats["out"] += 1
                else:
                    stats["removed"] += 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="HMDB肾脏代谢物筛选工具")
    parser.add_argument("--xml", default=DEFAULT_XML_PATH, help="HMDB XML文件路径")
    parser.add_argument("--xlsx-dir", default="data", help="输入Excel目录")
    parser.add_argument("--suffix", default=".kidney", help="输出文件后缀")
    args = parser.parse_args()
    
    if not os.path.exists(args.xml):
        raise SystemExit(f"错误: 找不到XML文件 {args.xml}")
    if not os.path.isdir(args.xlsx_dir):
        raise SystemExit(f"错误: 找不到目录 {args.xlsx_dir}")
    
    # 步骤1: 构建肾脏代谢物集合
    kidney_set = build_kidney_set(args.xml)
    
    # 步骤2: 处理Excel文件
    print(f"\n开始处理Excel文件 (目录: {args.xlsx_dir})")
    
    for name in sorted(os.listdir(args.xlsx_dir)):
        if not name.endswith(".xlsx") or args.suffix in name:
            continue
        
        src = os.path.join(args.xlsx_dir, name)
        out = os.path.join(args.xlsx_dir, name[:-5] + args.suffix + ".csv")
        
        print(f"\n处理: {name}")
        start = time.time()
        stats = filter_excel(src, out, kidney_set)
        
        print(f"完成: 输入 {stats['in']} 行, 输出 {stats['out']} 行, 跳过 {stats['removed']} 行")
        print(f"输出: {out} ({time.time()-start:.1f}s)")
    
    print("\n全部完成!")


if __name__ == "__main__":
    main()
```
## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


