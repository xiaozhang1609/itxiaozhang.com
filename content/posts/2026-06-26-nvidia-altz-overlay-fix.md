---
title: '无畏契约Alt+Z没反应怎么办？NVIDIA App游戏内覆盖层打不开解决方法'
url: valorant-alt-z-not-working-nvidia-app-in-game-overlay-fix
date: 2026-06-26T11:26:24+08:00
description: 《无畏契约》游戏内按 Alt+Z 无反应，仅在桌面可以打开 NVIDIA App 游戏内覆盖层，导致录屏、即时重放等功能无法使用。本文介绍该问题的原因及排查场景。
categories:
  - 游戏问题
tags:
  - 无畏契约
  - NVIDIA App
  - 游戏内覆盖层
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/valorant-alt-z-not-working-nvidia-app-in-game-overlay-fix/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

正常情况下，在游戏内按 **Alt + Z** 可以打开 **NVIDIA App** 游戏内覆盖（Overlay）界面。

出现问题后，仅在桌面或游戏外按 **Alt + Z** 可以正常打开 NVIDIA App 界面，而进入游戏后按 **Alt + Z** 无任何反应，导致录屏、即时重放等功能无法使用。

本文以《无畏契约》为例，其他使用 NVIDIA App 游戏内覆盖功能的游戏也可参考本文方法。

## 问题原因

该问题通常属于 **NVIDIA App 游戏内覆盖（In-Game Overlay）异常**。

由于 **NVIDIA Overlay.exe** 未优先使用独立显卡运行，导致游戏内覆盖无法正常加载，因此桌面环境可以正常调出覆盖界面，而进入游戏后 **Alt + Z** 无法生效。

## 解决办法

1. 使用 Everything 搜索工具或者 Windows 搜索工具，搜索 **NVIDIA Overlay.exe**。

2. 如果无法搜索到，可尝试前往默认安装目录查找，例如：

   ```text
   C:\Program Files\NVIDIA Corporation\NVIDIA App\NVIDIA Overlay.exe
   ```

   或：

   ```text
   C:\Program Files\NVIDIA Corporation\NvContainer\
   ```

3. 找到 **NVIDIA Overlay.exe** 后，右键选择**打开文件所在的位置**。

4. 复制该程序所在文件夹路径。

5. 打开：

   **设置 → 系统 → 屏幕 → 显示卡（图形）**

6. 点击 **添加桌面应用**。

7. 粘贴刚才复制的路径，找到并添加 **NVIDIA Overlay.exe**。

8. 在程序列表中找到刚添加的 **NVIDIA Overlay.exe**，点击**选项**。

9. 将 **GPU 首选项** 设置为：

   **高性能（独立显卡）**

10. 确认 **窗口化游戏优化** 已开启。

11. 关闭设置，重新启动电脑。

12. 重启后直接启动游戏，进入大厅或游戏内按 **Alt + Z**。


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


