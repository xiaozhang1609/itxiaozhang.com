---
title: 通过修改hosts文件屏蔽主流搜索引擎
permalink: /block-search-engines-windows-hosts/
date: 2025-04-15 19:06:50
description: 本文介绍如何在Windows 10系统中通过hosts文件屏蔽百度、搜狗、360搜索、谷歌等搜索引擎，包括域名列表、修改方法及注意事项。
category:
- 电脑维修
tags:
- hosts
- 搜索引擎
---

> 原文地址：<https://itxiaozhang.com/pinyin/>  
> 本文配合视频食用效果最佳，视频版本在文章末尾。

## 问题描述

用户希望通过修改Windows 10的hosts文件，屏蔽所有主流搜索引擎的访问，特别是适用于中国地区常见的搜索服务。常见域名包括：

「www.baidu.com」「www.sogou.com」「www.so.com」「m.sm.cn」「m.baidu.com」等。

## 问题原因

搜索引擎在国内分布广泛，拥有多个主域名与子域名。仅屏蔽主站可能无法完全限制访问，且部分浏览器可能绕过hosts文件规则。因此需：

- 收集完整的搜索引擎域名；
- 明确覆盖主域名、移动域名及搜索接口域名；
- 禁用浏览器的DoH功能，防止绕过hosts文件。

## 解决办法

1. **备份原始hosts文件**
   - 路径：`C:\Windows\System32\drivers\etc\hosts`
   - 复制文件到桌面等安全位置，备用恢复。

2. **以管理员身份编辑hosts文件**
   - 搜索“记事本” > 右键 > 选择「以管理员身份运行」；
   - 通过「文件 > 打开」进入上述路径，选择hosts文件（需显示所有文件类型）。

3. **添加搜索引擎域名（优化列表）**
   - 在文件末尾添加以下条目（推荐使用0.0.0.0）：

     ```bash
     0.0.0.0 www.baidu.com
     0.0.0.0 baidu.com
     0.0.0.0 m.baidu.com
     0.0.0.0 image.baidu.com
     0.0.0.0 zhidao.baidu.com
     0.0.0.0 www.sogou.com
     0.0.0.0 sogou.com
     0.0.0.0 m.sogou.com
     0.0.0.0 wap.sogou.com
     0.0.0.0 www.so.com
     0.0.0.0 so.com
     0.0.0.0 m.so.com
     0.0.0.0 www.sm.cn
     0.0.0.0 sm.cn
     0.0.0.0 m.sm.cn
     0.0.0.0 www.google.com
     0.0.0.0 google.com
     0.0.0.0 www.bing.com
     0.0.0.0 bing.com
     0.0.0.0 www.yandex.com
     0.0.0.0 yandex.com
     ```

4. **保存文件**
   - 使用`Ctrl + S`保存；
   - 若提示权限问题：右键hosts文件 > 属性 > 安全 > 编辑 > 赋予Users组“完全控制”。

5. **刷新DNS缓存**
   - 打开命令提示符（Win + R 输入`cmd`）；
   - 执行命令：

     ```bash
     ipconfig /flushdns
     ```

6. **测试屏蔽效果**
   - 使用浏览器隐私模式访问上述网址；
   - 显示“无法访问此网站”即为成功屏蔽。

## 视频版本

- [哔哩哔哩](https://space.bilibili.com/3546607630944387)
- [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
