---
title: 使用Python从HMDB网站提取代谢物生物来源信息
permalink: /python-hmdb-metabolite-biosource-extractor/
date: 2025-04-27 09:12:08
description: 使用Python从HMDB数据库获取代谢物的生物来源信息，结合智能HTML解析与关键词匹配算法，高效生成结构化数据报告。
category:
- 编程开发
tags:
- 数据采集
- hmdb
- Python
---

> 原文地址：<https://itxiaozhang.com/python-hmdb-metabolite-biosource-extractor/>  
> 本文配合视频食用效果最佳，视频版本在文章末尾。

## 核心功能

- **自动化数据采集**：基于requests库实现稳定可靠的数据抓取
- **智能内容解析**：采用lxml高效提取HTML中的关键信息
- **多维度分类**：精准识别7类生物来源（人类、食品、微生物等）
- **双语日志系统**：中英文混合日志记录，便于问题追踪
- **结构化输出**：标准CSV格式结果，兼容各类分析工具
- **实时进度监控**：可视化进度条显示任务执行情况

## 使用指南

### 准备工作

1. 创建输入文件`hmdb_id.txt`，每行包含一个HMDB ID
2. 推荐使用Python 3.7+环境

### 环境配置

```bash
# 安装依赖库
pip install requests lxml pandas
```

### 执行程序

```bash
python get_disposition.py
```

## 部分代码

```python
import requests
import os
import logging
from lxml import html
import html as html_module
import re
import csv
from typing import List, Dict, Any, Union

"""
================================
作者：IT小章
主页txiaozhang.com
时间：2025年04月20日
Copyright © 2025 IT小章
================================
"""

# 配置日志记录器
file_handler = logging.FileHandler('disposition_log.txt', mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(message)s'))
console_handler.addFilter(lambda record: not record.msg.startswith('\n'))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 关键词定义（按长度降序排列防止覆盖）
KEYWORDS = [
    {'pattern': r'\bAnimal\b(?!.{0,10}origin)', 'display_name': 'Animal'},
    {'pattern': r'\bAquatic\b(?!.{0,10}origin)', 'display_name': 'Aquatic'},
    {'pattern': r'\bEndogenous\b', 'display_name': 'Endogenous'},
    {'pattern': r'\bMollusk\b', 'display_name': 'Mollusk'},
    {'pattern': r'\bAnimal origin\b', 'display_name': 'Animal origin'},
    {'pattern': r'\bAquatic origin\b', 'display_name': 'Aquatic origin'},
    {'pattern': r'\bSource\b', 'display_name': 'Source'}
]


def process_node(node, indent_level=0) -> str:
    """递归处理HTML节点结构，将HTML转换为格式化文本
    
    Args:
        node: HTML节点
        indent_level: 缩进级别
        
    Returns:
        str: 格式化后的文本
    """
    text = ''
    if node.tag == 'br':
        return '\n'
    if node.tag in ['ul', 'ol']:
        text += '\n' + '  ' * indent_level
    if node.tag == 'li':
        bullet = ['- ', '* ', '• '][indent_level % 3]
        text += '\n' + '  ' * indent_level + bullet
    
    if node.text:
        text += node.text.strip()
    
    for child in node:
        text += process_node(child, indent_level + 1 if node.tag in ['ul', 'ol'] else indent_level)
        if child.tail and child.tail.strip():
            text += child.tail.strip() + ' '
    
    if node.tag in ['p', 'div']:
        text += '\n\n'
    return text


def clean_html_text(text: str) -> str:
    """清理HTML文本，移除HTML标签和实体
    
    Args:
        text: 原始HTML文本
        
    Returns:
        str: 清理后的文本
    """
    # 解码HTML实体
    text = html_module.unescape(text)
    # 替换所有残留实体
    text = re.sub(r'&\w+;', ' ', text)
    # 标准化空白符
    text = re.sub(r'[\t\r\f\v]+', ' ', text)
    # 合并连续空格
    text = re.sub(r' +', ' ', text)
    # 规范化换行
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    # 转换列表项
    text = re.sub(r'<li>', '\n- ', text)
    # 移除剩余HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 保留段落间距
    text = re.sub(r'\n{2,}', '\n\n', text).strip()
    
    return text


def get_disposition_source(hmdb_id: str) -> List[Union[str, int]]:
    url = f"https://hmdb.ca/metabolites/{hmdb_id}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        tree = html.fromstring(response.content)

        disposition_td = tree.xpath("//table//tr/th[contains(normalize-space(), 'Disposition')]/following-sibling::td")
        if not disposition_td:
            logging.info(f"未找到Disposition字段：{hmdb_id}")
            return [hmdb_id] + ['no'] * len(KEYWORDS)
            
        disposition_td = disposition_td[0]
        
        disposition_text = process_node(disposition_td)
        disposition_text = clean_html_text(disposition_text)
        
        # 仅在日志文件中记录详细内容
        file_handler = next(handler for handler in logging.getLogger().handlers if isinstance(handler, logging.FileHandler))
        file_handler.emit(logging.LogRecord(
            'root', logging.INFO, '', 0,
            f"\nHMDB ID: {hmdb_id}\n\nDisposition Content:\n{disposition_text}\n{'='*50}", (), None
        ))
        
        # 统计关键词出现次数并转换为yes/no
        keyword_stats = {}
        for kw in KEYWORDS:
            matches = re.findall(kw['pattern'], disposition_text, flags=re.IGNORECASE)
            keyword_stats[kw['display_name']] = 'yes' if matches else 'no'

        # 仅在日志文件中记录关键词统计
        stats_text = "\n关键词统计结果:\n" + "\n".join([f"- {kw}: {'是' if val == 'yes' else '否'}" for kw, val in keyword_stats.items()])
        file_handler.emit(logging.LogRecord(
            'root', logging.INFO, '', 0,
            f"{stats_text}\n{'='*50}", (), None
        ))
        
        return [hmdb_id] + [keyword_stats.get(kw['display_name'], 'no') for kw in KEYWORDS]
    
    except Exception as e:
        logging.error(f"处理失败: {hmdb_id}，错误信息: {str(e)}")
        return [hmdb_id] + ['no'] * len(KEYWORDS)


def main():
    """主函数，处理HMDB ID列表并生成结果CSV文件"""
    try:
        # 读取hmdb_id.txt文件
        with open('hmdb_id.txt', 'r') as f:
            hmdb_ids = [line.strip() for line in f if line.strip()]
        
        if not hmdb_ids:
            logging.error("HMDB ID文件为空或不存在有效ID")
            return
        
        csv_file_path = "disposition_results.csv"
        csv_headers = ["HMDB ID"] + [kw['display_name'] for kw in KEYWORDS]
        
        # 写入CSV文件
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(csv_headers)
            
            total = len(hmdb_ids)
            for idx, hmdb_id in enumerate(hmdb_ids, 1):
                try:
                    # 显示进度信息
                    logging.info(f"正在处理: {hmdb_id}，第{idx}个，共{total}个")
                    
                    # 获取处理结果并写入CSV
                    disposition_results = get_disposition_source(hmdb_id)
                    csv_writer.writerow(disposition_results)
                    csvfile.flush()  # 确保数据立即写入文件
                except Exception as e:
                    logging.error(f"处理失败: {hmdb_id}，错误信息: {str(e)}")
        
        logging.info(f"处理完成，共处理{total}个HMDB ID，结果已保存至{csv_file_path}")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()
```

## 输出结果

- `disposition_results.csv`：包含各ID的生物来源标记(yes/no)
- `disposition_log.txt`：详细抓取日志和关键词统计

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
