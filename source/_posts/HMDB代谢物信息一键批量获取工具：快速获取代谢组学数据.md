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
> 本文配合视频食用效果最佳，视频版本在文章末尾。

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

## 使用方法

1. 准备输入文件：
   - 创建`id.txt`文件
   - 每行输入一个HMDB ID
   - 示例格式：

   ```
   HMDB0013302
   HMDB0000562
   HMDB0000097
   ```

2. 运行程序：
   - 直接运行可执行文件或Python脚本
   - 程序会自动读取`id.txt`中的HMDB ID
   - 开始批量获取代谢物信息

3. 查看结果：
   - 程序运行完成后会生成`metabolite_data.csv`文件
   - 使用Excel或其他表格软件打开查看结果
   - 同时会生成日志文件记录运行过程

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
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
