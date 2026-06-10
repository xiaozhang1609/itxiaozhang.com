---
title: '打开特战英豪提示VAN9002需要启用Control Flow Guard CFG 控制流保护'
url: open-valorant-van9002-control-flow-guard-cfg-required
date: 2026-06-10T10:12:16+08:00
description: 打开特战英豪时出现 Vanguard 反作弊报错 VAN9002：This version of Vanguard requires Control Flow Guard (CFG) to be enabled in system exploit protection settings in order to play，导致游戏无法启动。
categories:
  - 游戏问题
tags:
  - 特战英豪
  - Vanguard
  - CFG
  - 控制流保护
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/open-valorant-van9002-control-flow-guard-cfg-required>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

打开《特战英豪》时弹出 Vanguard 反作弊报错：

> VAN9002
> This version of Vanguard requires Control Flow Guard (CFG) to be enabled in system exploit protection settings in order to play.
> See the Vanguard notification center in the tray for more details.

该错误表示 Vanguard 反作弊程序要求系统启用 Control Flow Guard（CFG，控制流保护）功能，否则游戏无法正常运行。

## 问题原因

CFG（Control Flow Guard，控制流保护）是 Windows 提供的一项安全防护机制，位于系统的攻击防护设置中。

正常情况下，该功能默认开启。如果因系统优化、修改安全设置或其他原因导致 CFG 被关闭，Vanguard 无法通过安全检查，从而触发 VAN9002 报错并阻止游戏启动。

## 解决办法

1. 打开 **Windows 安全中心**。
2. 点击左侧的 **“应用和浏览器控制”**。
3. 在右侧找到 **“攻击防护”**。
4. 点击 **“攻击防护设置”**。
5. 进入 **“系统设置”** 页面。
6. 找到第一项 **“控制流保护（CFG）”**。
7. 检查该功能是否已启用。
8. 如果 CFG 处于关闭状态，将其重新开启或恢复为默认设置。
9. 保存设置后重新启动游戏。

完成上述操作后，再次打开《特战英豪》，Vanguard 反作弊程序即可正常运行，VAN9002 报错通常会消失。


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


