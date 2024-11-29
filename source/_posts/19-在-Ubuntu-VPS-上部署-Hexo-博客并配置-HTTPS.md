---
title: 在 Ubuntu VPS 上部署 Hexo 博客并配置 HTTPS
permalink: /deploy-hexo-blog-on-ubuntu-vps-and-configure-https/
date: 2024-01-02 09:42:06
categories: 
  - 技术笔记
tags: 
  - hexo
---


### 1. **系统准备**
- 更新系统：`apt update && apt upgrade -y`
- 安装必要工具：`apt install -y vim wget curl unzip git`
- 安装 Nginx 和 Certbot：`apt install -y nginx certbot python3-certbot-nginx`
- 安装 Docker 和 Docker Compose：
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  apt install -y docker-compose
  ```

### 2. **部署 Hexo 博客**
- 配置 Nginx：
  创建文件 `/etc/nginx/sites-available/itxiaozhang.com`，添加配置：
  ```nginx
  server {
      listen 443 ssl;
      listen [::]:443 ssl;
      server_name itxiaozhang.com www.itxiaozhang.com;

      root /var/www/itxiaozhang.com;
      index index.html;

      ssl_certificate /etc/letsencrypt/live/itxiaozhang.com/fullchain.pem;
      ssl_certificate_key /etc/letsencrypt/live/itxiaozhang.com/privkey.pem;
      include /etc/letsencrypt/options-ssl-nginx.conf;
      ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

      location / {
          try_files $uri $uri/ =404;
      }
  }

  server {
      listen 80;
      listen [::]:80;
      server_name itxiaozhang.com www.itxiaozhang.com;
      return 301 https://$server_name$request_uri;
  }
  ```
- 获取 SSL 证书：  
  `certbot certonly --nginx --installer none -d itxiaozhang.com -d www.itxiaozhang.com`
- 启用 Nginx 配置：  
  `ln -s /etc/nginx/sites-available/itxiaozhang.com /etc/nginx/sites-enabled/`
- 重启 Nginx：`systemctl restart nginx`

### 3. **访问地址**
- Hexo 博客：`https://itxiaozhang.com`