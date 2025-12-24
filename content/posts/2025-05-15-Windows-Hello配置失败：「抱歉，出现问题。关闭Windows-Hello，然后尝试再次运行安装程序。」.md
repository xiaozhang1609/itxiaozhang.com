---
title: Windows Hello配置失败：「抱歉，出现问题。关闭Windows Hello，然后尝试再次运行安装程序。」
url: /windows-hello-error-close-then-try-again/
date: '2025-05-15 20:37:57 +0800'
description: 由于使用内置Administrator账户，Windows Hello功能被禁用。通过创建普通账户可恢复指纹与面部识别设置。
categories:
  - 电脑维修
tags:
  - windows
  - windows hello
  - administrator账户
author: IT小章
---

## 问题描述  

当尝试在Windows设备上配置Windows Hello时，出现以下错误提示：  
「抱歉，出现问题。关闭Windows Hello，然后尝试再次运行安装程序。」  
同时，在 **设置** → **账户** → **登录选项** 中，Windows Hello相关功能（指纹、面部识别等）显示为灰色不可用状态。

## 问题原因  

1. **系统内置的Administrator账户限制**  
   Windows默认禁止内置管理员账户使用Windows Hello功能，出于安全策略考虑，该账户被限制访问生物识别相关设置。  
2. **账户类型不兼容**  
   Windows Hello仅支持普通本地账户或微软账户登录。使用内置Administrator账户登录时，该功能会被禁用。

## 解决办法  

### 步骤1：切换至普通账户或微软账户  

1. **创建新本地账户**  
   - 打开「设置」→「账户」→「家庭和其他用户」→「将其他人添加到这台电脑」。  
   - 选择「我没有此人的登录信息」→「添加一个没有Microsoft账户的用户」。  
   - 输入用户名（如「User01」），点击「下一步」。  

2. **使用新账户登录**  
   - 重启电脑，使用新账户登录系统。  

### 步骤2：配置Windows Hello  

1. **设置PIN码**  
   - 打开「设置」→「账户」→「登录选项」→「PIN」→「添加」。  
   - 输入账户密码，设置PIN码。  

2. **启用Windows Hello**  
   - 返回「登录选项」，点击「指纹识别」或「面部识别」，按提示完成设置。  

### 注意事项  

- 如必须使用Administrator账户，可通过组策略或注册表启用该功能，但不推荐。  
- 请确保硬件驱动已正确安装，设备支持Windows Hello。

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)


> 原文地址：<https://itxiaozhang.com/windows-hello-error-close-then-try-again/>
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 
