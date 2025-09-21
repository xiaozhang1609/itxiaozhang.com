---
title: 使用 Python 批量替换图片局部区域
permalink: /batch-replace-fixed-region-images-python/
date: 2025-06-18 11:19:01
description: 使用Python脚本，批量替换长图中同一固定区域内容，适用于统一批改模板或替换页眉页脚。支持尺寸过滤、多线程处理，操作简单高效。
category:
- 编程开发
tags:
- 编程开发
- python
- 批量
- 图片
---

> 原文地址：<https://itxiaozhang.com/batch-replace-fixed-region-images-python/>  
> 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 

## 一、需求分析

在实际工作中，我们常常会遇到这样的需求：
有一批尺寸一致的长图（如公众号长截图、拼接图等），需要在同一固定区域内替换为统一的内容，比如覆盖新的标题栏、状态栏、Logo 等。

**目标要求如下：**

* 只处理尺寸为 **960×8049** 的 PNG 图像；
* 替换区域为垂直方向上 **第 115 至第 229 像素**（高 114 像素）；
* 使用一张大小为 **960×114** 的小图进行替换；
* 支持批量自动处理，提升效率；
* 提供错误处理和处理结果统计。

## 二、解决思路

我们使用 Python 语言和 Pillow 图像处理库来实现这一功能。整体流程如下：

1. **遍历图像文件夹**
   仅处理 `.png` 文件，并验证尺寸是否为 960×8049，其他自动跳过。

2. **图像处理逻辑**

   * 使用 Pillow 打开图片并转换为 `RGBA` 模式；
   * 将 960×114 的替换图粘贴到 `(0, 115)` 位置，覆盖目标区域；
   * 保存处理后的新图到输出文件夹。

3. **并发加速处理**
   借助 Python 内置的 `ThreadPoolExecutor` 并发模块，支持多线程批量处理。

4. **日志记录与统计**
   实时输出每张图的处理结果，最终打印成功、跳过和失败数量。

## 三、关键代码片段

```python
def process_image(path, top_img, output_dir):
    with Image.open(path).convert('RGBA') as img:
        if img.size != (960, 8049):
            return 'skipped'
        # 在 y=115 处替换 960×114 区域
        img.paste(top_img, (0, 115))
        img.save(os.path.join(output_dir, os.path.basename(path)))
        return 'done'
```

完整脚本中还包含：日志配置、多线程处理逻辑、输出统计等内容。运行脚本即可批量处理所有符合条件的图片。

## 四、使用方法

1. 安装依赖：

```bash
pip install pillow
```

2. 准备目录结构：

```
img/         # 存放原始大图（960×8049）
top.png      # 替换用的小图（960×114）
out/         # 输出目录（自动创建）
```

3. 运行脚本：

```bash
python script.py
```

脚本会自动扫描 `img/` 目录中的图像文件，处理后保存到 `out/` 目录中。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
