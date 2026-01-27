---
title: 'FACEIT 反作弊 VT SVM 报错怎么办'
url: faceit-anticheat-vt-svm-error-how-to-fix
date: 2026-01-27T09:31:44+08:00
description: '启动 FACEIT 时，反作弊程序报错，无法登录。 关键报错信息如下： FACEIT Anti-cheat：Your PC requires the following settings to be enabled in order to login: Intel VT-x/AMD SVM'
categories:
  - 游戏问题
tags:
  - 游戏
  - FACEIT
  - 反作弊
  - VTD
  - SVM
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/faceit-anticheat-vt-svm-error-how-to-fix>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 


## 问题描述

启动 FACEIT 时，反作弊程序报错，无法登录。  
关键报错信息如下：

FACEIT Anti-cheat：Your PC requires the following settings to be enabled in order to login: Intel VT-x/AMD SVM

## 问题原因

系统未正确启用 CPU 虚拟化相关功能。  
包括但不限于以下情况：

- BIOS 中未开启 AMD SVM（或 Intel VT-x）
- IOMMU / VT-d 未启用
- 内核 DMA 保护处于关闭状态
- 虚拟化相关设置虽部分开启，但未完整配置
- 安全启动未处于“启用 + 标准模式”状态

FACEIT 反作弊对硬件虚拟化、安全启动、TPM 等安全特性有完整校验，任一关键项缺失都会导致报错。

## 解决办法

1. 在系统中确认基础环境  
   - 打开设备管理器，确认 CPU 型号正常识别  
   - 运行 `msinfo32`  
     - BIOS 模式：UEFI  
     - 安全启动状态：启用  
     - BIOS 版本不过旧（过旧需升级）  
   - 运行 `tpm.msc`，确认 TPM 2.0 已开启  

2. 重启电脑并进入 BIOS 设置  

3. 启用 CPU 虚拟化相关选项（AMD 平台）  
   - 进入 **Advanced / Advanced CPU Configuration**  
   - 启用 **SVM Mode（Enable）**

4. 启用 IOMMU  
   - 在 BIOS 设置菜单中找到 **IOMMU**  
   - 设置为 **Enable**

5. 进入 AMD CBS（或同类高级设置）  
   - 找到 **IOMMU** 或相关虚拟化选项  
   - 再次确认设置为 **Enable**  
   - Intel 平台对应选项为 **VT-d**

6. 检查安全启动  
   - 确认 **Secure Boot** 为开启状态  
   - 模式为 **Standard**

7. 保存 BIOS 设置并重启系统  

8. 进入系统后启动 FACEIT  
   - 启动反作弊程序  
   - 根据提示重启电脑一次  
   - 重启后再次启动 FACEIT 并登录  
   - 反作弊状态显示 TPM、安全项均为正常


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


