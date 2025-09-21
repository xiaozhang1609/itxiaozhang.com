---
title: 桌面图标Bug：Win10/Win11桌面图标占用空间变成长方形怎么办？
permalink: /win10-win11-desktop-icon-bug-rectangular-fix/
date: 2024-05-07 10:32:36
description: 在使用Windows 10或Windows 11操作系统时，桌面图标的间距突然变得很大，变成了长方形。
tags:
    - 桌面图标
    - win10
    - win11
    - 修电脑
category:
    - 电脑维修
---

> 阅读全文：<https://itxiaozhang.com/win10-win11-desktop-icon-bug-rectangular-fix/>  
> 此教程配合视频学习效果最佳，视频教程在文章末尾。  

## 问题描述

在使用Windows 10或Windows 11操作系统时，桌面图标的间距突然变得很大，变成了长方形。该问题通常发生在修改屏幕分辨率、连接外部显示器、频繁缩放后等。

## 解决办法

1. **打开注册表编辑器**  
   - 按下`Win + R`快捷键打开“运行”对话框，输入`regedit`，然后按回车键。在弹出的用户账户控制提示中点击“是”以打开注册表编辑器。

2. **定位到相应键值**  
   - 在注册表编辑器的左侧目录树中，导航至以下路径：  
     `HKEY_CURRENT_USER\Control Panel\Desktop\WindowMetrics`

3. **备份注册表**  

4. **修改图标间距**  
   - 在右侧找到名为`IconSpacing`和`IconVerticalSpacing`的两个键值。  
   - 双击`IconSpacing`，将数值数据改为`-1125`，然后同样操作修改`IconVerticalSpacing`为`-1125`。  
   - 确认更改后关闭注册表编辑器。

5. **注销/重启计算机**  
   - 完成修改后，注销/重启电脑让更改生效。

## 视频教程

- [哔哩哔哩](https://www.bilibili.com/video/BV1u1421r7Ma/)
- [西瓜视频](https://www.ixigua.com/7366195971916726810)

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
