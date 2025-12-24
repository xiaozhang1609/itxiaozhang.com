---
title: 解决「CPU Virtualization Technology 未开启或被占用」弹窗问题
url: /fix-cpu-virtualization-technology-popup-issue/
date: '2025-06-27 22:24:29 +0800'
description: 启动腾讯游戏时出现「ACE安全中心」虚拟化相关报错。本文汇总各大主板开启虚拟化设置方法，并提供关闭HVCI、VBS、Hyper-V等系统占用功能的详细步骤，帮助用户彻底排查并解决弹窗问题。
categories:
  - 电脑维修
tags:
  - cpu虚拟化
  - bios
  - vt-x
  - 腾讯
author: IT小章
---

## 问题描述

报错内容：「ACE安全中心：您的电脑未开启或有其他软件占用CPU虚拟化功能（CPU Virtualization Technology），请重启电脑后进入BIOS开启VT-X/D或AMD-V。并关闭可能占用VT的相关软件或功能。」

## 问题原因

出现该提示通常由以下几种情况引起：

1. BIOS未开启VT-X（Intel）或AMD-V（AMD）虚拟化功能。
2. 虚拟化功能被系统安全组件（如Hyper-V、HVCI、VBS等）占用。
3. 第三方安全软件占用虚拟化接口。
4. 特定厂商BIOS定制化设置影响正常识别。

## 解决办法

请按下列步骤逐一排查与调整：

### 一、开启BIOS虚拟化功能

在开机启动画面出现时，连续按下相应快捷键进入 BIOS 设置，找到并启用 VT 相关选项。

| 主板品牌 | 快捷键          | 设置路径                                                                 |
| ---- | ------------ | -------------------------------------------------------------------- |
| 联想   | F1           | 更多设置 → 高级菜单 → Virtualization技术 + VT-d                                |
| 戴尔   | F2           | BIOS Setup → Virtualization Support                                  |
| 技嘉   | Delete / F12 | BIOS → 芯片组 → VT-d、Intel Virtualization Technology                    |
| 华硕   | Delete / F2  | Advanced → CPU Configuration → Intel Virtualization Technology / SVM |
| 惠普   | F10          | 高级 → 系统选项 → Virtualization Technology                                |
| 微星   | Delete       | OC → CPU Features → Intel VT-d 或 AMD SVM Mode                        |
| 宏碁   | F2           | Main → Enable Intel Virtualization Technology                        |
| 华擎   | F2 / Delete  | Advanced → CPU Configuration → SVM / Intel Virtualization Technology |

操作完成后，按F10保存并重启电脑。

**提示**：不同型号BIOS界面略有不同，如找不到上述选项，请查阅主板说明书或联系厂商支持。

### 二、关闭系统中占用VT的安全功能

1. **关闭HVCI（内存完整性）**
   路径：
   Windows 安全中心 → 设备安全性 → 内核隔离 → 关闭内存完整性。

2. **关闭VBS（内核隔离）**
   操作步骤：

   * 在开始菜单输入「cmd」，右键「以管理员身份运行」
   * 执行命令：

     ```
     bcdedit /set hypervisorlaunchtype off
     ```

   * 回车后重启电脑。

3. **禁用 Hyper-V**
   步骤：
   控制面板 → 程序和功能 → 启用或关闭 Windows 功能 → 取消勾选「Hyper-V」相关项 → 重启电脑。

### 三、排除第三方软件干扰

关闭或卸载如360、安全管家等第三方杀毒工具后，再尝试登录游戏。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


> 原文地址：<https://itxiaozhang.com/fix-cpu-virtualization-technology-popup-issue/>
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 
