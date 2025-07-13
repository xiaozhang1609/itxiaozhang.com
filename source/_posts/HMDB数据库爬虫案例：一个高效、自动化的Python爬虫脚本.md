---
title: HMDB数据库爬虫案例：一个高效、自动化的Python爬虫脚本
permalink: /hmdb-database-crawler-case-study-efficient-automated-python-script/
date: 2025-07-13 18:48:58
description: 本文介绍一个强大的Python爬虫脚本，能自动从HMDB网站批量抓取代谢物信息。它支持多线程、缓存和断点续传，极大提升科研数据获取效率。
category:
- 编程开发
tags:
- Python
- 网络爬虫
- HMDB
---

> 原文地址：<https://itxiaozhang.com/hmdb-database-crawler-case-study-efficient-automated-python-script/>  
> 本文配合视频食用效果最佳，视频版本在文章末尾。

## 这个程序是做什么的？

这是一个专门为科研人员设计的网络爬虫工具。它的主要任务是从一个名为HMDB（人类代谢物组数据库）的网站上，自动、批量地抓取代谢物的相关信息。简单来说，你给它一批代谢物的编号（HMDB ID），它就能帮你把这些编号对应的详细分类和来源信息从网站上找回来，并整理好。

## 主要功能

1. **读取数据源**：程序会自动读取`data`文件夹下所有的Excel文件，并从每个文件的第一列中提取出所有格式为`HMDBXXXXXXX`的代谢物编号。

2. **网络数据抓取**：对于每一个提取到的HMDB编号，程序会访问HMDB网站上对应的网页，并抓取以下三个关键信息：
    * **Class (分类)**
    * **Sub Class (亚类)**
    * **Source (来源)**: 判断该物质是内源性（Endogenous）还是外源性（Exogenous）。

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

## 代码

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
import pandas as pd
import time
import concurrent.futures
import logging
import argparse
import json
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import socket

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hmdb_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hmdb_scraper")

# 创建一个具有更强大重试机制的会话
def create_session(retries=5, backoff_factor=0.5, timeout=15):
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    })
    # 设置默认超时时间
    session.timeout = timeout
    return session

# 获取随机User-Agent
def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    ]
    return random.choice(user_agents)

# 清理URL，确保格式正确
def clean_url(url):
    # 移除URL末尾可能的逗号或其他非法字符
    url = re.sub(r'[,\s]+$', '', url)
    # 确保URL格式正确
    if not url.startswith('http'):
        url = 'https://hmdb.ca/metabolites/' + url
    return url

