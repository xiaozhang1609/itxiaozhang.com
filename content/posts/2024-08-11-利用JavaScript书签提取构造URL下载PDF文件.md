---
title: 利用JavaScript书签提取构造URL下载PDF文件
url: /create-bookmark-url-download-pdf/
date: '2024-08-11 12:09:58 +0800'
description: 本文介绍如何创建一个浏览器书签，通过JavaScript自动提取当前页面的ID参数，构造PDF文件的下载链接，并在新窗口中打开该链接。
categories:
  - 编程案例
tags:
  - 书签
  - 浏览器书签
  - js脚本
author: IT小章
---

## 1. 写脚本

```javascript
javascript:(function() {
    const id = new URLSearchParams(window.location.search).get('id');
    if (id) {
        const pdfUrl = `https://example.com/path/to/pdf/${id}.pdf`;
        window.open(pdfUrl, '_blank');
    }
})();
```

## 2. 创建书签

1. **打开书签管理器**：
   - **Chrome**: 按 `Ctrl + Shift + B` 或通过菜单进入“书签” -> “书签管理器”。
   - **Firefox**: 按 `Ctrl + Shift + B` 或通过菜单进入“书签” -> “管理所有书签”。
   - **Edge**: 按 `Ctrl + Shift + B` 或通过菜单进入“收藏夹” -> “管理收藏夹”。

2. **添加新书签**：
   - **名称**: “自动下载PDF”
   - **URL**: 粘贴上述JavaScript代码。

3. **保存书签**。

## 3. 使用书签

- 访问包含ID参数的页面（例如 `https://example.com/page?id=123`）。
- 点击书签“自动下载PDF”，新窗口将打开构造的PDF文件链接。

## 说明

- **提取ID**：使用 `URLSearchParams` 从当前页面的URL中提取ID参数。
- **构造URL**：根据提取的ID生成PDF文件的下载链接。
- **打开PDF**：使用 `window.open()` 在新窗口中打开构造的PDF文件链接。


> 原文地址：<https://itxiaozhang.com/create-bookmark-url-download-pdf/>
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 
