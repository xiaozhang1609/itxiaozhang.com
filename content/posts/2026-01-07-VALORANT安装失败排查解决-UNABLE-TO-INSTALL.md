---
title: 'VALORANT安装失败：UNABLE to INSTALL'
url: valorant-installation-unable-to-install
date: 2026-01-07T12:18:30+08:00
description: 双击打开 VALORANT 安装包时报错，无法继续安装，提示 UNABLE TO INSTALL
categories:
  - 游戏问题
tags:
  - valorant
  - 瓦洛兰特
  - 无畏契约
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/valorant-installation-unable-to-install>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 问题描述

双击打开 VALORANT 安装包时报错，无法继续安装，提示如下：

```
UNABLE TO INSTALL
Something went wrong during installation.
Please try again, and if the error persists restart your computer or contact our player support wizards.
```

## 问题原因

核心原因：Riot SSL 证书过期导致 TLS 验证失败，本地旧会话和 Cookie 与新证书冲突，安装或下载过程无法建立安全连接。

辅助因素：

* 系统时间或时区异常，导致证书校验失败
* 安装包所在路径为中文目录
* 浏览器缓存的站点数据异常

## 解决办法

### 一、基础检查与常规处理

1. 以管理员身份打开命令提示符

2. 打开网络设置，进入以太网属性

3. 暂时关闭 IPv6

4. 手动设置 DNS 为 `8.8.8.8`

5. 保存并关闭所有窗口

6. 右键系统时间 → 调整日期和时间

7. 开启以下选项：

   * 自动设置时间
   * 自动设置时区

8. 确认时间服务器为默认值，点击“立即同步”

9. 检查安装包路径

   * 确保不在中文文件夹中
   * 将安装包移动到纯英文或数字目录（如 `0105`）

10. 重新运行安装程序测试是否恢复正常

### 二、临时解决方案（不推荐长期使用）

1. 关闭自动设置时间与自动设置时区
2. 手动将系统日期修改为 **2026-01-04**
3. 保存后重新运行安装程序

> 该方式仅用于验证问题，属于临时规避手段。

### 三、永久解决方案（推荐）

1. 以管理员身份打开命令提示符
2. 执行以下命令，刷新系统根证书：

```bash
certutil -generateSSTFromWU roots.sst
```

3. 等待命令执行完成并提示成功

4. 确保系统时间同步：

   * 右键系统时间 → 调整日期和时间
   * 开启自动设置时间、自动设置时区
   * 确认时间服务器为默认值，点击“立即同步”

5. 打开浏览器，访问 VALORANT 官网

   * Chrome：点击地址栏图标
   * Edge：点击绿色锁标识

6. 进入「Cookie 和网站数据」

7. 删除与 VALORANT 相关的站点数据

8. 刷新页面并重新下载客户端

9. 将新下载的安装包放入英文或数字目录

10. 双击运行安装程序，正常安装即可



## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


