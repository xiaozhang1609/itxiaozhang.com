---
title: '反作弊提示 Please Enable DMA Protection 解决办法'
url: faceit-anti-cheat-please-enable-dma-protection-fix
date: 2026-01-17T09:51:30+08:00
description: 打开 FACEIT 报错 Please enable DMA Protection，原因是系统未启用内核 DMA 保护。通过 BIOS 启用 DMA Protection / IOMMU，并确认安全启动与 TPM 状态后即可恢复正常。
categories:
  - 游戏问题
tags:
  - 游戏
  - FACEIT
  - 反作弊
  - DMA Protection
  - IOMMU
  - 安全启动
  - TPM 2.0
  - DMA保护
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/faceit-anti-cheat-please-enable-dma-protection-fix>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

打开 FACEIT 时，反作弊程序报错：

**FACEIT Anti-cheat：Please enable DMA Protection**

## 问题原因

系统未启用 **内核 DMA 保护**。
虽然 TPM 2.0、BIOS 模式为 UEFI，且安全启动已开启，但内核 DMA Protection 处于关闭状态，导致 FACEIT 反作弊校验失败。

## 解决办法

1. 打开命令行窗口，输入 `tpm.msc`，确认 TPM 2.0 已启用。
2. 在命令行中输入 `msinfo32`，确认：

   * BIOS 模式为 UEFI
   * 安全启动状态为“已开启”
   * 内核 DMA 保护为“关闭”
3. 重启电脑，进入 BIOS，切换到高级模式。
4. 打开 **AMD CBS**（不同主板路径可能略有差异）。
5. 找到与 **DMA Protection / IOMMU** 相关的两个选项，将 **Auto** 改为 **Enable**。
6. 检查安全启动模式，确保为 **Windows UEFI 模式**，状态为正常激活。
7. 保存设置并退出 BIOS。
8. 系统启动后，以管理员身份打开命令行，输入 `msinfo32`，确认 **内核 DMA 保护** 显示为“已启用”。
9. 启动 FACEIT 反作弊程序，报错消失，反作弊状态正常。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


