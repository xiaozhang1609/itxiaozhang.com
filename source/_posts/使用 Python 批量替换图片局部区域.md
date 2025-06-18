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
> 本文配合视频食用效果最佳，视频版本在文章末尾。

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

## 三、关键代码

```python
import os
import sys
import logging
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_image(path, top_img, bottom_img, output_dir):
    basename = os.path.basename(path)
    try:
        with Image.open(path).convert('RGBA') as img:
            width, height = img.size
            if (width, height) != (960, 8049):
                logging.warning(f"跳过 {basename}，尺寸 {width}x{height} 不符合 960x8049")
                return 'skipped'

            # 覆盖固定区域（第2份）：y=115 到 y=229（高度114）
            y_start = 115
            region_h = 114
            # 检查 top_img 大小
            if top_img.size != (960, region_h):
                logging.error(f"top_image 尺寸 {top_img.size} 与目标区域 960x{region_h} 不匹配")
                return 'failed'

            # 直接不透明覆盖
            img.paste(top_img, (0, y_start))

            # 底部粘贴
            bottom_w, bottom_h = bottom_img.size
            img.paste(bottom_img, (0, height - bottom_h), bottom_img)

            # 保存
            out_path = os.path.join(output_dir, basename)
            img.save(out_path)
            logging.info(f"已保存 {out_path}")
            return 'done'
    except Exception as e:
        logging.error(f"处理 {basename} 时失败: {e}")
        return 'failed'


def overlay_replace(
    img_dir: str,
    top_path: str,
    bottom_path: str,
    output_dir: str,
    threads: int
) -> None:
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 加载覆盖图
    try:
        top_img = Image.open(top_path).convert('RGBA')
        bottom_img = Image.open(bottom_path).convert('RGBA')
    except Exception as e:
        logging.error(f"无法打开覆盖图: {e}")
        sys.exit(1)

    # 检查输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 收集待处理文件
    all_files = [f for f in os.listdir(img_dir) if f.lower().endswith('.png')]
    paths = [os.path.join(img_dir, f) for f in all_files]

    # 多线程执行
    results = {'done': 0, 'skipped': 0, 'failed': 0}
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_map = {executor.submit(process_image, p, top_img, bottom_img, output_dir): p for p in paths}
        for future in as_completed(future_map):
            res = future.result()
            if res in results:
                results[res] += 1

    # 汇总
    logging.info("处理完成：")
    logging.info(f"  成功: {results['done']}")
    logging.info(f"  跳过: {results['skipped']}")
    logging.info(f"  失败: {results['failed']}")


if __name__ == '__main__':
    # 固定参数配置
    img_dir = 'img'
    top_path = 'top.png'
    bottom_path = 'bottom.png'
    output_dir = 'out'
    threads = 8

    overlay_replace(
        img_dir=img_dir,
        top_path=top_path,
        bottom_path=bottom_path,
        output_dir=output_dir,
        threads=threads
    )

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
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
