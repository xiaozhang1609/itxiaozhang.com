---
title: 'Python爬虫实战: 58同城房产信息自动化采集'
permalink: /python-web-crawler-58city-real-estate-data-collection/
date: 2024-12-01 19:28:00
description: 这是一个基于Python开发的58同城房产信息采集系统,主要用于自动采集商铺、写字楼、厂房和生意转让等房产信息。系统提供图形界面操作,支持多城市数据采集。
category:
- 编程案例
tags:
- python
- 爬虫
- 58同城
---

> 原文地址：<https://itxiaozhang.com/python-web-crawler-58city-real-estate-data-collection/>  

## 1. 简介

这是一个基于Python开发的58同城房产信息采集系统,主要用于自动采集商铺、写字楼、厂房和生意转让等房产信息。系统提供图形界面操作,支持多城市数据采集。

## 2. 主要功能

- 多城市房产信息采集
- 多线程并发处理
- 自动代理IP切换
- 数据实时入库
- 自动去重过滤
- 定时采集更新

## 3. 技术特点

### 多线程采集

使用Python threading实现并发采集,提高效率。

### 代理IP池

自动维护代理IP池,避免被反爬:

```python
def roxies_ip(url):
    ip = requests.get(url).text
    proxies_ip_lists = []
    for i in ip:
        proxies_ip_lists.append({'https': "//" + i})
    return proxies_ip_lists[0]
```

### 数据存储

采用MySQL存储数据,支持实时入库和查重。

## 4. 使用方法

1. 配置数据库信息
2. 设置代理IP接口
3. 选择目标城市和类型
4. 设置采集间隔
5. 启动采集任务

## 相关源码

