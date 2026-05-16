---
title: 'Python批量筛选HMDB代谢物Detected and Quantified与Endogenous字段'
url: python-batch-hmdb-detected-quantified-endogenous-filter
date: 2026-05-16T12:56:59+08:00
description: 客户提供数万条 HMDB 代谢物 ID，需要批量判断 Status 是否为 Detected and Quantified，以及是否为 Endogenous。通过 Python 自动化处理 ID 清洗、字段匹配与结果输出，替代人工逐条查询，提高处理效率并减少错误。
categories:
  - 编程开发
tags:
  - Python
  - 数据处理
  - 自动化查询
  - XML 数据解析
  - 数据清洗
  - hmdb 数据库
  - hmdb 编程
  - 代谢物数据库
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/python-batch-hmdb-detected-quantified-endogenous-filter>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 


## 问题描述

客户提供了大量代谢物 ID，需要批量查询数据库，并判断两个关键字段：

* `Status` 是否为 **Detected and Quantified**
* 是否属于 **Endogenous**

判断规则：

* `Status = Detected and Quantified` → 标记 `yes`
* `Biospecimen = Endogenous` → 标记 `yes`
* 未命中则标记 `no`

由于数据量较大，人工逐条查询数据库效率较低，且容易出现误判。

原始数据约 3000~4000 条，但存在重复 ID、格式错误 ID，最终有效数据仅 **1437 条**。

客户同时要求程序尽可能简化操作流程，最好通过双击即可直接运行。

---

## 问题原因

### 1. 人工查询效率过低

需要反复进入数据库页面查询：

* `Detected and Quantified`
* `Endogenous`

重复操作耗时较长。

---

### 2. 原始数据质量较差

数据中存在：

* 重复 ID
* 非法格式 ID
* 无法匹配数据库的无效 ID

需要额外清洗。

---

### 3. 客户不具备编程环境

客户希望直接使用，无需安装 Python、配置环境或手动执行命令。

---

## 解决办法

### 1. 编写自动化查询脚本

程序核心逻辑：

* 读取用户提供的 ID 列表
* 自动校验 ID 格式
* 自动去重
* 查询 XML 数据
* 判断目标字段
* 输出结果 CSV

部分核心代码：

```python
def main():
    parser = argparse.ArgumentParser()

    # XML 数据源
    parser.add_argument("--xml", default="database.xml")

    # 用户输入的 ID 文件
    parser.add_argument("--ids", default="id.txt")

    # 输出结果
    parser.add_argument("--out", default="result.csv")

    args = parser.parse_args()

    # 检查 XML 是否存在
    if not os.path.exists(args.xml):
        raise SystemExit("找不到数据库 XML 文件")

    # 读取 ID
    input_ids = read_ids(args.ids)

    # 清洗无效 ID
    valid_ids = set()
    for item in input_ids:
        normalized = normalize_id(item)
        if normalized:
            valid_ids.add(normalized)

    # 查询注释信息
    annotation_map = build_annotation_map(
        xml_file=args.xml,
        wanted_ids=valid_ids
    )

    # 输出 CSV
    write_csv(
        output_file=args.out,
        input_ids=input_ids,
        annotation_map=annotation_map
    )

    print("处理完成")
```

---

### 2. 增加图形化操作

为了降低使用门槛，额外加入 GUI 文件选择逻辑：

```python
def select_txt_file():
    from tkinter import filedialog

    file_path = filedialog.askopenfilename(
        title="选择 ID 文件",
        filetypes=[("Text files", "*.txt")]
    )
    return file_path
```

当用户未手动传参时：

* 自动读取默认 `id.txt`
* 或弹窗让用户手动选择文件

---

### 3. 打包为 exe 文件

使用 PyInstaller 将 Python 脚本打包为 `.exe`

客户只需：

1. 打开 `id.txt`
2. 粘贴代谢物 ID
3. 保存关闭
4. 双击 exe 文件

即可完成全部处理。

---

### 4. 自动生成结果文件

程序运行后自动输出 CSV：

| ID       | Detected and Quantified | Endogenous |
| -------- | ----------------------- | ---------- |
| HMDBxxxx | yes                     | no         |

同时弹窗提示处理完成。

---

最终实现效果：

* 支持数千条 ID 批量处理
* 自动去重
* 自动过滤错误格式
* 自动判断目标字段
* 无需编程环境
* 客户双击即可使用



## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


