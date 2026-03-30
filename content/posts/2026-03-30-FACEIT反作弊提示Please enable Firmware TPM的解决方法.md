---
title: 'FACEIT反作弊提示Please Enable Firmware TPM的解决方法'
url: faceit-anti-cheat-enable-firmware-tpm-fix
date: 2026-03-30T18:03:26+08:00
description: '启动 FACEIT 反作弊时出现“FACEIT Anti-cheat: Please enable Firmware TPM (fTPM/PTT) to continue.”报错。系统已为 UEFI 且安全启动开启，但仍无法通过检测，提示需启用 TPM 相关功能。'
categories:
  - 游戏问题
tags:
  - FACEIT
  - 反作弊
  - TPM
  - UEFI
  - 安全启动
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/faceit-anti-cheat-enable-firmware-tpm-fix>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

打开 FACEIT 反作弊时弹出报错：

```
FACEIT Anti-cheat: Please enable Firmware TPM (fTPM/PTT) to continue.
```

系统信息中已显示 BIOS 模式为 UEFI，安全启动与内核保护已启用，但仍无法通过反作弊检测。

---

## 问题原因

系统启用了设备加密（BitLocker），在未解除加密的情况下修改 BIOS 安全设置，可能导致 TPM 状态异常或相关功能未完全生效。

同时，主板 BIOS 中 TPM（fTPM/PTT）及 PCH 安全相关选项未开启，导致 FACEIT 反作弊检测失败。

---

## 解决办法

1. **检查系统信息**

   * 打开命令行，输入：

     ```
     msinfo32
     ```
   * 确认：

     * BIOS 模式为 UEFI
     * 安全启动已启用

2. **检查并解除设备加密（BitLocker）**

   * 打开命令行，查看加密状态：

     ```
     manage-bde -status
     ```
   * 若为已加密状态，先暂停保护：

     ```
     manage-bde -protectors -disable C:
     ```
   * 执行解密：

     ```
     manage-bde -off C:
     ```
   * 等待解密完成（状态逐步下降至 0%）

3. **重启进入 BIOS 设置**

   * 重启电脑进入 BIOS
   * 找到以下选项并开启：

   **（1）Trusted Computing**

   * 启用 TPM（fTPM 或 Intel PTT）

   **（2）PCH-FW Configuration**

   * 开启 TPM/PTT 相关安全选项

4. **保存并重启**

   * 保存 BIOS 设置并退出
   * 系统自动重启

5. **验证 FACEIT 反作弊**

   * 启动 FACEIT 客户端并登录
   * 检查提示：

     * TPM 已开启
     * Secure Boot 已开启
     * IOMMU 已开启
   * 出现绿色提示并可点击 “Connect” 表示问题已解决



## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


