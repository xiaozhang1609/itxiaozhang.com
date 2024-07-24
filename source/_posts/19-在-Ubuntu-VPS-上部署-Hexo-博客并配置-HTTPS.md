---
title: 在 Ubuntu VPS 上部署 Hexo 博客并配置 HTTPS
permalink: /deploy-hexo-blog-on-ubuntu-vps-and-configure-https/
date: 2024-01-02 09:42:06
categories: 
  - 技术笔记
tags: 
  - hexo
---


## 准备工作

### 1. 更新

```bash
apt update && apt upgrade -y
```

### 2. 安装必要工具

安装我们将用到的工具：

```bash
apt install -y vim wget curl unzip git
```

### 3. 安装 Nginx 和 Certbot

```bash
apt install -y nginx certbot python3-certbot-nginx
```

### 4. 安装 Docker 和 Docker Compose

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装 Docker Compose
apt install -y docker-compose
```

## 部署 Hexo 博客

### 1. 准备 Hexo 博客文件

假设您已经在本地机器上创建了 Hexo 博客。使用 SCP 或其他方法将生成的静态文件传输到服务器：

```bash
# 在本地机器上执行
scp -r /path/to/local/hexo/public root@your_server_ip:/var/www/itxiaozhang.com
```

### 2. 配置 Nginx 为 Hexo 博客

创建 Nginx 配置文件：

```bash
vim /etc/nginx/sites-available/itxiaozhang.com
```

添加以下内容：

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

启用配置并检查 Nginx 配置：

```bash
ln -s /etc/nginx/sites-available/itxiaozhang.com /etc/nginx/sites-enabled/
nginx -t
```

### 3. 配置 SSL 证书

使用 Certbot 获取 SSL 证书，但不修改 Nginx 配置：

```bash
certbot certonly --nginx --installer none -d itxiaozhang.com -d www.itxiaozhang.com
```

按照提示完成配置。

### 4. 重启 Nginx

配置完成后，重启 Nginx 服务：

```bash
systemctl restart nginx
```

## 部署 Wallos 应用

### 1. 准备 Wallos 数据目录

```bash
mkdir -p /root/data/docker_data/wallos
cd /root/data/docker_data/wallos
```

### 2. 创建 Docker Compose 配置

使用 vim 创建并编辑 `docker-compose.yml` 文件：

```bash
vim docker-compose.yml
```

添加以下内容：

```yaml
version: '3.0'

services:
  wallos:
    container_name: wallos
    image: bellamy/wallos:latest
    ports:
      - "8282:80/tcp"
    environment:
      TZ: 'Asia/Shanghai'  # 设置为您的时区
    volumes:
      - './db:/var/www/html/db'
      - './logos:/var/www/html/images/uploads/logos'
    restart: unless-stopped
```

### 3. 启动 Wallos 应用

```bash
docker-compose up -d
```

### 4. 配置 Nginx 反向代理

创建 Nginx 配置文件：

```bash
vim /etc/nginx/sites-available/wallos.itxiaozhang.com
```

添加以下内容：

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name wallos.itxiaozhang.com;

    ssl_certificate /etc/letsencrypt/live/wallos.itxiaozhang.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wallos.itxiaozhang.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://localhost:8282;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name wallos.itxiaozhang.com;
    return 301 https://$server_name$request_uri;
}
```

启用配置：

```bash
ln -s /etc/nginx/sites-available/wallos.itxiaozhang.com /etc/nginx/sites-enabled/
nginx -t
```

### 5. 为 Wallos 配置 SSL

使用 Certbot 获取 SSL 证书，但不修改 Nginx 配置：

```bash
certbot certonly --nginx --installer none -d wallos.itxiaozhang.com
```

### 6. 重启 Nginx

配置完成后，重启 Nginx 服务：

```bash
systemctl restart nginx
```

## 完成部署

通过以下地址访问：

- Hexo 博客：<https://itxiaozhang.com>
- Wallos 应用：<https://wallos.itxiaozhang.com>

---
以上是新版本，以下是老版本。

---
> Ubuntu 20.04

1. **安装 Nginx 和 Certbot**
   - 使用 SSH 连接到你的 VPS。
   - 更新软件包列表并安装 Nginx 和 Certbot：

     ```bash
     sudo apt update
     sudo apt install nginx
     sudo apt install certbot python3-certbot-nginx
     ```

2. **配置 Hexo 博客**
   - 在本地搭建并生成 Hexo 博客，确保生成的静态文件位于本地目录中。

3. **将 Hexo 博客同步到 VPS**
   - 使用 SCP 或其他方法将本地生成的 Hexo 博客的静态文件复制到 VPS 上。

4. **申请 SSL 证书**
   - 运行 Certbot 命令申请 SSL 证书：

     ```bash
     sudo certbot certonly --nginx -d itxiaozhang.com -d www.itxiaozhang.com
     ```

   - 按提示提供电子邮件地址并同意服务条款。

5. **创建网站根目录**
   - 在 VPS 上创建存放网站文件的目录：

     ```bash
     sudo mkdir -p /var/www/itxiaozhang.com
     ```

6. **配置 Nginx 反向代理和 SSL**
   - 创建一个新的 Nginx 配置文件：

     ```bash
     sudo vim /etc/nginx/sites-available/itxiaozhang.com
     ```

   - 将以下配置粘贴到文件中：

     ```nginx
     server {
         listen 443 ssl;
         listen [::]:443 ssl;
         server_name itxiaozhang.com www.itxiaozhang.com;

         root /var/www/itxiaozhang.com;  # 替换为你的静态网页文件目录

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

   - 确保替换上述配置中的路径和域名为你的实际路径和域名。

7. **启用 Nginx 配置**
   - 创建符号链接以启用该配置：

     ```bash
     sudo ln -s /etc/nginx/sites-available/itxiaozhang.com /etc/nginx/sites-enabled/
     ```

8. **重新加载 Nginx**
   - 通过以下命令重新加载 Nginx 以应用新配置：

     ```bash
     sudo systemctl reload nginx
     ```
