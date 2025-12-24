---
title: 一种解决 Inaccessible Boot Device 蓝屏的方法
url: /solution-inaccessible-boot-device-blue-screen/
date: '2024-12-21 19:40:36 +0800'
description: 本文介绍了解决 Inaccessible Boot Device 蓝屏错误的两种方法：一是在 BIOS 中禁用 Intel VMD（Volume Management Device）功能，二是通过 PE 环境安装 VMD 驱动。
categories:
  - 电脑维修
tags:
  - 蓝屏
  - vmd
author: IT小章
---

## 科普：Intel VMD 与 Inaccessible Boot Device 蓝屏及解决方法

**Intel VMD（Volume Management Device）** 是英特尔推出的技术，旨在优化NVMe SSD的性能与管理。VMD将存储设备直接连接到CPU，通过PCIe总线减少延迟，支持热插拔并简化管理，增强系统的安全性与可靠性。

## **Inaccessible Boot Device 蓝屏**

**inaccessible_boot_device** 蓝屏错误通常发生在系统无法访问启动盘时，常见原因包括：

1. **VMD 驱动未安装**：系统无法识别启用的VMD控制器。
2. **BIOS 配置问题**：VMD在BIOS中启用时，可能导致存储设备无法被正确访问。

## **解决方法**

### 方法一：在 BIOS 中关闭 VMD

1. 进入 BIOS 设置，禁用 VMD 功能。
2. 保存并退出，重启系统，问题解决。

### 方法二：进入 PE 环境安装 VMD 驱动

1. 使用PE工具启动电脑，进入PE环境。
2. 安装VMD驱动后重启，系统正常启动。


> 原文地址：<https://itxiaozhang.com/solution-inaccessible-boot-device-blue-screen/>
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 
