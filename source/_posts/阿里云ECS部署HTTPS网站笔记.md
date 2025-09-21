---
title: 阿里云ECS部署HTTPS网站笔记
permalink: /aliyun-ecs-https-deployment-notes/
date: 2025-08-26 18:57:46
description: 本文记录了在阿里云ECS上部署HTTPS网站的全过程，包括环境准备、网页与证书上传、Nginx配置、验证及常见故障排查。
category:
- 技术笔记
tags:
- 阿里云
- ECS
- HTTPS
- Nginx
- SSL证书
---

> 原文地址：<https://itxiaozhang.com/aliyun-ecs-https-deployment-notes/>  
> 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 

## 一、服务器与环境准备

```bash
ssh root@<your-server>   # 登录服务器

sudo apt update && sudo apt upgrade -y
sudo apt install nginx -y

sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

## 二、上传网页与证书

### 1. 新建目录

```bash
sudo mkdir -p /var/www/html
sudo mkdir -p /etc/nginx/ssl
```

### 2. 上传文件

* 使用 **WindTerm** 上传网页文件到 `/var/www/html/`
* 使用 **WindTerm** 上传证书文件到 `/etc/nginx/ssl/`：

  * `24xiu.cn.pem`
  * `24xiu.cn.key`

### 3. 设置权限

```bash
sudo chmod 600 /etc/nginx/ssl/*
```

---

## 三、配置 Nginx

```bash
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
sudo vim /etc/nginx/sites-available/default
```

配置内容：

```nginx
# HTTP → HTTPS
server {
    listen 80;
    server_name 24xiu.cn www.24xiu.cn;
    return 301 https://$host$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name 24xiu.cn www.24xiu.cn;

    ssl_certificate /etc/nginx/ssl/24xiu.cn.pem;
    ssl_certificate_key /etc/nginx/ssl/24xiu.cn.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

## 四、验证

```bash
sudo nginx -t
sudo systemctl restart nginx
curl -I https://24xiu.cn
```

---

## 五、常见排查要点

1. **Nginx 状态**

   ```bash
   sudo nginx -t
   systemctl status nginx
   ```

2. **证书有效性**

   ```bash
   openssl x509 -in /etc/nginx/ssl/24xiu.cn.pem -noout -dates
   ```

3. **安全组**
   确认放行：

   * TCP 22
   * TCP 80
   * TCP 443

---

## 六、后续维护

* 证书到期后，在阿里云控制台续签并下载新证书（本次过期时间：2025-11-24）
* 覆盖 `/etc/nginx/ssl/24xiu.cn.pem` 和 `/etc/nginx/ssl/24xiu.cn.key`
* 重启 Nginx `sudo systemctl restart nginx`

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)

---
▶ 远程修电脑，请访问 [章九工具箱](https://zhang9.com/)，选择「电脑维修（国内）」或「电脑维修（海外）」加我微信咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
