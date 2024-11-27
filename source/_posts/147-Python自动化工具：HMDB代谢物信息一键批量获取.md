---
title: Python自动化工具：HMDB代谢物信息一键批量获取
permalink: /python-hmdb-metabolites-batch-extractor/
date: 2024-11-27 12:08:15
description: 本文介绍了一款基于Python开发的自动化工具，可批量获取HMDB数据库中的代谢物信息，支持正负离子模式，提高科研效率。
category:
- 编程案例
tags:
- python
- 脚本
- hmdb
---

> 原文地址：<https://itxiaozhang.com/python-hmdb-metabolites-batch-extractor/>  
> 本文配合视频食用效果最佳，视频版本在文章末尾。   




# HMDB代谢物批量提取工具

## 简介
这是一个用于从HMDB（人类代谢组数据库）批量提取代谢物信息的小工具。它可以帮助研究人员快速获取多个代谢物的详细信息，节省手动查询的时间。

## 功能特点
- 支持正负离子模式（Positive/Negative）
- 批量处理多个质量数
- 自动提取代谢物的关键信息
- 结果保存为Excel可直接打开的CSV文件
- 支持断点续传，出错自动重试

## 使用方法
1. 准备输入文件：
   - `positive.txt`：存放正离子模式的质量数
   - `negative.txt`：存放负离子模式的质量数
   - 每行一个质量数

2. 运行程序：
   - 双击运行程序
   - 等待程序自动处理
   - 完成后按回车键退出

3. 查看结果：
   - 程序会生成`代谢物数据.csv`文件
   - 使用Excel打开即可查看所有提取的信息

## 输出结果包含
- HMDB ID
- 离子模式
- 描述信息
- 分类信息（超类/类/子类）
- 来源信息
- 组织位置
- 相关数据库ID（KEGG/ChEBI/METLIN）
- 结构图链接
- 可增加其他字段

## 注意事项
- 请确保输入的质量数格式正确
- 程序运行需要网络连接
- 处理时间取决于数据量大小

## 相关代码

