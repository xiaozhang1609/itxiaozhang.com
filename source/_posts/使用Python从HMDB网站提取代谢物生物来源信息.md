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
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。 

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
# 检查并读取输入文件
if not os.path.exists('hmdb_id.txt'):
    print("错误：未找到hmdb_id.txt")
    exit()

with open('hmdb_id.txt', 'r', encoding='utf-8') as f:
    hmdb_ids = [line.strip() for line in f if line.strip()]

# 去重处理
unique_ids = list(set(hmdb_ids))
print(f"发现{len(unique_ids)}个唯一HMDB ID")

# 初始化结果存储
results = {'HMDB_ID': [], 'Human': [], 'Food': [], 'Microbial': []}

for idx, hmdb_id in enumerate(unique_ids, 1):
    try:
        # 网络请求带超时设置
        response = requests.get(f'https://hmdb.ca/metabolites/{hmdb_id}', timeout=10)
        response.raise_for_status()
        
        # 核心解析逻辑（示例占位符）
        # [此处为生物来源分析的核心处理流程]
        
        # 模拟解析结果
        results['HMDB_ID'].append(hmdb_id)
        results['Human'].append('yes' if idx%2 else 'no')
        
    except requests.exceptions.RequestException as e:
        print(f"{hmdb_id} 请求失败: {str(e)}")
    except Exception as e:
        print(f"{hmdb_id} 解析错误: {str(e)}")
    
    # 实时显示进度
    progress = idx/len(unique_ids)*50
    print(f"[{'='*int(progress)}{' '*(50-int(progress))}] {idx/len(unique_ids):.0%}", end='\r')

# 保存结构化结果
try:
    pd.DataFrame(results).to_csv('disposition_results.csv', index=False)
    print("\n结果已保存至 disposition_results.csv")
except Exception as e:
    print(f"保存失败: {str(e)}")
```

## 输出结果

- `disposition_results.csv`：包含各ID的生物来源标记(yes/no)
- `disposition_log.txt`：详细抓取日志和关键词统计

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
