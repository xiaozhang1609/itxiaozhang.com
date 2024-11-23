---
title: 使用 Python 从 HMDB 网站提取数据
permalink: /python-hmdb-data-extraction/
date: 2024-10-11 08:59:45
description: 本文介绍了一款自动化工具，用于从人类代谢组数据库（HMDB）批量提取代谢物信息，并根据需求整合。
category:
- 编程案例
tags:
- python
- 脚本
---

> 原文地址：<https://itxiaozhang.com/python-hmdb-data-extraction/>  
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
import re
import html as html_module
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
    url = f"https://hmdb.ca/metabolites/{hmdb_id}"
    
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    tree = html.fromstring(response.content)

    data = {'HMDB ID': hmdb_id}

    description = tree.xpath("//td[@class='met-desc']/text()")
    description_text = description[0].strip() if description else ''

    for column in NEW_COLUMNS:
        data[column] = 'yes' if column in description_text else 'no'

    super_class = tree.xpath("//tr/th[text()='Super Class']/following-sibling::td/a/text()")
    data['Super Class'] = super_class[0].strip() if super_class else ''

    ## 其他类似

    return data

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
        'Biological Properties_Biospecimen Locations',  # 添加新列
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
    results = {}
    total_ids = len(hmdb_ids)
    processed_count = 0
    success_count = 0
    failure_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(get_metabolite_data_with_retry, hmdb_id): hmdb_id for hmdb_id in hmdb_ids}
        
        for future in as_completed(future_to_id):
            hmdb_id = future_to_id[future]
            processed_count += 1
            try:
                data = future.result()
                if data:
                    results[hmdb_id] = data
                    status = "成功"
                    success_count += 1
                else:
                    status = "失败"
                    failure_count += 1
            except Exception:
                status = "失败"
                failure_count += 1
            
            print(f"正在处理第 {processed_count}/{total_ids} 个: {hmdb_id} - {status}")
            
            # 每处理10个数据后写入文件
            if processed_count % 10 == 0:
                write_to_csv(list(results.values()), '代谢物数据_最终.csv', mode='a')
                print(f"已保存到最终文件。已处理: {processed_count}, 成功: {success_count}, 失败: {failure_count}")
                results.clear()  # 清空已写入的结果，节省内存
    
    # 处理剩余的结果
    if results:
        write_to_csv(list(results.values()), '代谢物数据_最终.csv', mode='a')
    
    return success_count, failure_count

def main():
    try:
        # 检查 id.txt 是否存在
        if not os.path.exists('id.txt'):
            print("错误：找不到 id.txt 文件。请确保该文件与程序在同一目录下。")
            input("按回车键退出...")
            sys.exit(1)

        with open('id.txt', 'r') as f:
            hmdb_ids = f.read().splitlines()
        print(f"从id.txt加载了 {len(hmdb_ids)} 个ID")
        
        # 检查异常和重复数据
        invalid_ids, duplicates = check_ids(hmdb_ids)
        
        if invalid_ids:
            print("发现以下异常ID:")
            for index, id in invalid_ids:
                print(f"  第{index}行: {id}")
        
        if duplicates:
            print("发现以下重复ID:")
            for id, count in duplicates.items():
                print(f"  {id}: 重复{count}次")
        
        # 过滤掉无效ID，保留有效的唯一ID
        valid_ids = [id for id in hmdb_ids if id.startswith("HMDB")]
        unique_ids = list(dict.fromkeys(valid_ids))  # 保持顺序的去重
        
        print(f"将处理 {len(unique_ids)} 个有效且唯一的ID")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 清空或创建新的CSV文件
        write_to_csv([], '代谢物数据_最终.csv', mode='w')

        success_count, failure_count = process_ids(unique_ids)

        print(f"数据提取完成。总计: {len(unique_ids)}, 成功: {success_count}, 失败: {failure_count}")
        print(f"最终结果已保存在代谢物数据_最终.csv中")

        # 替换原来的 input() 调用
        print("按回车键退出程序...")
        try:
            input()
        except EOFError:
            pass

if __name__ == "__main__":
    main()
```

## 视频教程

- [哔哩哔哩](https://www.bilibili.com/video/BV1Lg22Y1Ebp)
- [YouTube](https://youtu.be/QXgs0mXYYnQ?si=rUa0uFDbycWNII0j)

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