def get_metabolite_data(url, session=None, max_retries=3):
    """
    从HMDB网站获取代谢物数据，增强错误处理
    """
    if session is None:
        session = create_session()
    
    # 清理URL
    url = clean_url(url)
    
    # 提取HMDB ID
    hmdb_id_match = re.search(r'HMDB\d{7}', url)
    if not hmdb_id_match:
        logger.error(f"无效的HMDB URL: {url}")
        return None
    
    hmdb_id = hmdb_id_match.group(0)
    
    # 重试机制
    for attempt in range(max_retries):
        try:
            # 添加随机延迟，避免请求过于规律
            if attempt > 0:
                sleep_time = random.uniform(2, 5) * (attempt + 1)
                logger.info(f"第{attempt+1}次重试 {hmdb_id}，等待 {sleep_time:.2f} 秒")
                time.sleep(sleep_time)
            
            # 发送HTTP请求获取网页内容
            response = session.get(url, timeout=session.timeout)
            
            # 检查请求是否成功
            if response.status_code == 404:
                logger.warning(f"HMDB ID不存在，URL: {url}, 状态码: {response.status_code}")
                return {
                    "Compound ID": hmdb_id,
                    "Class": "ID不存在",
                    "Sub Class": "ID不存在",
                    "Source": "ID不存在"
                }
            
            if response.status_code != 200:
                logger.warning(f"请求失败，URL: {url}, 状态码: {response.status_code}")
                continue  # 尝试重试
            
            # 解析HTML内容
            tree = html.fromstring(response.content)
            
            # 定义要提取的字段及其XPath
            fields = {
                "Class": "//tr/th[text()='Class']/following-sibling::td/a/text()",
                "Sub Class": "//tr/th[text()='Sub Class']/following-sibling::td/a/text()"
            }
            
            # 提取字段数据
            result = {"Compound ID": hmdb_id}
            
            for field_name, xpath in fields.items():
                values = tree.xpath(xpath)
                if values:
                    result[field_name] = values[0]
                else:
                    result[field_name] = "未找到"
            
            # 检测Source中的Endogenous和Exogenous
            source_types = []
            
            # 检查Disposition-Source下是否有Endogenous
            endogenous_xpath = "//a[text()='Disposition']/../..//a[text()='Source']/../..//a[text()='Endogenous']"
            if tree.xpath(endogenous_xpath):
                source_types.append("Endogenous")
            
            # 检查Disposition-Source下是否有Exogenous
            exogenous_xpath = "//a[text()='Disposition']/../..//a[text()='Source']/../..//a[text()='Exogenous']"
            if tree.xpath(exogenous_xpath):
                source_types.append("Exogenous")
            
            # 将结果添加到返回数据中，用逗号分隔
            if source_types:
                result["Source"] = ", ".join(source_types)
            else:
                result["Source"] = "未找到"
            
            return result
            
        except requests.exceptions.Timeout as e:
            logger.warning(f"请求超时，URL: {url}, 错误: {str(e)}")
            # 超时后增加超时时间再重试
            session.timeout = session.timeout + 5
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"连接错误，URL: {url}, 错误: {str(e)}")
            # 连接错误可能是网络问题，等待后重试
            time.sleep(random.uniform(5, 10))
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常，URL: {url}, 错误: {str(e)}")
        except socket.error as e:
            logger.error(f"套接字错误，URL: {url}, 错误: {str(e)}")
        except Exception as e:
            logger.error(f"处理数据异常，URL: {url}, 错误: {str(e)}")
    
    # 所有重试都失败
    logger.error(f"所有重试都失败，无法获取数据: {url}")
    return {
        "Compound ID": hmdb_id,
        "Class": "获取失败",
        "Sub Class": "获取失败",
        "Source": "获取失败"
    }

# 处理单个HMID的函数，用于多线程
def process_hmid(hmid, hmid_cache, session, retry_failed=True):
    """
    处理单个HMID，从缓存或网站获取数据
    """
    # 检查缓存中是否已有该hmid的数据
    if hmid in hmid_cache:
        # 如果缓存中的数据是失败的，并且设置了重试失败项
        if retry_failed and "获取失败" in hmid_cache[hmid].values():
            logger.info(f"重试之前失败的HMID: {hmid}")
        else:
            return hmid_cache[hmid]
    
    # 构建URL并获取数据
    url = f"https://hmdb.ca/metabolites/{hmid}"
    data = get_metabolite_data(url, session)
    
    if data:
        # 缓存数据
        hmid_cache[hmid] = data
        return data
    else:
        # 如果获取失败，添加空数据
        empty_data = {
            "Compound ID": hmid,
            "Class": "获取失败",
            "Sub Class": "获取失败",
            "Source": "获取失败"
        }
        hmid_cache[hmid] = empty_data
        return empty_data

def load_cache(cache_file):
    """
    从文件加载缓存数据
    """
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载缓存文件失败: {str(e)}")
            # 如果加载失败，尝试创建备份并重新开始
            try:
                backup_file = f"{cache_file}.bak"
                if os.path.exists(cache_file):
                    os.rename(cache_file, backup_file)
                    logger.info(f"已创建缓存文件备份: {backup_file}")
            except Exception:
                pass
    return {}

