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
> 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，点击电脑维修，加我微信咨询。 

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

## 部分代码

```python
"""代谢物数据处理工具"""

import json, os, logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from typing import List, Dict, Optional

class DataManager:
    def __init__(self, cache_file='cache.json', progress_file='progress.json'):
        self.cache_file = cache_file
        self.progress_file = progress_file
        self.cache = self._load_json(cache_file, {})
        self.progress = self._load_json(progress_file, {'processed': []})
    
    def _load_json(self, file: str, default: Dict) -> Dict:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return default
    
    def save_progress(self, item_id: str):
        if item_id not in self.progress['processed']:
            self.progress['processed'].append(item_id)
            self._save_json(self.progress_file, self.progress)
    
    def _save_json(self, file: str, data: Dict):
        try:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            logging.error(f"保存文件失败: {e}")
    
    def is_processed(self, item_id: str) -> bool:
        return item_id in self.progress['processed']
    
    def get_cache(self, key: str) -> Optional[Dict]:
        return self.cache.get(key)
    
    def set_cache(self, key: str, data: Dict):
        self.cache[key] = data
        self._save_json(self.cache_file, self.cache)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("处理日志.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def process_data(items: List[str], resume: bool = False) -> List[Dict]:
    """处理数据的主要函数
    
    Args:
        items: 待处理的数据项列表
        resume: 是否继续上次的进度
        
    Returns:
        处理结果列表
    """
    data_manager = DataManager()
    results = []
    
    for item in items:
        # 检查是否已处理
        if resume and data_manager.is_processed(item):
            continue
            
        # 获取数据 - 
        data = {"id": item, "status": "processed"}
        results.append(data)
        
        # 保存进度
        data_manager.save_progress(item)
    
    return results

def main():
    setup_logging()
    try:
        # 读取输入数据 - 
        items = ["item1", "item2", "item3"]
        
        # 处理数据
        results = process_data(items, resume=True)
        
        # 保存结果 - 
        if results:
            logging.info(f"成功处理 {len(results)} 条数据")
                
    except Exception as e:
        logging.error(f"程序执行出错: {e}")

if __name__ == "__main__":
    main()
```

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，点击电脑维修，加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
