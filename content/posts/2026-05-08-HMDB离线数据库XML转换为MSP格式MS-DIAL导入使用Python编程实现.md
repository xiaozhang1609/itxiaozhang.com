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

## 全部代码

```python
import argparse
import os
import zipfile
import xml.etree.ElementTree as ET


SOURCE_XML = r"C:\Users\Administrator\Documents\HMDB离线数据库\serum_metabolites\serum_metabolites.xml"
SPECTRA_ZIP = r"C:\Users\Administrator\Documents\HMDB离线数据库\hmdb_experimental_msms_spectra.zip"
DEFAULT_OUT_DIR = os.path.dirname(__file__)
DEFAULT_PARTS = 5
NS = {"h": "http://www.hmdb.ca"}


def text_or_empty(elem):
    return elem.text.strip() if elem is not None and elem.text else ""


def iter_metabolites(xml_path):
    context = ET.iterparse(xml_path, events=("start", "end"))
    context = iter(context)
    _, root = next(context)

    for event, elem in context:
        if event == "end" and elem.tag == "{http://www.hmdb.ca}metabolite":
            hmdb_id = text_or_empty(elem.find("h:accession", NS))
            spectrum_ids = []
            for spectrum in elem.findall("h:spectra/h:spectrum", NS):
                if text_or_empty(spectrum.find("h:type", NS)) != "Specdb::MsMs":
                    continue
                sid = text_or_empty(spectrum.find("h:spectrum_id", NS))
                if sid:
                    spectrum_ids.append(sid)

            yield {
                "hmdb_id": hmdb_id,
                "name": text_or_empty(elem.find("h:name", NS)),
                "formula": text_or_empty(elem.find("h:chemical_formula", NS)),
                "smiles": text_or_empty(elem.find("h:smiles", NS)),
                "inchikey": text_or_empty(elem.find("h:inchikey", NS)),
                "msms_spectrum_ids": spectrum_ids,
            }

            elem.clear()
            root.clear()


def safe_text(elem):
    if elem is None:
        return ""
    if elem.attrib.get("nil") == "true":
        return ""
    return elem.text.strip() if elem.text else ""


def normalize_number(value):
    try:
        x = float(value)
    except Exception:
        return ""
    return f"{x:.10g}"


def load_msms_spectrum_from_zip(zf, entry_name):
    try:
        raw = zf.read(entry_name)
    except KeyError:
        return None

    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return None

    peaks_parent = root.find("ms-ms-peaks")
    if peaks_parent is None:
        return None
    peaks = []
    for peak in peaks_parent.findall("ms-ms-peak"):
        mz = normalize_number(safe_text(peak.find("mass-charge")))
        intensity = normalize_number(safe_text(peak.find("intensity")))
        if mz and intensity:
            peaks.append((mz, intensity))
    if not peaks:
        return None

    ion_mode = safe_text(root.find("ionization-mode")) or "Unknown"
    precursor_type = safe_text(root.find("adduct-type")) or safe_text(root.find("adduct")) or "Unknown"
    precursor_mz = normalize_number(safe_text(root.find("adduct-mass")))

    return {
        "ion_mode": ion_mode,
        "precursor_type": precursor_type,
        "precursor_mz": precursor_mz,
        "peaks": peaks,
    }


def count_output_records(xml_path, zf, zip_names, progress_every):
    total = 0
    metabolite_count = 0
    for m in iter_metabolites(xml_path):
        metabolite_count += 1
        hmdb_id = m["hmdb_id"]
        for sid in m["msms_spectrum_ids"]:
            entry_name = f"{hmdb_id}_ms_ms_spectrum_{sid}_experimental.xml"
            if entry_name not in zip_names:
                continue
            spec = load_msms_spectrum_from_zip(zf, entry_name)
            if spec is None:
                continue
            total += 1
        if progress_every > 0 and metabolite_count % progress_every == 0:
            print(f"统计中：已扫描 {metabolite_count} 条代谢物...", end="\r")
    if progress_every > 0:
        print(" " * 60, end="\r")
    return total


def compute_targets(total, parts):
    base = total // parts
    rem = total % parts
    return [base + (1 if i < rem else 0) for i in range(parts)]


def base_name_from_source(source_xml):
    return os.path.splitext(os.path.basename(source_xml))[0]


def full_output_filename(source_xml, out_dir):
    base = base_name_from_source(source_xml)
    return os.path.join(out_dir, f"{base}.msp")


def split_output_dir(source_xml, out_dir, parts):
    base = base_name_from_source(source_xml)
    return os.path.join(out_dir, f"{base}_split_{parts}")


def split_output_filenames(source_xml, out_dir, parts):
    base = os.path.splitext(os.path.basename(source_xml))[0]
    return [os.path.join(out_dir, f"{base}_part{i+1:03d}.msp") for i in range(parts)]


def write_msp_record(f, name, hmdb_id, spectrum_id, formula, inchikey, smiles, spec):
    f.write(f"Name: {name}\n")
    if spec.get("precursor_mz"):
        f.write(f"PrecursorMZ: {spec['precursor_mz']}\n")
    f.write(f"Precursor_type: {spec.get('precursor_type') or 'Unknown'}\n")
    f.write(f"Ion_mode: {spec.get('ion_mode') or 'Unknown'}\n")
    if formula:
        f.write(f"Formula: {formula}\n")
    if inchikey:
        f.write(f"InChIKey: {inchikey}\n")
    if smiles:
        f.write(f"SMILES: {smiles}\n")
    f.write(f"Comment: HMDB_ID={hmdb_id}; SpectrumID={spectrum_id}\n")
    peaks = spec["peaks"]
    f.write(f"Num Peaks: {len(peaks)}\n")
    for mz, intensity in peaks:
        f.write(f"{mz}\t{intensity}\n")
    f.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=SOURCE_XML)
    parser.add_argument("--spectra-zip", default=SPECTRA_ZIP)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--parts", type=int, default=DEFAULT_PARTS)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--progress-every", type=int, default=2000)
    args = parser.parse_args()

    if not os.path.exists(args.source):
        raise FileNotFoundError(f"未找到离线数据库文件: {args.source}")
    if not os.path.exists(args.spectra_zip):
        raise FileNotFoundError(f"未找到 MS/MS 谱图压缩包: {args.spectra_zip}")
    if args.parts != 5:
        raise ValueError("本项目需求固定为平均分为 5 份（--parts 必须为 5）")
    if args.progress_every < 0:
        raise ValueError("--progress-every 不能为负数")

    os.makedirs(args.out_dir or ".", exist_ok=True)
    full_path = full_output_filename(args.source, args.out_dir)
    split_dir = split_output_dir(args.source, args.out_dir, args.parts)
    split_paths = split_output_filenames(args.source, split_dir, args.parts)

    existing = [p for p in [full_path, *split_paths] if os.path.exists(p)]
    if existing and not args.force:
        raise FileExistsError(f"输出文件已存在（如需覆盖请加 --force）：{existing[0]}")

    with zipfile.ZipFile(args.spectra_zip) as zf:
        zip_names = set(zf.namelist())
        total = count_output_records(args.source, zf, zip_names, args.progress_every)
        targets = compute_targets(total, args.parts)
        print(f"可输出谱图记录数：{total}")
        print(f"分配到 5 份：{targets}")

        os.makedirs(split_dir, exist_ok=True)
        full_writer = open(full_path, "w", encoding="utf-8", newline="\n")
        writers = [open(p, "w", encoding="utf-8", newline="\n") for p in split_paths]
        try:
            part_idx = 0
            written_in_part = 0
            written_total = 0
            metabolite_count = 0
            for m in iter_metabolites(args.source):
                metabolite_count += 1
                hmdb_id = m["hmdb_id"]
                for sid in m["msms_spectrum_ids"]:
                    entry_name = f"{hmdb_id}_ms_ms_spectrum_{sid}_experimental.xml"
                    if entry_name not in zip_names:
                        continue
                    spec = load_msms_spectrum_from_zip(zf, entry_name)
                    if spec is None:
                        continue

                    while part_idx < args.parts and targets[part_idx] == 0:
                        part_idx += 1
                        written_in_part = 0
                    if part_idx >= args.parts:
                        break

                    write_msp_record(
                        full_writer,
                        name=m["name"],
                        hmdb_id=hmdb_id,
                        spectrum_id=sid,
                        formula=m["formula"],
                        inchikey=m["inchikey"],
                        smiles=m["smiles"],
                        spec=spec,
                    )
                    write_msp_record(
                        writers[part_idx],
                        name=m["name"],
                        hmdb_id=hmdb_id,
                        spectrum_id=sid,
                        formula=m["formula"],
                        inchikey=m["inchikey"],
                        smiles=m["smiles"],
                        spec=spec,
                    )

                    written_total += 1
                    written_in_part += 1
                    if written_in_part >= targets[part_idx]:
                        part_idx += 1
                        written_in_part = 0

                if args.progress_every > 0 and metabolite_count % args.progress_every == 0:
                    print(
                        f"输出中：已扫描 {metabolite_count} 条代谢物，已输出 {written_total}/{total} 条谱图记录...",
                        end="\r",
                    )
            if args.progress_every > 0:
                print(" " * 90, end="\r")
        finally:
            full_writer.close()
            for f in writers:
                f.close()

    print(f"完成：共输出 {total} 条谱图记录（无峰列表的已跳过）")
    print(f"输出文件：{full_path}")
    for p in split_paths:
        print(f"输出文件：{p}")


if __name__ == "__main__":
    main()

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


