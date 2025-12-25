---
title: Apex英雄启动错误：「请在开始游戏前关闭ACE-BASE」
url: /apex-error-close-ace-base-fix/
date: '2025-03-27 11:09:38 +0800'
description: Apex英雄启动时报错「请在开始游戏前关闭ACE-BASE」，主要由于腾讯ACE与Easy Anti-Cheat（EAC）存在冲突。本文介绍如何使用geek和Everything查找并删除ACE相关文件，从而解决该问题，确保游戏正常运行。
categories:
  - 电脑维修
tags:
  - apex
  - ace
  - eac
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/apex-error-close-ace-base-fix/>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。

## 问题描述  

启动《Apex英雄》时，出现错误提示：「启动错误 请在开始游戏前关闭ACE-BASE」。  

## 问题原因  

该错误是由于腾讯的ACE（Anti-Cheat Expert）与《Apex英雄》主要采用的反作弊系统Easy Anti-Cheat（EAC）存在冲突，导致游戏无法正常启动。ACE可能是由其他游戏或软件安装的，当它与EAC同时运行时，会影响游戏的正常启动。  

## 解决办法  

1. **下载必要工具**  
   - 打开浏览器，访问「zhang9.com」，进入章九工具箱。  
   - 在工具箱搜索「geek」，点击官方网站，下载ZIP文件并保存。  
   - 在工具箱搜索「Everything」，点击官方网站，下载64位便携版并保存。  

2. **检查并删除ACE相关文件**  
   - 打开geek软件，搜索是否存在ACE相关进程，若未找到可忽略此步骤。  
   - 以管理员身份运行命令提示符（CMD），执行系统扫描。  
   - 打开Everything软件，在搜索栏输入「AntiCheatEx」，查找相关文件。  
   - 删除所有搜索到的「AntiCheatEx」相关文件。  

3. **重启计算机并验证**  
   - 删除ACE相关文件后，关闭Everything软件。  
   - 重启计算机，再次尝试启动《Apex英雄》。  
   - 若无其他问题，游戏应可正常进入。  

4. **注意事项**  
   - ACE为某些国内游戏的反作弊系统，若删除后运行相关游戏可能会报错。  
   - 若需使用ACE，可等待系统提示安装时重新同意安装，确保其正常运行。  
   - 确保ACE和EAC均无异常时，二者可以共存，否则可能影响游戏体验。  

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)