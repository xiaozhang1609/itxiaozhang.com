---
title: >-
  港服《瓦罗兰特》启动报错「VAN9003 This version of Vanguard requires secure boot to be
  enabled in order to play」解决方法
permalink: /valorant-van9003-secure-boot-tpm2-fix/
date: 2025-08-08 11:46:50
description: 本文介绍港服《瓦罗兰特》启动时报错 VAN9003 的原因，涵盖 Secure Boot 与 TPM 2.0 的启用方法，帮助用户快速恢复游戏正常运行。
category:
- 电脑维修
tags:
- 瓦罗兰特
- VAN9003
- Secure Boot
- TPM 2.0
---

> 原文地址：<https://itxiaozhang.com/valorant-van9003-secure-boot-tpm2-fix/>  
> 本文配合视频食用效果最佳，视频版本在文章末尾。

## 问题描述

原始报错：「VAN9003 This version of Vanguard requires secure boot to be enabled in order to play. See the Vanguard notification center in the tray for more details.」
该报错出现在启动港服《瓦罗兰特》时，提示必须开启安全启动（Secure Boot）才能运行游戏。

## 问题原因

电脑的安全启动功能（Secure Boot）未开启，或 TPM 2.0 未启用。Vanguard 反作弊系统要求系统在 UEFI 模式下启用 Secure Boot，并检测到 TPM 处于工作状态，才能正常运行游戏。

## 解决办法

### 1. 启用 Secure Boot

* **进入 BIOS/UEFI**

  * 重启电脑并按制造商快捷键：华硕 F2；戴尔 F2/F12；惠普 F10；联想台式机 F1；联想笔记本 F2。
  * 或通过 Windows 高级启动：设置 → 系统 → 恢复 → 高级启动 → UEFI 固件设置。
* **修改 Secure Boot 设置**

  * 在 BIOS 的「Boot」「Security」或「系统配置」标签页，将「Secure Boot」设为 Enabled。
  * 若选项为灰色：先调整「Erase all Secure Boot Settings」或「Restore Secure Boot to Factory Settings」状态（Enabled↔Disabled），保存重启后再启用。
* **验证是否生效**

  * 按「Win + R」，输入「msinfo32」，查看「安全启动状态」是否为开启。

### 2. 启用 TPM 2.0

* **在 BIOS 启用**

  * 在「Security」或「TPM」标签页，启用「TPM 2.0」或「Intel Platform Trust Technology」。
* **Windows 验证**

  * 按「Win + R」，输入「tpm.msc」，确认显示「TPM is ready for use」且规格版本为 2.0。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
