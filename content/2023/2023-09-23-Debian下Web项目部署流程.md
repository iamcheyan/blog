---
title: Debian 下 Web 项目部署流程
slug: 2023-09-23-Debian下Web项目部署流程
datetime: 2023-09-23 00:00
date: 2023-09-23 00:00
summary: 记录在 Debian 系统下部署 Web 应用的完整流程，包括 systemd 服务配置、Nginx 反向代理和 SSL 证书配置。
tags: Debian, systemd, Nginx, 运维, 部署
---

本文介绍在 Debian 系统下部署 Web 应用的完整流程，适用于 Python、Node.js 等 Web 服务。

## 前置准备

1. **服务器环境**：Debian 系统（Ubuntu 也适用）
2. **应用已准备好**：代码已上传到服务器，依赖已安装
3. **端口规划**：确定应用运行的端口号

## 1. 创建 systemd 服务

### 创建服务文件

创建 systemd 服务文件，路径：`/etc/systemd/system/<app>.service`

```ini
[Unit]
Description=<App Name> Web App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/www/<app>
ExecStart=/home/ubuntu/miniconda3/envs/<env_name>/bin/python app.py <port>
Restart=always

[Install]
WantedBy=multi-user.target
```

### 配置说明

- **Description**：服务描述
- **User**：运行服务的用户（根据实际情况修改）
- **WorkingDirectory**：应用的工作目录
- **ExecStart**：启动命令
  - 如果使用 conda 环境：`/path/to/miniconda3/envs/<env_name>/bin/python`
  - 如果使用 venv：`/path/to/venv/bin/python`
  - 端口号根据实际需求设置
- **Restart=always**：服务异常退出时自动重启

### 示例（Flask 应用）

```ini
[Unit]
Description=MyBlog Web Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/www/myblog
ExecStart=/home/ubuntu/miniconda3/envs/blog_env/bin/python app.py 5000
Restart=always
Environment="FLASK_ENV=production"

[Install]
WantedBy=multi-user.target
```

## 2. 加载并启用服务

### 加载服务配置

```bash
sudo systemctl daemon-reload
```

### 启用并启动服务

```bash
# 启用服务（开机自启）
sudo systemctl enable <app>

# 启动服务
sudo systemctl start <app>

# 或者同时启用和启动
sudo systemctl enable --now <app>
```

### 检查服务状态

```bash
# 查看服务状态
sudo systemctl status <app>

# 查看服务日志
sudo journalctl -u <app> -f
```

### 如果使用调度任务

如果应用还需要定时任务调度器，可以创建另一个服务：

```bash
sudo systemctl enable --now <app>_scheduler

# 检查状态
sudo systemctl status <app>_scheduler
```

## 3. 配置 Nginx 反向代理

### 创建 Nginx 配置文件

路径：`/etc/nginx/conf.d/<domain>.conf`

```nginx
server {
    listen 80;
    server_name <domain>;

    location / {
        proxy_pass http://127.0.0.1:<port>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 配置说明

- **listen 80**：监听 HTTP 端口
- **server_name**：域名（如 `blog.iamcheyan.com`）
- **proxy_pass**：反向代理到本地应用端口
- **proxy_set_header**：传递必要的请求头信息

### 示例配置

```nginx
server {
    listen 80;
    server_name blog.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 测试并重启 Nginx

```bash
# 测试配置文件语法
sudo nginx -t

# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 或重启 Nginx
sudo systemctl restart nginx
```

## 4. 配置 HTTPS (SSL)

### 安装 Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### 申请 SSL 证书

```bash
sudo certbot --nginx -d <domain>
```

例如：

```bash
sudo certbot --nginx -d blog.example.com
```

### Certbot 自动完成的工作

1. **申请证书**：从 Let's Encrypt 自动申请 SSL 证书
2. **安装证书**：证书保存在 `/etc/letsencrypt/live/<domain>/`
3. **配置 Nginx**：自动修改 Nginx 配置，添加 443 端口监听
4. **配置自动续期**：证书有效期 90 天，Certbot 会自动续期

### 证书自动续期

Certbot 会创建定时任务自动续期，也可以手动测试：

```bash
# 测试自动续期
sudo certbot renew --dry-run
```

### 强制 HTTPS 跳转

Certbot 安装过程中会询问是否强制跳转 HTTP → HTTPS，选择 **Yes** 即可。

或者手动在 Nginx 配置中添加：

```nginx
server {
    listen 80;
    server_name blog.example.com;
    return 301 https://$server_name$request_uri;
}
```

## 5. 验证部署

### 检查服务运行状态

```bash
# 检查 systemd 服务
sudo systemctl status <app>

# 检查端口监听
sudo netstat -tlnp | grep <port>
# 或
sudo ss -tlnp | grep <port>
```

### 测试访问

```bash
# HTTP 访问（应跳转到 HTTPS）
curl http://<domain>

# HTTPS 访问
curl https://<domain>
```

### 检查 SSL 证书

```bash
# 查看证书信息
sudo certbot certificates
```

## 6. 常用管理命令

### systemd 服务管理

```bash
# 启动服务
sudo systemctl start <app>

# 停止服务
sudo systemctl stop <app>

# 重启服务
sudo systemctl restart <app>

# 查看状态
sudo systemctl status <app>

# 查看日志
sudo journalctl -u <app> -f
```

### Nginx 管理

```bash
# 重新加载配置
sudo systemctl reload nginx

# 重启服务
sudo systemctl restart nginx

# 测试配置
sudo nginx -t
```

### SSL 证书管理

```bash
# 查看证书列表
sudo certbot certificates

# 手动续期
sudo certbot renew

# 删除证书
sudo certbot delete --cert-name <domain>
```

## 故障排查

### 服务无法启动

1. **检查日志**：`sudo journalctl -u <app> -n 50`
2. **检查权限**：确保用户有权限访问工作目录和文件
3. **检查端口**：确保端口未被占用
4. **检查路径**：确认 Python 环境和脚本路径正确

### Nginx 502 错误

1. **检查后端服务**：确保应用服务正在运行
2. **检查端口**：确认 proxy_pass 的端口与应用端口一致
3. **检查防火墙**：确保本地端口可访问

### SSL 证书问题

1. **检查域名解析**：确保域名正确解析到服务器 IP
2. **检查防火墙**：确保 80 和 443 端口开放
3. **查看证书**：`sudo certbot certificates`

## 完整示例

假设要部署一个 Flask 博客应用到 `blog.example.com`：

```bash
# 1. 创建 systemd 服务
sudo nano /etc/systemd/system/myblog.service

# 2. 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable --now myblog

# 3. 配置 Nginx
sudo nano /etc/nginx/conf.d/blog.example.com.conf
sudo nginx -t
sudo systemctl reload nginx

# 4. 申请 SSL 证书
sudo certbot --nginx -d blog.example.com

# 5. 验证
curl https://blog.example.com
```

## 总结

在 Debian 下部署 Web 应用的标准流程：

1. ✅ 使用 systemd 管理应用服务（确保服务稳定运行）
2. ✅ 使用 Nginx 作为反向代理（统一入口）
3. ✅ 使用 Certbot 配置 SSL（HTTPS 加密）

这种部署方式具有以下优势：
- **稳定性**：systemd 自动重启失败的服务
- **安全性**：SSL 证书加密传输
- **可维护性**：服务化管理，便于监控和维护
- **扩展性**：易于添加多个服务和管理多域名

