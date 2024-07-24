---
title: 1panel部署wordpress
permalink: /1panel-deployment-wordpress/
date: 2023-12-30 15:42:06
tags: 
  - 网站维护
categories: 
  - 技术笔记
---

_[1Panel在线安装文档](https://1panel.cn/docs/installation/online_installation/)_

## 环境

> 发行版本 ubuntu-20.04 内核版本 5.4.0-28-generic 系统类型 x86\_64

## 安装部署
<!--more-->

```
curl -sSL https://resource.fit2cloud.com/1panel/package/quick_start.sh -o quick_start.sh && sudo bash quick_start.sh
```

安装成功后，控制台会打印面板访问信息，可通过浏览器访问 1Panel：

```
http://目标服务器 IP 地址:目标端口/安全入口
```

## 备份网站

1. 使用word press自带导出功能，导出所有的文章内容：工具→导出
2. 使用1panel备份功能，可以将备份文章内容和一些配置，并可以下载到本地：备份列表→备份
3. 使用1panel快照功能，可以全部本份到第三方网盘：面板设置→快照

## 1panel常用命令

```
Commands: 
1pctl status 查看 1Panel 服务运行状态
1pctl start 启动 1Panel 服务
1pctl stop 停止 1Panel 服务
1pctl restart 重启 1Panel 服务
1pctl uninstall 卸载 1Panel 服务
1pctl user-info 获取 1Panel 用户信息
1pctl listen-ip 切换 1Panel 监听 IP
1pctl version 查看 1Panel 版本信息
1pctl update 修改 1Panel 系统信息
1pctl reset 重置 1Panel 系统信息
1pctl restore 恢复 1Panel 服务及数据
```
