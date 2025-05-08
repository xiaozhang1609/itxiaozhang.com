---
title: 利用Python从HMDB数据库批量提取质谱数据中的化合物信息
permalink: /python-hmdb-mass-spectrometry-compound-extraction/
date: 2025-05-08 15:11:58
description: 本工具通过Python脚本，利用质谱数据中的质量数，从HMDB数据库批量提取化合物信息，包括HMDB ID、常用名称、化学式及结构图片，并将结果导出为CSV文件，极大提升代谢物注释效率。
category:
- 编程开发
tags:
- HMDB数据库
- HMDB
- python
---

> 原文地址：<https://itxiaozhang.com/python-hmdb-mass-spectrometry-compound-extraction/>  
> 本文配合视频食用效果最佳，视频版本在文章末尾。

## 需求分析

本工具旨在帮助用户根据质谱数据（质量数），自动从HMDB数据库批量检索代谢物信息，包括HMDB ID、常用名称、化学式及结构图片等，并导出为Excel可直接打开的CSV文件，极大提升代谢物注释效率。

## 程序介绍

1. **准备数据**：将所有待检索的质量数写入`negative.txt`文件，每行一个。
2. **运行脚本**：
   - 双击或命令行运行`hmdb_metabolite_extractor.py`脚本。
   - 程序自动读取`negative.txt`，并按负离子模式批量检索HMDB。
   - 检索结果自动保存为`代谢物数据.csv`，日志信息保存在`代谢物提取.log`。
3. **主要功能模块**：
   - 质量数批量检索：自动根据质量数和离子模式检索HMDB ID
   - 代谢物详细信息抓取：根据HMDB ID获取常用名称、化学式、结构图片等信息
   - 并发加速与重试机制：采用多线程并发抓取，自动重试机制
   - 结果导出：自动整理为CSV文件，支持Excel直接打开

## 全部代码