```python
"""
================================
作者：IT小章
网站：itxiaozhang.com
时间：2024年11月27日
Copyright © 2024 IT小章
================================
"""

import requests
import re
import csv
import time
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from lxml import html


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("代谢物提取.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 常量定义
HMDB_PATTERN = r'HMDB\d{7}'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
BASE_URL = "https://hmdb.ca"
RETRY_DELAYS = [2, 4, 8]  # 重试延迟时间（秒）
MAX_WORKERS = 5  # 最大并发数
TOLERANCE = '0.05'  # 质量误差
TOLERANCE_UNITS = 'Da'  # 质量单位

def search_hmdb_ids(mass, ion_mode='positive'):
    """搜索HMDB IDs"""
    url = f"{BASE_URL}/spectra/ms/search"
    
    # 根据ion_mode选择adduct_type
    if ion_mode == 'positive':
        adduct_types = ['M+H', 'M+Li', 'M+NH4', 'M+Na']
    else:  # negative
        adduct_types = ['M-H']
    
    data = {
        'query_masses': mass,
        'ms_search_ion_mode': ion_mode,
        'adduct_type[]': adduct_types,
        'tolerance': TOLERANCE,
        'tolerance_units': TOLERANCE_UNITS,
        'commit': 'Search'
    }
    
    try:
        response = requests.post(url, data=data, headers=HEADERS)
        response.raise_for_status()
        
        # 提取HMDB IDs
        hmdb_ids = re.findall(HMDB_PATTERN, response.text)
        hmdb_ids = list(dict.fromkeys(hmdb_ids))  # 去重
        logging.info(f"在{ion_mode}模式下找到 {len(hmdb_ids)} 个唯一HMDB ID (质量数: {mass})")
        return hmdb_ids
        
    except Exception as e:
        logging.error(f"搜索HMDB ID时出错: {e}")
        return []
    
def get_metabolite_data(hmdb_id, ion_mode):
    """获取单个HMDB ID的详细信息"""
    url = f"{BASE_URL}/metabolites/{hmdb_id}"
    logging.debug(f"正在获取 {hmdb_id} 的数据")
    
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    tree = html.fromstring(response.content)
    data = {
        'HMDB ID': hmdb_id,
        'Ion_Mode': ion_mode
    }
    
    # 定义要提取的字段和对应的XPath
    fields = {
        'Description': "//td[@class='met-desc']/text()",
        'Super Class': "//tr/th[text()='Super Class']/following-sibling::td/a/text()",
        'Class': "//tr/th[text()='Class']/following-sibling::td/a/text()",
        'Sub Class': "//tr/th[text()='Sub Class']/following-sibling::td/a/text()",
        'Disposition_source': "//tr/th[text()='Disposition']/following-sibling::td/text()",
        'KEGG Compound ID': "//tr/th[text()='KEGG Compound ID']/following-sibling::td/a/text()",
        'ChEBI ID': "//tr/th[text()='ChEBI ID']/following-sibling::td/a/text()",
        'METLIN ID': "//tr/th[text()='METLIN ID']/following-sibling::td/a/text()"
    }

    # 提取基本字段
    for field, xpath in fields.items():
        elements = tree.xpath(xpath)
        data[field] = elements[0].strip() if elements else ''
        logging.debug(f"{hmdb_id} - {field}: {data[field]}")

    # 提取特殊字段
    endogenous = tree.xpath("//th[contains(text(), 'Origin')]/following-sibling::td//li[contains(@class, 'list-group-item')]/text()")
    data['Endogenous'] = ', '.join([item.strip() for item in endogenous]) if endogenous else ''

    tissue_locations = tree.xpath("//th[contains(text(), 'Tissue Locations')]/following-sibling::td//li/text()")
    data['Biological Properties_Tissue Locations'] = ', '.join([item.strip() for item in tissue_locations]) if tissue_locations else ''

    # 提取Structure图片URL
    structure_src = tree.xpath("//img[contains(@src, '/system/metabolites/thumbs/')]/@src")
    if not structure_src:
        structure_src = tree.xpath("//a[contains(@class, 'moldbi-vector-thumbnail')]/img/@src")
    
    if structure_src:
        data['Structure'] = BASE_URL + structure_src[0]
        logging.debug(f"{hmdb_id} - Structure URL: {data['Structure']}")
    else:
        data['Structure'] = ''
        logging.warning(f"{hmdb_id} - 未找到结构图")

    return data

def get_metabolite_data_with_retry(hmdb_id, ion_mode, max_retries=3):
    """带重试机制的数据获取"""
    for attempt, delay in enumerate(RETRY_DELAYS[:max_retries]):
        try:
            return get_metabolite_data(hmdb_id, ion_mode)
        except Exception as e:
            logging.error(f"[{hmdb_id}] 错误: {e}. 第 {attempt + 1}/{max_retries} 次尝试")
            if attempt < max_retries - 1:
                time.sleep(delay)
    logging.error(f"[{hmdb_id}] 所有重试都失败了")
    return None

def process_ids(hmdb_ids, ion_mode):
    """并发处理多个HMDB IDs"""
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_id = {
            executor.submit(get_metabolite_data_with_retry, hmdb_id, ion_mode): hmdb_id 
            for hmdb_id in hmdb_ids
        }
        
        with tqdm(total=len(hmdb_ids), desc=f"处理{ion_mode}模式的ID") as pbar:
            for future in as_completed(future_to_id):
                hmdb_id = future_to_id[future]
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                except Exception as e:
                    logging.error(f"[{hmdb_id}] 未处理的异常: {e}")
                finally:
                    pbar.update(1)
    
    return results

def save_to_csv(results, filename='代谢物数据.csv'):
    """保存结果到CSV文件"""
    try:
        fieldnames = [
            'HMDB ID', 'Ion_Mode', 'Description', 'Super Class', 
            'Class', 'Sub Class', 'Disposition_source', 'Endogenous', 
            'Biological Properties_Tissue Locations', 'KEGG Compound ID', 
            'ChEBI ID', 'METLIN ID', 'Structure'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:  # 使用utf-8-sig以支持Excel打开
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        logging.info(f"数据已保存到 {filename}")
    except Exception as e:
        logging.critical(f"保存CSV文件失败: {e}")

def process_mass_file(filename, ion_mode):
    """处理单个质量文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            masses = [line.strip() for line in f if line.strip()]
        
        logging.info(f"从 {filename} 加载了 {len(masses)} 个质量数")
        
        results = []
        for mass in masses:
            logging.info(f"处理质量数: {mass} ({ion_mode}模式)")
            hmdb_ids = search_hmdb_ids(mass, ion_mode)
            
            if hmdb_ids:
                mass_results = process_ids(hmdb_ids, ion_mode)
                results.extend(mass_results)
            else:
                logging.warning(f"质量数 {mass} 在{ion_mode}模式下未找到HMDB ID")
                
        return results
    except FileNotFoundError:
        logging.error(f"文件未找到: {filename}")
        return []
    except Exception as e:
        logging.error(f"处理文件 {filename} 时出错: {e}")
        return []

def main():
    try:
        # 设置调试级别
        logging.getLogger().setLevel(logging.INFO)
        logging.info("程序开始运行...")
        
        all_results = []
        
        # 处理positive mode
        logging.info("开始处理positive模式...")
        positive_results = process_mass_file('positive.txt', 'positive')
        all_results.extend(positive_results)
        
        # 处理negative mode
        logging.info("开始处理negative模式...")
        negative_results = process_mass_file('negative.txt', 'negative')
        all_results.extend(negative_results)
        
        if all_results:
            # 保存所有结果
            save_to_csv(all_results)
            logging.info(f"处理完成，共获取 {len(all_results)} 条结果")
        else:
            logging.error("未找到任何结果")
            
    except Exception as e:
        logging.critical(f"程序运行失败: {e}")
    finally:
        logging.info("程序运行结束")
        print("\n" + "="*50)
        input("按回车键退出程序...")

if __name__ == "__main__":
    main()
```



## 视频版本

- [哔哩哔哩](lianjie)
- [YouTube](lianjie)

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
