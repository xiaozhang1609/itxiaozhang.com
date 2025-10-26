---
title: 如何解决「管理员已阻止你运行此应用」错误（mmc.exe）
permalink: /how-to-fix-admin-blocked-mmc-exe-error/
date: 2025-03-14 09:13:27
description: 本文介绍了如何解决Windows系统中出现的「管理员已阻止你运行此应用」错误，针对mmc.exe文件无法运行的常见原因，提供了注册表修改、组策略调整和防火墙例外设置三种有效的解决方法。
category:
- 电脑维修
tags:
- mmc.exe
- 用户账户控制
- 组策略
---

> 原文地址：<https://itxiaozhang.com/how-to-fix-admin-blocked-mmc-exe-error/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。 

## 问题描述

报错信息：  
用户帐户控制  
为了对电脑进行保护，已经阻止此应用。  
管理员已阻止你运行此应用。有关详细信息，请与管理员联系。  
mmc.exe  
发布者：未知  
文件源：此计算机上的硬盘驱动器  
程序位置："C:\WINDOWS\system32\mmc.exe" C:\WINDOWS\system32\devmgmt.msc  
关闭。

## 问题原因

1. **用户账户控制（UAC）限制**：Windows的用户账户控制可能误判了mmc.exe的安全性，导致其被阻止执行。
2. **注册表或组策略配置错误**：某些注册表项（如EnableLUA、FilterAdministratorToken）被修改，或者组策略设置了管理员批准模式，阻止了mmc.exe的运行。
3. **防火墙或安全软件拦截**：某些防火墙或第三方安全软件可能会误判mmc.exe，并阻止其运行。

## 解决办法

### 方法1：通过注册表修改（推荐）

1. 以管理员身份运行记事本，创建新文件并粘贴以下内容：

   ```
   Windows Registry Editor Version 5.00
   [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System]
   "EnableLUA"=dword:00000000
   "FilterAdministratorToken"=dword:00000001
   ```

2. 保存文件为 `.reg` 格式（如 `fix_mmc.reg`），双击文件导入注册表。
3. 重启计算机，使设置生效。

### 方法2：组策略调整

1. 按 `Win + R`，输入 `gpedit.msc` 打开组策略编辑器。
2. 依次展开：计算机配置 → Windows设置 → 安全设置 → 本地策略 → 安全选项。
3. 修改以下两项：
   - 用户账户控制: 用于内置管理员账户的管理员批准模式 → 设置为已启用。
   - 用户账户控制: 以管理员批准模式运行所有管理员 → 设置为已禁用。
4. 重启计算机。

### 方法3：防火墙例外设置

1. 打开控制面板 → Windows Defender 防火墙。
2. 点击“允许应用或功能通过防火墙”，然后点击“更改设置”。
3. 点击“允许其他应用”，定位到 `C:\Windows\System32\mmc.exe` 并添加。
4. 勾选“专用”和“公用网络”权限，保存后注销系统。

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
