---
title: HMDB代谢物信息一键批量获取工具：快速获取代谢组学数据
permalink: /hmdb-metabolite-batch-extraction-tool/
date: 2025-05-15 10:38:01
description: 这是一款专为代谢组学研究设计的Python自动化工具，能够从HMDB数据库批量获取代谢物信息，包括物质分类、组织定位和相关数据库ID等关键信息，大幅提升数据收集效率。
category:
- 编程开发
tags:
- HMDB数据库
- HMDB
- python
- 代谢组学工具
---

> 原文地址：<https://itxiaozhang.com/hmdb-metabolite-batch-extraction-tool/>  
> 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 

## 功能特性

- 支持批量查询HMDB代谢物信息
- 自动提取关键信息，包括：
  - 代谢物描述
  - 超类(Super Class)
  - 类别(Class)
  - 子类(Sub Class)
  - 来源(Disposition)
  - 内源性(Endogenous)
  - 组织定位(Tissue Locations)
  - 相关ID(KEGG、ChEBI、METLIN)
- 支持正负离子模式搜索
- 自动导出CSV格式结果
- 内置日志记录功能

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


## 使用方法

1. 准备输入文件：
   - `positive.txt`：存放正离子模式的质量数
   - `negative.txt`：存放负离子模式的质量数
   - 每行一个质量数

2. 运行程序：
   - 执行程序
   - 等待程序自动处理
   - 完成后按回车键退出

3. 查看结果：
   - 程序会生成`代谢物数据.csv`文件
   - 使用Excel打开即可查看所有提取的信息

## 输出示例

程序会生成包含以下字段的CSV文件：

- HMDB ID
- Description
- Super Class
- Class
- Sub Class
- Disposition_source
- Endogenous
- Biological Properties_Tissue Locations
- KEGG Compound ID
- ChEBI ID
- METLIN ID

## 注意事项

1. 确保网络连接稳定
2. 输入文件格式需要严格遵循要求
3. 大量数据查询可能需要较长时间，请耐心等待
4. 建议定期检查日志文件了解运行状态

## 依赖环境

- Python 3.6+
- requests
- lxml
- logging

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
