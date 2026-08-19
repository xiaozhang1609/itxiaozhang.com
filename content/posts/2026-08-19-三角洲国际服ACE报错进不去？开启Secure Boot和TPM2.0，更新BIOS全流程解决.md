---
title: '三角洲国际服ACE弹窗警告：Secure Boot和TPM2.0未开启'
url: delta-force-ace-secure-boot-tpm2-fix
date: 2026-08-19T00:00:00+08:00
description: 启动三角洲国际服时弹出ACE Security Center窗口，提示账号需开启Secure Boot和Firmware TPM 2.0才能游戏，点击确定跳转指引连接，游戏无法正常进入。
categories:
  - 游戏问题
tags:
  - delta-force
  - tpm2.0
  - ACE报错
  - 安全启动
  - BIOS更新
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/delta-force-ace-secure-boot-tpm2-fix/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

启动三角洲国际服时，弹出 **ACE Security Center** 警告窗口，提示账号需要开启以下设置才能进行游戏：

```
ACE Security Center

您的账号需要在开启以下设置的情况下才能进行游戏

-Secure Boot enable
-Firmware TPM 2.0 enable

点击"确定"自动跳转指引连接
```

点击「确定」后仅跳转指引链接，游戏无法正常启动或直接退出。

## 问题原因

经过排查，问题可能与以下几项系统设置相关：

1. 磁盘分区格式不是 GPT（GUID 分区表），而是 MBR / Legacy / 传统模式
2. BIOS 模式不是 UEFI，而是 Legacy / 传统模式
3. 安全启动（Secure Boot）状态为关闭
4. 主板 BIOS 版本过旧，可能导致 Firmware TPM 2.0 检测异常

## 解决办法

### 一、检查系统环境

1. 右键 Windows 开始菜单，打开「磁盘管理」。
2. 右键磁盘 → 「属性」 → 「卷」选项卡，查看「磁盘分区形式」：
   - 显示 **GUID 分区表 (GPT)** 即为正常
   - 若显示「主启动记录 (MBR)」或 Legacy / 传统字样，需要转换为 GPT（转换操作涉及数据风险，建议提前备份）
3. 右键 Windows 开始菜单，以管理员身份打开命令提示符，输入：

   ```
   msinfo32
   ```

4. 在「系统信息」界面中重点检查以下三项：
   - **BIOS 模式**：应为 `UEFI`，若显示 Legacy / 传统则需要修改
   - **安全启动状态**：若显示「关闭」则需要后续在 BIOS 中开启
   - **BIOS 版本/日期**：记录当前版本号，稍后对比官网最新版

### 二、下载并更新 BIOS

> 更新 BIOS 存在风险，操作过程中切勿断电或强行关机。如不熟悉操作，建议寻求专业人员协助。

1. 根据主板型号，到官方网站下载最新的 BIOS 固件文件。
2. 准备一个 U 盘，格式化为 **FAT32** 文件系统，U 盘内尽量保持空白。
3. 将下载好的 BIOS 固件文件复制到 U 盘根目录。
4. （使用微软在线账户的用户）打开「设置」 → 「隐私和安全性」，检查是否存在「设备加密」选项，如有则**必须先关闭设备加密**，避免更新 BIOS 后无法进入系统。
5. 重启电脑，进入 BIOS 界面。
6. 在 BIOS 中找到 BIOS 更新/固件升级功能，选择 U 盘中的 BIOS 文件，按照提示确认更新。
7. 更新过程中电脑可能会连续重启多次，期间切勿断电或关机。

### 三、开启安全启动（Secure Boot）

1. BIOS 更新完成并进入系统后，再次重启电脑进入 BIOS。
2. 找到 **Secure Boot**（安全启动）相关选项，一般位于 Boot / Security 分类下。
3. 将 Secure Boot 的值从 `Disable` 修改为 `Enable`。
4. 保存设置并退出 BIOS。

### 四、验证修复结果

1. 进入系统后，重新打开命令提示符，输入：

   ```
   msinfo32
   ```

2. 确认以下状态：
   - BIOS 版本已更新为官网下载的最新版本
   - 安全启动状态显示为「开启」
3. 在命令提示符中输入：

   ```
   tpm.msc
   ```

4. 打开 TPM 管理控制台，确认 TPM 状态正常可用（支持 2.0 版本）。
5. 启动三角洲国际服，ACE Security Center 弹窗不再出现，游戏可正常进入。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)
