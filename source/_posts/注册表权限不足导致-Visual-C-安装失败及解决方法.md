---
title: 注册表权限不足导致 Visual C++ 安装失败及解决方法
permalink: /fix-visual-cpp-error-1402-registry-permission/
date: 2025-09-28 23:38:47
description: 安装 Microsoft Visual C++ Redistributable 时遇 Error 1402，因注册表关键项权限不足导致。通过 PsExec 提升系统权限修改注册表权限，即可解决安装失败问题。
category:
- 电脑维修
tags:
- 注册表
- 运行库
- PsExec
- Visual C++
---

> 原文地址：<https://itxiaozhang.com/fix-visual-cpp-error-1402-registry-permission/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。

## 问题描述

安装运行库时出现报错：
「Product: Microsoft Visual C++ [版本号] Redistributable - [具体版本号] Error 1402. Could not open key: UNKNOWN\Components[GUID][子键]. System error 5.」

为了解决该问题，需要修改注册表权限。但在操作过程中，系统又提示：
「注册表编辑器无法在当前所选的项及其部分子项上设置安全性」。

## 问题原因

1. Visual C++ 安装失败的根本原因是注册表关键项权限不足，系统错误 5 表示拒绝访问。
2. 使用普通管理员权限修改注册表时，无法对部分系统级注册表项设置安全性。

## 解决办法

1. 下载微软官方的 [PsExec](https://learn.microsoft.com/zh-cn/sysinternals/downloads/psexec) 工具。
2. 解压工具包。
3. 关闭所有已打开的注册表编辑器。
4. 以管理员身份打开命令提示符，进入解压目录：

   * 输入磁盘号（如「D:」）；
   * 输入「cd 文件夹名」进入解压目录。
5. 执行命令：

   ```
   psexec -i -d -s regedit
   ```

   此时以系统权限打开注册表编辑器。
6. 定位到报错提示的注册表路径：
   「UNKNOWN\Components[GUID][子键]」。
7. 右键该项，选择「权限」，为「Administrators」组赋予完全控制权限。
8. 保存设置后，重新运行 Visual C++ 安装程序，即可完成安装。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
