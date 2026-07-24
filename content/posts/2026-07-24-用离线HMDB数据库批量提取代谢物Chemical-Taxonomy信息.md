---
title: '用离线HMDB数据库批量提取代谢物Chemical Taxonomy信息'
url: hmdb-metabolite-chemical-taxonomy-export
date: 2026-07-24T16:41:06+08:00
description: 使用 Python 基于离线 HMDB XML 数据库，根据 HMDB ID 批量提取 Chemical Taxonomy 分类信息，并解决 CSV 输出 PermissionError 权限错误问题。
categories:
  - 编程开发
tags:
  - python
  - xml
  - 数据处理
  - 代谢物
  - 离线数据库
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/hmdb-metabolite-chemical-taxonomy-export/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 


最近处理了一个比较具体的数据整理需求：

根据一批 HMDB ID，从离线 HMDB 数据库中批量提取 Chemical Taxonomy 分类信息，并导出为 CSV 文件。

这个需求看起来并不复杂，但在实际科研数据处理中非常常见。

很多时候，用户手里已经有一批代谢物 ID，例如 HMDB 编号，但不希望逐个打开网页查询。他们真正需要的是：

> 一份可以直接筛选、统计、分析和交付的数据表。

如果你也有类似需求，例如：

1. 已经拥有一批 HMDB ID，需要批量补充分类信息。
2. 希望将离线数据库整理成 Excel、CSV 等结构化数据。
3. 想把一次性处理脚本整理成可重复运行的小工具。

这类任务通常都可以通过自动化脚本解决。

---

## 一、需求分析

这次需求最终整理为以下几个目标：

### 1. 输入 HMDB ID 列表

输入文件：

```
id.txt
```

格式：

```
HMDB0000122
HMDB0000123
HMDB0000124
```

每行一个 HMDB ID。

---

### 2. 输入数据预处理

读取后需要进行基础清洗：

* 删除空行。
* 去除首尾空格。
* 删除重复 ID。
* 保留第一次出现的顺序。

这样可以避免重复查询，同时保证输出结果和原始列表顺序一致。

---

### 3. 使用离线 HMDB 数据库

不依赖在线网页接口，而是直接读取：

```
hmdb_metabolites.xml
```

这样有几个优势：

* 不受网络影响。
* 查询速度更稳定。
* 适合大量 ID 批量处理。

---

### 4. 自动寻找数据库文件

脚本不会固定绑定某个绝对路径。

优先查找：

1. 当前项目目录。
2. 项目子目录。
3. 指定备用路径。

这样换电脑或者迁移项目时，不需要重新修改代码。

---

### 5. 提取目标字段

最终只保留 Chemical Taxonomy 相关字段：

| 字段            |
| ------------- |
| Description   |
| Kingdom       |
| Super Class   |
| Class         |
| Sub Class     |
| Direct Parent |

---

### 6. 保留未匹配记录

如果某个 HMDB ID 在数据库中没有找到：

仍然保留该行：

```
HMDB ID
```

其他字段为空。

这样方便后续人工检查缺失数据。

---

### 7. 输出 CSV

最终输出：

```
output/hmdb_taxonomy_export.csv
```

编码：

```
UTF-8-SIG
```

方便 Windows Excel 直接打开。

---

# 二、实现思路

整个处理流程主要分为四个步骤。

---

## 第一步：清洗 HMDB ID

首先读取输入文件。

这一部分看似简单，但非常重要。

实际数据来源通常比较杂：

* 手工整理的数据。
* 不同软件导出的列表。
* 多次合并后的文件。

其中经常包含：

* 空行。
* 重复值。
* 多余空格。

提前清洗，可以避免后续结果数量异常。

---

## 第二步：自动定位 HMDB XML

为了提高脚本可移植性，没有直接写死：

例如：

```
C:\Users\xxx\hmdb_metabolites.xml
```

而是设计为自动搜索：

```
项目目录
 ├── hmdb_metabolites.xml
 ├── data/
 │    └── hmdb_metabolites.xml
```

如果项目目录没有找到，再尝试备用路径。

---

## 第三步：流式解析 HMDB XML

HMDB XML 文件体积较大。

如果直接：

```python
tree = ET.parse("hmdb_metabolites.xml")
```