def save_cache(cache_data, cache_file):
    """
    保存缓存数据到文件
    """
    try:
        # 先保存到临时文件，然后重命名，避免写入过程中程序崩溃导致缓存文件损坏
        temp_file = f"{cache_file}.temp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        # 如果成功写入临时文件，则替换原文件
        if os.path.exists(cache_file):
            os.replace(temp_file, cache_file)
        else:
            os.rename(temp_file, cache_file)
    except Exception as e:
        logger.warning(f"保存缓存文件失败: {str(e)}")

def process_excel_files(max_workers=5, use_cache=True, delay=0.5, retry_failed=True, chunk_size=100):
    """
    处理Excel文件，提取HMID并获取相关数据
    增加了分块处理功能，避免一次处理过多数据
    """
    # 确保result文件夹存在
    result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    # 获取data文件夹路径
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    # 缓存文件路径
    cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hmid_cache.json")
    
    # 加载缓存
    hmid_cache = load_cache(cache_file) if use_cache else {}
    
    # 获取所有Excel文件
    excel_files = [f for f in os.listdir(data_dir) if f.endswith(".xlsx")]
    total_files = len(excel_files)
    
    logger.info(f"总共发现 {total_files} 个Excel文件")
    
    # 创建一个会话，所有请求共享
    session = create_session()
    
    # 统计总数据量
    total_hmids_all_files = 0
    file_hmid_counts = {}
    
    # 先统计所有文件中的HMID数量
    for filename in excel_files:
        file_path = os.path.join(data_dir, filename)
        try:
            df = pd.read_excel(file_path)
            first_column = df.columns[0]
            hmid_pattern = re.compile(r'^HMDB\d{7}$')
            hmids = []
            for item in df[first_column]:
                if isinstance(item, str) and hmid_pattern.match(item):
                    hmids.append(item)
                elif isinstance(item, (int, float)) and not pd.isna(item):
                    str_item = str(int(item))
                    if hmid_pattern.match(f"HMDB{str_item.zfill(7)}"):
                        hmids.append(f"HMDB{str_item.zfill(7)}")
            
            file_hmid_counts[filename] = len(hmids)
            total_hmids_all_files += len(hmids)
        except Exception as e:
            logger.error(f"统计文件 {filename} 中的HMID时出错: {str(e)}")
            file_hmid_counts[filename] = 0
    
    logger.info(f"所有文件共包含 {total_hmids_all_files} 个HMID")
    
    # 处理计数器
    processed_hmids_count = 0
    
    # 遍历data文件夹中的所有xlsx文件
    for file_index, filename in enumerate(excel_files, 1):
        file_path = os.path.join(data_dir, filename)
        logger.info(f"[{file_index}/{total_files}] 处理文件: {filename} (包含 {file_hmid_counts[filename]} 个HMID)")
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 获取第一列名称
            first_column = df.columns[0]
            
            # 提取符合格式的hmid
            hmid_pattern = re.compile(r'^HMDB\d{7}$')
            hmids = []
            hmid_indices = {}  # 记录每个HMID在原始数据中的位置
            
            for idx, item in enumerate(df[first_column]):
                if isinstance(item, str) and hmid_pattern.match(item):
                    hmids.append(item)
                    hmid_indices[item] = idx
                elif isinstance(item, (int, float)) and not pd.isna(item):
                    # 处理可能是数字格式的hmid
                    str_item = str(int(item))
                    hmid = f"HMDB{str_item.zfill(7)}"
                    if hmid_pattern.match(hmid):
                        hmids.append(hmid)
                        hmid_indices[hmid] = idx
            
            total_hmids = len(hmids)
            logger.info(f"  文件 {filename} 中发现 {total_hmids} 个HMID")
            
            if not hmids:
                logger.warning(f"  警告: 在文件 {filename} 中没有找到符合格式的HMID")
                continue
            
            # 创建结果DataFrame，保持原始hmid顺序
            result_data = [None] * len(hmids)  # 预分配空间
            
            # 分块处理HMID，避免一次处理过多数据
            for chunk_start in range(0, len(hmids), chunk_size):
                chunk_end = min(chunk_start + chunk_size, len(hmids))
                chunk_hmids = hmids[chunk_start:chunk_end]
                
                logger.info(f"  处理HMID块 {chunk_start+1}-{chunk_end} / {total_hmids}")
                
                # 使用线程池处理HMID
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # 创建任务
                    future_to_hmid = {}
                    for i, hmid in enumerate(chunk_hmids):
                        future = executor.submit(process_hmid, hmid, hmid_cache, session, retry_failed)
                        future_to_hmid[future] = (i + chunk_start, hmid)
                    
                    # 使用tqdm显示进度条
                    with tqdm(total=len(chunk_hmids), desc=f"  处理HMID块 {chunk_start+1}-{chunk_end}", unit="个") as pbar:
                        for future in concurrent.futures.as_completed(future_to_hmid):
                            idx, hmid = future_to_hmid[future]
                            try:
                                data = future.result()
                                result_data[idx] = data
                                processed_hmids_count += 1
                                pbar.set_postfix({"总进度": f"{processed_hmids_count}/{total_hmids_all_files}"})
                            except Exception as e:
                                logger.error(f"    处理HMID {hmid} 时出错: {str(e)}")
                                # 添加空数据
                                empty_data = {
                                    "Compound ID": hmid,
                                    "Class": "处理异常",
                                    "Sub Class": "处理异常",
                                    "Source": "处理异常"
                                }
                                result_data[idx] = empty_data
                                processed_hmids_count += 1
                            finally:
                                pbar.update(1)
                                # 添加小延时，避免请求过于频繁
                                time.sleep(delay)
                
                # 每处理完一个块就保存一次缓存
                if use_cache:
                    save_cache(hmid_cache, cache_file)
                    logger.info(f"  已保存缓存，当前进度: {processed_hmids_count}/{total_hmids_all_files}")
            
            # 过滤掉None值（可能由于某些原因没有处理的HMID）
            result_data = [data for data in result_data if data is not None]
            
            # 创建结果DataFrame
            result_df = pd.DataFrame(result_data)
            
            # 保存结果到result文件夹中的同名文件
            result_file_path = os.path.join(result_dir, filename)
            result_df.to_excel(result_file_path, index=False)
            logger.info(f"  结果已保存到: {result_file_path}")
                
        except Exception as e:
            logger.error(f"  处理文件 {filename} 时出错: {str(e)}")
    
    # 保存最终缓存
    if use_cache:
        save_cache(hmid_cache, cache_file)
        logger.info(f"缓存已保存到: {cache_file}")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='HMDB数据爬取工具')
    parser.add_argument('--workers', type=int, default=5, help='并行处理的线程数 (默认: 5)')
    parser.add_argument('--no-cache', action='store_true', help='禁用缓存')
    parser.add_argument('--delay', type=float, default=0.5, help='请求间隔时间(秒) (默认: 0.5)')
    parser.add_argument('--no-retry-failed', action='store_true', help='不重试之前失败的项')
    parser.add_argument('--chunk-size', type=int, default=100, help='每次处理的HMID块大小 (默认: 100)')
    args = parser.parse_args()
    
    logger.info("开始处理Excel文件")
    logger.info(f"配置: 线程数={args.workers}, 使用缓存={not args.no_cache}, 延迟={args.delay}秒, 重试失败项={not args.no_retry_failed}, 块大小={args.chunk_size}")
    
    start_time = time.time()
    # 处理Excel文件
    process_excel_files(
        max_workers=args.workers,
        use_cache=not args.no_cache,
        delay=args.delay,
        retry_failed=not args.no_retry_failed,
        chunk_size=args.chunk_size
    )
    end_time = time.time()
    
    logger.info(f"处理完成，总耗时: {end_time - start_time:.2f}秒")

if __name__ == "__main__":
    main()
```

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
