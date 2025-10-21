---
title: Ubuntu下快速部署多个静态网站（含HTTPS配置）
permalink: /ubuntu-multiple-static-sites-deployment-guide/
date: 2024-11-29 13:30:16
description: 本文介绍如何在Ubuntu服务器上快速部署多个静态网站，通过一个简单的脚本实现自动化配置，并详细说明HTTPS证书的申请步骤。
category:
- 技术笔记
tags:
- 静态网站
- hexo
- 博客
- Ubuntu
- 建站
---

> 原文地址：<https://itxiaozhang.com/ubuntu-multiple-static-sites-deployment-guide/>  

## 环境

- 一台运行 Ubuntu 的服务器（本教程使用 Ubuntu 20.04）
- 已经购买的域名（支持配置多个域名）

## 一句话
教程分为两个主要步骤：第一步执行setup_static_sites.sh脚本，实现nginx安装和多站点的基础HTTP配置；第二步执行certbot相关命令，完成SSL证书申请和HTTPS的配置，

## 1. 准备部署脚本

创建文件 `setup_static_sites.sh`

```bash
#!/bin/bash

# 配置区域 ====================
DOMAINS=(
    "zhang9.com"
    "itxiaozhang.com"
)
WEB_ROOT="/var/www/html"
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"

# 工具函数 ====================
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    log "错误: $1"
    exit 1
}

# 配置单个域名
configure_domain() {
    local DOMAIN=$1
    log "配置域名: $DOMAIN"
    local SITE_ROOT="$WEB_ROOT/$DOMAIN"

    # 检查并创建网站目录
    [ ! -d "$SITE_ROOT" ] && mkdir -p "$SITE_ROOT"
    chown -R www-data:www-data "$SITE_ROOT"
    chmod -R 755 "$SITE_ROOT"

    # 配置Nginx（直接覆盖已存在的配置）
    cat > "/etc/nginx/sites-available/$DOMAIN" << EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    root $SITE_ROOT;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }

    access_log /var/log/nginx/$DOMAIN.access.log;
    error_log /var/log/nginx/$DOMAIN.error.log;
}
EOF

    # 启用配置
    ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/"
}

# 主程序
main() {
    [ "$(id -u)" != "0" ] && error "需要root权限"
    
    # 安装必要软件
    apt update
    apt install -y nginx python3-certbot-nginx

    # 删除默认配置
    rm -f "/etc/nginx/sites-enabled/default"

    # 配置每个域名
    for domain in "${DOMAINS[@]}"; do
        configure_domain "$domain"
    done

    # 检查并重启Nginx
    nginx -t && systemctl restart nginx

    # 输出说明
    log "配置完成！后续步骤:"
    for domain in "${DOMAINS[@]}"; do
        log "1. 上传网站文件到: $WEB_ROOT/$domain/"
    done
}

main
```

## 2. 配置脚本权限并执行

```bash
chmod +x setup_static_sites.sh
sudo ./setup_static_sites.sh
```

## 3. 配置域名解析

在域名管理面板中添加以下记录：

- 记录类型：A记录
- 主机记录：@ 和 www
- 记录值：你的服务器IP
- TTL：600（或默认值）

> 如果使用Cloudflare，请暂时关闭代理（将云朵图标设置为灰色）

## 4. 上传网站文件

将网站文件上传到对应目录。我的文件托管在GitHub，每次有新的提交后，GitHub会同步文件到VPS。  
[GitHub Actions 自动部署：配置 GitHub 仓库指定文件夹到 Ubuntu 服务器](https://itxiaozhang.com/github-actions-sync-specific-folder-to-ubuntu-server-complete-guide/)

## 5. 配置HTTPS

1. 为每个域名申请证书：

```bash
certbot --nginx -d example1.com -d www.example1.com
certbot --nginx -d example2.com -d www.example2.com
```

第一个提示填写自己的邮箱，第二个提示选择选项2，强制HTTPS访问。

2. 验证自动续期：

```bash
certbot renew --dry-run
```

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，点击电脑维修，加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