```python
"""
================================
作者：IT小章
网站：itxiaozhang.com
时间：2025年04月28日
Copyright © 2024 IT小章
================================
"""

import requests
import re
import csv
import time
import logging
import os
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from lxml import html
from typing import List, Dict, Optional

class Config:
    def __init__(self):
        self.HMDB_PATTERN = r'HMDB\d{7}'
        self.HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        self.BASE_URL = "https://hmdb.ca"
        self.RETRY_DELAYS = [2, 4, 8]
        self.MAX_WORKERS = 5
        self.TOLERANCE = '5'
        self.TOLERANCE_UNITS = 'ppm'
        self.REQUEST_INTERVAL = 1
        self.CACHE_FILE = 'cache.json'
        self.PROGRESS_FILE = 'progress.json'

config = Config()

class ProgressManager:
    def __init__(self, progress_file: str):
        self.progress_file = progress_file
        self.progress = self.load_progress()

    def load_progress(self) -> Dict:
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"加载进度失败: {e}")
        return {'processed_masses': [], 'last_mass': None}

    def save_progress(self, mass: str = None):
        if mass and mass not in self.progress['processed_masses']:
            self.progress['processed_masses'].append(mass)
            self.progress['last_mass'] = mass
            try:
                with open(self.progress_file, 'w', encoding='utf-8') as f:
                    json.dump(self.progress, f)
            except Exception as e:
                logging.error(f"保存进度失败: {e}")

    def is_mass_processed(self, mass: str) -> bool:
        return mass in self.progress['processed_masses']

class CacheManager:
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self) -> Dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"加载缓存失败: {e}")
        return {}

    def save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logging.error(f"保存缓存失败: {e}")

    def get_metabolite_data(self, hmdb_id: str) -> Optional[Dict]:
        return self.cache.get(hmdb_id)

    def set_metabolite_data(self, hmdb_id: str, data: Dict):
        self.cache[hmdb_id] = data
        self.save_cache()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler("代谢物提取.log", encoding='utf-8'), logging.StreamHandler()]
    )

def parse_arguments():
    parser = argparse.ArgumentParser(description='HMDB代谢物自动提取工具')
    parser.add_argument('--input', '-i', default='negative.txt', help='输入文件路径')
    parser.add_argument('--output', '-o', default='代谢物数据.csv', help='输出文件路径')
    parser.add_argument('--mode', '-m', default='negative', choices=['positive', 'negative'], help='离子模式')
    parser.add_argument('--workers', '-w', type=int, default=5, help='并发线程数')
    parser.add_argument('--resume', '-r', action='store_true', help='是否继续上次的进度')
    return parser.parse_args()

def validate_mass(mass: str) -> bool:
    try:
        float(mass)
        return True
    except ValueError:
        return False

def search_hmdb_ids(mass: str, ion_mode: str = 'positive') -> List[str]:
    if not validate_mass(mass):
        logging.error(f"无效的质量数: {mass}")
        return []

    url = f"{config.BASE_URL}/spectra/ms/search"
    adduct_types = ['M+H', 'M+Li', 'M+NH4', 'M+Na'] if ion_mode == 'positive' else ['M+Cl']
    data = {
        'query_masses': mass,
        'ms_search_ion_mode': ion_mode,
        'adduct_type[]': adduct_types,
        'tolerance': config.TOLERANCE,
        'tolerance_units': config.TOLERANCE_UNITS,
        'commit': 'Search'
    }
    
    try:
        response = requests.post(url, data=data, headers=config.HEADERS)
        response.raise_for_status()
        hmdb_ids = list(dict.fromkeys(re.findall(config.HMDB_PATTERN, response.text)))
        logging.info(f"在{ion_mode}模式下找到 {len(hmdb_ids)} 个唯一HMDB ID (质量数: {mass})")
        return hmdb_ids
    except Exception as e:
        logging.error(f"搜索HMDB ID失败: {e}")
        return []

def get_metabolite_data(hmdb_id: str, ion_mode: str, cache_manager: CacheManager) -> Optional[Dict]:
    cached_data = cache_manager.get_metabolite_data(hmdb_id)
    if cached_data:
        return cached_data

    url = f"{config.BASE_URL}/metabolites/{hmdb_id}"
    try:
        response = requests.get(url, headers=config.HEADERS)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        data = {'HMDB ID': hmdb_id, 'Ion_Mode': ion_mode}

        structure_src = tree.xpath("//img[contains(@src, '/system/metabolites/thumbs/')]/@src")
        if not structure_src:
            structure_src = tree.xpath("//a[contains(@class, 'moldbi-vector-thumbnail')]/img/@src")
        data['Structure'] = config.BASE_URL + structure_src[0] if structure_src else ''

        common_name = tree.xpath("//tr/th[text()='Common Name']/following-sibling::td/strong/text()")
        data['Common Name'] = common_name[0] if common_name else ''

        chemical_formula = tree.xpath("//tr/th[text()='Chemical Formula']/following-sibling::td//text()")
        data['Chemical Formula'] = ''.join(chemical_formula).strip() if chemical_formula else ''

        cache_manager.set_metabolite_data(hmdb_id, data)
        time.sleep(config.REQUEST_INTERVAL)
        return data
    except Exception as e:
        logging.error(f"获取代谢物数据失败: {e}")
        return None

def process_ids(hmdb_ids: List[str], ion_mode: str, cache_manager: CacheManager) -> List[Dict]:
    results = []
    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
        futures = {executor.submit(get_metabolite_data, hmdb_id, ion_mode, cache_manager): hmdb_id for hmdb_id in hmdb_ids}
        for future in tqdm(as_completed(futures), total=len(hmdb_ids), desc=f"处理{ion_mode}模式的ID"):
            try:
                data = future.result()
                if data:
                    results.append(data)
            except Exception as e:
                logging.error(f"处理ID失败: {e}")
    return results

def save_to_csv(results: List[Dict], filename: str):
    if not results:
        logging.warning("没有找到任何结果")
        return

    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    fieldnames = ['Mass', 'HMDB ID', 'Ion_Mode', 'Common Name', 'Chemical Formula', 'Structure']
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logging.info(f"已保存 {len(results)} 条记录到 {filename}")
    except Exception as e:
        logging.error(f"保存CSV文件失败: {e}")

def main():
    setup_logging()
    args = parse_arguments()
    config.MAX_WORKERS = args.workers
    
    cache_manager = CacheManager(config.CACHE_FILE)
    progress_manager = ProgressManager(config.PROGRESS_FILE)
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            masses = [line.strip() for line in f if line.strip() and validate_mass(line.strip())]
        
        if not masses:
            logging.error("输入文件为空或不包含有效的质量数")
            return
        
        logging.info(f"从 {args.input} 加载了 {len(masses)} 个质量数")
        all_results = []
        
        for mass in masses:
            if args.resume and progress_manager.is_mass_processed(mass):
                logging.info(f"跳过已处理的质量数: {mass}")
                continue
                
            ids = search_hmdb_ids(mass, args.mode)
            if ids:
                mass_results = process_ids(ids, args.mode, cache_manager)
                for result in mass_results:
                    if result:
                        result['Mass'] = mass
                all_results.extend(mass_results)
                progress_manager.save_progress(mass)
        
        save_to_csv(all_results, args.output)
            
    except FileNotFoundError:
        logging.error(f"找不到输入文件: {args.input}")
    except Exception as e:
        logging.error(f"程序执行出错: {e}")

if __name__ == "__main__":
    main()
```

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
