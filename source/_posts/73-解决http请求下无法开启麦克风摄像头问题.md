---
title: 解决http请求下无法开启麦克风/摄像头问题
permalink: /fixing-microphone-camera-not-working-under-http-request-issue/
date: 2024-01-04 15:42:06
categories: 
  - 电脑维修
tags: 
  - 电脑维修
---

- 打开浏览器，输入 `chrome://flags/#unsafely-treat-insecure-origin-as-secure`。
- 将此选项更改为“Enabled”。
- 在出现的输入框中输入需要访问的地址。若有多个地址，请用逗号分隔。
<!--more-->
- 点击右下角的“Relaunch”按钮，浏览器将自动重启。重启后，您可以在添加的HTTP地址下使用麦克风和摄像头。

*来源：[解决http请求下无法开启麦克风问题\_unsafely-treat-insecure-origin-as-secure-CSDN博客](https://blog.csdn.net/wanghaoyingand/article/details/126336278)_*
