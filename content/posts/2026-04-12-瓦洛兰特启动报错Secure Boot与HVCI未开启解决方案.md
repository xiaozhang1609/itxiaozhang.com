---
title: '瓦洛兰特启动报错Secure Boot与HVCI未开启解决方案'
url: valorant-secure-boot-hvci-not-enabled-fix
date: 2026-04-12T09:24:58+08:00
description: 启动瓦洛兰特国际服时报错“Secure Boot not enabled”“HVCI not enabled”，系统信息显示安全启动关闭，导致反作弊无法运行，需开启相关安全与虚拟化功能。
categories:
  - 游戏问题
tags:
  - 瓦洛兰特
  - 启动报错
  - 安全启动
  - 虚拟化
  - 内存完整性
  - 反作弊
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/valorant-secure-boot-hvci-not-enabled-fix>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

启动《瓦洛兰特》国际服时弹窗报错：

* `VAN: RESTRICTION`
* `Your account does not meet the following requirements in order to play:`
* `UEFI Secure boot enabled`
* `HVCI enabled`

## 问题原因

系统未开启 UEFI 安全启动（Secure Boot）及 HVCI（内核隔离/内存完整性），不满足反作弊系统运行要求，从而触发限制报错。

## 解决办法

1. 卸载现有反作弊程序

   * 在系统中找到对应反作弊组件并卸载
   * 完成后关闭窗口

2. 进入 BIOS 开启虚拟化功能

   * 重启电脑，通过 `Delete` 或 `F2` 进入 BIOS
   * 进入 `Advanced` → `CPU Configuration`
   * Intel 主板开启 `Intel Virtualization Technology (VMX)`
   * AMD 主板开启 `SVM Mode`
   * 确保 `VT-d` 已开启

3. 开启安全启动（Secure Boot）

   * 进入 `Boot` → `Secure Boot`
   * 将模式设置为 `Windows UEFI`
   * 启用 Secure Boot
   * 保存并退出

4. 启用 HVCI（内存完整性）

   * 打开“Windows 安全中心” → “设备安全性”
   * 进入“内核隔离”
   * 打开“内存完整性”
   * 如提示不兼容驱动，按提示卸载对应驱动

5. 重启系统验证

   * 打开“系统信息”，确认“安全启动状态”为“已启用”

6. 重新安装反作弊并启动游戏

   * 启动游戏按提示安装反作弊程序
   * 根据提示重启电脑
   * 再次启动游戏即可正常运行


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


