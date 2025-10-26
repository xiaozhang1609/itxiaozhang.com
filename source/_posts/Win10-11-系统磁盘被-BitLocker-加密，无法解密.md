---
title: Win10/11 系统磁盘被 BitLocker 加密，无法解密
permalink: /win10-11-bitlocker-disk-cannot-decrypt/
date: 2025-09-02 13:37:33
description: Windows 10/11 系统磁盘启用 BitLocker 后加密暂停导致无法解密，本文提供管理员命令操作步骤，恢复加密并完成解密。
category:
- 电脑维修
tags:
- BitLocker
- Windows 10
- Windows 11
- 加密
- BitLocker
---

> 原文地址：<https://itxiaozhang.com/win10-11-bitlocker-disk-cannot-decrypt/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。 

## 问题描述

在 Windows 10/11 系统中，磁盘启用 BitLocker 后异常：

* 设置界面提示「你的加密由 BitLocker 管理」，无法进行操作；
* 尝试关闭 BitLocker 时仅弹出提示窗口并关闭，无进一步选项；
* 使用命令「manage-bde -status C:」查看时，状态显示：

  * 「Conversion Status: Encryption Paused」
  * 「Percentage Encrypted: 98.8%」
  * 「Protection Status: Protection Off」
  * 「Lock Status: Unlocked」
    此时无法继续加密，也无法解密。

## 问题原因

BitLocker 在加密过程中中断，导致驱动器停留在「Encryption Paused」状态。由于加密未完成，系统界面缺少操作选项，用户陷入无法加密完成也无法解密的状态。

## 解决办法

1. **以管理员身份运行命令提示符**

   * 搜索「cmd」→ 右键 →「以管理员身份运行」。

2. **检查磁盘状态**

   * 输入：

     ```
     manage-bde -status C:
     ```

   * 确认「Encryption Paused」。

3. **禁用保护机制**

   * 输入：

     ```
     manage-bde -protectors -disable C:
     ```

4. **恢复加密进程**

   * 输入：

     ```
     manage-bde -resume C:
     ```

5. **确认状态变化**

   * 输入：

     ```
     manage-bde -status C:
     ```

   * 应显示「Encryption in Progress」。

6. **等待加密完成**

   * 持续检查，直到「Percentage Encrypted」为 100%，状态为「Fully Encrypted」。

7. **关闭 BitLocker 解密磁盘**

   * 输入：

     ```
     manage-bde -off C:
     ```

   * 完成后驱动器上的锁标志消失。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
