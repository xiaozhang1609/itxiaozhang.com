---
title: HMDB数据库爬虫案例：一个高效、自动化的Python爬虫脚本
url: /hmdb-database-crawler-case-study-efficient-automated-python-script/
date: '2025-07-13 18:48:58 +0800'
description: 本文介绍一个强大的Python爬虫脚本，能自动从HMDB网站批量抓取代谢物信息。它支持多线程、缓存和断点续传，极大提升科研数据获取效率。
categories:
  - 编程开发
tags:
  - python
  - 网络爬虫
  - hmdb
author: IT小章
---

## 这个程序是做什么的？

这是一个专门为科研人员设计的网络爬虫工具。它的主要任务是从一个名为HMDB（人类代谢物组数据库）的网站上，自动、批量地抓取代谢物的相关信息。简单来说，你给它一批代谢物的编号（HMDB ID），它就能帮你把这些编号对应的详细分类和来源信息从网站上找回来，并整理好。

## 主要功能

1. **读取数据源**：程序会自动读取`data`文件夹下所有的Excel文件，并从每个文件的第一列中提取出所有格式为`HMDBXXXXXXX`的代谢物编号。

2. **网络数据抓取**：对于每一个提取到的HMDB编号，程序会访问HMDB网站上对应的网页，并抓取以下三个关键信息：
    * **Class (分类)**
    * **Sub Class (亚类)**
    * **Source (来源)**：判断该物质是内源性（Endogenous）还是外源性（Exogenous）。

3. **结果保存**：抓取到的信息会以表格形式，保存到`result`文件夹下一个同名的Excel文件中。每一行对应一个HMDB编号和它抓取到的信息。

4. **缓存机制**：程序非常智能，它会把查询过的结果保存在一个名为`hmid_cache.json`的缓存文件中。下次运行时，如果遇到相同的编号，它会直接从缓存中读取数据，而不是重新访问网站，这极大地提高了效率并减少了不必要的网络请求。

5. **断点续传**：得益于缓存机制，如果程序在中途因为网络问题或其他原因中断，下次重新运行时它会自动跳过已经成功处理的编号，从上次中断的地方继续，非常省心。

## 程序特点

1. **自动化与批量处理**：你只需要把包含HMDB编号的Excel文件放进`data`文件夹，运行一次程序，它就能自动处理所有文件，无需人工干预。

2. **高效稳定**：
    * **多线程处理**：程序会同时开启多个线程（默认为5个，可以自己设置）来抓取数据，就像多个人同时在工作，速度比单线程快很多。
    * **智能重试**：如果遇到网络波动或网站临时访问不了，程序会自动尝试重新连接，确保数据抓取的成功率。

3. **用户友好**：
    * **进度条显示**：在程序运行时，你会看到一个清晰的进度条，告诉你当前处理到哪里了，还剩多少任务。
    * **详细日志**：程序会把运行过程中的所有重要信息（如哪个文件处理成功，哪个编号查询失败）记录在`hmdb_scraper.log`日志文件中，方便你随时查看或排查问题。

4. **高可配置性**：你可以通过命令行参数来调整程序的行为，例如：
    * 调整同时工作的线程数量（`--workers`）。
    * 设置是否使用缓存（`--no-cache`）。
    * 调整请求之间的时间间隔（`--delay`）。

## 部分代码

```python
"""
================================
作者：IT小章
博客：itxiaozhang.com
时间：2025年7月13日
Copyright © 2024 IT小章
================================
"""

import requests
from lxml import html
import re
import os

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hmdb_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hmdb_scraper")

# 会话创建（细节省略）
def create_session(*args, **kwargs):
    session = requests.Session()
    # ...屏蔽实现...
    return session

# 随机User-Agent（细节省略）
def get_random_user_agent():
    # ...屏蔽实现...
    return "User-Agent-Placeholder"

# 清理URL
def clean_url(url):
    # ...屏蔽实现...
    return url

# 获取代谢物数据（核心内容已屏蔽）
def get_metabolite_data(url, session=None, max_retries=3):
    if session is None:
        session = create_session()
    url = clean_url(url)
    # ...屏蔽核心爬虫逻辑...
    return {
        "Compound ID": "HMDBXXXXXXX",
        "Class": "屏蔽",
        "Sub Class": "屏蔽",
        "Source": "屏蔽"
    }

# 单个HMID处理函数
def process_hmid(hmid, hmid_cache, session, retry_failed=True):
    if hmid in hmid_cache:
        if retry_failed and "获取失败" in hmid_cache[hmid].values():
            logger.info(f"重试失败项: {hmid}")
        else:
            return hmid_cache[hmid]
    url = f"https://hmdb.ca/metabolites/{hmid}"
    data = get_metabolite_data(url, session)
    hmid_cache[hmid] = data or {
        "Compound ID": hmid,
        "Class": "获取失败",
        "Sub Class": "获取失败",
        "Source": "获取失败"
    }
    return hmid_cache[hmid]

def load_cache(cache_file):
    # ...屏蔽缓存读取实现...
    return {}

def save_cache(cache_data, cache_file):
    # ...屏蔽缓存保存实现...
    pass

# 处理Excel文件（调用逻辑保留）
def process_excel_files(max_workers=5, use_cache=True, delay=0.5, retry_failed=True, chunk_size=100):
    # ...屏蔽部分实现，仅保留接口调用结构与日志...
    logger.info("模拟处理Excel文件...")
    time.sleep(1)
    logger.info("模拟完成。")

def main():
    parser = argparse.ArgumentParser(description='HMDB数据爬取工具（公开版本）')
    parser.add_argument('--workers', type=int, default=5)
    parser.add_argument('--no-cache', action='store_true')
    parser.add_argument('--delay', type=float, default=0.5)
    parser.add_argument('--no-retry-failed', action='store_true')
    parser.add_argument('--chunk-size', type=int, default=100)
    args = parser.parse_args()
    logger.info("启动爬虫（敏感实现已屏蔽）")
    process_excel_files(
        max_workers=args.workers,
        use_cache=not args.no_cache,
        delay=args.delay,
        retry_failed=not args.no_retry_failed,
        chunk_size=args.chunk_size
    )

if __name__ == "__main__":
    main()

```

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


> 原文地址：<https://itxiaozhang.com/hmdb-database-crawler-case-study-efficient-automated-python-script/>
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 
