---
title: HMDB代谢物信息批量获取工具：支持PPM误差计算的Python代谢组学数据提取解决方案
permalink: /hmdb-metabolite-batch-extractor-python-tool-with-ppm-error-calculation/
date: 2025-09-15 09:31:16
description: 文介绍了一个专业的HMDB代谢物信息批量获取工具，该工具支持双离子模式、灵活的Da/PPM误差计算、智能缓存机制和并发处理。通过Python实现，具备企业级稳定性和用户友好的配置界面，为代谢组学研究提供高效的数据获取和代谢物注释解决方案，显著提升科研效率。
category:
- 编程开发
tags:
- HMDB
- Python
- 代谢组学工具
- 质谱数据分析
---

> 原文地址：<https://itxiaozhang.com/hmdb-metabolite-batch-extractor-python-tool-with-ppm-error-calculation/>  
> 本文配合视频食用效果最佳，视频版本在文章末尾。
> 本文对应60号代码。

## 这个程序是做什么的？

HMDB代谢物信息批量获取工具是一个专业的生物信息学工具，专门用于从HMDB（Human Metabolome Database，人类代谢组数据库）批量获取代谢物的详细信息。该工具通过输入代谢物的质量数，自动搜索并提取相关的代谢物数据，为代谢组学研究提供高效的数据获取解决方案。

### 核心用途

- **代谢组学研究**：为质谱分析结果提供代谢物注释
- **化合物鉴定**：根据精确质量数快速匹配可能的代谢物
- **数据库查询**：批量获取代谢物的生物学信息
- **科研辅助**：为生物医学研究提供代谢物数据支持

## 主要功能

### 1. 双离子模式支持

- **正离子模式**：支持M+H、M+Li、M+NH4、M+Na等加合离子
- **负离子模式**：支持M-H加合离子
- **智能模式选择**：用户可根据实验条件选择合适的离子化模式

### 2. 灵活的误差计算方式

- **固定Da误差**：传统的绝对误差计算方式
- **PPM相对误差**：科学的相对误差计算，公式为 `(实验值-理论值)/理论值×10^6`
- **用户可配置**：通过da.txt和ppm.txt文件自定义误差参数

### 3. 智能缓存机制

- **本地缓存**：避免重复请求相同的代谢物数据
- **断点续传**：支持程序中断后继续处理
- **批量保存**：优化I/O操作，提高处理效率

### 4. 高效并发处理

- **多线程处理**：同时处理多个HMDB ID查询
- **智能限流**：控制并发数量，避免服务器过载
- **进度显示**：实时显示处理进度和统计信息

### 5. robust错误处理

- **智能重试**：针对网络错误和服务器503错误的特殊处理
- **指数退避**：逐步增加重试间隔，提高成功率
- **详细日志**：完整记录处理过程和错误信息

### 6. 丰富的数据提取

程序能够提取以下代谢物信息：

- 基本信息：HMDB ID、通用名称、化学式
- 分类信息：超类、类别、子类
- 生物学性质：内源性、组织分布
- 数据库交叉引用：KEGG、ChEBI、METLIN ID
- 结构信息：分子结构图链接

## 程序特点

### 1. 用户友好的交互界面

```
📁 检查输入文件:
   ✓ positive.txt (5 个质量数)
   ✓ negative.txt (2 个质量数)
   ✓ da.txt (3 个Da选项)
   ✓ ppm.txt (4 个PPM选项)

⚙️ 请选择误差计算方式:
   1. 固定Da误差模式 (使用da.txt配置)
   2. PPM相对误差模式 (使用ppm.txt配置)
```

### 2. 高度可配置性

- **配置文件驱动**：所有参数都可通过配置文件调整
- **多精度选择**：支持不同精度要求的应用场景
- **向后兼容**：保持与旧版本的兼容性

### 3. 企业级稳定性

- **连接池管理**：优化网络连接使用
- **内存优化**：智能缓存管理，避免内存溢出
- **异常恢复**：程序崩溃后可从断点继续

