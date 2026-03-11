---
title: '离线HMDB数据库XML文件转换为CSV格式'
url: parse-hmdb-xml-extract-compounds-to-csv
date: 2026-03-11T21:21:57+08:00
description: HMDB数据库提供约845MB的XML数据文件，包含65000多条化合物记录。由于XML结构无法直接用于分析软件，需要解析文件并提取HMDB ID、名称、分子式、质量、SMILES、保留时间及MS/MS信息，整理为CSV表格数据。
categories:
  - 编程开发
tags:
  - HMDB数据库
  - XML文件
  - CSV格式
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/parse-hmdb-xml-extract-compounds-to-csv>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 需求分析

在使用安捷伦 **MassHunter** 分析软件进行数据处理时，需要使用 **HMDB 数据库**中的化合物信息作为分析数据来源。

HMDB 官方提供的数据为 **XML 格式文件**，文件体积约 **845 MB**，解压后包含 **65000 多条化合物记录**。该数据结构无法直接用于分析软件，同时部分分析所需字段未以结构化方式提供，需要进行数据整理与提取。

为满足分析需求，需要从 XML 文件中提取有效化合物数据，并整理为结构化表格格式。目标数据需包含以下字段：

* HMDB ID
* 化合物名称（Name）
* 分子式（Formula）
* 质量（Mass）
* SMILES
* 保留时间（Retention Time）
* 二级质谱信息（MS/MS）

由于原始 XML 数据量较大，人工整理不可行，因此需要通过程序自动解析 XML 文件，提取符合要求的化合物记录，并补充所需字段信息。

最终需要将整理后的数据输出为 **CSV 文件**，形成标准化数据表，以便在分析软件中进行后续数据处理与分析。

需要注意的是，同一化合物可能对应不同的质谱信息或属性，因此在结果数据中可能出现名称相同但属性不同的多条记录，这属于正常情况。

---

## 开始实现

### 1. 下载 HMDB XML 数据文件

从 HMDB 数据库下载完整数据包，获取约 **845 MB 的 XML 文件**。

下载完成后进行解压，得到包含约 **65000 多条化合物数据**的 XML 文件。

---

### 2. 解析 XML 文件

对 XML 文件进行解析，读取其中的化合物节点信息，并提取有效数据记录。

重点提取以下字段：

* HMDB ID
* Name（名称）
* Formula（分子式）
* Mass（质量）
* SMILES
* Retention Time（保留时间）
* MS/MS（二级质谱信息）

解析过程中需要过滤无效或缺失关键字段的记录。

---

### 3. 数据整理与字段补充

将解析得到的化合物信息进行结构化整理：

* 按字段整理为统一的数据表结构
* 对缺失字段进行补充或统一格式
* 保证所有记录字段完整

需要注意：

* 同一化合物可能存在多条记录
* 不同记录对应不同的质谱或属性信息
* 因此结果中出现名称重复属于正常情况

---

### 4. 生成 CSV 数据文件

将整理后的化合物数据导出为 **CSV 文件**。

CSV 文件包含以下列：

* HMDB ID
* Name
* Formula
* Mass
* SMILES
* Retention Time
* MS/MS

最终生成的文件数据量约 **65000 条记录**，可直接用于后续分析软件的数据导入或处理。

## 全部代码

### Python

