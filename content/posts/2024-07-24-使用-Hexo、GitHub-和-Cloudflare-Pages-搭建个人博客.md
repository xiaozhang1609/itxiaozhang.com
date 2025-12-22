---
title: 使用 Hexo、GitHub 和 Cloudflare Pages 搭建个人博客
url: /building-personal-blog-with-hexo-github-cloudflare-pages/
date: '2024-07-24 22:38:03 +0800'
description: 这篇文章记录我使用 Hexo、GitHub 和 Cloudflare Pages 搭建个人博客，记录如何安装和配置 Hexo，如何通过 SSH 将项目推送到 GitHub，以及如何在 Cloudflare Pages 部署博客并设置自定义域名。
categories:
  - 技术笔记
tags:
  - hexo
  - 博客
  - cloudflare
author: IT小章
---
> 原文地址：<https://itxiaozhang.com/building-personal-blog-with-hexo-github-cloudflare-pages/>  

## 一、安装 Node.js

1. **下载 Node.js 安装包**
   - 前往 Node.js 官网 [https://nodejs.org/](https://nodejs.org/)，点击“LTS”按钮下载最新的 LTS 版本。

2. **安装 Node.js**
   - 双击下载的安装包，按照提示进行安装。默认选择即可。安装完成后，会自动安装 Node.js 和 npm（Node.js 的包管理工具）。
   - 安装完成后，打开命令提示符（可以通过按 `Win + R`，输入 `cmd`，然后按回车键打开），输入以下命令检查 Node.js 和 npm 是否安装成功：

     ```bash
     node -v
     npm -v
     ```

   - 你应该会看到 Node.js 和 npm 的版本号。

## 二、安装和配置 Hexo

1. **安装 Hexo CLI**
   - 在命令提示符中输入以下命令安装 Hexo CLI：

     ```bash
     npm install -g hexo-cli
     ```

2. **初始化 Hexo 项目**
   - 在命令提示符中，切换到你想要存放博客文件的目录，例如 `D:\Blogs`：

     ```bash
     cd /d D:\Blogs
     ```

   - 初始化 Hexo 项目：

     ```bash
     hexo init my-blog
     cd my-blog
     npm install
     ```

3. **生成静态文件并测试**
   - 在命令提示符中输入以下命令生成静态文件：

     ```bash
     hexo generate
     ```

   - 启动本地服务器进行测试：

     ```bash
     hexo server
     ```

   - 打开浏览器，访问 [http://localhost:4000/](http://localhost:4000/) 以查看生成的博客页面。

4. **取消忽略 `public` 目录**
   - 打开 `D:\Blogs\my-blog` 目录，找到并编辑 `.gitignore` 文件，删除 `public/` 这一行，使 `public` 目录不再被忽略。

## 三、使用 SSH 链接 GitHub

1. **生成 SSH 密钥对**
   - 打开 Git Bash（如果没有请自行安装），输入以下命令生成 SSH 密钥对：

     ```bash
     ssh-keygen -t rsa -b 4096 -C "xiaozhang@example.com"
     ```

   - 按照提示操作，默认路径即可（按 3 次回车），生成的密钥对通常保存在 `C:\Users\YourUsername\.ssh` 目录中。

2. **将公钥添加到 GitHub**
   - 打开文件资源管理器，导航到 `C:\Users\YourUsername\.ssh`，用记事本打开 `id_rsa.pub` 文件，复制文件内容。
   - 登录 GitHub，进入 `Settings` > `SSH and GPG keys`，点击 `New SSH key`，将公钥粘贴进去并保存。

3. **验证 SSH 链接成功**
   - 在 Git Bash 中输入以下命令验证与 GitHub 的连接：

     ```bash
     ssh -T git@github.com
     ```

   - 如果连接成功，你将看到类似以下的输出：

     ```plaintext
     Hi xiaozhang! You've successfully authenticated, but GitHub does not provide shell access.
     ```

   - 如果看到这条信息，说明 SSH 连接配置成功。

## 四、创建 GitHub 仓库

1. **登录 GitHub 并创建一个新的仓库**
   - 登录 GitHub，点击右上角的“+”，选择 `New repository`，创建一个新的仓库。
   - 仓库名（随便起）：`xiaozhang.github.io`
   - 仓库类型：Public

2. **在本地仓库中添加 GitHub 远程仓库**
   - 打开命令提示符，导航到 Hexo 项目目录：

     ```bash
     cd /d D:\Blogs\my-blog
     ```

   - 初始化 Git 并添加远程仓库：

     ```bash
     git init
     git remote add origin git@github.com:xiaozhang/xiaozhang.github.io.git
     ```

3. **将整个项目文件夹推送到 GitHub 的 `main` 分支**
   - 首先，确保 `.gitignore` 文件已经配置好，以便包括 `public` 目录中的内容。然后，执行以下命令：

     ```bash
     git add .
     git commit -m "Initial commit"
     git branch -M main
     git push -u origin main
     ```

## 五、配置 Cloudflare Pages

1. **登录 Cloudflare 并创建一个 Pages 项目**
   - 登录 Cloudflare，进入 Dashboard，点击 `Pages`，然后点击 `Create a project`。
   - 选择 `Connect to Git`，并连接到你在 GitHub 上的仓库 `xiaozhang.github.io`。
   - 选择 `main` 分支作为构建分支。

2. **配置 Cloudflare Pages**
   - 在设置页面中，将 “Output Directory” 设为 `public`。其他设置保持默认即可。

## 六、配置自定义域名

1. **在 Cloudflare 上添加域名**
   - 登录 Cloudflare，进入 Dashboard，点击 `Add a Site`，添加域名。

2. **配置 DNS 记录**
   - 在 Cloudflare 的 DNS 管理页面中，添加一条 CNAME 记录，指向 Cloudflare Pages 的默认域名（如 `xiaozhang.github.io`）。

3. **在 Cloudflare Pages 上配置自定义域名**
   - 进入 Cloudflare Pages 项目的设置页面，找到 `Custom Domains`，添加自定义域名。

---

> 备注：
> sticky: true  # 添加这一行来置顶文章，有些主题可能需要特定的格式或数值

---
▶ 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
