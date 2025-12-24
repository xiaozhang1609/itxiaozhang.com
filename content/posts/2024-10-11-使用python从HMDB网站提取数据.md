---
title: 使用 Python 从 HMDB 网站提取数据
url: /python-hmdb-data-extraction/
date: '2024-10-11 08:59:45 +0800'
description: 本文介绍了一款自动化工具，用于从人类代谢组数据库（HMDB）批量提取代谢物信息，并根据需求整合。
categories:
  - 编程案例
tags:
  - python
  - 脚本
author: IT小章
---
> 本文配合视频食用效果最佳，视频教程在文章末尾。  

## 这个程序是做什么的？

这个程序可以从人类代谢组数据库（HMDB）网站<https://hmdb.ca/>上获取代谢物的信息。你只需要提供一些HMDB ID，程序就会自动去网站上查找并下载相关数据。

## 主要功能

1. **批量处理**：可以一次处理很多HMDB ID。

2. **数据检查**：会检查你输入的ID是否正确，有没有重复的。

3. **信息收集**：从网站上获取代谢物的各种信息，比如它的分类、在人体内的分布等。

4. **自动重试**：如果因为网络问题失败了，会自动再试几次。

5. **进度显示**：会告诉你现在处理到哪里了，完成了多少。

6. **定期保存**：每处理一些数据就会保存一次，防止意外丢失。

## 程序特点

1. **容易使用**：设计得比较简单，普通人也能操作。

2. **速度快**：可以同时处理多个请求，所以比较快。

3. **不容易出错**：有很多防错设计，运行起来比较稳定。

4. **中文界面**：所有提示都是中文的，看起来更容易懂。

## 源代码

```python
"""
================================
作者：IT小章
网站：itxiaozhang.com
时间：2024年10月11日
Copyright © 2024 IT小章
================================
"""

import csv
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
import os
from collections import Counter
import sys

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

NEW_COLUMNS = [
    "exists in all living species, ranging from bacteria to humans",
    "only found in individuals that have used or taken this drug",
    "not a naturally occurring metabolite and is only found in those individuals exposed to this compound or its derivatives"
]

def check_ids(ids):
    invalid_ids = []
    id_counts = Counter(ids)
    duplicates = {id: count for id, count in id_counts.items() if count > 1}
    
    for index, id in enumerate(ids, 1):
        if not id.startswith("HMDB"):
            invalid_ids.append((index, id))
    
    return invalid_ids, duplicates

def get_metabolite_data(hmdb_id):
    # 省略
    pass

def get_metabolite_data_with_retry(hmdb_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            return get_metabolite_data(hmdb_id)
        except Exception:
            if attempt == max_retries - 1:
                print(f"[{hmdb_id}] 所有重试尝试均失败。")
            time.sleep(2 ** attempt)
    return None

def write_to_csv(results, filename, mode='a'):
    fieldnames = ['HMDB ID'] + NEW_COLUMNS + [
        'Super Class', 'Class', 'Sub Class', 
        'Disposition_source(Endogenous)', 'Endogenous(plant or animal or more)', 
        'Biological Properties_Biospecimen Locations',
        'Biological Properties_Tissue Locations',
        'KEGG Compound ID', 'ChEBI ID', 'METLIN ID'
    ]
    
    file_exists = os.path.isfile(filename)
    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists or mode == 'w':
            writer.writeheader()
        writer.writerows(results)

def process_ids(hmdb_ids, max_workers=5):
    # 省略
    pass

def main():
    try:
        if not os.path.exists('id.txt'):
            print("错误：找不到 id.txt 文件。")
            return

        with open('id.txt', 'r') as f:
            hmdb_ids = f.read().splitlines()
        
        invalid_ids, duplicates = check_ids(hmdb_ids)
        valid_ids = [id for id in hmdb_ids if id.startswith("HMDB")]
        unique_ids = list(dict.fromkeys(valid_ids))
        
        write_to_csv([], '代谢物数据_最终.csv', mode='w')
        success_count, failure_count = process_ids(unique_ids)
        
        print(f"数据提取完成。总计: {len(unique_ids)}, 成功: {success_count}, 失败: {failure_count}")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
```

## 视频教程

- [哔哩哔哩](https://www.bilibili.com/video/BV1Lg22Y1Ebp)
- [YouTube](https://youtu.be/QXgs0mXYYnQ?si=rUa0uFDbycWNII0j)


> 原文地址：<https://itxiaozhang.com/python-hmdb-data-extraction/>
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 