可能会占用大量内存。

因此采用流式解析方式：

* 逐条读取 metabolite 节点。
* 判断 HMDB ID 是否需要。
* 提取需要字段。
* 释放已经处理的 XML 节点。

这样可以降低内存占用，更适合大规模数据处理。

---

## 第四步：保持原始顺序输出

虽然输入 ID 已经去重，但输出不能重新排序。

例如：

输入：

```
HMDB0003
HMDB0001
HMDB0002
```

输出仍保持：

```
HMDB0003
HMDB0001
HMDB0002
```

这样方便和原始数据进行比对。

---

# 三、遇到的 PermissionError 问题

开发过程中遇到了一个比较典型的问题。

脚本扫描过程正常：

```
已扫描 210000 条 metabolite，
匹配到 1345 / 1381 个 ID
```

但是在最后写 CSV 时失败：

```
PermissionError: [Errno 13] Permission denied:
'C:\Users\Administrator\Documents\hmdb0723\output\hmdb_taxonomy_export.csv'
```

---

这个错误并不是 XML 解析失败。

而是发生在文件写入阶段。

常见原因包括：

### 1. CSV 文件正在被 Excel 打开

Windows 下，如果 Excel 占用了文件：

```
hmdb_taxonomy_export.csv
```

Python 会无法覆盖写入。

解决：

关闭 Excel 后重新运行。

---

### 2. 输出目录权限不足

例如：

* 系统保护目录。
* 只读目录。
* 没有写入权限的位置。

解决：

换到普通用户目录。

---

### 3. 文件被其他程序锁定

例如：

* 杀毒软件扫描。
* 同步工具占用。
* 文件预览程序占用。

---

这类问题在数据处理脚本中非常常见。

很多时候，核心逻辑已经完成，最后一步文件输出反而成为失败点。

---

# 四、部分代码示例

下面只展示核心思路。

---

## 读取并去重 HMDB ID

```python
def load_unique_ids(id_path):
    seen = set()
    ordered_ids = []

    with open(id_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            hmdb_id = raw_line.strip()

            if not hmdb_id:
                continue

            if hmdb_id in seen:
                continue

            seen.add(hmdb_id)
            ordered_ids.append(hmdb_id)

    return ordered_ids
```

---

## 自动定位 XML 数据库

```python
def resolve_xml_path(project_root, cli_xml_path=None):

    if cli_xml_path:
        return cli_xml_path

    candidates = find_project_xml_candidates(project_root)

    if candidates:
        return candidates[0]

    if os.path.exists(FALLBACK_XML_PATH):
        return FALLBACK_XML_PATH

    raise FileNotFoundError(
        "未找到 hmdb_metabolites.xml"
    )
```

---

## 提取 Chemical Taxonomy

```python
def extract_taxonomy_record(elem):

    return {
        "HMDB ID": get_text(...),
        "Description": get_text(...),
        "Kingdom": get_text(...),
        "Super Class": get_text(...),
        "Class": get_text(...),
        "Sub Class": get_text(...),
        "Direct Parent": get_text(...),
    }
```

---

完整版本中还包含：

1. XML 命名空间处理。
2. 大文件流式解析优化。
3. 节点释放控制。
4. 未匹配 ID 保留逻辑。
5. CSV 编码处理。
6. 数据统计输出。

这些部分才是让脚本真正稳定运行的关键。

---

# 五、最终效果

最终脚本可以实现：

1. 从 `id.txt` 批量读取 HMDB ID。
2. 自动定位离线 HMDB XML 数据库。
3. 提取 Chemical Taxonomy 分类信息。
4. 导出标准 CSV 文件。
5. 保留未匹配记录。
6. 支持重复运行。

对于科研数据整理、代谢物分析、数据库转换等场景，这类自动化工具非常实用。

它不一定复杂，但可以明显减少重复劳动。

---

# 六、我能提供的帮助

如果你也有类似的数据处理需求，例如：

1. 批量提取 HMDB、KEGG、PubChem 等数据库字段。
2. 将离线数据库转换成 CSV、Excel 或内部数据表。
3. 将一次性脚本整理成稳定、可重复运行的小工具。

都可以联系我，请[加我微信](https://zhang9.cn)咨询。  



## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


