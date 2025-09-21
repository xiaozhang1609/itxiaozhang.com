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
> 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 

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

## 部分代码

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

class MetaboliteExtractor:
    """代谢物数据提取器"""
    
    def __init__(self):
        self.base_url = "https://hmdb.ca"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def process_files(self):
        """处理输入文件"""
        try:
            logging.info("程序开始运行...")
            results = []
            
            # 处理positive模式
            if os.path.exists('positive.txt'):
                logging.info("处理positive.txt...")
                results.extend(self._process_file('positive.txt', 'positive'))
            
            # 处理negative模式
            if os.path.exists('negative.txt'):
                logging.info("处理negative.txt...")
                results.extend(self._process_file('negative.txt', 'negative'))
            
            if results:
                self._save_results(results)
                logging.info(f"处理完成，共获取 {len(results)} 条结果")
            else:
                logging.error("未找到任何结果")
                
        except Exception as e:
            logging.error(f"处理过程出错: {str(e)}")
        finally:
            logging.info("程序运行结束")
            print("\n" + "="*50)
            input("按回车键退出程序...")
    
    def _process_file(self, filename, mode):
        """处理单个文件（具体实现已隐藏）"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = f.read().strip()
            if not data:
                logging.warning(f"{filename} 为空")
                return []
            logging.info(f"正在处理 {filename}")
            return self._extract_data(data, mode)
        except FileNotFoundError:
            logging.error(f"未找到文件: {filename}")
            return []
    
    def _extract_data(self, data, mode):
        """提取数据（具体实现已隐藏）"""
        # 核心实现已隐藏
        pass
    
    def _save_results(self, results):
        """保存结果到CSV"""
        try:
            filename = '代谢物数据.csv'
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
            logging.info(f"数据已保存到 {filename}")
        except Exception as e:
            logging.error(f"保存数据失败: {str(e)}")

def main():
    extractor = MetaboliteExtractor()
    extractor.process_files()

if __name__ == "__main__":
    main()
```

## 视频版本

- [哔哩哔哩](https://www.bilibili.com/video/BV1DsBQYwEC4/)
- [YouTube](https://youtu.be/LWwqvTgxm3o?si=Uqy46agi8KYQpD9H)

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