```python
"""
================================
作者：IT小章
网站：itxiaozhang.com
时间：2024年12月01日
Copyright © 2024 IT小章
================================
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import time
import json
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import random
import re
from queue import Queue

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Config:
    """配置管理类"""
    # 示例城市配置
    CITIES = {
        "北京": {"北京": "bj|1"},
        "上海": {"上海": "sh|2"},
        "广州": {"广州": "gz|3"},
        "深圳": {"深圳": "sz|4"}
    }
    
    # 房产类型配置
    HOUSE_TYPES = {
        "商铺": "/shangpucz/0/",
        "写字楼": "/zhaozu/0/",
        "厂房": "/changfang/0/",
        "生意转让": "/shengyizr/0/"
    }

    @staticmethod
    def load_config(file_path="config.json"):
        """加载配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning(f"配置文件 {file_path} 不存在，使用默认配置")
            return {}

class ProxyPool:
    """代理IP池管理类"""
    def __init__(self):
        self.proxies = Queue()
        self.lock = threading.Lock()

    def add_proxy(self, proxy):
        """添加代理"""
        self.proxies.put(proxy)

    def get_proxy(self):
        """获取代理"""
        try:
            return self.proxies.get()
        except:
            return None

    def remove_proxy(self, proxy):
        """移除失效代理"""
        with self.lock:
            if proxy in self.proxies.queue:
                self.proxies.queue.remove(proxy)

class DataStorage:
    """数据存储类"""
    def __init__(self):
        self.data_queue = Queue()

    def save(self, data):
        """保存数据
        实际使用时请实现具体的存储逻辑
        """
        logging.info(f"保存数据: {data}")
        self.data_queue.put(data)

class HouseCrawler:
    """房产信息爬虫类"""
    def __init__(self):
        self.proxy_pool = ProxyPool()
        self.storage = DataStorage()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_page(self, url, retry_times=3):
        """获取页面内容"""
        for _ in range(retry_times):
            try:
                proxy = self.proxy_pool.get_proxy()
                response = requests.get(url, headers=self.headers, proxies=proxy, timeout=10)
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    return response.text
            except Exception as e:
                logging.error(f"获取页面失败: {e}")
                if proxy:
                    self.proxy_pool.remove_proxy(proxy)
        return None

    def parse_list_page(self, html):
        """解析列表页"""
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            items = soup.select('ul .item')
            results = []
            
            for item in items:
                try:
                    title = item.select_one('.title').text.strip()
                    link = item.select_one('.link')['href']
                    results.append({
                        'title': title,
                        'link': link
                    })
                except Exception as e:
                    logging.error(f"解析列表项失败: {e}")
                    
            return results
        except Exception as e:
            logging.error(f"解析列表页失败: {e}")
            return []

    def parse_detail_page(self, html):
        """解析详情页"""
        if not html:
            return None
            
        try:
            # 示例解析逻辑
            data = {
                'title': '',
                'price': '',
                'area': '',
                'location': '',
                'contact': '',
                'description': ''
            }
            
            soup = BeautifulSoup(html, 'lxml')
            
            # 实际使用时需要根据具体网页结构实现解析逻辑
            
            return data
        except Exception as e:
            logging.error(f"解析详情页失败: {e}")
            return None
class GUI:
    """图形界面类"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("58同城房产信息采集系统 (学习版)")
        self.root.geometry('500x400')
        self.crawler = HouseCrawler()
        self.setup_gui()

    def setup_gui(self):
        """设置GUI界面"""
        # 城市选择
        tk.Label(self.root, text="选择城市:").grid(row=0, column=0, padx=5, pady=5)
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(self.root, textvariable=self.city_var, state="readonly")
        self.city_combo['values'] = list(Config.CITIES.keys())
        self.city_combo.current(0)
        self.city_combo.grid(row=0, column=1, padx=5, pady=5)

        # 房产类型选择
        tk.Label(self.root, text="房产类型:").grid(row=1, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(self.root, textvariable=self.type_var, state="readonly")
        self.type_combo['values'] = list(Config.HOUSE_TYPES.keys())
        self.type_combo.current(0)
        self.type_combo.grid(row=1, column=1, padx=5, pady=5)

        # 页数设置
        tk.Label(self.root, text="采集页数:").grid(row=2, column=0, padx=5, pady=5)
        self.pages_var = tk.StringVar(value="1")
        self.pages_entry = tk.Entry(self.root, textvariable=self.pages_var)
        self.pages_entry.grid(row=2, column=1, padx=5, pady=5)

        # 间隔时间设置
        tk.Label(self.root, text="间隔时间(秒):").grid(row=3, column=0, padx=5, pady=5)
        self.interval_var = tk.StringVar(value="5")
        self.interval_entry = tk.Entry(self.root, textvariable=self.interval_var)
        self.interval_entry.grid(row=3, column=1, padx=5, pady=5)

        # 状态显示
        self.status_text = tk.Text(self.root, height=10, width=50)
        self.status_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # 控制按钮
        self.start_button = tk.Button(self.root, text="开始采集", command=self.start_crawl)
        self.start_button.grid(row=5, column=0, padx=5, pady=5)
        
        self.stop_button = tk.Button(self.root, text="停止采集", command=self.stop_crawl)
        self.stop_button.grid(row=5, column=1, padx=5, pady=5)

        # 采集状态
        self.is_running = False

    def log_message(self, message):
        """显示日志信息"""
        self.status_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)

    def start_crawl(self):
        """开始采集"""
        if self.is_running:
            messagebox.showwarning("警告", "采集任务正在进行中")
            return

        try:
            pages = int(self.pages_var.get())
            interval = int(self.interval_var.get())
            if pages < 1 or interval < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "请输入有效的页数和间隔时间")
            return

        self.is_running = True
        threading.Thread(target=self.crawl_task, args=(pages, interval)).start()
        self.log_message("开始采集任务...")

    def stop_crawl(self):
        """停止采集"""
        self.is_running = False
        self.log_message("正在停止采集任务...")

    def crawl_task(self, pages, interval):
        """采集任务"""
        city = self.city_var.get()
        house_type = self.type_var.get()
        
        try:
            for page in range(1, pages + 1):
                if not self.is_running:
                    break
                
                self.log_message(f"正在采集第 {page} 页...")
                url = self.generate_url(city, house_type, page)
                
                # 获取列表页
                html = self.crawler.get_page(url)
                if not html:
                    self.log_message(f"获取第 {page} 页失败，跳过...")
                    continue

                # 解析列表页
                items = self.crawler.parse_list_page(html)
                self.log_message(f"第 {page} 页发现 {len(items)} 条房源信息")

                # 处理每个房源
                for item in items:
                    if not self.is_running:
                        break
                    
                    # 获取详情页
                    detail_html = self.crawler.get_page(item['link'])
                    if detail_html:
                        detail_data = self.crawler.parse_detail_page(detail_html)
                        if detail_data:
                            self.crawler.storage.save(detail_data)
                            self.log_message(f"成功采集: {item['title']}")
                    
                    # 间隔等待
                    time.sleep(interval)

        except Exception as e:
            self.log_message(f"采集过程出错: {str(e)}")
        finally:
            self.is_running = False
            self.log_message("采集任务已完成")

    def generate_url(self, city, house_type, page):
        """生成目标URL"""
        city_code = Config.CITIES[city][city].split('|')[0]
        type_path = Config.HOUSE_TYPES[house_type]
        return f"https://{city_code}.58.com{type_path}pn{page}/"

    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主程序入口"""
    try:
        # 启动GUI界面
        app = GUI()
        app.run()
    except Exception as e:
        logging.error(f"程序运行出错: {str(e)}")
        messagebox.showerror("错误", f"程序运行出错: {str(e)}")

if __name__ == "__main__":
    """
    使用说明：
    1. 安装依赖包：
       pip install requests beautifulsoup4 lxml
    
    2. 运行程序：
       python crawler.py
    
    3. 使用步骤：
       - 选择目标城市
       - 选择房产类型
       - 设置采集页数
       - 设置采集间隔时间
       - 点击"开始采集"
       
    4. 注意事项：
       - 采集间隔建议设置在5秒以上
       - 采集页数建议从小到大测试
       - 如遇到错误，请查看日志信息
       - 使用代理IP可以提高采集成功率
    
    5. 数据存储：
       - 默认将数据打印到日志
       - 可以修改DataStorage类实现其他存储方式
       
    6. 代理设置：
       - 默认使用直连方式
       - 可以修改ProxyPool类实现代理池功能
    """
    main()
```

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
