---
title: 离线安装 Microsoft Store 微软商店中的软件
permalink: /offline-installation-of-apps-from-microsoft-store/
date: 2024-03-07 15:42:06
categories: 
  - 技术笔记
tags: 
  - microsoft-store
  - 微软商店
---

## 背景

由于某些网络环境限制或系统配置问题，我们无法直接 Microsoft Store 安装软件，在这种情况下，我们可以选择另外一种方法。本文中，我用 WinDbg Preview 下载安装举例。

<!--more-->
## 教程

1. 网页端 Microsoft Store 中搜索 [WinDbg Preview](https://apps.microsoft.com/detail/9pgjgd53tn86?hl=en-us&gl=US "WinDbg Preview") ，并获取链接。
2. 打开 [https://store.rg-adguard.net](https://store.rg-adguard.net) ，使用这个网站解析第一步获取到的链接。
3. 选择一个版本下载，后缀名一般是 .msixbundle 或者 .appx。
4. 双击安装。
