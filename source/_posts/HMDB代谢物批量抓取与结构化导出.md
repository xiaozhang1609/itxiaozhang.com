---
title: HMDB代谢物批量抓取与结构化导出
permalink: /hmdb-metabolite-batch-extraction-csv-export/
date: 2025-11-03 20:56:43
description: 这篇文章介绍了一个HMDB代谢物批量爬虫工具，自持同时爬取几万条数据、并发限速与重试、断点续跑，解析25项核心字段并导出CSV。
category:
- 编程开发
tags:
- HMDB
- 代谢物
- Python
- 爬虫
---

> 原文地址：<https://itxiaozhang.com/hmdb-metabolite-batch-extraction-csv-export/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。    


## 需求介绍
- 自动化获取多个 HMDB ID 的完整字段，减少手工搜索与遗漏。
- 稳定可靠：处理限速与网络波动，不中断、可续跑。
- 输出可用：统一字段、原始顺序、便于下游分析与复现。

## 程序如何运行
- 准备
  - 在 `id.txt` 放入待处理 ID（如 `HMDB0000123`），一行一个。
  - 安装依赖：
    ```bash
    pip install requests lxml psutil pandas
    ```
- 执行
  ```bash
  python HMDB_Metabolite_Extractor.py
  ```
- 结果
  - 数据：`代谢物数据_最终.csv`（按原始 ID 顺序）。
  - 失败：`失败.txt`（便于回补）。
  - 进度：`progress.json`（断点续跑）。

## 整体框架
- I/O 层
  - 读取 `id.txt`；写入 `代谢物数据_最终.csv`；失败与进度持久化。
- 抓取层
  - `requests` + 全局 `RateLimiter` 控制 QPS；统一超时与重试策略。
- 解析层
  - `lxml` + 细粒度 XPath，覆盖 25 个关键字段（名称、化学式、分子量、分类层级、性质、通路、浓度、疾病参考、外部 ID 等）。
- 并发层
  - `ThreadPoolExecutor`；批量写入、降内存；进度与估时。
- 排序与收尾
  - 按原始 ID 重新排序；清理临时文件；统计汇总。

## 全部代码（Windows10）

