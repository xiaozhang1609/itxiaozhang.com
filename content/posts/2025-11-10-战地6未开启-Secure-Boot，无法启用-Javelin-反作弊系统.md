---
title: 战地6未开启 Secure Boot，无法启用 Javelin 反作弊系统
url: /battlefield6-javelin-anti-cheat-secure-boot-error/
date: '2025-11-10 17:23:17 +0800'
description: 《战地6》启动时若提示系统未启用 Secure Boot，无法正常启动 Javelin 反作弊系统。本文介绍检查与开启安全启动的方法，帮助解决无法启动的问题。
categories:
  - 电脑维修
tags:
  - 战地6
  - javelin
  - 反作弊
  - secure boot
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/battlefield6-javelin-anti-cheat-secure-boot-error/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。

## 问题描述

启动《战地6》时会出现提示：未开启 Secure Boot，导致无法正常启动 Javelin 反作弊系统，游戏无法进入。

## 问题原因

系统的 Secure Boot（安全启动）被关闭。Javelin 反作弊要求系统处于 Secure Boot 已启用状态，若未开启，反作弊驱动/模块无法初始化，从而阻止游戏启动。TPM 状态正常并不能替代 Secure Boot。

## 解决办法

1. **确认系统信息**

   * 按「Win + R」，输入「msinfo32」并回车。
   * 查看「BIOS 模式」是否为「UEFI」，并确认「安全启动状态」是否为「关闭」。

2. **确认 TPM（可选）**

   * 按「Win + R」，输入「tpm.msc」。
   * 若显示「TPM 已启用」且为「2.0」，无须调整；若未启用，按主板/系统说明启用 TPM。

3. **启用 Secure Boot**

   * 重启进入 BIOS/UEFI 设置（常见按键：F2、Del、F10，依厂商而定）。
   * 切换到「高级模式」，找到「Security（安全性）」或「Boot」项。
   * 将「Secure Boot Control／Secure Boot」设为「Enabled／开启」。
   * 若存在「OS Type」或「Boot Mode」选项，确保使用「UEFI」或「Windows UEFI」模式。
   * 保存并退出（Save & Exit）。

4. **验证与重试**

   * 系统重启后再次运行「msinfo32」，确认「安全启动状态」显示为「已启用」。
   * 启动《战地6》，会出现「正在启动 Javelin 反作弊系统」提示，但此时 Javelin 应能正常加载，游戏可进入。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)