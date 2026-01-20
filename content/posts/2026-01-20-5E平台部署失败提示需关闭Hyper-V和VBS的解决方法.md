---
title: '5E平台部署失败提示需关闭Hyper-V和VBS的解决方法'
url: 5e-platform-deployment-fail-requires-disabling-hyper-v-and-vbs
date: 2026-01-20T09:17:19+08:00
description: 打开 5E 平台时出现部署失败和反作弊异常提示，原因是系统开启了 Hyper-V 或 VBS 虚拟化功能。通过关闭相关功能、清理占用虚拟化的软件并进行系统检查，可恢复平台正常运行。
categories:
  - 游戏问题
tags:
  - 部署失败
  - 反作弊异常
  - Hyper-V
  - VBS
  - 5E平台
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/5e-platform-deployment-fail-requires-disabling-hyper-v-and-vbs/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

打开 5E 平台时提示部署失败，并出现反作弊异常提示：

反作弊异常：您的机器需要关闭 hyper-v 和 VBS 相关功能，请根据指引卸载 hyper-v 和关闭 VBS 后重试。

## 问题原因

5E 平台反作弊系统检测到电脑启用了 Hyper-V 和 VBS 等虚拟化相关功能。上述功能会与反作弊驱动产生冲突，导致平台部署失败，无法正常运行。

同时，系统中存在占用虚拟化的第三方软件、异常启动项或恶意程序，也可能引发或加重该问题。

## 解决办法

1. 以管理员身份打开命令行窗口，执行关闭相关虚拟化功能的指令：`bcdedit /set hypervisorlaunchtype off`。
2. 打开 Windows 安全中心 → 进入「设备安全性」→ 点击「内核隔离详细信息」。找到「内存完整性」选项，将其开关切换为 **关闭** 。
3. 打开 appwiz.cpl，进入“程序和功能”，检查是否存在占用虚拟化的程序，如有则卸载或关闭。
4. 进入“启用或关闭 Windows 功能”，取消勾选 Hyper-V，确认并等待系统组件更新完成，暂不重启。
5. 对系统进行全盘病毒扫描，发现威胁后进行隔离处理。
6. 清理多余的开机启动项，卸载无关或垃圾软件。
7. 完成以上操作后重启电脑。
8. 若问题仍存在，将 BIOS 设置恢复为默认状态。


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