```
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
import threading
import json
from datetime import datetime
import psutil
import queue

# 作者：IT小章
# 时间：2025年11月01日
# 网站：itxiaozhang.com

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 配置常量
MAX_WORKERS = 5
REQUESTS_PER_SECOND = 5
BATCH_WRITE_SIZE = 500
PROGRESS_REPORT_INTERVAL = 100
REQUEST_TIMEOUT = (5, 15)  # 连接超时5秒，读取超时15秒
MAX_RETRIES = 2

class RateLimiter:
    """全局速率限制器 - 令牌桶算法"""
    def __init__(self, rate):
        self.rate = rate  # 每秒允许的请求数
        self.tokens = rate
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def acquire(self):
        """获取一个令牌，如果没有可用令牌则等待"""
        with self.lock:
            now = time.time()
            # 添加新令牌
            self.tokens = min(self.rate, self.tokens + (now - self.last_update) * self.rate)
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            else:
                # 计算需要等待的时间
                wait_time = (1 - self.tokens) / self.rate
                return wait_time

# 全局速率限制器实例
rate_limiter = RateLimiter(REQUESTS_PER_SECOND)

def check_ids(ids):
    invalid_ids = []
    id_counts = Counter(ids)
    duplicates = {id: count for id, count in id_counts.items() if count > 1}
    
    for index, id in enumerate(ids, 1):
        if not id.startswith("HMDB"):
            invalid_ids.append((index, id))
    
    return invalid_ids, duplicates

def clean_text(text):
    # 移除不可见字符和特殊字符
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\u200B-\u200D\uFEFF]', '', text)
    # 将多个空格替换为单个空格
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def get_metabolite_data(hmdb_id):
    url = f"https://hmdb.ca/metabolites/{hmdb_id}"
    
    # 速率限制
    wait_time = rate_limiter.acquire()
    if wait_time is not True:
        time.sleep(wait_time)
        rate_limiter.acquire()  # 再次获取令牌
    
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    
    tree = html.fromstring(response.content)

    data = {}
    
    # 01_HMDB_ID
    data['HMDB_ID'] = hmdb_id
    
    # 02_Common_Name - 恢复原始精确逻辑
    common_name_element = tree.xpath('//th[text()="Common Name"]/following-sibling::td[1]')
    if not common_name_element:
        # 备选方案：从页面标题获取
        title_element = tree.xpath('//h1[@class="page-header"]')
        data['Common_Name'] = clean_text(title_element[0].text_content()) if title_element else ""
    else:
        data['Common_Name'] = clean_text(common_name_element[0].text_content())
    
    # 03_Description - 根据源码修复提取逻辑
    # 方法1：通过class属性定位
    description_element = tree.xpath('//td[@class="met-desc"]')
    if description_element:
        # 获取完整的文本内容，包括链接中的文本
        description_text = description_element[0].text_content()
        data['Description'] = clean_text(html_module.unescape(description_text))
    else:
        # 方法2：通过th标签定位
        description_element = tree.xpath('//th[text()="Description"]/following-sibling::td[1]')
        if description_element:
            description_text = description_element[0].text_content()
            data['Description'] = clean_text(html_module.unescape(description_text))
        else:
            data['Description'] = ""
    
    # 04_Synonyms - 恢复原始表格结构提取
    synonyms = []
    synonym_table = tree.xpath('//th[text()="Synonyms"]/following-sibling::td[1]//table//tbody/tr')
    for row in synonym_table:
        cells = row.xpath('.//td')
        if len(cells) >= 2:
            value = clean_text(cells[0].text_content())
            source = clean_text(cells[1].text_content())
            if value and value not in ["Value", "Source"]:  # 排除表头
                formatted_synonym = f"{value} ({source})" if source else value
                synonyms.append(formatted_synonym)
    data['Synonyms'] = "; ".join(synonyms) if synonyms else ""
    
    # 05_Chemical_Formula - 恢复原始逻辑，获取完整化学式
    formula_element = tree.xpath('//th[text()="Chemical Formula"]/following-sibling::td[1]')
    if formula_element:
        # 使用//text()获取包含sub标签在内的所有文本
        formula_texts = formula_element[0].xpath('.//text()')
        data['Chemical_Formula'] = ''.join(formula_texts)
    else:
        data['Chemical_Formula'] = ""
    
    # 06_Average_Molecular_Weight - 恢复精确匹配
    avg_weight_element = tree.xpath('//th[text()="Average Molecular Weight"]/following-sibling::td[1]')
    data['Average_Molecular_Weight'] = clean_text(avg_weight_element[0].text_content()) if avg_weight_element else ""
    
    # 07_Monoisotopic_Molecular_Weight - 恢复精确匹配
    mono_weight_element = tree.xpath('//th[text()="Monoisotopic Molecular Weight"]/following-sibling::td[1]')
    data['Monoisotopic_Molecular_Weight'] = clean_text(mono_weight_element[0].text_content()) if mono_weight_element else ""
    
    # 08_IUPAC_Name - 恢复精确匹配
    iupac_element = tree.xpath('//th[text()="IUPAC Name"]/following-sibling::td[1]')
    data['IUPAC_Name'] = clean_text(iupac_element[0].text_content()) if iupac_element else ""
    
    # 09_Traditional_Name - 恢复精确匹配
    traditional_element = tree.xpath('//th[text()="Traditional Name"]/following-sibling::td[1]')
    data['Traditional_Name'] = clean_text(traditional_element[0].text_content()) if traditional_element else ""
    
    # 10_CAS_Registry_Number - 恢复精确匹配
    cas_element = tree.xpath('//th[text()="CAS Registry Number"]/following-sibling::td[1]')
    data['CAS_Registry_Number'] = clean_text(cas_element[0].text_content()) if cas_element else ""
    
    # 11_SMILES - 恢复原始备选方案逻辑
    smiles_div = tree.xpath('//div[@id="smiles-canonical"]')
    if smiles_div:
        data['SMILES'] = clean_text(smiles_div[0].text_content())
    else:
        # 备选方案：从表格中获取
        smiles_element = tree.xpath('//th[text()="SMILES"]/following-sibling::td[1]')
        data['SMILES'] = clean_text(smiles_element[0].text_content()) if smiles_element else ""
    
    # 12_Kingdom - 恢复精确匹配和链接文本提取
    kingdom_element = tree.xpath('//th[text()="Kingdom"]/following-sibling::td[1]//a')
    if not kingdom_element:
        kingdom_element = tree.xpath('//th[text()="Kingdom"]/following-sibling::td[1]')
    data['Kingdom'] = clean_text(kingdom_element[0].text_content()) if kingdom_element else ""
    
    # 13_Super_Class - 恢复精确匹配和链接文本提取
    super_class_element = tree.xpath('//th[text()="Super Class"]/following-sibling::td[1]//a')
    if not super_class_element:
        super_class_element = tree.xpath('//th[text()="Super Class"]/following-sibling::td[1]')
    data['Super_Class'] = clean_text(super_class_element[0].text_content()) if super_class_element else ""
    
    # 14_Class - 恢复精确匹配和链接文本提取
    class_element = tree.xpath('//th[text()="Class"]/following-sibling::td[1]//a')
    if not class_element:
        class_element = tree.xpath('//th[text()="Class"]/following-sibling::td[1]')
    data['Class'] = clean_text(class_element[0].text_content()) if class_element else ""
    
    # 15_Sub_Class - 恢复精确匹配和链接文本提取
    sub_class_element = tree.xpath('//th[text()="Sub Class"]/following-sibling::td[1]//a')
    if not sub_class_element:
        sub_class_element = tree.xpath('//th[text()="Sub Class"]/following-sibling::td[1]')
    data['Sub_Class'] = clean_text(sub_class_element[0].text_content()) if sub_class_element else ""
    
    # 16_Direct_Parent - 恢复精确匹配和链接文本提取
    direct_parent_element = tree.xpath('//th[text()="Direct Parent"]/following-sibling::td[1]//a')
    if not direct_parent_element:
        direct_parent_element = tree.xpath('//th[text()="Direct Parent"]/following-sibling::td[1]')
    data['Direct_Parent'] = clean_text(direct_parent_element[0].text_content()) if direct_parent_element else ""
    
    # 17_Experimental_Molecular_Properties - 使用精确的XPath定位
    exp_properties = []
    exp_headers = tree.xpath("//tr/th[text()='Experimental Molecular Properties']/following-sibling::td//table//thead//tr//th/text()")
    exp_rows = tree.xpath("//tr/th[text()='Experimental Molecular Properties']/following-sibling::td//table//tbody//tr")
    for row in exp_rows:
        cells = row.xpath(".//td//text()")
        if len(cells) >= 3:
            property_name = clean_text(html_module.unescape(cells[0].strip()))
            property_value = clean_text(html_module.unescape(cells[1].strip()))
            property_reference = clean_text(html_module.unescape(cells[2].strip()))
            if property_value and property_value.lower() != "not available":
                exp_properties.append(f"{property_name}: {property_value} (Ref: {property_reference})")
    if exp_properties:
        if len(exp_headers) >= 3:
            header_title = f"{exp_headers[0]}-{exp_headers[1]}-{exp_headers[2]}"
            data['Experimental_Molecular_Properties'] = f"{header_title}: " + '; '.join(exp_properties)
        else:
            data['Experimental_Molecular_Properties'] = '; '.join(exp_properties)
    else:
        data['Experimental_Molecular_Properties'] = ''
    
    # 18_Predicted_Molecular_Properties - 使用精确的XPath定位
    predicted_props = []
    # 获取Predicted Molecular Properties表格的表头信息
    pred_headers = tree.xpath("//tr/th[text()='Predicted Molecular Properties']/following-sibling::td//table//thead//tr//th/text()")
    
    # 获取Predicted Molecular Properties表格中的所有行
    pred_rows = tree.xpath("//tr/th[text()='Predicted Molecular Properties']/following-sibling::td//table//tbody//tr")
    for row in pred_rows:
        cells = row.xpath(".//td//text()")
        if len(cells) >= 3:
            property_name = clean_text(html_module.unescape(cells[0].strip()))
            property_value = clean_text(html_module.unescape(cells[1].strip()))
            property_source = clean_text(html_module.unescape(cells[2].strip()))
            # 所有预测属性都保留，不过滤
            predicted_props.append(f"{property_name}: {property_value} (Source: {property_source})")
    
    # 格式化为期望的输出格式：用双引号包围，分号空格分隔
    if predicted_props:
        # 从源码中获取的表头信息构建标题（如果存在的话）
        if len(pred_headers) >= 3:
            header_title = f"{pred_headers[0]}-{pred_headers[1]}-{pred_headers[2]}"
            # 在输出中包含从源码提取的标题，用空格分隔
            data['Predicted_Molecular_Properties'] = f'{header_title}: ' + '; '.join(predicted_props)
        else:
            data['Predicted_Molecular_Properties'] = '; '.join(predicted_props)
    else:
        data['Predicted_Molecular_Properties'] = ''
    
    # 19_Pathways - 恢复原始复杂表格结构提取
    pathways = []
    pathway_table = tree.xpath('//th[text()="Pathways"]/following-sibling::td[1]//table//tbody/tr')
    for row in pathway_table:
        cells = row.xpath('.//td')
        if len(cells) >= 1:
            # 提取Name
            name_cell = cells[0]
            pathway_name = clean_text(name_cell.text_content())
            
            # 跳过表头
            if pathway_name and pathway_name not in ["Name", "SMPDB", "KEGG"]:
                pathway_info = [pathway_name]
                
                # 提取SMPDB/PathBank链接
                if len(cells) > 1:
                    smpdb_cell = cells[1]
                    smpdb_links = smpdb_cell.xpath('.//a')
                    if smpdb_links:
                        smpdb_link = smpdb_links[0].get('href', '')
                        if smpdb_link:
                            pathway_info.append(f"SMPDB: {smpdb_link}")
                
                # 提取KEGG链接
                if len(cells) > 2:
                    kegg_cell = cells[2]
                    kegg_links = kegg_cell.xpath('.//a')
                    if kegg_links:
                        kegg_link = kegg_links[0].get('href', '')
                        if kegg_link:
                            pathway_info.append(f"KEGG: {kegg_link}")
                
                pathways.append(" | ".join(pathway_info))
    
    # 添加表头信息
    if pathways:
        pathways.insert(0, "Name | SMPDB | KEGG")
    
    data['Pathways'] = "; ".join(pathways) if pathways else ""
    
    # 20_Normal_Concentrations
    normal_concentrations = []
    # 查找Normal Concentrations表格 - 更精确的定位
    normal_conc_tables = tree.xpath("//tr[@id='concentrations']/following-sibling::tr[1]//table[contains(@class, 'concentrations')]")
    if normal_conc_tables:
        table = normal_conc_tables[0]
        # 获取表头信息
        headers = table.xpath(".//thead//tr//th/text()")
        # 获取所有数据行
        rows = table.xpath(".//tbody//tr")
        for row in rows:
            # 获取各列的数据，使用更精确的方法
            biospecimen_cell = row.xpath(".//td[1]")
            status_cell = row.xpath(".//td[2]")
            value_cell = row.xpath(".//td[3]")
            age_cell = row.xpath(".//td[4]")
            sex_cell = row.xpath(".//td[5]")
            condition_cell = row.xpath(".//td[6]")
            reference_cell = row.xpath(".//td[7]")
            
            if len(biospecimen_cell) > 0 and len(condition_cell) > 0:
                # 提取各字段的文本内容
                biospecimen = clean_text(html_module.unescape(''.join(biospecimen_cell[0].xpath(".//text()")).strip()))
                status = clean_text(html_module.unescape(''.join(status_cell[0].xpath(".//text()")).strip())) if status_cell else ''
                value = clean_text(html_module.unescape(''.join(value_cell[0].xpath(".//text()")).strip())) if value_cell else ''
                age = clean_text(html_module.unescape(''.join(age_cell[0].xpath(".//text()")).strip())) if age_cell else ''
                sex = clean_text(html_module.unescape(''.join(sex_cell[0].xpath(".//text()")).strip())) if sex_cell else ''
                
                # 特殊处理Condition字段，可能包含comment-icon
                condition_texts = condition_cell[0].xpath(".//text()") if condition_cell else []
                condition = clean_text(html_module.unescape(''.join([t.strip() for t in condition_texts if t.strip()])))
                
                # 提取Reference信息 - 包含链接和文本
                if reference_cell:
                    ref_links = reference_cell[0].xpath(".//a/@href")
                    ref_link_texts = reference_cell[0].xpath(".//a/text()")
                    ref_plain_texts = [t.strip() for t in reference_cell[0].xpath(".//text()") if t.strip() and not any(t.strip() in link_text for link_text in ref_link_texts)]
                    
                    reference_parts = []
                    # 添加链接信息
                    for i, link in enumerate(ref_links):
                        link_text = ref_link_texts[i] if i < len(ref_link_texts) else link
                        reference_parts.append(f"{link_text}({link})")
                    
                    # 添加纯文本信息
                    for text in ref_plain_texts:
                        if text and text not in ['', ' ']:
                            reference_parts.append(text)
                    
                    reference = ' || '.join(reference_parts) if reference_parts else 'Not Available'
                else:
                    reference = 'Not Available'
                
                # 只提取Normal条件的数据
                if biospecimen and condition.lower() == 'normal':
                    normal_concentrations.append(f"{biospecimen}: {status}, {value}, Age={age}, Sex={sex} (Ref: {reference})")
    
    if normal_concentrations:
        if len(headers) >= 7:
            header_title = f"{headers[0]}-{headers[1]}-{headers[2]}-{headers[3]}-{headers[4]}-{headers[5]}-{headers[6]}"
            data['Normal_Concentrations'] = f"{header_title}: " + '; '.join(normal_concentrations)
        else:
            data['Normal_Concentrations'] = '; '.join(normal_concentrations)
    else:
        data['Normal_Concentrations'] = ''
    
    # 21_Abnormal_Concentrations
    abnormal_concentrations = []
    # 查找Abnormal Concentrations表格（通常在Normal Concentrations之后）
    abnormal_conc_tables = tree.xpath("//tr[th[contains(text(), 'Abnormal Concentrations')]]/following-sibling::tr[1]//table[contains(@class, 'concentrations')]")
    
    if not abnormal_conc_tables:
        # 如果没有专门的Abnormal Concentrations表格，从Normal Concentrations表格中筛选非Normal条件的数据
        if normal_conc_tables:
            table = normal_conc_tables[0]
            headers = table.xpath(".//thead//tr//th/text()")
            rows = table.xpath(".//tbody//tr")
            for row in rows:
                # 使用与Normal_Concentrations相同的提取逻辑
                biospecimen_cell = row.xpath(".//td[1]")
                status_cell = row.xpath(".//td[2]")
                value_cell = row.xpath(".//td[3]")
                age_cell = row.xpath(".//td[4]")
                sex_cell = row.xpath(".//td[5]")
                condition_cell = row.xpath(".//td[6]")
                reference_cell = row.xpath(".//td[7]")
                
                if len(biospecimen_cell) > 0 and len(condition_cell) > 0:
                    biospecimen = clean_text(html_module.unescape(''.join(biospecimen_cell[0].xpath(".//text()")).strip()))
                    status = clean_text(html_module.unescape(''.join(status_cell[0].xpath(".//text()")).strip())) if status_cell else ''
                    value = clean_text(html_module.unescape(''.join(value_cell[0].xpath(".//text()")).strip())) if value_cell else ''
                    age = clean_text(html_module.unescape(''.join(age_cell[0].xpath(".//text()")).strip())) if age_cell else ''
                    sex = clean_text(html_module.unescape(''.join(sex_cell[0].xpath(".//text()")).strip())) if sex_cell else ''
                    
                    condition_texts = condition_cell[0].xpath(".//text()") if condition_cell else []
                    condition = clean_text(html_module.unescape(''.join([t.strip() for t in condition_texts if t.strip()])))
                    
                    # 提取Reference信息
                    if reference_cell:
                        ref_links = reference_cell[0].xpath(".//a/@href")
                        ref_link_texts = reference_cell[0].xpath(".//a/text()")
                        ref_plain_texts = [t.strip() for t in reference_cell[0].xpath(".//text()") if t.strip() and not any(t.strip() in link_text for link_text in ref_link_texts)]
                        
                        reference_parts = []
                        for i, link in enumerate(ref_links):
                            link_text = ref_link_texts[i] if i < len(ref_link_texts) else link
                            reference_parts.append(f"{link_text}({link})")
                        
                        for text in ref_plain_texts:
                            if text and text not in ['', ' ']:
                                reference_parts.append(text)
                        
                        reference = ' || '.join(reference_parts) if reference_parts else 'Not Available'
                    else:
                        reference = 'Not Available'
                    
                    # 只提取非Normal条件的数据
                    if biospecimen and condition.lower() != 'normal':
                        abnormal_concentrations.append(f"{biospecimen}: {status}, {value}, Age={age}, Sex={sex}, Condition={condition} (Ref: {reference})")
    else:
        # 如果有专门的Abnormal Concentrations表格
        table = abnormal_conc_tables[0]
        headers = table.xpath(".//thead//tr//th/text()")
        rows = table.xpath(".//tbody//tr")
        for row in rows:
            biospecimen_cell = row.xpath(".//td[1]")
            status_cell = row.xpath(".//td[2]")
            value_cell = row.xpath(".//td[3]")
            age_cell = row.xpath(".//td[4]")
            sex_cell = row.xpath(".//td[5]")
            condition_cell = row.xpath(".//td[6]")
            reference_cell = row.xpath(".//td[7]")
            
            if len(biospecimen_cell) > 0:
                biospecimen = clean_text(html_module.unescape(''.join(biospecimen_cell[0].xpath(".//text()")).strip()))
                status = clean_text(html_module.unescape(''.join(status_cell[0].xpath(".//text()")).strip())) if status_cell else ''
                value = clean_text(html_module.unescape(''.join(value_cell[0].xpath(".//text()")).strip())) if value_cell else ''
                age = clean_text(html_module.unescape(''.join(age_cell[0].xpath(".//text()")).strip())) if age_cell else ''
                sex = clean_text(html_module.unescape(''.join(sex_cell[0].xpath(".//text()")).strip())) if sex_cell else ''
                
                condition_texts = condition_cell[0].xpath(".//text()") if condition_cell else []
                condition = clean_text(html_module.unescape(''.join([t.strip() for t in condition_texts if t.strip()])))
                
                # 提取Reference信息
                if reference_cell:
                    ref_links = reference_cell[0].xpath(".//a/@href")
                    ref_link_texts = reference_cell[0].xpath(".//a/text()")
                    ref_plain_texts = [t.strip() for t in reference_cell[0].xpath(".//text()") if t.strip() and not any(t.strip() in link_text for link_text in ref_link_texts)]
                    
                    reference_parts = []
                    for i, link in enumerate(ref_links):
                        link_text = ref_link_texts[i] if i < len(ref_link_texts) else link
                        reference_parts.append(f"{link_text}({link})")
                    
                    for text in ref_plain_texts:
                        if text and text not in ['', ' ']:
                            reference_parts.append(text)
                    
                    reference = ' || '.join(reference_parts) if reference_parts else 'Not Available'
                else:
                    reference = 'Not Available'
                
                if biospecimen:
                    abnormal_concentrations.append(f"{biospecimen}: {status}, {value}, Age={age}, Sex={sex}, Condition={condition} (Ref: {reference})")
    
    if abnormal_concentrations:
        if len(headers) >= 7:
            header_title = f"{headers[0]}-{headers[1]}-{headers[2]}-{headers[3]}-{headers[4]}-{headers[5]}-{headers[6]}"
            data['Abnormal_Concentrations'] = f"{header_title}: " + '; '.join(abnormal_concentrations)
        else:
            data['Abnormal_Concentrations'] = '; '.join(abnormal_concentrations)
    else:
        data['Abnormal_Concentrations'] = ''
    
    # 22_Disease_References
    disease_references = []
    # 查找Disease References表格 - 严格按照源码结构
    disease_ref_row = tree.xpath("//tr/th[text()='Disease References']/following-sibling::td")
    if disease_ref_row:
        # 获取disease-table中的所有疾病条目
        disease_table = disease_ref_row[0].xpath(".//table[@class='disease-table']")
        if disease_table:
            table = disease_table[0]
            # 获取所有疾病名称（th标签）
            disease_headers = table.xpath(".//tr/th")
            for disease_header in disease_headers:
                disease_name = clean_text(html_module.unescape(disease_header.text.strip())) if disease_header.text else ''
                if disease_name:
                    # 查找该疾病对应的参考文献（下一个tr中的ol.references li）
                    ref_row = disease_header.xpath("./parent::tr/following-sibling::tr[1]")
                    if ref_row:
                        references = ref_row[0].xpath(".//ol[@class='references']/li")
                        ref_texts = []
                        for ref in references:
                            # 提取完整的参考文献文本，包括PubMed链接
                            ref_text_parts = []
                            # 获取所有文本内容
                            all_texts = ref.xpath(".//text()")
                            # 获取PubMed链接
                            pubmed_links = ref.xpath(".//a[contains(@href, 'pubmed')]/@href")
                            pubmed_ids = ref.xpath(".//a[contains(@href, 'pubmed')]/text()")
                            
                            # 组合文本内容
                            full_text = clean_text(html_module.unescape(' '.join([t.strip() for t in all_texts if t.strip()])))
                            if full_text:
                                ref_texts.append(full_text)
                        
                        if ref_texts:
                            full_refs = ' | '.join(ref_texts)
                            disease_references.append(f"{disease_name}: {full_refs}")
    
    data['Disease_References'] = ' || '.join(disease_references) if disease_references else ''
    
    # 23_Associated_OMIM_IDs - 恢复原始精确结构
    omim_ids = []
    omim_list = tree.xpath('//th[text()="Associated OMIM IDs"]/following-sibling::td[1]//li')
    
    for item in omim_list:
        # 提取OMIM ID链接
        omim_link = item.xpath('.//a[contains(@href, "omim.org")]')
        if omim_link:
            omim_id = clean_text(omim_link[0].text_content())
            omim_url = omim_link[0].get('href', '')
            
            # 提取疾病名称（在括号中或链接后的文本）
            full_text = clean_text(item.text_content())
            disease_match = re.search(r'\((.*?)\)', full_text)
            disease_name = disease_match.group(1) if disease_match else ""
            
            if omim_id:
                entry_parts = [omim_id]
                if omim_url:
                    entry_parts.append(f"URL: {omim_url}")
                if disease_name:
                    entry_parts.append(f"Disease: {disease_name}")
                
                omim_ids.append(" | ".join(entry_parts))
    
    # 如果上面的方法没有找到，尝试备用方法
    if not omim_ids:
        omim_links = tree.xpath('//a[contains(@href, "omim.org")]')
        for link in omim_links:
            omim_text = clean_text(link.text_content())
            omim_url = link.get('href', '')
            if omim_text:
                entry = omim_text
                if omim_url:
                    entry += f" | URL: {omim_url}"
                if entry not in omim_ids:
                    omim_ids.append(entry)
    
    data['Associated_OMIM_IDs'] = "; ".join(omim_ids) if omim_ids else ""
    
    # 24_KEGG_Compound_ID - 恢复原始精确XPath和错误处理
    kegg_id = ""
    try:
        kegg_element = tree.xpath('//th[text()="KEGG Compound ID"]/following-sibling::td[1]//a')
        if kegg_element:
            kegg_id = clean_text(kegg_element[0].text_content())
            kegg_url = kegg_element[0].get('href', '')
            if kegg_url:
                kegg_id += f" | URL: {kegg_url}"
        else:
            # 备用方法：直接查找KEGG链接
            kegg_links = tree.xpath('//a[contains(@href, "genome.jp/dbget-bin/www_bget?cpd:")]')
            if kegg_links:
                kegg_id = clean_text(kegg_links[0].text_content())
                kegg_url = kegg_links[0].get('href', '')
                if kegg_url:
                    kegg_id += f" | URL: {kegg_url}"
    except Exception as e:
        print(f"KEGG提取错误 [{hmdb_id}]: {e}")
    
    data['KEGG_Compound_ID'] = kegg_id
    
    # 25_PubChem_Compound - 恢复原始精确XPath和错误处理
    pubchem_id = ""
    try:
        pubchem_element = tree.xpath('//th[text()="PubChem Compound"]/following-sibling::td[1]//a')
        if pubchem_element:
            pubchem_id = clean_text(pubchem_element[0].text_content())
            pubchem_url = pubchem_element[0].get('href', '')
            if pubchem_url:
                pubchem_id += f" | URL: {pubchem_url}"
        else:
            # 备用方法：查找PubChem链接
            pubchem_links = tree.xpath('//a[contains(@href, "pubchem.ncbi.nlm.nih.gov")]')
            if pubchem_links:
                pubchem_id = clean_text(pubchem_links[0].text_content())
                pubchem_url = pubchem_links[0].get('href', '')
                if pubchem_url:
                    pubchem_id += f" | URL: {pubchem_url}"
    except Exception as e:
        print(f"PubChem提取错误 [{hmdb_id}]: {e}")
    
    data['PubChem_Compound'] = pubchem_id
    
    # 对所有字段应用HTML实体解码
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = html_module.unescape(value)
    
    return data

def should_retry(exception, status_code=None):
    """判断是否应该重试"""
    if isinstance(exception, requests.exceptions.Timeout):
        return True
    if isinstance(exception, requests.exceptions.ConnectionError):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        if status_code:
            # 429, 502, 503, 504 应该重试
            if status_code in [429, 502, 503, 504]:
                return True
            # 404, 400, 403 不重试
            if status_code in [404, 400, 403]:
                return False
        return True
    return True

def get_metabolite_data_with_retry(hmdb_id, max_retries=MAX_RETRIES):
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return get_metabolite_data(hmdb_id)
        except requests.exceptions.HTTPError as e:
            last_exception = e
            status_code = e.response.status_code if e.response else None
            
            if not should_retry(e, status_code):
                break
                
            if attempt < max_retries - 1:  # 只在非最后一次重试时延时
                wait_time = 2 ** attempt
                if status_code == 429:  # Too Many Requests
                    # 检查Retry-After头
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait_time = max(wait_time, int(retry_after))
                        except ValueError:
                            pass
                time.sleep(wait_time)
                
        except Exception as e:
            last_exception = e
            if not should_retry(e):
                break
                
            if attempt < max_retries - 1:  # 只在非最后一次重试时延时
                time.sleep(2 ** attempt)
    
    # 记录失败信息
    error_msg = f"[{hmdb_id}] 重试失败: {str(last_exception)}"
    print(error_msg)
    return None

def save_failed_ids(failed_ids, filename='失败.txt'):
    """保存失败的ID到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for hmdb_id, error in failed_ids:
            f.write(f"{hmdb_id}\t{error}\n")

def save_progress(processed_ids, filename='progress.json'):
    """保存处理进度"""
    progress_data = {
        'processed_ids': list(processed_ids),
        'timestamp': datetime.now().isoformat(),
        'count': len(processed_ids)
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def load_progress(filename='progress.json'):
    """加载处理进度"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
                return set(progress_data.get('processed_ids', []))
        except Exception as e:
            print(f"加载进度文件失败: {e}")
    return set()

def get_memory_usage():
    """获取当前内存使用情况（MB）"""
    try:
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except:
        return 0

def write_to_csv(results, filename, mode='a'):
    fieldnames = [
        'HMDB_ID',                              # 01
        'Common_Name',                          # 02
        'Description',                          # 03
        'Synonyms',                             # 04
        'Chemical_Formula',                     # 05
        'Average_Molecular_Weight',             # 06
        'Monoisotopic_Molecular_Weight',        # 07
        'IUPAC_Name',                           # 08
        'Traditional_Name',                     # 09
        'CAS_Registry_Number',                  # 10
        'SMILES',                               # 11
        'Kingdom',                              # 12
        'Super_Class',                          # 13
        'Class',                                # 14
        'Sub_Class',                            # 15
        'Direct_Parent',                        # 16
        'Experimental_Molecular_Properties',    # 17
        'Predicted_Molecular_Properties',       # 18
        'Pathways',                             # 19
        'Normal_Concentrations',                # 20
        'Abnormal_Concentrations',              # 21
        'Disease_References',                   # 22
        'Associated_OMIM_IDs',                  # 23
        'KEGG_Compound_ID',                     # 24
        'PubChem_Compound'                      # 25
    ]
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode, newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        if not file_exists or mode == 'w':
            writer.writeheader()
        writer.writerows(results)

def process_ids(hmdb_ids, max_workers=MAX_WORKERS):
    # 加载已处理的ID
    processed_ids = load_progress()
    remaining_ids = [id for id in hmdb_ids if id not in processed_ids]
    
    if not remaining_ids:
        print("所有ID都已处理完成！")
        return len(hmdb_ids), 0, []
    
    print(f"发现 {len(processed_ids)} 个已处理的ID，剩余 {len(remaining_ids)} 个待处理")
    
    # 使用字典存储结果，保持原始顺序
    results_dict = {}
    failed_ids = []
    total_ids = len(hmdb_ids)
    current_processed = len(processed_ids)
    success_count = len(processed_ids)
    failure_count = 0
    start_time = time.time()
    
    print(f"开始处理，使用 {max_workers} 个线程，全局限制 {REQUESTS_PER_SECOND} 请求/秒")
    print(f"总计: {total_ids} 个ID，已完成: {current_processed} 个，剩余: {len(remaining_ids)} 个")
    print("-" * 80)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(get_metabolite_data_with_retry, hmdb_id): hmdb_id for hmdb_id in remaining_ids}
        
        for future in as_completed(future_to_id):
            hmdb_id = future_to_id[future]
            current_processed += 1
            
            try:
                data = future.result()
                if data:
                    results_dict[hmdb_id] = data  # 存储到字典中
                    processed_ids.add(hmdb_id)
                    status = "✓"
                    success_count += 1
                else:
                    failed_ids.append((hmdb_id, "数据获取失败"))
                    status = "✗"
                    failure_count += 1
            except Exception as e:
                failed_ids.append((hmdb_id, str(e)))
                status = "✗"
                failure_count += 1
            
            # 进度报告
            if current_processed % PROGRESS_REPORT_INTERVAL == 0 or current_processed == total_ids:
                remaining = total_ids - current_processed
                percentage = (current_processed / total_ids) * 100
                elapsed_time = time.time() - start_time
                avg_time_per_item = elapsed_time / (current_processed - len(processed_ids) + len(remaining_ids)) if current_processed > len(processed_ids) else 0
                estimated_remaining_time = avg_time_per_item * remaining if avg_time_per_item > 0 else 0
                memory_usage = get_memory_usage()
                
                print(f"进度: {current_processed}/{total_ids} ({percentage:.1f}%) | "
                      f"剩余: {remaining} | 成功: {success_count} | 失败: {failure_count} | "
                      f"内存: {memory_usage:.1f}MB | 预计剩余: {estimated_remaining_time/60:.1f}分钟")
            
            # 批量写入 - 按原始顺序
            if len(results_dict) >= BATCH_WRITE_SIZE:
                # 按照hmdb_ids的原始顺序排列结果
                ordered_results = []
                for hmdb_id in hmdb_ids:
                    if hmdb_id in results_dict:
                        ordered_results.append(results_dict[hmdb_id])
                        del results_dict[hmdb_id]  # 删除已写入的结果以节省内存
                
                if ordered_results:
                    write_to_csv(ordered_results, '代谢物数据_最终.csv', mode='a')
                    print(f"已保存 {len(ordered_results)} 条记录到文件（按原始顺序）")
                
                # 保存进度
                save_progress(processed_ids)
                
                # 内存检查
                memory_usage = get_memory_usage()
                if memory_usage > 1000:  # 超过1GB强制清理
                    print(f"内存使用过高 ({memory_usage:.1f}MB)，强制清理...")
                    results_dict.clear()
    
    # 保存剩余结果 - 按原始顺序
    if results_dict:
        ordered_results = []
        for hmdb_id in hmdb_ids:
            if hmdb_id in results_dict:
                ordered_results.append(results_dict[hmdb_id])
        
        if ordered_results:
            write_to_csv(ordered_results, '代谢物数据_最终.csv', mode='a')
            print(f"保存最后 {len(ordered_results)} 条记录（按原始顺序）")
    
    # 保存失败的ID
    if failed_ids:
        save_failed_ids(failed_ids)
        print(f"已保存 {len(failed_ids)} 个失败ID到 失败.txt")
    
    # 保存最终进度
    save_progress(processed_ids)
    
    return success_count, failure_count, failed_ids

def main():
    start_time = time.time()
    
    try:
        print("=" * 80)
        print("HMDB代谢物数据提取工具 - 优化版")
        print(f"配置: {MAX_WORKERS}线程 | {REQUESTS_PER_SECOND}请求/秒 | {BATCH_WRITE_SIZE}条/批次")
        print("=" * 80)
        
        if not os.path.exists('id.txt'):
            print("错误：找不到 id.txt 文件。请确保该文件与程序在同一目录下。")
            input("按回车键退出...")
            sys.exit(1)

        with open('id.txt', 'r', encoding='utf-8') as f:
            hmdb_ids = f.read().splitlines()
        print(f"从id.txt加载了 {len(hmdb_ids)} 个ID")
        
        invalid_ids, duplicates = check_ids(hmdb_ids)
        
        if invalid_ids:
            print("发现以下异常ID:")
            for index, id in invalid_ids[:10]:  # 只显示前10个
                print(f"  第{index}行: {id}")
            if len(invalid_ids) > 10:
                print(f"  ... 还有 {len(invalid_ids) - 10} 个异常ID")
        
        if duplicates:
            print("发现重复ID:")
            for id, count in list(duplicates.items())[:10]:  # 只显示前10个
                print(f"  {id}: 重复{count}次")
            if len(duplicates) > 10:
                print(f"  ... 还有 {len(duplicates) - 10} 个重复ID")
        
        valid_ids = [id for id in hmdb_ids if id.startswith("HMDB")]
        unique_ids = list(dict.fromkeys(valid_ids))
        
        print(f"将处理 {len(unique_ids)} 个有效且唯一的ID")
        print("-" * 80)
        
        # 初始化输出文件
        if not os.path.exists('progress.json'):
            write_to_csv([], '代谢物数据_最终.csv', mode='w')
            print("已初始化输出文件")

        success_count, failure_count, failed_ids = process_ids(unique_ids)

        # 最终排序确保顺序正确
        print("\n正在按原始ID顺序整理CSV文件...")
        sort_csv_by_original_order(unique_ids, '代谢物数据_最终.csv')

        # 计算总耗时
        total_time = time.time() - start_time
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        
        print("=" * 80)
        print("处理完成！")
        print(f"总计: {len(unique_ids)} 个ID")
        print(f"成功: {success_count} 个 ({success_count/len(unique_ids)*100:.1f}%)")
        print(f"失败: {failure_count} 个 ({failure_count/len(unique_ids)*100:.1f}%)")
        print(f"总耗时: {hours}小时{minutes}分钟{seconds}秒")
        print(f"平均速度: {len(unique_ids)/total_time*60:.1f} 个/分钟")
        print(f"最终结果已保存在: 代谢物数据_最终.csv（按原始ID顺序排列）")
        
        if failed_ids:
            print(f"失败记录已保存在: 失败.txt")
        
        # 清理临时文件
        if os.path.exists('progress.json'):
            os.remove('progress.json')
            print("已清理临时进度文件")
        
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        print("进度已保存，可以重新运行程序继续处理")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 80)
        print("程序运行完成！")
        print("按任意键退出...")
        try:
            input()
        except:
            pass

def sort_csv_by_original_order(original_ids, csv_file):
    """
    按照原始ID顺序重新排列CSV文件
    """
    try:
        import pandas as pd
        
        # 读取CSV文件
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        if df.empty or 'HMDB_ID' not in df.columns:
            print("CSV文件为空或缺少HMDB_ID列，跳过排序")
            return
        
        # 创建ID顺序映射
        id_order = {hmdb_id: i for i, hmdb_id in enumerate(original_ids)}
        
        # 为DataFrame添加排序键
        df['sort_key'] = df['HMDB_ID'].map(id_order)
        
        # 按排序键排序
        df_sorted = df.sort_values('sort_key').drop('sort_key', axis=1)
        
        # 重新写入CSV文件
        df_sorted.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"CSV文件已按原始ID顺序重新排列，共 {len(df_sorted)} 条记录")
        
    except ImportError:
        print("警告：pandas未安装，无法进行最终排序。请安装pandas: pip install pandas")
    except Exception as e:
        print(f"排序CSV文件时出错: {e}")

if __name__ == "__main__":
    main()
```

