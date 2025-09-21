---
title: 七彩虹隐星 G16 24 笔记本 Secure Boot 报错 VAN9003 解决方案
permalink: /colorful-g16-24-secure-boot-van9003-fix/
date: 2025-09-04 19:56:22
description: 笔记本在启动港服《瓦罗兰特》时出现 VAN9003 报错，需要启用 Secure Boot，但 BIOS 菜单被隐藏。通过官方 BIOS 升级包刷新 BIOS 并恢复默认设置后，可成功启用 Secure Boot，解决报错问题。
category:
- 电脑维修
tags:
- 七彩虹
- G16 24
- Secure Boot
- BIOS升级
- VAN9003
---

> 原文地址：<https://itxiaozhang.com/colorful-g16-24-secure-boot-van9003-fix/>  
> 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 

## 问题描述

七彩虹隐星 G16 24 笔记本在启动港服《瓦罗兰特》时出现报错：

```
VAN9003 This version of Vanguard requires secure boot to be enabled in order to play. See the Vanguard notification center in the tray for more details.
```

尝试在 BIOS 中开启 Secure Boot 时，又出现报错：

```
Secure boot can be enabled when system in user mode. Repeat operation after enrolling platform key (PK)
```

同时，部分 BIOS 菜单被隐藏，无法直接修改 Secure Boot 设置。

## 问题原因

1. 笔记本出厂设置下，部分高级 BIOS 菜单被隐藏，用户无法直接修改 Secure Boot 相关选项。
2. BIOS 配置未处于用户模式（User Mode），导致启用 Secure Boot 时出现报错。
3. 官方 BIOS 升级包未安装或未正确操作，造成系统无法识别平台密钥（Platform Key，PK）。

## 解决办法

1. **准备工作**

   * 确认笔记本已连接电源适配器，避免中途关机或断电。
   * 下载官方提供的 BIOS 升级包：[QP162.zip](https://nim.nosdn.127.net/MjYxNjUyODA=/bmltYV8yMjQ0OTM5MTMzMzhfMTc1Njk3MTQyMDc5Nl9iZjBiZWI4NS04OTNmLTRhMmEtODdhYy01NWZhMDk3NjM5OTg=?createTime=1756971426412&download=QP162.zip)。

2. **升级 BIOS**

   * 在 Windows 中右击 `NLY_QP162.EXE`，选择「以管理员身份运行」。
   * 按照提示完成 BIOS 刷新操作。升级过程中不要重启或断电。

3. **恢复默认设置**

   * 升级完成后，进入 BIOS，点击「Restore to Default」恢复默认模式。
   * 保存并退出 BIOS，然后再次进入 BIOS。

4. **启用 Secure Boot**

   * 在恢复默认设置后，Secure Boot 菜单将可修改。
   * 按照提示完成平台密钥（PK）的注册，启用 Secure Boot。
   * 保存并退出 BIOS，重启电脑后即可正常启动游戏。

5. **注意事项**

   * 升级 BIOS 存在一定风险，操作前请确保数据已备份。
   * 遵循官方操作指南，避免使用非官方工具或方法强制修改 BIOS。

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
