---
title: 'HMDB代谢物离线数据库XML转CSV文件Python编程实现'
url: hmdb-xml-to-csv-python-implementation
date: 2026-04-22T12:37:32+08:00
description: 使用 Python 解析 HMDB 离线数据库 XML 文件并转换为 CSV，导出约 21 万条代谢物数据（含 HMDB ID、分子式、分子量、SMILES、KEGG ID 等字段），生成文件体积较大，支持 gzip 压缩及字段筛选以降低内存占用。
categories:
  - 编程开发
tags:
  - Python
  - HMDB
  - XML
  - CSV
  - HMDB代谢物数据库
  - 格式转换
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/hmdb-xml-to-csv-python-implementation>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 客户需求

将 HMDB 离线数据库提供的 XML 文件转换为 CSV 格式，并按需提取指定字段（如 ID、名称、分子式、分子量、结构等）。

由于转换后数据量约 21 万条，生成的 CSV 文件体积约 96MB，在内存较小的设备上直接打开可能出现程序无响应或崩溃（内存不足）问题，因此需要支持对结果文件进行拆分，以便在不同设备环境下正常使用。

## 解决办法

1. 使用脚本将 XML 数据转换为 CSV 格式

   * 基于 Python 实现
   * 按需提取字段（如 ID、名称、分子式、分子量、结构等）
   * 支持自定义列，按实际需求选择字段输出

2. 对生成的 CSV 文件进行拆分

   * 编写独立的 Python 脚本进行切割
   * 按份数平均拆分（如 10 份、15 份等）

3. 根据设备性能选择使用方式

   * 内存较小：打开拆分后的子文件
   * 内存充足：可直接打开完整 CSV 文件

4. 优化数据导出策略

   * 仅导出必要字段，避免冗余数据
   * 减少文件体积，提高加载速度

## 部分代码

```python
# export_hmdb_selected_fields.py
import csv
import xml.etree.ElementTree as ET

SOURCE_XML = "input.xml"
OUTPUT_CSV = "output.csv"

def parse_xml_stream(xml_path):
    # 流式解析（具体实现已简化）
    context = ET.iterparse(xml_path, events=("end",))
    for event, elem in context:
        if elem.tag.endswith("metabolite"):
            yield extract_fields(elem)
            elem.clear()

def extract_fields(elem):
    # 字段提取逻辑（已隐藏细节）
    return {
        "HMDB ID": "...",
        "代谢物名称": "...",
        "分子式": "...",
        "分子量": "...",
        "SMILES 结构": "...",
        "KEGG ID": "...",
        "PubChem CID": "...",
        "InChIKey": "...",
        "所属通路": "...",
    }

def write_csv(rows, output_path):
    headers = [
        "HMDB ID", "代谢物名称", "分子式", "分子量",
        "SMILES 结构", "KEGG ID", "PubChem CID",
        "InChIKey", "所属通路"
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    rows = parse_xml_stream(SOURCE_XML)
    write_csv(rows, OUTPUT_CSV)
    print("处理完成")

if __name__ == "__main__":
    main()

```

```python
# split_csv.py
import argparse
import csv
import gzip
import math
import os
import sys


def open_input(path):
    if path.lower().endswith(".gz"):
        return gzip.open(path, "rt", newline="", encoding="utf-8-sig")
    return open(path, "r", newline="", encoding="utf-8-sig")


def open_output(path):
    return open(path, "w", newline="", encoding="utf-8-sig")


def count_data_rows(input_path):
    with open_input(input_path) as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return 0
        n = 0
        for _ in reader:
            n += 1
        return n


def split_by_rows(input_path, out_dir, base_name, rows_per_file, force):
    if rows_per_file <= 0:
        raise ValueError("--rows-per-file 必须是正整数")

    os.makedirs(out_dir, exist_ok=True)

    with open_input(input_path) as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("输入 CSV 为空，无法切割")

        part_index = 0
        current_out = None
        writer = None
        row_in_part = 0
        total_rows = 0

        def start_new_part():
            nonlocal part_index, current_out, writer, row_in_part
            if current_out is not None:
                current_out.close()
            part_index += 1
            out_path = os.path.join(out_dir, f"{base_name}.part{part_index:04d}.csv")
            if os.path.exists(out_path) and not force:
                raise FileExistsError(f"输出文件已存在（如需覆盖请加 --force）：{out_path}")
            current_out = open_output(out_path)
            writer = csv.writer(current_out)
            writer.writerow(header)
            row_in_part = 0
            return out_path

        out_path = start_new_part()
        out_paths = [out_path]

        for row in reader:
            if row_in_part >= rows_per_file:
                out_path = start_new_part()
                out_paths.append(out_path)
            writer.writerow(row)
            row_in_part += 1
            total_rows += 1

        if current_out is not None:
            current_out.close()

        return total_rows, out_paths


def split_by_parts(input_path, out_dir, base_name, parts, force):
    if parts <= 0:
        raise ValueError("--parts 必须是正整数")

    total_rows = count_data_rows(input_path)
    if total_rows == 0:
        raise ValueError("输入 CSV 没有数据行，无法切割")

    rows_per_file = math.ceil(total_rows / parts)
    total_rows_written, out_paths = split_by_rows(
        input_path=input_path,
        out_dir=out_dir,
        base_name=base_name,
        rows_per_file=rows_per_file,
        force=force,
    )
    return total_rows_written, out_paths, rows_per_file


def main():
    try:
        csv.field_size_limit(sys.maxsize)
    except (OverflowError, ValueError):
        csv.field_size_limit(1024 * 1024 * 1024)

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--base-name", default=None)
    parser.add_argument("--rows-per-file", type=int, default=None)
    parser.add_argument("--parts", type=int, default=None)
    parser.add_argument("--max-files", type=int, default=2000)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.rows_per_file is None and args.parts is None:
        raise ValueError("必须指定 --rows-per-file 或 --parts")
    if args.rows_per_file is not None and args.parts is not None:
        raise ValueError("--rows-per-file 与 --parts 只能二选一")

    base_name = args.base_name
    if not base_name:
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        if base_name.lower().endswith(".csv"):
            base_name = base_name[:-4]

    if args.rows_per_file is not None:
        if args.max_files is not None and args.max_files > 0:
            estimated_files = math.ceil(count_data_rows(args.input) / args.rows_per_file) if args.rows_per_file > 0 else 0
            if estimated_files > args.max_files:
                raise ValueError(
                    f"预计会生成 {estimated_files} 个文件，超过 --max-files={args.max_files}。"
                    f"请增大 --rows-per-file，或提高 --max-files，或使用 --parts。"
                )

        total_rows, out_paths = split_by_rows(
            input_path=args.input,
            out_dir=args.out_dir,
            base_name=base_name,
            rows_per_file=args.rows_per_file,
            force=args.force,
        )
        print(f"完成：共写入 {total_rows} 行数据（不含表头）")
        print(f"输出文件数：{len(out_paths)}")
        print(f"输出目录：{args.out_dir}")
        return

    total_rows, out_paths, rows_per_file = split_by_parts(
        input_path=args.input,
        out_dir=args.out_dir,
        base_name=base_name,
        parts=args.parts,
        force=args.force,
    )
    print(f"完成：共写入 {total_rows} 行数据（不含表头）")
    print(f"输出文件数：{len(out_paths)}")
    print(f"每个文件最大数据行：{rows_per_file}")
    print(f"输出目录：{args.out_dir}")


if __name__ == "__main__":
    main()

```

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