## 全部代码（Ubuntu 22.04）
```
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
import threading
import json
from datetime import datetime
import psutil
import queue
import logging
import platform
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 作者：IT小章
# 时间：2025年11月01日
# 网站：itxiaozhang.com
# 
# 低配置VPS优化版本说明：
# ================================
# 本版本专门针对1核心1G内存的VPS环境进行优化：
# 
# 主要优化项：
# 1. 降低并发数：MAX_WORKERS = 2（减少CPU和内存压力）
# 2. 降低请求频率：REQUESTS_PER_SECOND = 2（减少网络压力）
# 3. 减少批处理大小：BATCH_WRITE_SIZE = 50（降低内存使用）
# 4. 增加重试间隔：更长的等待时间，减少服务器压力
# 5. 内存监控：实时监控内存使用，超过阈值自动清理
# 6. 系统资源检查：定期检查CPU和内存，资源不足时暂停处理
# 7. 垃圾回收：更频繁的垃圾回收，防止内存泄漏
# 
# 运行建议（Ubuntu系统）：
# - 确保VPS有至少500MB可用内存
# - 关闭不必要的服务：sudo systemctl stop apache2 mysql nginx
# - 清理系统缓存：sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
# - 建议在系统负载较低时运行
# - 后台运行：nohup python3 102511.py > output.log 2>&1 &
# - 监控进程：htop 或 top -p $(pgrep -f 102511.py)
# - 查看日志：tail -f output.log
# ================================

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 配置常量 - 针对Ubuntu 22.04优化，性能翻倍
MAX_WORKERS = 4  # 提升并发数，充分利用VPS性能
REQUESTS_PER_SECOND = 4  # 提升请求频率，加快处理速度
BATCH_WRITE_SIZE = 100  # 增加批处理大小，提高I/O效率
PROGRESS_REPORT_INTERVAL = 50  # 更频繁的进度报告
REQUEST_TIMEOUT = (10, 30)  # 增加超时时间，适应低配置网络环境
MAX_RETRIES = 3  # 增加重试次数，提高成功率

# 会话池（全局复用，提升稳定性与性能）
SESSION = None
SESSION_LOCK = threading.Lock()

def get_http_session():
    """获取全局HTTP会话，启用连接池（禁用自动重试，保留自定义重试策略）"""
    global SESSION
    if SESSION is not None:
        return SESSION
    with SESSION_LOCK:
        if SESSION is None:
            s = requests.Session()
            adapter = HTTPAdapter(
                pool_connections=MAX_WORKERS * 2,
                pool_maxsize=MAX_WORKERS * 4,
                max_retries=Retry(total=0, connect=0, read=0, backoff_factor=0)
            )
            s.mount('https://', adapter)
            s.mount('http://', adapter)
            SESSION = s
    return SESSION

# 日志配置 - Ubuntu 22.04优化
def setup_logging():
    """设置专业的日志系统"""
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler('logs/hmdb_extractor.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 创建专用日志器
    logger = logging.getLogger('HMDB_Extractor')
    
    # 添加错误日志文件处理器
    error_handler = logging.FileHandler('logs/errors.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(error_handler)
    
    return logger

# 初始化日志系统
logger = setup_logging()

class RateLimiter:
    """简化的速率限制器 - 适用于低配置环境"""
    def __init__(self, rate):
        self.rate = rate  # 每秒允许的请求数
        self.interval = 1.0 / rate  # 请求间隔
        self.last_request = 0
        self.lock = threading.Lock()
    
    def acquire(self):
        """阻塞直到可用令牌，确保全局不超速"""
        with self.lock:
            now = time.monotonic()
            wait_time = max(0.0, self.last_request + self.interval - now)
            # 记录下一次允许时间点，保证并发下全局节流
            self.last_request = now + wait_time
        if wait_time > 0:
            time.sleep(wait_time)
        return True

# 全局速率限制器实例
rate_limiter = RateLimiter(REQUESTS_PER_SECOND)

def check_ids(ids):
    invalid_ids = []
    id_counts = Counter(ids)
    duplicates = {id: count for id, count in id_counts.items() if count > 1}
    
    for index, id in enumerate(ids, 1):
        if not id.startswith("HMDB"):
            invalid_ids.append((index, id))
    
    return invalid_ids, duplicates

def clean_text(text):
    # 移除不可见字符和特殊字符
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\u200B-\u200D\uFEFF]', '', text)
    # 将多个空格替换为单个空格
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def get_metabolite_data(hmdb_id):
    url = f"https://hmdb.ca/metabolites/{hmdb_id}"

    # 速率限制（阻塞直到可用）
    rate_limiter.acquire()

    # 复用会话与连接池
    session = get_http_session()
    response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    
    tree = html.fromstring(response.content)

    data = {}
    
    # 01_HMDB_ID
    data['HMDB_ID'] = hmdb_id
    
    # 02_Common_Name - 恢复原始精确逻辑
    common_name_element = tree.xpath('//th[text()="Common Name"]/following-sibling::td[1]')
    if not common_name_element:
        # 备选方案：从页面标题获取
        title_element = tree.xpath('//h1[@class="page-header"]')
        data['Common_Name'] = clean_text(title_element[0].text_content()) if title_element else ""
    else:
        data['Common_Name'] = clean_text(common_name_element[0].text_content())
    
    # 03_Description - 根据源码修复提取逻辑
    # 方法1：通过class属性定位
    description_element = tree.xpath('//td[@class="met-desc"]')
    if description_element:
        # 获取完整的文本内容，包括链接中的文本
        description_text = description_element[0].text_content()
        data['Description'] = clean_text(html_module.unescape(description_text))
    else:
        # 方法2：通过th标签定位
        description_element = tree.xpath('//th[text()="Description"]/following-sibling::td[1]')
        if description_element:
            description_text = description_element[0].text_content()
            data['Description'] = clean_text(html_module.unescape(description_text))
        else:
            data['Description'] = ""
    
    # 04_Synonyms - 恢复原始表格结构提取
    synonyms = []
    synonym_table = tree.xpath('//th[text()="Synonyms"]/following-sibling::td[1]//table//tbody/tr')
    for row in synonym_table:
        cells = row.xpath('.//td')
        if len(cells) >= 2:
            value = clean_text(cells[0].text_content())
            source = clean_text(cells[1].text_content())
            if value and value not in ["Value", "Source"]:  # 排除表头
                formatted_synonym = f"{value} ({source})" if source else value
                synonyms.append(formatted_synonym)
    data['Synonyms'] = "; ".join(synonyms) if synonyms else ""
    
    # 05_Chemical_Formula - 恢复原始逻辑，获取完整化学式
    formula_element = tree.xpath('//th[text()="Chemical Formula"]/following-sibling::td[1]')
    if formula_element:
        # 使用//text()获取包含sub标签在内的所有文本
        formula_texts = formula_element[0].xpath('.//text()')
        data['Chemical_Formula'] = ''.join(formula_texts)
    else:
        data['Chemical_Formula'] = ""
    
    # 06_Average_Molecular_Weight - 恢复精确匹配
    avg_weight_element = tree.xpath('//th[text()="Average Molecular Weight"]/following-sibling::td[1]')
    data['Average_Molecular_Weight'] = clean_text(avg_weight_element[0].text_content()) if avg_weight_element else ""
    
    # 07_Monoisotopic_Molecular_Weight - 恢复精确匹配
    mono_weight_element = tree.xpath('//th[text()="Monoisotopic Molecular Weight"]/following-sibling::td[1]')
    data['Monoisotopic_Molecular_Weight'] = clean_text(mono_weight_element[0].text_content()) if mono_weight_element else ""
    
    # 08_IUPAC_Name - 恢复精确匹配
    iupac_element = tree.xpath('//th[text()="IUPAC Name"]/following-sibling::td[1]')
    data['IUPAC_Name'] = clean_text(iupac_element[0].text_content()) if iupac_element else ""
    
    # 09_Traditional_Name - 恢复精确匹配
    traditional_element = tree.xpath('//th[text()="Traditional Name"]/following-sibling::td[1]')
    data['Traditional_Name'] = clean_text(traditional_element[0].text_content()) if traditional_element else ""
    
    # 10_CAS_Registry_Number - 恢复精确匹配
    cas_element = tree.xpath('//th[text()="CAS Registry Number"]/following-sibling::td[1]')
    data['CAS_Registry_Number'] = clean_text(cas_element[0].text_content()) if cas_element else ""
    
    # 11_SMILES - 恢复原始备选方案逻辑
    smiles_div = tree.xpath('//div[@id="smiles-canonical"]')
    if smiles_div:
        data['SMILES'] = clean_text(smiles_div[0].text_content())
    else:
        # 备选方案：从表格中获取
        smiles_element = tree.xpath('//th[text()="SMILES"]/following-sibling::td[1]')
        data['SMILES'] = clean_text(smiles_element[0].text_content()) if smiles_element else ""
    
    # 12_Kingdom - 恢复精确匹配和链接文本提取
    kingdom_element = tree.xpath('//th[text()="Kingdom"]/following-sibling::td[1]//a')
    if not kingdom_element:
        kingdom_element = tree.xpath('//th[text()="Kingdom"]/following-sibling::td[1]')
    data['Kingdom'] = clean_text(kingdom_element[0].text_content()) if kingdom_element else ""
    
    # 13_Super_Class - 恢复精确匹配和链接文本提取
    super_class_element = tree.xpath('//th[text()="Super Class"]/following-sibling::td[1]//a')
    if not super_class_element:
        super_class_element = tree.xpath('//th[text()="Super Class"]/following-sibling::td[1]')
    data['Super_Class'] = clean_text(super_class_element[0].text_content()) if super_class_element else ""
    
    # 14_Class - 恢复精确匹配和链接文本提取
    class_element = tree.xpath('//th[text()="Class"]/following-sibling::td[1]//a')
    if not class_element:
        class_element = tree.xpath('//th[text()="Class"]/following-sibling::td[1]')
    data['Class'] = clean_text(class_element[0].text_content()) if class_element else ""
    
    # 15_Sub_Class - 恢复精确匹配和链接文本提取
    sub_class_element = tree.xpath('//th[text()="Sub Class"]/following-sibling::td[1]//a')
    if not sub_class_element:
        sub_class_element = tree.xpath('//th[text()="Sub Class"]/following-sibling::td[1]')
    data['Sub_Class'] = clean_text(sub_class_element[0].text_content()) if sub_class_element else ""
    
    # 16_Direct_Parent - 恢复精确匹配和链接文本提取
    direct_parent_element = tree.xpath('//th[text()="Direct Parent"]/following-sibling::td[1]//a')
    if not direct_parent_element:
        direct_parent_element = tree.xpath('//th[text()="Direct Parent"]/following-sibling::td[1]')
    data['Direct_Parent'] = clean_text(direct_parent_element[0].text_content()) if direct_parent_element else ""
    
    # 17_Experimental_Molecular_Properties - 使用精确的XPath定位
    exp_properties = []
    exp_headers = tree.xpath("//tr/th[text()='Experimental Molecular Properties']/following-sibling::td//table//thead//tr//th/text()")
    exp_rows = tree.xpath("//tr/th[text()='Experimental Molecular Properties']/following-sibling::td//table//tbody//tr")
    for row in exp_rows:
        cells = row.xpath(".//td//text()")
        if len(cells) >= 3:
            property_name = clean_text(html_module.unescape(cells[0].strip()))
            property_value = clean_text(html_module.unescape(cells[1].strip()))
            property_reference = clean_text(html_module.unescape(cells[2].strip()))
            if property_value and property_value.lower() != "not available":
                exp_properties.append(f"{property_name}: {property_value} (Ref: {property_reference})")
    if exp_properties:
        if len(exp_headers) >= 3:
            header_title = f"{exp_headers[0]}-{exp_headers[1]}-{exp_headers[2]}"
            data['Experimental_Molecular_Properties'] = f"{header_title}: " + '; '.join(exp_properties)
        else:
            data['Experimental_Molecular_Properties'] = '; '.join(exp_properties)
    else:
        data['Experimental_Molecular_Properties'] = ''
    
    # 18_Predicted_Molecular_Properties - 使用精确的XPath定位
    predicted_props = []
    # 获取Predicted Molecular Properties表格的表头信息
    pred_headers = tree.xpath("//tr/th[text()='Predicted Molecular Properties']/following-sibling::td//table//thead//tr//th/text()")
    
    # 获取Predicted Molecular Properties表格中的所有行
    pred_rows = tree.xpath("//tr/th[text()='Predicted Molecular Properties']/following-sibling::td//table//tbody//tr")
    for row in pred_rows:
        cells = row.xpath(".//td//text()")
        if len(cells) >= 3:
            property_name = clean_text(html_module.unescape(cells[0].strip()))
            property_value = clean_text(html_module.unescape(cells[1].strip()))
            property_source = clean_text(html_module.unescape(cells[2].strip()))
            # 所有预测属性都保留，不过滤
            predicted_props.append(f"{property_name}: {property_value} (Source: {property_source})")
    
    # 格式化为期望的输出格式：用双引号包围，分号空格分隔
    if predicted_props:
        # 从源码中获取的表头信息构建标题（如果存在的话）
        if len(pred_headers) >= 3:
            header_title = f"{pred_headers[0]}-{pred_headers[1]}-{pred_headers[2]}"
            # 在输出中包含从源码提取的标题，用空格分隔
            data['Predicted_Molecular_Properties'] = f'{header_title}: ' + '; '.join(predicted_props)
        else:
            data['Predicted_Molecular_Properties'] = '; '.join(predicted_props)
    else:
        data['Predicted_Molecular_Properties'] = ''
    
    # 19_Pathways - 恢复原始复杂表格结构提取
    pathways = []
    pathway_table = tree.xpath('//th[text()="Pathways"]/following-sibling::td[1]//table//tbody/tr')
    for row in pathway_table:
        cells = row.xpath('.//td')
        if len(cells) >= 1:
            # 提取Name
            name_cell = cells[0]
            pathway_name = clean_text(name_cell.text_content())
            
            # 跳过表头
            if pathway_name and pathway_name not in ["Name", "SMPDB", "KEGG"]:
                pathway_info = [pathway_name]
                
                # 提取SMPDB/PathBank链接
                if len(cells) > 1:
                    smpdb_cell = cells[1]
                    smpdb_links = smpdb_cell.xpath('.//a')
                    if smpdb_links:
                        smpdb_link = smpdb_links[0].get('href', '')
                        if smpdb_link:
                            pathway_info.append(f"SMPDB: {smpdb_link}")
                
                # 提取KEGG链接
                if len(cells) > 2:
                    kegg_cell = cells[2]
                    kegg_links = kegg_cell.xpath('.//a')
                    if kegg_links:
                        kegg_link = kegg_links[0].get('href', '')
                        if kegg_link:
                            pathway_info.append(f"KEGG: {kegg_link}")
                
                pathways.append(" | ".join(pathway_info))
    
    # 添加表头信息
    if pathways:
        pathways.insert(0, "Name | SMPDB | KEGG")
    
    data['Pathways'] = "; ".join(pathways) if pathways else ""
    
    # 20_Normal_Concentrations
    normal_concentrations = []
    # 查找Normal Concentrations表格 - 更精确的定位
    normal_conc_tables = tree.xpath("//tr[@id='concentrations']/following-sibling::tr[1]//table[contains(@class, 'concentrations')]")
    if normal_conc_tables:
        table = normal_conc_tables[0]
        # 获取表头信息
        headers = table.xpath(".//thead//tr//th/text()")
        # 获取所有数据行
        rows = table.xpath(".//tbody//tr")
        for row in rows:
            # 获取各列的数据，使用更精确的方法
            biospecimen_cell = row.xpath(".//td[1]")
            status_cell = row.xpath(".//td[2]")
            value_cell = row.xpath(".//td[3]")
            age_cell = row.xpath(".//td[4]")
            sex_cell = row.xpath(".//td[5]")
            condition_cell = row.xpath(".//td[6]")
            reference_cell = row.xpath(".//td[7]")
            
            if len(biospecimen_cell) > 0 and len(condition_cell) > 0:
                # 提取各字段的文本内容
                biospecimen = clean_text(html_module.unescape(''.join(biospecimen_cell[0].xpath(".//text()")).strip()))
                status = clean_text(html_module.unescape(''.join(status_cell[0].xpath(".//text()")).strip())) if status_cell else ''
                value = clean_text(html_module.unescape(''.join(value_cell[0].xpath(".//text()")).strip())) if value_cell else ''
                age = clean_text(html_module.unescape(''.join(age_cell[0].xpath(".//text()")).strip())) if age_cell else ''
                sex = clean_text(html_module.unescape(''.join(sex_cell[0].xpath(".//text()")).strip())) if sex_cell else ''
                
                # 特殊处理Condition字段，可能包含comment-icon
                condition_texts = condition_cell[0].xpath(".//text()") if condition_cell else []
                condition = clean_text(html_module.unescape(''.join([t.strip() for t in condition_texts if t.strip()])))
                
                # 提取Reference信息 - 包含链接和文本
                if reference_cell:
                    ref_links = reference_cell[0].xpath(".//a/@href")
                    ref_link_texts = reference_cell[0].xpath(".//a/text()")
                    ref_plain_texts = [t.strip() for t in reference_cell[0].xpath(".//text()") if t.strip() and not any(t.strip() in link_text for link_text in ref_link_texts)]
                    
                    reference_parts = []
                    # 添加链接信息
                    for i, link in enumerate(ref_links):
                        link_text = ref_link_texts[i] if i < len(ref_link_texts) else link
                        reference_parts.append(f"{link_text}({link})")
                    
                    # 添加纯文本信息
                    for text in ref_plain_texts:
                        if text and text not in ['', ' ']:
                            reference_parts.append(text)
                    
                    reference = ' || '.join(reference_parts) if reference_parts else 'Not Available'
                else:
                    reference = 'Not Available'
                
                # 只提取Normal条件的数据
                if biospecimen and condition.lower() == 'normal':
                    normal_concentrations.append(f"{biospecimen}: {status}, {value}, Age={age}, Sex={sex} (Ref: {reference})")
    
    if normal_concentrations:
        if len(headers) >= 7:
            header_title = f"{headers[0]}-{headers[1]}-{headers[2]}-{headers[3]}-{headers[4]}-{headers[5]}-{headers[6]}"
            data['Normal_Concentrations'] = f"{header_title}: " + '; '.join(normal_concentrations)
        else:
            data['Normal_Concentrations'] = '; '.join(normal_concentrations)
    else:
        data['Normal_Concentrations'] = ''
    
    # 21_Abnormal_Concentrations
    abnormal_concentrations = []
    # 查找Abnormal Concentrations表格（通常在Normal Concentrations之后）
    abnormal_conc_tables = tree.xpath("//tr[th[contains(text(), 'Abnormal Concentrations')]]/following-sibling::tr[1]//table[contains(@class, 'concentrations')]")
    
    if not abnormal_conc_tables:
        # 如果没有专门的Abnormal Concentrations表格，从Normal Concentrations表格中筛选非Normal条件的数据
        if normal_conc_tables:
            table = normal_conc_tables[0]
            headers = table.xpath(".//thead//tr//th/text()")
            rows = table.xpath(".//tbody//tr")
            for row in rows:
                # 使用与Normal_Concentrations相同的提取逻辑
                biospecimen_cell = row.xpath(".//td[1]")
                status_cell = row.xpath(".//td[2]")
                value_cell = row.xpath(".//td[3]")
                age_cell = row.xpath(".//td[4]")
                sex_cell = row.xpath(".//td[5]")
                condition_cell = row.xpath(".//td[6]")
                reference_cell = row.xpath(".//td[7]")
                
                if len(biospecimen_cell) > 0 and len(condition_cell) > 0:
                    biospecimen = clean_text(html_module.unescape(''.join(biospecimen_cell[0].xpath(".//text()")).strip()))
                    status = clean_text(html_module.unescape(''.join(status_cell[0].xpath(".//text()")).strip())) if status_cell else ''
                    value = clean_text(html_module.unescape(''.join(value_cell[0].xpath(".//text()")).strip())) if value_cell else ''
                    age = clean_text(html_module.unescape(''.join(age_cell[0].xpath(".//text()")).strip())) if age_cell else ''
                    sex = clean_text(html_module.unescape(''.join(sex_cell[0].xpath(".//text()")).strip())) if sex_cell else ''
                    
                    condition_texts = condition_cell[0].xpath(".//text()") if condition_cell else []
                    condition = clean_text(html_module.unescape(''.join([t.strip() for t in condition_texts if t.strip()])))
                    
                    # 提取Reference信息
                    if reference_cell:
                        ref_links = reference_cell[0].xpath(".//a/@href")
                        ref_link_texts = reference_cell[0].xpath(".//a/text()")
                        ref_plain_texts = [t.strip() for t in reference_cell[0].xpath(".//text()") if t.strip() and not any(t.strip() in link_text for link_text in ref_link_texts)]
                        
                        reference_parts = []
                        for i, link in enumerate(ref_links):
                            link_text = ref_link_texts[i] if i < len(ref_link_texts) else link
                            reference_parts.append(f"{link_text}({link})")
                        
                        for text in ref_plain_texts:
                            if text and text not in ['', ' ']:
                                reference_parts.append(text)
                        
                        reference = ' || '.join(reference_parts) if reference_parts else 'Not Available'
                    else:
                        reference = 'Not Available'
                    
                    # 只提取非Normal条件的数据
                    if biospecimen and condition.lower() != 'normal':
                        abnormal_concentrations.append(f"{biospecimen}: {status}, {value}, Age={age}, Sex={sex}, Condition={condition} (Ref: {reference})")
    else:
        # 如果有专门的Abnormal Concentrations表格
        table = abnormal_conc_tables[0]
        headers = table.xpath(".//thead//tr//th/text()")
        rows = table.xpath(".//tbody//tr")
        for row in rows:
            biospecimen_cell = row.xpath(".//td[1]")
            status_cell = row.xpath(".//td[2]")
            value_cell = row.xpath(".//td[3]")
            age_cell = row.xpath(".//td[4]")
            sex_cell = row.xpath(".//td[5]")
            condition_cell = row.xpath(".//td[6]")
            reference_cell = row.xpath(".//td[7]")
            
            if len(biospecimen_cell) > 0:
                biospecimen = clean_text(html_module.unescape(''.join(biospecimen_cell[0].xpath(".//text()")).strip()))
                status = clean_text(html_module.unescape(''.join(status_cell[0].xpath(".//text()")).strip())) if status_cell else ''
                value = clean_text(html_module.unescape(''.join(value_cell[0].xpath(".//text()")).strip())) if value_cell else ''
                age = clean_text(html_module.unescape(''.join(age_cell[0].xpath(".//text()")).strip())) if age_cell else ''
                sex = clean_text(html_module.unescape(''.join(sex_cell[0].xpath(".//text()")).strip())) if sex_cell else ''
                
                condition_texts = condition_cell[0].xpath(".//text()") if condition_cell else []
                condition = clean_text(html_module.unescape(''.join([t.strip() for t in condition_texts if t.strip()])))
                
                # 提取Reference信息
                if reference_cell:
                    ref_links = reference_cell[0].xpath(".//a/@href")
                    ref_link_texts = reference_cell[0].xpath(".//a/text()")
                    ref_plain_texts = [t.strip() for t in reference_cell[0].xpath(".//text()") if t.strip() and not any(t.strip() in link_text for link_text in ref_link_texts)]
                    
                    reference_parts = []
                    for i, link in enumerate(ref_links):
                        link_text = ref_link_texts[i] if i < len(ref_link_texts) else link
                        reference_parts.append(f"{link_text}({link})")
                    
                    for text in ref_plain_texts:
                        if text and text not in ['', ' ']:
                            reference_parts.append(text)
                    
                    reference = ' || '.join(reference_parts) if reference_parts else 'Not Available'
                else:
                    reference = 'Not Available'
                
                if biospecimen:
                    abnormal_concentrations.append(f"{biospecimen}: {status}, {value}, Age={age}, Sex={sex}, Condition={condition} (Ref: {reference})")
    
    if abnormal_concentrations:
        if len(headers) >= 7:
            header_title = f"{headers[0]}-{headers[1]}-{headers[2]}-{headers[3]}-{headers[4]}-{headers[5]}-{headers[6]}"
            data['Abnormal_Concentrations'] = f"{header_title}: " + '; '.join(abnormal_concentrations)
        else:
            data['Abnormal_Concentrations'] = '; '.join(abnormal_concentrations)
    else:
        data['Abnormal_Concentrations'] = ''
    
    # 22_Disease_References
    disease_references = []
    # 查找Disease References表格 - 严格按照源码结构
    disease_ref_row = tree.xpath("//tr/th[text()='Disease References']/following-sibling::td")
    if disease_ref_row:
        # 获取disease-table中的所有疾病条目
        disease_table = disease_ref_row[0].xpath(".//table[@class='disease-table']")
        if disease_table:
            table = disease_table[0]
            # 获取所有疾病名称（th标签）
            disease_headers = table.xpath(".//tr/th")
            for disease_header in disease_headers:
                disease_name = clean_text(html_module.unescape(disease_header.text.strip())) if disease_header.text else ''
                if disease_name:
                    # 查找该疾病对应的参考文献（下一个tr中的ol.references li）
                    ref_row = disease_header.xpath("./parent::tr/following-sibling::tr[1]")
                    if ref_row:
                        references = ref_row[0].xpath(".//ol[@class='references']/li")
                        ref_texts = []
                        for ref in references:
                            # 提取完整的参考文献文本，包括PubMed链接
                            ref_text_parts = []
                            # 获取所有文本内容
                            all_texts = ref.xpath(".//text()")
                            # 获取PubMed链接
                            pubmed_links = ref.xpath(".//a[contains(@href, 'pubmed')]/@href")
                            pubmed_ids = ref.xpath(".//a[contains(@href, 'pubmed')]/text()")
                            
                            # 组合文本内容
                            full_text = clean_text(html_module.unescape(' '.join([t.strip() for t in all_texts if t.strip()])))
                            if full_text:
                                ref_texts.append(full_text)
                        
                        if ref_texts:
                            full_refs = ' | '.join(ref_texts)
                            disease_references.append(f"{disease_name}: {full_refs}")
    
    data['Disease_References'] = ' || '.join(disease_references) if disease_references else ''
    
    # 23_Associated_OMIM_IDs - 恢复原始精确结构
    omim_ids = []
    omim_list = tree.xpath('//th[text()="Associated OMIM IDs"]/following-sibling::td[1]//li')
    
    for item in omim_list:
        # 提取OMIM ID链接
        omim_link = item.xpath('.//a[contains(@href, "omim.org")]')
        if omim_link:
            omim_id = clean_text(omim_link[0].text_content())
            omim_url = omim_link[0].get('href', '')
            
            # 提取疾病名称（在括号中或链接后的文本）
            full_text = clean_text(item.text_content())
            disease_match = re.search(r'\((.*?)\)', full_text)
            disease_name = disease_match.group(1) if disease_match else ""
            
            if omim_id:
                entry_parts = [omim_id]
                if omim_url:
                    entry_parts.append(f"URL: {omim_url}")
                if disease_name:
                    entry_parts.append(f"Disease: {disease_name}")
                
                omim_ids.append(" | ".join(entry_parts))
    
    # 如果上面的方法没有找到，尝试备用方法
    if not omim_ids:
        omim_links = tree.xpath('//a[contains(@href, "omim.org")]')
        for link in omim_links:
            omim_text = clean_text(link.text_content())
            omim_url = link.get('href', '')
            if omim_text:
                entry = omim_text
                if omim_url:
                    entry += f" | URL: {omim_url}"
                if entry not in omim_ids:
                    omim_ids.append(entry)
    
    data['Associated_OMIM_IDs'] = "; ".join(omim_ids) if omim_ids else ""
    
    # 24_KEGG_Compound_ID - 恢复原始精确XPath和错误处理
    kegg_id = ""
    try:
        kegg_element = tree.xpath('//th[text()="KEGG Compound ID"]/following-sibling::td[1]//a')
        if kegg_element:
            kegg_id = clean_text(kegg_element[0].text_content())
            kegg_url = kegg_element[0].get('href', '')
            if kegg_url:
                kegg_id += f" | URL: {kegg_url}"
        else:
            # 备用方法：直接查找KEGG链接
            kegg_links = tree.xpath('//a[contains(@href, "genome.jp/dbget-bin/www_bget?cpd:")]')
            if kegg_links:
                kegg_id = clean_text(kegg_links[0].text_content())
                kegg_url = kegg_links[0].get('href', '')
                if kegg_url:
                    kegg_id += f" | URL: {kegg_url}"
    except Exception as e:
        print(f"KEGG提取错误 [{hmdb_id}]: {e}")
    
    data['KEGG_Compound_ID'] = kegg_id
    
    # 25_PubChem_Compound - 恢复原始精确XPath和错误处理
    pubchem_id = ""
    try:
        pubchem_element = tree.xpath('//th[text()="PubChem Compound"]/following-sibling::td[1]//a')
        if pubchem_element:
            pubchem_id = clean_text(pubchem_element[0].text_content())
            pubchem_url = pubchem_element[0].get('href', '')
            if pubchem_url:
                pubchem_id += f" | URL: {pubchem_url}"
        else:
            # 备用方法：查找PubChem链接
            pubchem_links = tree.xpath('//a[contains(@href, "pubchem.ncbi.nlm.nih.gov")]')
            if pubchem_links:
                pubchem_id = clean_text(pubchem_links[0].text_content())
                pubchem_url = pubchem_links[0].get('href', '')
                if pubchem_url:
                    pubchem_id += f" | URL: {pubchem_url}"
    except Exception as e:
        print(f"PubChem提取错误 [{hmdb_id}]: {e}")
    
    data['PubChem_Compound'] = pubchem_id
    
    # 对所有字段应用HTML实体解码
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = html_module.unescape(value)
    
    return data

def should_retry(exception, status_code=None):
    """判断是否应该重试"""
    if isinstance(exception, requests.exceptions.Timeout):
        return True
    if isinstance(exception, requests.exceptions.ConnectionError):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        if status_code:
            # 429, 502, 503, 504 应该重试
            if status_code in [429, 502, 503, 504]:
                return True
            # 404, 400, 403 不重试
            if status_code in [404, 400, 403]:
                return False
        return True
    return True

def get_metabolite_data_with_retry(hmdb_id, max_retries=MAX_RETRIES):
    import random
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return get_metabolite_data(hmdb_id)
        except requests.exceptions.HTTPError as e:
            last_exception = e
            status_code = e.response.status_code if e.response else None
            
            if not should_retry(e, status_code):
                break
                
            if attempt < max_retries - 1:  # 只在非最后一次重试时延时
                # 增加基础等待时间，适应低配置环境
                base_wait = 3 + (2 ** attempt)  # 基础等待时间更长
                jitter = random.uniform(0.5, 1.5)  # 添加随机抖动
                wait_time = base_wait * jitter
                
                if status_code == 429:  # Too Many Requests
                    # 检查Retry-After头
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait_time = max(wait_time, int(retry_after) + random.uniform(1, 3))
                        except ValueError:
                            pass
                elif status_code in [503, 502, 504]:  # 服务器错误，等待更长时间
                    wait_time = max(wait_time, 5 + random.uniform(2, 5))
                
                time.sleep(wait_time)
                
        except Exception as e:
            last_exception = e
            if not should_retry(e):
                break
                
            if attempt < max_retries - 1:  # 只在非最后一次重试时延时
                # 增加基础等待时间
                base_wait = 3 + (2 ** attempt)
                jitter = random.uniform(0.5, 1.5)
                wait_time = base_wait * jitter
                time.sleep(wait_time)
    
    # 记录失败信息
    error_msg = f"[{hmdb_id}] 重试失败: {str(last_exception)}"
    logger.error(error_msg)
    return None

def save_failed_ids(failed_ids, filename='失败.txt'):
    """保存失败的ID到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for hmdb_id, error in failed_ids:
            f.write(f"{hmdb_id}\t{error}\n")

def save_progress(processed_ids, filename='progress.json'):
    """保存处理进度"""
    progress_data = {
        'processed_ids': list(processed_ids),
        'timestamp': datetime.now().isoformat(),
        'count': len(processed_ids)
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def load_progress(filename='progress.json'):
    """加载处理进度"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
                return set(progress_data.get('processed_ids', []))
        except Exception as e:
            print(f"加载进度文件失败: {e}")
    return set()

def get_memory_usage():
    """获取当前内存使用情况（MB）"""
    try:
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except:
        return 0

def get_system_resources():
    """获取系统资源使用情况（Ubuntu优化版）"""
    try:
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / 1024 / 1024  # MB
        memory_total = memory.total / 1024 / 1024  # MB
        
        # CPU使用情况
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 系统负载（Linux特有）
        load_avg = None
        try:
            load_avg = os.getloadavg()[0]  # 1分钟平均负载
        except:
            pass
        
        # 磁盘使用情况
        disk_usage = None
        try:
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
        except:
            pass
        
        return {
            'memory_percent': memory_percent,
            'memory_available_mb': memory_available,
            'memory_total_mb': memory_total,
            'cpu_percent': cpu_percent,
            'load_avg': load_avg,
            'disk_usage': disk_usage
        }
    except:
        return {
            'memory_percent': 0,
            'memory_available_mb': 0,
            'memory_total_mb': 0,
            'cpu_percent': 0,
            'load_avg': None,
            'disk_usage': None
        }

def check_system_resources():
    """检查系统资源，如果资源不足则暂停处理（Ubuntu 22.04优化版）"""
    resources = get_system_resources()
    
    # 提高内存阈值，适应性能翻倍的需求 - Ubuntu 22.04优化
    if resources['memory_percent'] > 90 or resources['memory_available_mb'] < 50:
        logger.warning(f"系统内存不足 (使用率: {resources['memory_percent']:.1f}%, 可用: {resources['memory_available_mb']:.1f}MB)")
        logger.info("暂停30秒等待系统资源释放...")
        time.sleep(30)
        return False
    
    # 提高CPU阈值，适应更高并发
    if resources['cpu_percent'] > 95:
        logger.warning(f"CPU使用率过高 ({resources['cpu_percent']:.1f}%)，暂停5秒...")
        time.sleep(5)
        return False
    
    # Ubuntu 22.04系统负载检查 - 提高阈值
    if resources['load_avg'] is not None and resources['load_avg'] > 4.0:
        logger.warning(f"系统负载过高 (负载: {resources['load_avg']:.2f})，暂停10秒...")
        time.sleep(10)
        return False
    
    # 磁盘使用检查
    if resources['disk_usage'] is not None and resources['disk_usage'] > 95:
        logger.warning(f"磁盘空间不足 (使用率: {resources['disk_usage']:.1f}%)，请清理磁盘空间")
        time.sleep(5)
        return False
    
    return True

def write_to_csv(results, filename, mode='a'):
    fieldnames = [
        'HMDB_ID',                              # 01
        'Common_Name',                          # 02
        'Description',                          # 03
        'Synonyms',                             # 04
        'Chemical_Formula',                     # 05
        'Average_Molecular_Weight',             # 06
        'Monoisotopic_Molecular_Weight',        # 07
        'IUPAC_Name',                           # 08
        'Traditional_Name',                     # 09
        'CAS_Registry_Number',                  # 10
        'SMILES',                               # 11
        'Kingdom',                              # 12
        'Super_Class',                          # 13
        'Class',                                # 14
        'Sub_Class',                            # 15
        'Direct_Parent',                        # 16
        'Experimental_Molecular_Properties',    # 17
        'Predicted_Molecular_Properties',       # 18
        'Pathways',                             # 19
        'Normal_Concentrations',                # 20
        'Abnormal_Concentrations',              # 21
        'Disease_References',                   # 22
        'Associated_OMIM_IDs',                  # 23
        'KEGG_Compound_ID',                     # 24
        'PubChem_Compound'                      # 25
    ]
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode, newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        if not file_exists or mode == 'w':
            writer.writeheader()
        writer.writerows(results)

def process_ids(hmdb_ids, max_workers=MAX_WORKERS):
    import gc  # 导入垃圾回收模块
    
    # 加载已处理的ID
    processed_ids = load_progress()
    remaining_ids = [id for id in hmdb_ids if id not in processed_ids]
    
    if not remaining_ids:
        print("所有ID都已处理完成！")
        return len(hmdb_ids), 0, []
    
    print(f"发现 {len(processed_ids)} 个已处理的ID，剩余 {len(remaining_ids)} 个待处理")
    
    # 使用字典存储结果，保持原始顺序
    results_dict = {}
    failed_ids = []
    total_ids = len(hmdb_ids)
    current_processed = len(processed_ids)
    success_count = len(processed_ids)
    failure_count = 0
    start_time = time.time()
    
    # 初始内存使用情况
    initial_memory = get_memory_usage()
    logger.info(f"初始内存使用: {initial_memory:.1f}MB")
    logger.info(f"开始处理，使用 {max_workers} 个线程，全局限制 {REQUESTS_PER_SECOND} 请求/秒")
    logger.info(f"总计: {total_ids} 个ID，已完成: {current_processed} 个，剩余: {len(remaining_ids)} 个")
    logger.info("-" * 80)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(get_metabolite_data_with_retry, hmdb_id): hmdb_id for hmdb_id in remaining_ids}
        
        for future in as_completed(future_to_id):
            hmdb_id = future_to_id[future]
            current_processed += 1
            
            # 系统资源检查
            if current_processed % 10 == 0:  # 每10个请求检查一次
                if not check_system_resources():
                    gc.collect()  # 强制垃圾回收
            
            try:
                data = future.result()
                if data:
                    results_dict[hmdb_id] = data  # 存储到字典中
                    processed_ids.add(hmdb_id)
                    status = "✓"
                    success_count += 1
                else:
                    failed_ids.append((hmdb_id, "数据获取失败"))
                    status = "✗"
                    failure_count += 1
            except Exception as e:
                failed_ids.append((hmdb_id, str(e)))
                status = "✗"
                failure_count += 1
            
            # 进度报告和内存监控
            if current_processed % PROGRESS_REPORT_INTERVAL == 0 or current_processed == total_ids:
                remaining = total_ids - current_processed
                percentage = (current_processed / total_ids) * 100
                elapsed_time = time.time() - start_time
                avg_time_per_item = elapsed_time / (current_processed - len(processed_ids) + len(remaining_ids)) if current_processed > len(processed_ids) else 0
                estimated_remaining_time = avg_time_per_item * remaining if avg_time_per_item > 0 else 0
                memory_usage = get_memory_usage()
                
                logger.info(f"进度: {current_processed}/{total_ids} ({percentage:.1f}%) | "
                      f"剩余: {remaining} | 成功: {success_count} | 失败: {failure_count} | "
                      f"内存: {memory_usage:.1f}MB | 预计剩余: {estimated_remaining_time/60:.1f}分钟")
                
                # 提高内存阈值，适应性能翻倍
                if memory_usage > 800:  # 提高到800MB阈值
                    gc.collect()
                    logger.info(f"执行垃圾回收，内存使用: {get_memory_usage():.1f}MB")
            
            # 批量写入 - 按原始顺序（更频繁的写入以减少内存使用）
            if len(results_dict) >= BATCH_WRITE_SIZE:
                # 按照hmdb_ids的原始顺序排列结果
                ordered_results = []
                for hmdb_id in hmdb_ids:
                    if hmdb_id in results_dict:
                        ordered_results.append(results_dict[hmdb_id])
                        del results_dict[hmdb_id]  # 删除已写入的结果以节省内存
                
                if ordered_results:
                    write_to_csv(ordered_results, '代谢物数据_最终.csv', mode='a')
                    logger.info(f"已保存 {len(ordered_results)} 条记录到文件（按原始顺序）")
                    # 清理局部变量
                    del ordered_results
                
                # 保存进度
                save_progress(processed_ids)
                
                # 强制垃圾回收
                gc.collect()
                
                # 内存检查 - 提高阈值适应性能翻倍
                memory_usage = get_memory_usage()
                if memory_usage > 1000:  # 提高到1000MB阈值
                    logger.warning(f"内存使用过高 ({memory_usage:.1f}MB)，强制清理...")
                    results_dict.clear()
                    gc.collect()
                    logger.info(f"清理后内存使用: {get_memory_usage():.1f}MB")
    
    # 保存剩余结果 - 按原始顺序
    if results_dict:
        ordered_results = []
        for hmdb_id in hmdb_ids:
            if hmdb_id in results_dict:
                ordered_results.append(results_dict[hmdb_id])
        
        if ordered_results:
            write_to_csv(ordered_results, '代谢物数据_最终.csv', mode='a')
            print(f"保存最后 {len(ordered_results)} 条记录（按原始顺序）")
    
    # 保存失败的ID
    if failed_ids:
        save_failed_ids(failed_ids)
        print(f"已保存 {len(failed_ids)} 个失败ID到 失败.txt")
    
    # 保存最终进度
    save_progress(processed_ids)
    
    return success_count, failure_count, failed_ids

def main():
    # 初始化日志系统
    setup_logging()
    
    start_time = time.time()
    
    try:
        logger.info("=" * 80)
        logger.info("HMDB代谢物数据提取工具 - Ubuntu 22.04性能优化版")
        logger.info(f"配置: {MAX_WORKERS}线程 | {REQUESTS_PER_SECOND}请求/秒 | {BATCH_WRITE_SIZE}条/批次")
        logger.info("=" * 80)
        
        # 系统环境检查（Ubuntu 22.04版）
        resources = get_system_resources()
        system_info = platform.system() + " " + platform.release()
        logger.info(f"{system_info} 系统资源状态:")
        logger.info(f"  总内存: {resources['memory_total_mb']:.0f}MB")
        logger.info(f"  内存使用率: {resources['memory_percent']:.1f}%")
        logger.info(f"  可用内存: {resources['memory_available_mb']:.1f}MB")
        logger.info(f"  CPU使用率: {resources['cpu_percent']:.1f}%")
        
        if resources['load_avg'] is not None:
            logger.info(f"  系统负载: {resources['load_avg']:.2f}")
        
        if resources['disk_usage'] is not None:
            logger.info(f"  磁盘使用率: {resources['disk_usage']:.1f}%")
        
        # Ubuntu 22.04系统建议 - 调整阈值适应性能翻倍
        if resources['memory_available_mb'] < 100:
            logger.warning("可用内存不足100MB")
            logger.info("   建议执行: sudo systemctl stop apache2 mysql nginx")
        if resources['memory_percent'] > 85:
            logger.warning("内存使用率过高")
            logger.info("   建议执行: sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches")
        if resources['load_avg'] is not None and resources['load_avg'] > 3.0:
            logger.warning(f"系统负载较高 ({resources['load_avg']:.2f})")
            logger.info("   建议等待系统负载降低后再运行")
        
        logger.info("-" * 80)
        
        if not os.path.exists('id.txt'):
            logger.error("找不到 id.txt 文件。请确保该文件与程序在同一目录下。")
            input("按回车键退出...")
            sys.exit(1)

        with open('id.txt', 'r', encoding='utf-8') as f:
            hmdb_ids = f.read().splitlines()
        logger.info(f"从id.txt加载了 {len(hmdb_ids)} 个ID")
        
        invalid_ids, duplicates = check_ids(hmdb_ids)
        
        if invalid_ids:
            logger.warning("发现以下异常ID:")
            for index, id in invalid_ids[:10]:  # 只显示前10个
                logger.warning(f"  第{index}行: {id}")
            if len(invalid_ids) > 10:
                logger.warning(f"  ... 还有 {len(invalid_ids) - 10} 个异常ID")
        
        if duplicates:
            logger.warning("发现重复ID:")
            for id, count in list(duplicates.items())[:10]:  # 只显示前10个
                logger.warning(f"  {id}: 重复{count}次")
            if len(duplicates) > 10:
                logger.warning(f"  ... 还有 {len(duplicates) - 10} 个重复ID")
        
        valid_ids = [id for id in hmdb_ids if id.startswith("HMDB")]
        unique_ids = list(dict.fromkeys(valid_ids))
        
        logger.info(f"将处理 {len(unique_ids)} 个有效且唯一的ID")
        logger.info("-" * 80)
        
        # 初始化输出文件
        if not os.path.exists('progress.json'):
            write_to_csv([], '代谢物数据_最终.csv', mode='w')
            logger.info("已初始化输出文件")

        success_count, failure_count, failed_ids = process_ids(unique_ids)

        # 最终排序确保顺序正确
        logger.info("正在按原始ID顺序整理CSV文件...")
        sort_csv_by_original_order(unique_ids, '代谢物数据_最终.csv')

        # 计算总耗时
        total_time = time.time() - start_time
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        
        logger.info("=" * 80)
        logger.info("处理完成！")
        logger.info(f"总计: {len(unique_ids)} 个ID")
        logger.info(f"成功: {success_count} 个 ({success_count/len(unique_ids)*100:.1f}%)")
        logger.info(f"失败: {failure_count} 个 ({failure_count/len(unique_ids)*100:.1f}%)")
        logger.info(f"总耗时: {hours}小时{minutes}分钟{seconds}秒")
        logger.info(f"平均速度: {len(unique_ids)/total_time*60:.1f} 个/分钟")
        logger.info(f"最终结果已保存在: 代谢物数据_最终.csv（按原始ID顺序排列）")
        
        if failed_ids:
            logger.info(f"失败记录已保存在: 失败.txt")
        
        # 清理临时文件
        if os.path.exists('progress.json'):
            os.remove('progress.json')
            logger.info("已清理临时进度文件")
        
        logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.warning("程序被用户中断")
        logger.info("进度已保存，可以重新运行程序继续处理")
    except Exception as e:
        logger.error(f"发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("程序运行完成！")
        logger.info("日志已保存到 logs/ 目录")
        print("按任意键退出...")
        try:
            input()
        except:
            pass

def sort_csv_by_original_order(original_ids, csv_file):
    """
    按照原始ID顺序重新排列CSV文件
    """
    try:
        import pandas as pd
        
        # 读取CSV文件
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        if df.empty or 'HMDB_ID' not in df.columns:
            print("CSV文件为空或缺少HMDB_ID列，跳过排序")
            return
        
        # 创建ID顺序映射
        id_order = {hmdb_id: i for i, hmdb_id in enumerate(original_ids)}
        
        # 为DataFrame添加排序键
        df['sort_key'] = df['HMDB_ID'].map(id_order)
        
        # 按排序键排序
        df_sorted = df.sort_values('sort_key').drop('sort_key', axis=1)
        
        # 重新写入CSV文件
        df_sorted.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"CSV文件已按原始ID顺序重新排列，共 {len(df_sorted)} 条记录")
        
    except ImportError:
        print("警告：pandas未安装，无法进行最终排序。请安装pandas: pip install pandas")
    except Exception as e:
        print(f"排序CSV文件时出错: {e}")

if __name__ == "__main__":
    main()

"""
Ubuntu 22.04系统运行指南：
========================

1. 安装依赖：
   sudo apt update
   sudo apt install python3 python3-pip python3-dev htop
   pip3 install requests lxml psutil pandas

2. Ubuntu 22.04性能优化（运行前执行）：
   # 停止不必要的服务
   sudo systemctl stop apache2 2>/dev/null || true
   sudo systemctl stop mysql 2>/dev/null || true
   sudo systemctl stop nginx 2>/dev/null || true
   sudo systemctl stop snapd 2>/dev/null || true
   
   # 增加文件描述符限制（支持更高并发）
   echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
   echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
   
   # 优化网络参数（适配低配置VPS）
   echo "net.core.rmem_max = 33554432" | sudo tee -a /etc/sysctl.conf
   echo "net.core.wmem_max = 33554432" | sudo tee -a /etc/sysctl.conf
   echo "net.ipv4.tcp_rmem = 4096 87380 33554432" | sudo tee -a /etc/sysctl.conf
   echo "net.ipv4.tcp_wmem = 4096 65536 33554432" | sudo tee -a /etc/sysctl.conf
   echo "net.core.netdev_max_backlog = 5000" | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   
   # 优化内存管理（适配小内存环境）
   echo "vm.swappiness = 10" | sudo tee -a /etc/sysctl.conf
   echo "vm.dirty_ratio = 15" | sudo tee -a /etc/sysctl.conf
   echo "vm.dirty_background_ratio = 5" | sudo tee -a /etc/sysctl.conf
   
   # 清理系统缓存
   sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
   
   # 检查可用内存
   free -h

3. 运行程序：
   # 前台运行（可以看到实时输出）
   python3 102511.py
   
   # 后台运行（推荐）
   nohup python3 102511.py > output.log 2>&1 &
   
   # 查看运行状态
   tail -f output.log
   
   # 查看进程
   ps aux | grep python3

4. 监控资源：
   # 实时监控
   htop
   
   # 查看特定进程
   top -p $(pgrep -f 102511.py)
   
   # 查看内存使用
   free -h
   
   # 查看系统负载
   uptime
   
   # 实时监控脚本性能
   watch -n 5 'ps aux | grep 102511.py'
   
   # 监控网络连接
   ss -tuln | grep :80

5. 停止程序：
   # 查找进程ID
   ps aux | grep 102511.py
   
   # 优雅停止（推荐）
   kill -TERM <PID>
   
   # 强制停止
   kill -9 <PID>
   
   # 批量停止
   pkill -f 102511.py

6. 故障排除：
   - 如果内存不足：重启VPS或清理缓存
   - 如果网络超时：检查网络连接和DNS设置
   - 如果权限错误：确保有写入当前目录的权限
   - 如果系统负载过高：等待负载降低或重启系统
   - 如果磁盘空间不足：清理日志文件和临时文件
   
注意：程序会自动保存进度，中断后重新运行会从断点继续。
"""
```


## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