```python
import os
import csv
import glob
import time
import xml.etree.ElementTree as ET

def text_or_empty(el):
    """Safely return stripped text from an element."""
    return el.text.strip() if el is not None and el.text is not None else ""

def iter_metabolites(xml_path):
    """
    Generator that yields metabolite info from the large HMDB XML file.
    This uses iterparse to keep memory usage low.
    """
    print(f"Start parsing metabolite data from {xml_path}...")
    context = ET.iterparse(xml_path, events=("start", "end"))
    context = iter(context)
    event, root = next(context)
    
    ns = {"h": "http://www.hmdb.ca"}
    
    count = 0
    for event, elem in context:
        if event == "end" and elem.tag == "{http://www.hmdb.ca}metabolite":
            # Extract fields
            accession = text_or_empty(elem.find("h:accession", ns))
            name = text_or_empty(elem.find("h:name", ns))
            formula = text_or_empty(elem.find("h:chemical_formula", ns))
            # Try monoisotopic, fallback to average
            mass = text_or_empty(elem.find("h:monisotopic_molecular_weight", ns))
            if not mass:
                mass = text_or_empty(elem.find("h:average_molecular_weight", ns))
            
            smiles = text_or_empty(elem.find("h:smiles", ns))
            
            # Secondary accessions (optional but good for matching)
            secondary_accs = []
            sa_elem = elem.find("h:secondary_accessions", ns)
            if sa_elem is not None:
                for acc in sa_elem.findall("h:accession", ns):
                    txt = text_or_empty(acc)
                    if txt:
                        secondary_accs.append(txt)

            yield {
                "accession": accession,
                "name": name,
                "formula": formula,
                "mass": mass,
                "smiles": smiles,
                "secondary_accessions": secondary_accs
            }
            
            # Clear the element to save memory
            elem.clear()
            # Also remove from root to prevent accumulation of empty tags
            if root is not None:
                root.clear()
            
            count += 1
            if count % 10000 == 0:
                print(f"Processed {count} metabolites...", end="\r")
    
    print(f"\nFinished parsing {count} metabolites.")

def load_metabolite_dict(xml_path):
    """
    Loads metabolite data into a dictionary for fast lookup.
    Returns: dict[accession] -> {name, formula, mass, smiles}
    """
    meta_dict = {}
    if not os.path.exists(xml_path):
        print(f"Warning: Metabolite XML not found at {xml_path}")
        return meta_dict

    for m in iter_metabolites(xml_path):
        acc = m["accession"]
        if not acc:
            continue
        
        data = {
            "name": m["name"],
            "formula": m["formula"],
            "mass": m["mass"],
            "smiles": m["smiles"]
        }
        
        # Map primary accession
        meta_dict[acc] = data
        
        # Map secondary accessions to the same data
        for sec in m["secondary_accessions"]:
            # Only map if not already present (primary takes precedence)
            if sec not in meta_dict:
                meta_dict[sec] = data
                
    return meta_dict

def parse_msms_peaks(root):
    """Extract peaks as 'mz:intensity' string."""
    peaks = []
    # Try different paths for peaks
    # Standard HMDB format
    for peak in root.findall(".//ms-ms-peaks/ms-ms-peak"):
        mz = text_or_empty(peak.find("mass-charge"))
        intensity = text_or_empty(peak.find("intensity"))
        if mz and intensity:
            try:
                if float(mz) > 0 and float(intensity) >= 0:
                    peaks.append(f"{mz}:{intensity}")
            except ValueError:
                continue
    
    # Fallback format
    if not peaks:
        for peak in root.findall(".//peaks/peak"):
            mz = text_or_empty(peak.find("mz"))
            intensity = text_or_empty(peak.find("intensity"))
            if mz and intensity:
                try:
                    if float(mz) > 0 and float(intensity) >= 0:
                        peaks.append(f"{mz}:{intensity}")
                except ValueError:
                    continue
                    
    return ";".join(peaks)

def find_first_text(root, paths):
    for p in paths:
        el = root.find(p)
        if el is not None and el.text:
            t = el.text.strip()
            if t:
                return t
    return ""

def parse_msms_file(path, meta_dict):
    """Parse a single MS/MS XML file and enrich with metabolite data."""
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError:
        return None

    # Extract ID from MS/MS file
    hmdb_id = find_first_text(root, [".//database-id", ".//accession", ".//metabolite/accession"])
    
    # Extract MS/MS specific metadata
    rt_value = find_first_text(root, [".//retention_time", ".//retention-time", ".//chromatography/retention_time"])
    rt_unit = find_first_text(root, [".//retention_time_units", ".//retention-time-units", ".//chromatography/retention_time_units"])
    polarity = find_first_text(root, [".//ionization-mode", ".//polarity"])
    collision_energy = find_first_text(root, [".//collision-energy-voltage", ".//collision_energy", ".//collision-energy", ".//collision-energy-level"])
    instrument = find_first_text(root, [".//instrument-type", ".//instrument"])
    peaks = parse_msms_peaks(root)

    # Enrich from metabolite dictionary
    meta_info = meta_dict.get(hmdb_id, {})
    
    name = meta_info.get("name", "")
    formula = meta_info.get("formula", "")
    mass = meta_info.get("mass", "")
    smiles = meta_info.get("smiles", "")
    
    # If name is missing in dict, try to find in XML (rare)
    if not name:
        name = find_first_text(root, [".//metabolite/name", ".//compound/name", ".//name"])
    
    return {
        "hmdb_id": hmdb_id,
        "name": name,
        "formula": formula,
        "mass": mass,
        "smiles": smiles,
        "rt_value": rt_value,
        "rt_unit": rt_unit,
        "polarity": polarity,
        "collision_energy": collision_energy,
        "instrument": instrument,
        "peaks": peaks,
        "source_file": os.path.basename(path),
    }

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Paths
    metabolites_xml = os.path.join(base_dir, "hmdb_metabolites", "hmdb_metabolites.xml")
    spectra_dir = os.path.join(base_dir, "hmdb_experimental_msms_spectra")
    output_dir = os.path.join(base_dir, "output")
    out_csv = os.path.join(output_dir, "hmdb_msms_full_enriched.csv")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Metabolite Data
    t0 = time.time()
    meta_dict = load_metabolite_dict(metabolites_xml)
    print(f"Loaded {len(meta_dict)} accession entries in {time.time() - t0:.2f}s")
    
    # 2. Process Spectra Files
    files = sorted(glob.glob(os.path.join(spectra_dir, "*.xml")))
    print(f"Found {len(files)} MS/MS XML files to process.")
    
    header = [
        "hmdb_id", "name", "formula", "mass", "smiles", 
        "rt_value", "rt_unit", "polarity", "collision_energy", 
        "instrument", "peaks", "source_file"
    ]
    
    # Using a buffer/batch write could be slightly faster, but row-by-row is safer for memory
    # and allows stopping early without losing everything.
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        
        count = 0
        for f in files:
            rec = parse_msms_file(f, meta_dict)
            if rec:
                writer.writerow(rec)
                count += 1
            
            if count % 1000 == 0:
                print(f"Processed {count} spectra files...", end="\r")
                
    print(f"\nDone! Exported {count} records to {out_csv}")

if __name__ == "__main__":
    main()

```


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)