### 4. 性能优化

- **批量处理**：一次性处理大量质量数
- **并发控制**：平衡处理速度和服务器负载
- **缓存命中率统计**：实时监控缓存效果

## 全部代码

```python
"""
================================
作者：IT小章
网站：itxiaozhang.com
时间：2025年09月10日
Copyright © 2025 IT小章
================================
"""

import requests
import re
import csv
import time
import logging
import os
import json
import random
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from lxml import html
from typing import List, Dict, Optional
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def print_watermark():
    """打印水印"""
    os.system('cls' if os.name == 'nt' else 'clear')
    watermark = """
================================
作者：IT小章
网站：itxiaozhang.com
时间：2025年09月10日
Copyright © 2025 IT小章
================================
    """
    print(watermark)

# 在配置日志之前先打印水印
print_watermark()

class Config:
    def __init__(self):
        self.HMDB_PATTERN = r'HMDB\d{7}'
        self.HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate'
        }
        self.BASE_URL = "https://hmdb.ca"
        # 优化：增加重试延迟时间，使用指数退避
        self.RETRY_DELAYS = [2, 5, 10, 20, 40]  # 增加延迟时间和重试次数
        # 优化：降低并发数到5
        self.MAX_WORKERS = 5
        self.TOLERANCE = '0.05'
        self.TOLERANCE_UNITS = 'Da'
        # 优化：增加请求间隔
        self.REQUEST_INTERVAL = 1.5  # 从0.2秒增加到1.5秒
        self.CACHE_FILE = 'cache.json'
        self.PROGRESS_FILE = 'progress.json'
        # 优化：减少批量缓存大小，更频繁保存
        self.BATCH_CACHE_SIZE = 20  # 从50减少到20
        # 新增：连接池配置
        self.CONNECTION_POOL_SIZE = 10
        self.CONNECTION_POOL_MAXSIZE = 20
        # 新增：503错误特殊处理延迟
        self.SERVER_ERROR_DELAY = 30  # 遇到503错误时的特殊延迟
        # 新增误差配置
        self.ERROR_MODE = 'da'  # 默认使用Da模式
        self.DA_CONFIG_FILE = 'da.txt'
        self.PPM_CONFIG_FILE = 'ppm.txt'
        self.DA_VALUES = [0.05, 0.01, 0.1]  # 默认Da值
        self.PPM_VALUES = [10.0, 5.0, 15.0]  # 默认PPM值
        self.SELECTED_DA_INDEX = 0  # 默认选择第一个Da值
        self.SELECTED_PPM_INDEX = 0  # 默认选择第一个PPM值

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

    def clear_progress(self):
        """清空进度记录"""
        self.progress = {'processed_masses': [], 'last_mass': None}
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)

class CacheManager:
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.cache = self.load_cache()
        self.pending_cache = {}
        self.cache_counter = 0
        # 新增：缓存统计
        self.cache_hits = 0
        self.cache_misses = 0

    def load_cache(self) -> Dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    logging.info(f"加载缓存成功，包含 {len(cache_data)} 条记录")
                    return cache_data
            except Exception as e:
                logging.warning(f"加载缓存失败: {e}")
        return {}

    def save_cache(self, force=False):
        """批量保存缓存，减少I/O次数"""
        if not self.pending_cache and not force:
            return
            
        try:
            self.cache.update(self.pending_cache)
            pending_count = len(self.pending_cache)
            self.pending_cache.clear()
            
            # 创建备份
            backup_file = f"{self.cache_file}.backup"
            if os.path.exists(self.cache_file):
                shutil.copy2(self.cache_file, backup_file)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            
            logging.info(f"批量保存了 {pending_count} 条缓存记录，总缓存: {len(self.cache)} 条")
        except Exception as e:
            logging.error(f"保存缓存失败: {e}")

    def get_metabolite_data(self, hmdb_id: str) -> Optional[Dict]:
        # 先检查内存缓存
        if hmdb_id in self.pending_cache:
            self.cache_hits += 1
            return self.pending_cache[hmdb_id]
        
        # 再检查持久化缓存
        if hmdb_id in self.cache:
            self.cache_hits += 1
            return self.cache[hmdb_id]
        
        self.cache_misses += 1
        return None

    def set_metabolite_data(self, hmdb_id: str, data: Dict):
        """批量缓存，减少I/O频率"""
        self.pending_cache[hmdb_id] = data
        self.cache_counter += 1
        
        if self.cache_counter >= config.BATCH_CACHE_SIZE:
            self.save_cache()
            self.cache_counter = 0
    
    def flush_cache(self):
        """强制保存所有待写入缓存"""
        self.save_cache(force=True)
        self.cache_counter = 0
        
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        return {
            'total_cached': len(self.cache) + len(self.pending_cache),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.2f}%"
        }

class ErrorConfigManager:
    def __init__(self, da_file: str, ppm_file: str):
        self.da_file = da_file
        self.ppm_file = ppm_file
        self.da_values = self.load_da_config()
        self.ppm_values = self.load_ppm_config()
    
    def load_da_config(self) -> List[float]:
        """加载Da配置文件"""
        try:
            if os.path.exists(self.da_file):
                with open(self.da_file, 'r', encoding='utf-8') as f:
                    values = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                value = float(line.split('#')[0].strip())
                                if 0.0001 <= value <= 1.0:
                                    values.append(value)
                            except ValueError:
                                continue
                    return values if values else [0.05, 0.01, 0.1]
        except Exception as e:
            logging.warning(f"加载Da配置文件失败: {e}")
        return [0.05, 0.01, 0.1]  # 默认值
    
    def load_ppm_config(self) -> List[float]:
        """加载PPM配置文件"""
        try:
            if os.path.exists(self.ppm_file):
                with open(self.ppm_file, 'r', encoding='utf-8') as f:
                    values = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                value = float(line.split('#')[0].strip())
                                if 0.1 <= value <= 1000:
                                    values.append(value)
                            except ValueError:
                                continue
                    return values if values else [10.0, 5.0, 15.0]
        except Exception as e:
            logging.warning(f"加载PPM配置文件失败: {e}")
        return [10.0, 5.0, 15.0]  # 默认值
    
    def calculate_tolerance(self, mass: float, mode: str, da_index: int = 0, ppm_index: int = 0) -> float:
        """计算误差值"""
        if mode == 'da':
            return self.da_values[da_index] if da_index < len(self.da_values) else self.da_values[0]
        elif mode == 'ppm':
            ppm_value = self.ppm_values[ppm_index] if ppm_index < len(self.ppm_values) else self.ppm_values[0]
            return mass * ppm_value / 1_000_000
        else:
            return 0.05  # 默认值

def select_error_mode(error_config_manager: ErrorConfigManager) -> Dict:
    """选择误差计算方式"""
    print("\n⚙️ 请选择误差计算方式:")
    print("   1. 固定Da误差模式 (使用da.txt配置)")
    print("   2. PPM相对误差模式 (使用ppm.txt配置)")
    
    while True:
        choice = input("\n请选择 (1/2，默认为1): ").strip()
        if choice in ['1', '']:
            # 显示Da选项
            print("\n📋 可用的Da误差值:")
            for i, da_val in enumerate(error_config_manager.da_values):
                print(f"   {i+1}. {da_val} Da")
            
            while True:
                da_choice = input(f"\n请选择Da值 (1-{len(error_config_manager.da_values)}，默认为1): ").strip()
                if da_choice == '':
                    da_index = 0
                    break
                try:
                    da_index = int(da_choice) - 1
                    if 0 <= da_index < len(error_config_manager.da_values):
                        break
                    else:
                        print(f"请输入1到{len(error_config_manager.da_values)}之间的数字")
                except ValueError:
                    print("请输入有效的数字")
            
            return {'mode': 'da', 'da_index': da_index, 'ppm_index': 0}
            
        elif choice == '2':
            # 显示PPM选项
            print("\n📋 可用的PPM误差值:")
            for i, ppm_val in enumerate(error_config_manager.ppm_values):
                print(f"   {i+1}. {ppm_val} PPM")
            
            while True:
                ppm_choice = input(f"\n请选择PPM值 (1-{len(error_config_manager.ppm_values)}，默认为1): ").strip()
                if ppm_choice == '':
                    ppm_index = 0
                    break
                try:
                    ppm_index = int(ppm_choice) - 1
                    if 0 <= ppm_index < len(error_config_manager.ppm_values):
                        break
                    else:
                        print(f"请输入1到{len(error_config_manager.ppm_values)}之间的数字")
                except ValueError:
                    print("请输入有效的数字")
            
            return {'mode': 'ppm', 'da_index': 0, 'ppm_index': ppm_index}
        else:
            print("请输入 1 或 2")

# 优化请求会话配置
session = requests.Session()
session.headers.update(config.HEADERS)

# 配置连接池和重试策略（兼容性版本）
try:
    # 尝试使用新版本参数
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=2
    )
except TypeError:
    # 如果失败，使用旧版本参数
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=2
    )

adapter = HTTPAdapter(
    pool_connections=config.CONNECTION_POOL_SIZE,
    pool_maxsize=config.CONNECTION_POOL_MAXSIZE,
    max_retries=retry_strategy
)
session.mount("http://", adapter)
session.mount("https://", adapter)

def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("代谢物提取.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def validate_mass(mass: str) -> bool:
    """验证质量数格式"""
    try:
        float(mass)
        return True
    except ValueError:
        return False

def search_hmdb_ids(mass: str, ion_mode: str, error_config_manager: ErrorConfigManager, error_settings: Dict) -> List[str]:
    if not validate_mass(mass):
        logging.error(f"无效的质量数: {mass}")
        return []

    mass_float = float(mass)
    tolerance = error_config_manager.calculate_tolerance(
        mass_float, 
        error_settings['mode'], 
        error_settings['da_index'], 
        error_settings['ppm_index']
    )
    
    url = f"{config.BASE_URL}/spectra/ms/search"
    if ion_mode == 'positive':
        adduct_types = ['M+H', 'M+Li', 'M+NH4', 'M+Na']
    else:
        adduct_types = ['M-H']
    
    data = {
        'query_masses': mass,
        'ms_search_ion_mode': ion_mode,
        'adduct_type[]': adduct_types,
        'tolerance': str(tolerance),
        'tolerance_units': 'Da',  # 始终使用Da单位，因为我们已经计算好了
        'commit': 'Search'
    }
    
    try:
        time.sleep(random.uniform(0.5, 1.5))
        response = session.post(url, data=data, timeout=15)
        response.raise_for_status()
        hmdb_ids = list(dict.fromkeys(re.findall(config.HMDB_PATTERN, response.text)))
        
        mode_desc = f"{error_settings['mode'].upper()}模式"
        if error_settings['mode'] == 'da':
            tolerance_desc = f"{tolerance} Da"
        else:
            tolerance_desc = f"{error_config_manager.ppm_values[error_settings['ppm_index']]} PPM ({tolerance:.6f} Da)"
        
        logging.info(f"在{ion_mode}模式下找到 {len(hmdb_ids)} 个唯一HMDB ID (质量数: {mass}, {mode_desc}, 误差: {tolerance_desc})")
        return hmdb_ids
    except Exception as e:
        logging.error(f"搜索HMDB ID失败: {e}")
        return []

def get_metabolite_data_with_retry(hmdb_id: str, ion_mode: str, cache_manager: CacheManager, max_retries: int = 5) -> Optional[Dict]:
    """带智能重试机制的数据获取"""
    for attempt in range(max_retries):
        try:
            return get_metabolite_data(hmdb_id, ion_mode, cache_manager)
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            
            # 特殊处理503错误
            if "503" in error_msg or "Service Temporarily Unavailable" in error_msg:
                if attempt < max_retries - 1:
                    delay = config.SERVER_ERROR_DELAY + random.uniform(5, 15)
                    logging.warning(f"[{hmdb_id}] 服务器503错误，等待 {delay:.1f} 秒后重试 (尝试 {attempt+1}/{max_retries})")
                    time.sleep(delay)
                    continue
            
            # 其他错误使用指数退避
            if attempt < max_retries - 1:
                delay = config.RETRY_DELAYS[min(attempt, len(config.RETRY_DELAYS)-1)]
                # 添加随机抖动
                jitter = random.uniform(0.5, 1.5)
                actual_delay = delay * jitter
                logging.warning(f"[{hmdb_id}] 错误: {error_msg}. 等待 {actual_delay:.1f} 秒后重试 (尝试 {attempt+1}/{max_retries})")
                time.sleep(actual_delay)
            else:
                logging.error(f"[{hmdb_id}] 最终错误: {error_msg}")
        except Exception as e:
            logging.error(f"[{hmdb_id}] 未知错误: {e}. 第 {attempt + 1}/{max_retries} 次尝试")
            if attempt < max_retries - 1:
                delay = config.RETRY_DELAYS[min(attempt, len(config.RETRY_DELAYS)-1)]
                time.sleep(delay)
    
    logging.error(f"[{hmdb_id}] 所有重试都失败了")
    return None

def get_metabolite_data(hmdb_id: str, ion_mode: str, cache_manager: CacheManager) -> Optional[Dict]:
    # 首先检查缓存
    cached_data = cache_manager.get_metabolite_data(hmdb_id)
    if cached_data:
        cached_data['Ion_Mode'] = ion_mode
        logging.debug(f"[{hmdb_id}] 使用缓存数据")
        return cached_data

    url = f"{config.BASE_URL}/metabolites/{hmdb_id}"
    try:
        # 添加随机延迟，避免请求过于规律
        base_delay = config.REQUEST_INTERVAL
        random_delay = random.uniform(base_delay * 0.5, base_delay * 1.5)
        time.sleep(random_delay)
        
        logging.debug(f"[{hmdb_id}] 发起网络请求: {url}")
        response = session.get(url, timeout=15)  # 增加超时时间
        response.raise_for_status()
        
        tree = html.fromstring(response.content)
        data = {
            'HMDB ID': hmdb_id,
            'Ion_Mode': ion_mode
        }

        fields = {
            'Description': "//td[@class='met-desc']/text()",
            'Common Name': "//tr/th[text()='Common Name']/following-sibling::td/strong/text()",
            'Chemical Formula': "//tr/th[text()='Chemical Formula']/following-sibling::td//text()",
            'Super Class': "//tr/th[text()='Super Class']/following-sibling::td/a/text()",
            'Class': "//tr/th[text()='Class']/following-sibling::td/a/text()",
            'Sub Class': "//tr/th[text()='Sub Class']/following-sibling::td/a/text()",
            'Disposition_source': "//tr/th[text()='Disposition']/following-sibling::td/text()",
            'KEGG Compound ID': "//tr/th[text()='KEGG Compound ID']/following-sibling::td/a/text()",
            'ChEBI ID': "//tr/th[text()='ChEBI ID']/following-sibling::td/a/text()",
            'METLIN ID': "//tr/th[text()='METLIN ID']/following-sibling::td/a/text()"
        }

        for field, xpath in fields.items():
            elements = tree.xpath(xpath)
            if field == 'Chemical Formula':
                data[field] = ''.join(elements).strip() if elements else ''
            else:
                data[field] = elements[0].strip() if elements else ''

        endogenous = tree.xpath("//th[contains(text(), 'Origin')]/following-sibling::td//li[contains(@class, 'list-group-item')]/text()")
        data['Endogenous'] = ', '.join([item.strip() for item in endogenous]) if endogenous else ''

        tissue_locations = tree.xpath("//th[contains(text(), 'Tissue Locations')]/following-sibling::td//li/text()")
        data['Biological Properties_Tissue Locations'] = ', '.join([item.strip() for item in tissue_locations]) if tissue_locations else ''

        structure_src = tree.xpath("//img[contains(@src, '/system/metabolites/thumbs/')]/@src")
        if not structure_src:
            structure_src = tree.xpath("//a[contains(@class, 'moldbi-vector-thumbnail')]/img/@src")
        data['Structure'] = config.BASE_URL + structure_src[0] if structure_src else ''

        # 保存到缓存
        cache_manager.set_metabolite_data(hmdb_id, data)
        logging.debug(f"[{hmdb_id}] 数据获取成功并已缓存")
        
        return data
    except Exception as e:
        logging.error(f"[{hmdb_id}] 获取代谢物数据失败: {e}")
        raise  # 重新抛出异常，让重试机制处理

def process_ids(hmdb_ids: List[str], ion_mode: str, cache_manager: CacheManager) -> List[Dict]:
    results = []
    
    # 显示缓存统计
    cache_stats = cache_manager.get_cache_stats()
    logging.info(f"开始处理 {len(hmdb_ids)} 个ID，当前缓存统计: {cache_stats}")
    
    # 过滤已缓存的ID
    uncached_ids = [hmdb_id for hmdb_id in hmdb_ids if not cache_manager.get_metabolite_data(hmdb_id)]
    cached_count = len(hmdb_ids) - len(uncached_ids)
    
    if cached_count > 0:
        logging.info(f"发现 {cached_count} 个已缓存的ID，将直接使用缓存数据")
        # 添加缓存数据到结果
        for hmdb_id in hmdb_ids:
            cached_data = cache_manager.get_metabolite_data(hmdb_id)
            if cached_data:
                cached_data['Ion_Mode'] = ion_mode
                results.append(cached_data)
    
    if uncached_ids:
        logging.info(f"需要网络请求的ID数量: {len(uncached_ids)}")
        
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            future_to_id = {
                executor.submit(get_metabolite_data_with_retry, hmdb_id, ion_mode, cache_manager): hmdb_id 
                for hmdb_id in uncached_ids
            }
            
            with tqdm(total=len(uncached_ids), desc=f"处理{ion_mode}模式的ID") as pbar:
                for future in as_completed(future_to_id):
                    hmdb_id = future_to_id[future]
                    try:
                        data = future.result()
                        if data:
                            results.append(data)
                        else:
                            logging.warning(f"[{hmdb_id}] 未能获取数据")
                    except Exception as e:
                        logging.error(f"[{hmdb_id}] 未处理的异常: {e}")
                    finally:
                        pbar.update(1)
                        
                        # 每处理10个ID就保存一次缓存
                        if pbar.n % 10 == 0:
                            cache_manager.flush_cache()
    
    # 最终保存缓存
    cache_manager.flush_cache()
    
    # 显示最终统计
    final_stats = cache_manager.get_cache_stats()
    logging.info(f"处理完成，最终缓存统计: {final_stats}")
    
    return results

def process_mass_file(filename: str, ion_mode: str, cache_manager: CacheManager, progress_manager: ProgressManager, error_config_manager: ErrorConfigManager, error_settings: Dict, resume: bool = False) -> List[Dict]:
    """处理单个质量文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            masses = [line.strip() for line in f if line.strip() and validate_mass(line.strip())]
        
        if not masses:
            logging.warning(f"文件 {filename} 为空或不包含有效的质量数")
            return []
        
        logging.info(f"从 {filename} 加载了 {len(masses)} 个质量数")
        
        results = []
        for mass in masses:
            if resume and progress_manager.is_mass_processed(f"{mass}_{ion_mode}"):
                logging.info(f"跳过已处理的质量数: {mass} ({ion_mode}模式)")
                continue
                
            logging.info(f"处理质量数: {mass} ({ion_mode}模式)")
            hmdb_ids = search_hmdb_ids(mass, ion_mode, error_config_manager, error_settings)
            
            if hmdb_ids:
                mass_results = process_ids(hmdb_ids, ion_mode, cache_manager)
                for result in mass_results:
                    if result:
                        result['Mass'] = mass
                results.extend(mass_results)
                progress_manager.save_progress(f"{mass}_{ion_mode}")
            else:
                logging.warning(f"质量数 {mass} 在{ion_mode}模式下未找到HMDB ID")
                
        return results
    except FileNotFoundError:
        logging.error(f"文件未找到: {filename}")
        return []
    except Exception as e:
        logging.error(f"处理文件 {filename} 时出错: {e}")
        return []

def save_to_csv(results: List[Dict], filename: str):
    if not results:
        logging.warning("没有找到任何结果")
        return

    fieldnames = [
        'Mass', 'HMDB ID', 'Ion_Mode', 'Description', 'Common Name', 'Chemical Formula',
        'Super Class', 'Class', 'Sub Class', 'Disposition_source', 'Endogenous', 
        'Biological Properties_Tissue Locations', 'KEGG Compound ID', 
        'ChEBI ID', 'METLIN ID', 'Structure'
    ]
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logging.info(f"已保存 {len(results)} 条记录到 {filename}")
    except Exception as e:
        logging.error(f"保存CSV文件失败: {e}")

def check_input_files():
    """检查输入文件是否存在"""
    files_info = []
    
    if os.path.exists('positive.txt'):
        with open('positive.txt', 'r', encoding='utf-8') as f:
            pos_count = len([line for line in f if line.strip() and validate_mass(line.strip())])
        files_info.append(f"✓ positive.txt ({pos_count} 个质量数)")
    else:
        files_info.append("✗ positive.txt (文件不存在)")
    
    if os.path.exists('negative.txt'):
        with open('negative.txt', 'r', encoding='utf-8') as f:
            neg_count = len([line for line in f if line.strip() and validate_mass(line.strip())])
        files_info.append(f"✓ negative.txt ({neg_count} 个质量数)")
    else:
        files_info.append("✗ negative.txt (文件不存在)")
    
    return files_info

def user_interaction():
    """用户交互界面"""
    print("\n" + "="*60)
    print("           HMDB代谢物信息批量获取工具")
    print("="*60)
    
    print("\n📁 检查输入文件:")
    files_info = check_input_files()
    for info in files_info:
        print(f"   {info}")
    
    has_positive = os.path.exists('positive.txt')
    has_negative = os.path.exists('negative.txt')
    
    if not has_positive and not has_negative:
        print("\n❌ 错误: 未找到 positive.txt 或 negative.txt 文件！")
        print("\n📝 使用说明:")
        print("   1. 请在程序同目录下创建 positive.txt 和/或 negative.txt 文件")
        print("   2. 每个文件中写入质量数，每行一个")
        print("   3. 重新运行程序")
        input("\n按回车键退出程序...")
        return None
    
    progress_manager = ProgressManager(config.PROGRESS_FILE)
    if progress_manager.progress['processed_masses']:
        print(f"\n🔄 检测到上次未完成的任务 (已处理 {len(progress_manager.progress['processed_masses'])} 个质量数)")
        while True:
            choice = input("   是否继续上次的进度？(y/n): ").lower().strip()
            if choice in ['y', 'yes', '是', '']:
                return 'resume'
            elif choice in ['n', 'no', '否']:
                progress_manager.clear_progress()
                break
            else:
                print("   请输入 y 或 n")
    
    print("\n⚙️ 请选择处理模式:")
    if has_positive and has_negative:
        print("   1. 处理正离子模式 (positive.txt)")
        print("   2. 处理负离子模式 (negative.txt)")
        print("   3. 处理双离子模式 (positive.txt + negative.txt) [推荐]")
        
        while True:
            choice = input("\n请选择 (1/2/3，默认为3): ").strip()
            if choice == '1':
                return 'positive'
            elif choice == '2':
                return 'negative'
            elif choice in ['3', '']:
                return 'both'
            else:
                print("请输入 1、2 或 3")
    elif has_positive:
        print("   自动选择: 正离子模式 (positive.txt)")
        return 'positive'
    elif has_negative:
        print("   自动选择: 负离子模式 (negative.txt)")
        return 'negative'

def check_expiration():
    """检查软件是否过期"""
    # 设置到期日期：2026年9月10日
    expiry_date = datetime(2026, 9, 10)
    current_date = datetime.now()
    
    if current_date > expiry_date:
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 显示到期信息
        expiry_message = """
================================

该工具已过期。

如需继续使用，请联系：
邮箱：xiaozhang.tech@hotmail.com
哔哩哔哩：https://space.bilibili.com/3546893749586357

感谢您的使用！
================================
        """
        print(expiry_message)
        input("\n按回车键退出程序...")
        exit(0)  # 退出程序
    
    # 如果未到期，可以添加剩余天数提示（可选）
    days_remaining = (expiry_date - current_date).days
    if days_remaining <= 30:  # 剩余30天内提醒
        print(f"\n⚠️  软件将在 {days_remaining} 天后到期 (到期日期: 2026年9月10日)")
        print("如需续期，请联系：xiaozhang.tech@hotmail.com\n")

def main():
    try:
        # 首先检查软件是否过期
        check_expiration()
        
        setup_logging()
        
        # 初始化误差配置管理器
        error_config_manager = ErrorConfigManager(config.DA_CONFIG_FILE, config.PPM_CONFIG_FILE)
        
        mode = user_interaction()
        if mode is None:
            return
        
        resume = (mode == 'resume')
        if resume:
            mode = 'both'
        
        # 选择误差计算方式
        error_settings = select_error_mode(error_config_manager)
        
        print(f"\n🚀 开始处理，模式: {mode}")
        print(f"📊 误差设置: {error_settings['mode'].upper()}模式")
        if error_settings['mode'] == 'da':
            print(f"   Da误差值: {error_config_manager.da_values[error_settings['da_index']]} Da")
        else:
            print(f"   PPM误差值: {error_config_manager.ppm_values[error_settings['ppm_index']]} PPM")
        print("\n" + "="*60)
        
        cache_manager = CacheManager(config.CACHE_FILE)
        progress_manager = ProgressManager(config.PROGRESS_FILE)
        
        all_results = []
        
        if mode in ['positive', 'both'] and os.path.exists('positive.txt'):
            logging.info("开始处理positive模式...")
            positive_results = process_mass_file('positive.txt', 'positive', cache_manager, progress_manager, error_config_manager, error_settings, resume)
            all_results.extend(positive_results)
        
        if mode in ['negative', 'both'] and os.path.exists('negative.txt'):
            logging.info("开始处理negative模式...")
            negative_results = process_mass_file('negative.txt', 'negative', cache_manager, progress_manager, error_config_manager, error_settings, resume)
            all_results.extend(negative_results)
        
        if all_results:
            save_to_csv(all_results, '代谢物数据.csv')
            print(f"\n✅ 处理完成！共获取 {len(all_results)} 条结果")
            print(f"📄 结果已保存到: 代谢物数据.csv")
            print(f"📋 日志已保存到: 代谢物提取.log")
            
            # 显示最终缓存统计
            final_cache_stats = cache_manager.get_cache_stats()
            print(f"📊 缓存统计: {final_cache_stats}")
            
            progress_manager.clear_progress()
        else:
            print("\n❌ 未找到任何结果")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断程序")
        logging.info("用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        logging.critical(f"程序运行失败: {e}")
    finally:
        print("\n" + "="*60)
        input("按回车键退出程序...")

if __name__ == "__main__":
    main()
```

## 技术亮点

1. **科学的误差计算**：支持PPM相对误差，适应不同质量范围的化合物
2. **智能网络处理**：针对HMDB服务器特点优化的请求策略
3. **高效缓存机制**：多层缓存设计，显著提高处理效率
4. **robust错误处理**：全面的异常处理和恢复机制
5. **用户友好设计**：直观的配置文件和交互界面

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
