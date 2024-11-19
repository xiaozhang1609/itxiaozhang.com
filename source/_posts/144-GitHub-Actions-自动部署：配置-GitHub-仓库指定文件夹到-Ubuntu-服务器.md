---
title: GitHub Actions 自动部署：配置 GitHub 仓库指定文件夹到 Ubuntu 服务器
permalink: /github-actions-sync-specific-folder-to-ubuntu-server-complete-guide/
date: 2024-11-19 23:10:18
description: 本文详细介绍如何使用 GitHub Actions 实现代码自动部署，通过配置 SSH 和 rsync，将 GitHub 仓库中的指定文件夹自动同步到 Ubuntu 服务器。适合需要自动化部署静态网站的开朋友。
category:
- 技术笔记
tags:
- GitHub
- GitHub Actions
- 博客
---

> 原文地址：<https://itxiaozhang.com//github-actions-sync-specific-folder-to-ubuntu-server-complete-guide/>  

### 需求分析

1. **源**：
   - GitHub 仓库：[你的仓库地址]
   - 需同步的文件夹：public/

2. **目标**：
   - 服务器：[服务器IP]
   - SSH 端口：[SSH端口]
   - 用户：[用户名]
   - 目标路径：/var/www/html/[你的域名]

3. **功能要求**：
   - 当 push 到 main 分支时自动部署
   - 只同步 public 文件夹内容
   - 部署前清空目标目录
   - 无需构建步骤
   - 无需部署后操作

### 工作流程

1. 生成新的 public 文件夹中的文件
2. 提交并推送到 GitHub
3. GitHub Actions 自动触发
4. Actions 通过 SSH 连接服务器
5. 清空目标目录
6. 同步新文件到服务器

### 详细教程

#### 1. 服务器配置

```bash
# 1.1 SSH 登录服务器
ssh [用户名]@[服务器IP] -p [SSH端口]

# 1.2 生成 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy"
# 按三次回车，使用默认设置

# 1.3 设置 SSH 目录权限
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 1.4 配置授权
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 1.5 查看私钥（需要复制这个内容）
vim ~/.ssh/id_ed25519
# 使用 y 复制内容
# 使用 :q 退出

# 1.6 创建并设置部署目录
mkdir -p /var/www/html/[你的域名]
chmod 755 /var/www/html/[你的域名]
```

#### 2. GitHub 配置

1. **添加 Repository Secrets**
   - 访问你的 GitHub 仓库的 Settings > Secrets and variables > Actions
   - 点击 "New repository secret"
   - 添加以下 secrets：

     ```
     SERVER_HOST: [服务器IP]
     SERVER_PORT: [SSH端口]
     SERVER_USERNAME: [用户名]
     SERVER_SSH_KEY: [粘贴之前复制的私钥内容]
     DEPLOY_PATH: /var/www/html/[你的域名]
     ```

2. **创建 GitHub Actions 配置**
   - 在仓库中创建 `.github/workflows/deploy.yml`：

```yaml:.github/workflows/deploy.yml
name: Deploy to Server

on:
  push:
    branches: [ main ]
    paths:
      - 'public/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install SSH Key
        uses: shimataro/ssh-key-action@v2
        with:
          key: ${{ secrets.SERVER_SSH_KEY }}
          known_hosts: unnecessary
          if_key_exists: replace
          
      - name: Adding Known Hosts
        run: ssh-keyscan -p ${{ secrets.SERVER_PORT }} -H ${{ secrets.SERVER_HOST }} >> ~/.ssh/known_hosts
      
      - name: Clear target directory
        run: ssh -p ${{ secrets.SERVER_PORT }} ${{ secrets.SERVER_USERNAME }}@${{ secrets.SERVER_HOST }} "rm -rf ${{ secrets.DEPLOY_PATH }}/*"
      
      - name: Deploy with rsync
        run: rsync -avz -e "ssh -p ${{ secrets.SERVER_PORT }}" ./public/ ${{ secrets.SERVER_USERNAME }}@${{ secrets.SERVER_HOST }}:${{ secrets.DEPLOY_PATH }}
```

#### 3. 提交配置

```bash
# 如果是新仓库，先克隆
git clone [你的仓库地址]
cd [仓库名]

# 创建 workflows 目录
mkdir -p .github/workflows

# 创建并编辑配置文件
vim .github/workflows/deploy.yml
# 粘贴上面的配置内容

# 提交更改
git add .github/workflows/deploy.yml
git commit -m "Add deployment workflow"
git push

# 如果遇到 GitHub 认证提示，输入 yes
```

#### 4. 验证部署

1. 访问 GitHub 仓库的 Actions 标签页
2. 应该能看到一个新的 workflow 运行
3. 检查服务器目标目录：

```bash
ls -la /var/www/html/[你的域名]
```

#### 5. 故障排查

如果部署失败：

1. 检查 GitHub Actions 日志
2. 验证 SSH 连接：

```bash
ssh -p [SSH端口] [用户名]@[服务器IP]
```

3. 检查目标目录权限
4. 确认 Secrets 是否正确设置

---
▶ 可以在[关于](https://itxiaozhang.com/about/)或者[这篇文章](https://itxiaozhang.com/about-computer-repair-services-with-me/)找到我的联系方式。
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
