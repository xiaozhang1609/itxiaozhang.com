---
title: '启动瓦罗兰特提示VAN INCOMPATIBLE OEM DRIVER检测到mtkwl6ex Sys不兼容需更新驱动后才能运行游戏'
url: valorant-van-incompatible-oem-driver-mediatek-rz616-wifi-6e-adapter-driver-mtkwl6ex-sys/
date: 2026-05-23T17:45:05+08:00
description: 启动 Valorant 时出现报错“VAN INCOMPATIBLE OEM DRIVER”，提示 MediaTek RZ616 Wi-Fi 6E Adapter 驱动文件 mtkwl6ex.sys 不兼容，要求更新 OEM 驱动后才能进入游戏。
categories:
  - 游戏问题
tags:
  - valorant
  - 瓦罗兰特
  - 游戏问题
  - 驱动不兼容
  - 更新驱动


author: IT小章
---

> 原文地址：<https://itxiaozhang.com/valorant-van-incompatible-oem-driver-mediatek-rz616-wifi-6e-adapter-driver-mtkwl6ex-sys/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

启动《Valorant》时弹出反作弊报错窗口，提示：

```text
VAN: INCOMPATIBLE OEM DRIVER

⚠️ Incompatible OEM driver detected ⚠️

MediaTek RZ616 Wi-Fi 6E Adapter Driver - mtkwl6ex.sys

You must update all incompatible OEM drivers in order to play

Press OK to visit our support page for more information:
```

报错信息表明，反作弊系统检测到 `MediaTek RZ616 Wi-Fi 6E Adapter` 无线网卡驱动不兼容，相关驱动文件为 `mtkwl6ex.sys`，必须更新 OEM 驱动后才能正常进入游戏。

检查设备管理器发现，无线网卡驱动日期为 2023 年。同时任务栏中的 ACE（AntiCheatExpert）安全中心图标显示异常状态并带有感叹号。

## 问题原因

《Valorant》反作弊系统会对系统中的部分硬件驱动进行兼容性检测。

当检测到 OEM 驱动版本过旧、存在兼容性问题或未达到反作弊要求时，会触发 `VAN: INCOMPATIBLE OEM DRIVER` 报错，并阻止游戏启动。

本案例中，电脑使用的是 MediaTek RZ616 Wi-Fi 6E Adapter 无线网卡，驱动版本较旧（2023 年版本），被反作弊系统判定为不兼容驱动。更新联想官方提供的 OEM 无线网卡驱动后即可恢复正常。联想官方提供了 Lenovo Quick Fix 驱动安装工具，可自动检测机型并安装适配驱动。([iknow.lenovo.com.cn][1])

## 解决办法

1. 检查任务栏右下角 ACE（AntiCheatExpert）安全中心状态。

2. 如果 ACE 图标显示感叹号或异常状态，可先卸载 ACE 安全中心。

3. 右键开始菜单，打开“设备管理器”。

4. 展开“网络适配器”。

5. 双击 `MediaTek RZ616 Wi-Fi 6E Adapter`。

6. 打开“驱动程序”选项卡，查看当前驱动日期和版本。

7. 右键开始菜单，选择“终端（管理员）”。

8. 输入以下命令并回车：

   ```cmd
   msinfo32
   ```

9. 在“系统信息”窗口中查看电脑品牌和具体型号。

10. 根据电脑型号下载对应厂商提供的驱动更新工具。

11. 本案例为 Lenovo 联想笔记本，使用联想官方驱动安装工具：

[Lenovo Quick Fix 驱动安装工具](https://iknow.lenovo.com.cn/detail/419379?utm_source=chatgpt.com)

12. 打开工具后勾选许可协议。

13. 工具会自动识别当前电脑型号。

14. 点击“查询”，扫描当前设备可更新的驱动程序。

15. 在驱动列表中找到无线网卡驱动更新项目。

16. 安装联想提供的最新 OEM 无线网卡驱动。

17. 更新完成后重新打开设备管理器。

18. 再次查看无线网卡驱动信息，确认驱动已由 2023 年版本升级至更新版本。

19. 关闭所有窗口并重新启动《Valorant》。

20. 游戏再次启动后，不再出现 `VAN: INCOMPATIBLE OEM DRIVER` 报错，可正常进入游戏并稳定运行。


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


