---
title: '关闭Hyper v VBS和内存完整性解决游戏兼容性问题'
url: disable-hyper-v-vbs-hvci-fix-game-compatibility
date: 2026-06-07T10:57:21+08:00
description: 通过关闭 Hyper-V、VBS 和内存完整性（HVCI）功能，解决游戏启动失败、反作弊报错、系统环境异常以及 Hyper-V 冲突等问题。
categories:
  - 游戏问题
tags:
  - Hyper-V
  - VBS
  - HVCI
  - 游戏兼容性
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/disable-hyper-v-vbs-hvci-fix-game-compatibility>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 


## 使用场景

当启动游戏、反作弊程序或虚拟机相关软件时，可能会因为 Windows 的虚拟化安全功能导致兼容性问题，例如：

* 启动游戏提示系统环境异常
* BattlEye、ACE、Easy Anti-Cheat 等反作弊报错
* 提示检测到 Hyper-V 已开启
* 提示开启了虚拟化安全（VBS）
* 提示开启了内存完整性（Memory Integrity）
* 提示存在 Hypervisor（虚拟机监控程序）
* 游戏无法启动或闪退

此时可以尝试关闭 Hyper-V、VBS（基于虚拟化的安全）以及 HVCI（内存完整性）功能。

---

## 执行以下命令

请以**管理员身份运行命令提示符（CMD）**，依次执行以下命令：

```cmd
bcdedit /set hypervisorlaunchtype off

reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v "EnableVirtualizationBasedSecurity" /t REG_DWORD /d 0 /f

reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" /v "Enabled" /t REG_DWORD /d 0 /f
```

执行完成后重启电脑生效。

---

## 命令说明

### 1. 关闭 Hyper-V 虚拟机监控程序

```cmd
bcdedit /set hypervisorlaunchtype off
```

作用：

* 禁止 Windows 启动 Hyper-V Hypervisor
* 阻止系统在开机时加载虚拟化层
* 解决部分反作弊软件检测到 Hyper-V 的问题

对应功能：

* Hyper-V
* Windows Hypervisor Platform
* Virtual Machine Platform

---

### 2. 关闭 VBS（基于虚拟化的安全）

```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v "EnableVirtualizationBasedSecurity" /t REG_DWORD /d 0 /f
```

作用：

* 关闭 Virtualization Based Security（VBS）
* 禁止系统利用虚拟化环境隔离敏感数据
* 避免部分游戏或驱动与 VBS 冲突

注册表位置：

```text
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\DeviceGuard
```

对应键值：

```text
EnableVirtualizationBasedSecurity = 0
```

---

### 3. 关闭 HVCI（内存完整性）

```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" /v "Enabled" /t REG_DWORD /d 0 /f
```

作用：

* 关闭 Hypervisor Enforced Code Integrity（HVCI）
* 即 Windows 安全中心中的“内存完整性”
* 避免驱动程序、反作弊组件与内核保护机制冲突

注册表位置：

```text
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity
```

对应键值：

```text
Enabled = 0
```




## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


