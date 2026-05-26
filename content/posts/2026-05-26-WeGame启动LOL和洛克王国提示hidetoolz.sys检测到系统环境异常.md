---
title: 'WeGame启动LOL和洛克王国提示hidetoolz.sys检测到系统环境异常'
url: wegame-lol-luokewangguo-hidetoolz-sys-system-environment-abnormal-fix
date: 2026-05-26T18:51:33+08:00
description: 通过WeGame启动英雄联盟和洛克王国时，ACE安全中心及反作弊组件提示“hidetoolz.sys检测到系统环境异常”，报错代码(13-131107-3)，导致游戏无法正常启动。
categories:
  - 游戏问题
tags:
  - 游戏问题
  - 驱动不兼容
  - 更新驱动
  - ACE安全中心
  - 英雄联盟
  - 洛克王国
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/wegame-lol-luokewangguo-hidetoolz-sys-system-environment-abnormal-fix/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

WeGame 启动英雄联盟时出现以下报错：

```text
【警告 (13, 131107, 3)】
[hidetoolz.sys]检测到系统环境异常。请关闭并卸载可能影响游戏安全的软件，用杀毒软件进行杀毒清理，重启后重试。
```

通过 WeGame 启动洛克王国时出现以下报错：

```text
【ACE安全中心 [28a20ff026456c6c6c4598]】
检测到系统环境异常。请关闭并卸载可能影响游戏安全的软件，用杀毒软件进行杀毒清理，重启后重试。
hidetoolz.sys
(13-131107-3)
```

两款游戏均因 `hidetoolz.sys` 驱动文件被安全组件判定为异常驱动，导致系统环境检测失败，游戏无法正常启动。

## 问题原因

`hidetoolz.sys` 是系统中加载的驱动文件。

排查过程中发现电脑存在异常驱动文件及安全功能异常现象，系统安全中心无法正常工作。相关驱动可能由恶意程序、病毒或第三方工具安装到系统中，被英雄联盟反作弊系统及 ACE 安全中心识别为存在安全风险，因此触发系统环境异常检测并阻止游戏启动。

## 解决办法

1. 安装杀毒软件并更新病毒库。

2. 执行全盘扫描，对系统进行全面查杀。

3. 以管理员身份打开命令提示符，删除异常驱动对应的系统服务：

   ```cmd
   sc delete hidetoolz
   ```

4. 打开以下目录：

   ```text
   C:\Windows\System32\drivers
   ```

5. 找到异常驱动文件：

   ```text
   hidetoolz.sys
   ```

6. 将文件重命名，例如：

   ```text
   hidetoolz.sys.bak
   ```

   防止系统再次加载该驱动。

7. 等待杀毒软件完成扫描，将发现的病毒或恶意程序全部隔离或删除。

8. 重启电脑，使驱动服务删除及病毒清理结果生效。

9. 打开 WeGame，对英雄联盟执行“修复”。

10. 若检测到文件异常，执行深度修复；未检测到异常则执行快速修复。

11. 对洛克王国执行相同修复操作。

12. 修复完成后重新启动游戏。

13. 英雄联盟反作弊检测及 ACE 安全中心检测恢复正常，游戏可正常启动并进入更新或登录界面。


## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


