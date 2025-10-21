---
title: 用python写一个网页源码下载器
permalink: /python-webpage-source-downloader/
date: 2024-10-17 11:42:12
description: 这个Python脚本能帮助您轻松保存完整网页,包括图片、样式和脚本。
category:
- 编程案例
tags:
- python
- python代码
---

> 原文地址：<https://itxiaozhang.com/python-webpage-source-downloader/>  
> 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，点击电脑维修，加我微信咨询。 

## 介绍

这个Python脚本能帮助您轻松保存完整网页,包括图片、样式和脚本。

## 主要功能

- 下载指定网页的HTML内容
- 获取并内嵌所有资源(图片、CSS、JavaScript等)
- 将完整网页保存为单个HTML文件
- 支持同时处理多个网页

## 源代码

```python
# 作者：IT小章
# 时间：2024年10月16日
# 网站：itxiaozhang.com

import os
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_resource(url, base_url, scraper):
    try:
        response = scraper.get(url, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').split(';')[0]
            return f"data:{content_type};base64,{base64.b64encode(response.content).decode('utf-8')}"
    except:
        pass
    return urljoin(base_url, url)

def save_webpage(url, output_file):
    # 创建一个cloudscraper实例
    scraper = cloudscraper.create_scraper(browser='chrome')
    
    # 获取网页内容
    response = scraper.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 处理外部资源
    for tag in soup.find_all(['img', 'script', 'link']):
        if tag.name == 'img' and tag.has_attr('src'):
            tag['src'] = download_resource(tag['src'], url, scraper)
        elif tag.name == 'script' and tag.has_attr('src'):
            tag['src'] = download_resource(tag['src'], url, scraper)
        elif tag.name == 'link' and tag.has_attr('href'):
            tag['href'] = download_resource(tag['href'], url, scraper)

    # 处理内联样式中的URL
    for tag in soup.find_all(style=True):
        style = tag['style']
        urls = [u.strip() for u in style.split('url(') if ')' in u]
        for u in urls:
            old_url = u.split(')')[0].strip("'").strip('"')
            new_url = download_resource(old_url, url, scraper)
            style = style.replace(f"url({old_url})", f"url({new_url})")
        tag['style'] = style

    # 保存处理后的HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"网页已保存至 {output_file}")

def save_multiple_webpages(urls_and_outputs):
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(save_webpage, url, output): url for url, output in urls_and_outputs}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as exc:
                print(f'{url} 生成过程中产生了一个异常: {exc}')


urls_and_outputs = [
    ("https://lasempresas.com.mx/", "saved_webpage_1.html"),
    ("https://indialei.in/", "saved_webpage_2.html"),
    ("https://www.zaubacorp.com/", "saved_webpage_3.html"),
]

save_multiple_webpages(urls_and_outputs)
```

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，点击电脑维修，加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
