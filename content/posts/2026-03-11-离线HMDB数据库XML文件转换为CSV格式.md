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

## 部分代码


```python
import os
import csv
import glob

def load_metabolite_dict(xml_path):
    raise NotImplementedError

def parse_msms_file(path, meta_dict):
    raise NotImplementedError

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    metabolites_xml = os.path.join(base_dir, "hmdb_metabolites", "hmdb_metabolites.xml")
    spectra_dir = os.path.join(base_dir, "hmdb_experimental_msms_spectra")
    output_dir = os.path.join(base_dir, "output")
    out_csv = os.path.join(output_dir, "hmdb_msms_full_enriched.csv")

    os.makedirs(output_dir, exist_ok=True)

    meta_dict = load_metabolite_dict(metabolites_xml)
    files = sorted(glob.glob(os.path.join(spectra_dir, "*.xml")))

    header = [
        "hmdb_id", "name", "formula", "mass", "smiles",
        "rt_value", "rt_unit", "polarity", "collision_energy",
        "instrument", "peaks", "source_file"
    ]

    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for f in files:
            rec = parse_msms_file(f, meta_dict)
            if rec:
                writer.writerow(rec)

if __name__ == "__main__":
    main()
```


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)



