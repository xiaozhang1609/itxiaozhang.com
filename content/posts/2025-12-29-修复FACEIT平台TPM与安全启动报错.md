---
title: '修复FACEIT平台TPM与安全启动报错'
url: fix-faceit-tpm-secure-boot-error-bios-update
date: 2025-12-29T17:50:48+08:00
description: 本文针对 FACEIT 平台提示 TPM 及 Secure Boot 报错的问题，以技嘉 B550M 主板为例，提供了从关闭设备加密、制作 FAT32 格式 BIOS 升级盘，到使用 Q-Flash 刷入固件并开启安全启动的完整解决方案。
categories:
  - 游戏问题
tags:
  - faceit
  - bios
  - 安全启动
  - 技嘉
  - 游戏
  - cs2
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/fix-faceit-tpm-secure-boot-error-bios-update>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

运行 FACEIT 平台（主要用于 CS2、Dota 2 等竞技游戏）时无法正常进入，依次出现以下两条报错信息：

1. **TPM 相关报错**：
   > Warning: TPM attestation is not ready, please upgrade your BIOS.
   > The deadline has passed, and you risk being blocked from playing if you don’t.
   >
   > 警告：TPM 验证未就绪，请升级 BIOS。截止日期已过，若不升级，您将面临被禁止游戏的风险。


2. **安全启动报错**（解决第一个问题后可能出现）：
   > Your PC requires the following settings to be enabled in order to login: Secure Boot.
   >
   > 您的电脑需要启用以下设置才能登录：安全启动（Secure Boot）。



## 问题原因

1. **BIOS 版本过低**：主板当前的 BIOS 版本较旧，导致 TPM（可信平台模块）功能无法通过 FACEIT 反作弊系统的验证。
2. **安全启动未开启**：主板 BIOS 设置中的“安全启动（Secure Boot）”功能处于关闭状态，不符合平台登录的安全要求。

## 解决办法

以技嘉 B550M 主板为例，解决该问题需要升级 BIOS 并开启安全启动。具体步骤如下：

**1. 关闭设备加密（重要）**

* 检查系统是否开启了 BitLocker 或设备加密功能。
* 如果使用的是在线微软账户，务必在“设置”中找到“设备加密”并将其**关闭**。
* **注意**：若不关闭此功能，BIOS 升级后可能导致系统被锁定无法进入。

**2. 准备 BIOS 升级 U 盘**

* 准备一个 U 盘，将其格式化为 **FAT32** 格式。
* **注意**：部分大容量 U 盘在 Windows 下可能默认只支持 exFAT 或 NTFS。若无法选择 FAT32，需使用 DiskGenius 等第三方分区工具删除分区后重新建立为 FAT32 格式，以确保主板 BIOS 能正确识别。

**3. 下载 BIOS 固件**

* 前往主板官网（如技嘉官网），搜索对应主板型号。
* 下载最新的 BIOS 固件文件。
* **提示**：若不确定主板的具体修订版本（如 rev 1.4/1.5/1.7），可将可能适配的几个版本均下载并解压至 U 盘根目录。技嘉 Q-Flash 工具具备自动校验功能，会自动识别并拦截不匹配的固件。

**4. 刷新 BIOS**

* 插入 U 盘，重启电脑并按 **F8** 键进入 Q-Flash 刷机界面。
* 在列表中选择 U 盘内对应的 BIOS 文件，点击确认（Yes）。
* 等待进度条完成更新。
* **警告**：更新过程中绝对不能断电或强制重启。

**5. 开启安全启动**

* BIOS 升级完成后，电脑会自动重启。再次进入 BIOS 设置界面。
* 找到 **Secure Boot（安全启动）** 选项，将其状态修改为 **Enabled（开启）**。
* 保存设置并重启电脑。

完成以上步骤后，再次启动 FACEIT 客户端，校验过程即可通过，能够正常登录并开始游戏。


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


