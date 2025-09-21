---
title: 批量图片去水印：使用 IOPaint 实现固定掩膜批量去除图片水印
permalink: /iopaint-fixed-mask-batch-inpainting-cpu/
date: 2025-05-19 18:27:22
description: 使用 IOPaint CLI 和固定掩膜图，在 CPU 环境下实现图片水印的批量自动去除，兼顾高效率与低门槛，适用于无 GPU 用户的图像处理需求。
category:
- 编程开发
tags:
- 批量处理
- IOPaint
- 水印
- python
---

> 原文地址：<https://itxiaozhang.com/iopaint-fixed-mask-batch-inpainting-cpu/>  
> 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 

## 一、需求分析

在批量处理图片的实际工作中，常会遇到统一位置的水印（如顶部编号、底部标识等）。手动擦除效率低，借助 AI 图像修复工具如 IOPaint（原 Lama Cleaner）可实现自动化处理。然而其默认使用 Web 界面，不能直接批处理，因此本文目标是：

- **批量处理整目录图片**
- **使用一个固定掩膜去除相同水印位置**
- **全自动运行，无需交互操作**
- **使用 CPU，兼容所有普通电脑**
- **输出保持原分辨率与文件名**
- **生成完整处理日志**

---

## 二、解决思路

### 1. 工具选择

使用开源图像修复工具 [IOPaint](https://github.com/Sanster/IOPaint)，支持命令行调用与 AI 修复模型（默认 lama），适合图像 inpainting 任务，兼容 CPU 和 GPU。

### 2. 执行流程

- 安装 Python 与 IOPaint CLI
- 使用 Lama Cleaner 在线版手动生成统一的掩膜图
- 用 Python 脚本批量执行 CLI 命令
- 支持多进程并发，加速 CPU 处理

---

## 三、掩膜文件准备与优化

### 1. 掩膜制作

打开 [Lama Cleaner Hugging Face 页面](https://huggingface.co/spaces/Sanster/Lama-Cleaner-lama)，加载任意一张图，进行掩膜绘制：

- 勾选「Download Mask」
- 勾选「Manual Inpainting Mode」
- 用画笔框选需要去除的水印区域
- 点击「Download Mask」按钮下载掩膜图

掩膜图与原图尺寸一致，白色区域为需修复部分。

### 2. 掩膜要求

- 保存为 `fixed_mask.jpg`，与原图尺寸相同（如 960x8049）
- 白色区域表示需要修复，黑色保留不变
- 掩膜应统一应用于所有图像

---

## 四、脚本开发与并行优化（仅使用 CPU）

为提升批量处理效率，我们开发了一个支持多进程并发的 Python 脚本。虽然运行在 CPU 上，但并行仍能显著提速。

### 📁 文件结构

```

项目目录/
├─ input/              # 原始图片目录
├─ output/             # 输出目录（自动创建）
├─ fixed\_mask.jpg      # 掩膜图
├─ parallel\_iopaint.py # 主执行脚本

````

### 📜 脚本核心内容（简要）

- 遍历 `input/` 目录中的图片
- 为每张图调用 IOPaint CLI 命令行工具
- 使用 `multiprocessing.Pool` 并发处理多个任务
- 日志记录每张图是否成功及处理耗时

### 🔧 主要命令调用

```python
subprocess.run([
    "iopaint", "run",
    "--model", "lama",
    "--device", "cpu",           # 明确使用 CPU，兼容性好
    "--image", input_path,
    "--mask", mask_path,
    "--output", output_dir
])
````

---

## 五、使用说明

### 1. 环境安装（无 Anaconda，纯 pip）

确保已安装 Python 3.9/3.10，并添加到 PATH：

```bash
pip install torch torchvision
pip install iopaint
```

> 无需 GPU、CUDA，直接使用 CPU 即可。

### 2. 执行脚本

将图片放入 `input/`，掩膜命名为 `fixed_mask.jpg`，运行命令：

```bash
python parallel_iopaint.py
```

所有图片将自动处理，输出保存在 `output/`，日志记录写入 `process.log`。

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
