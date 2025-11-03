---
title: FedoraKDE 下 WinBoat 安装记录
slug: 2025-11-03-安装WInBoat记录-fedora
datetime: 2025-11-03 21:39
date: 2025-11-03 21:39
summary: Fedora（38~43）系统下 WinBoat 从零完整安装流程与实用笔记：依赖准备、Docker/KVM/Wayland 优化、常见问题与快捷脚本全方案。
tags: [Fedora, WinBoat, KVM, Docker, Wayland, 虚拟化, 安装指南]

---

![image](/assets/2025/1762173639427.png)
![image](/assets/2025/1762173645850.png)


---

### 🧩 一、系统要求

WinBoat 是一个基于 Docker + KVM + FreeRDP 的虚拟化系统，要求如下：

| 项目   | 要求               |
| ------ | ------------------ |
| 系统   | Fedora 38–43 (Workstation 推荐) |
| 架构   | x86_64             |
| CPU    | 支持虚拟化 (Intel VT-x / AMD-V) |
| 内存   | ≥ 8 GB             |
| GPU    | 建议开启硬件加速（Wayland / KWin）|
| 权限   | 用户可使用 sudo     |

---

### 🐳 二、安装 Docker 环境（Fedora 特殊步骤）

Fedora 不再提供 docker-ce，改用 moby-engine。

1. 安装 Docker 兼容包
   ```bash
   sudo dnf install -y moby-engine docker-compose
   ```
2. 启动 Docker 服务
   ```bash
   sudo systemctl enable --now docker
   ```
3. 将当前用户加入 docker 组
   ```bash
   sudo groupadd docker 2>/dev/null
   sudo usermod -aG docker $USER
   ```
4. 重新登录（或执行）
   ```bash
   newgrp docker
   ```
5. 验证
   ```bash
   docker run hello-world
   ```
   ✅ 出现 “Hello from Docker!” 表示成功。

---

### 🧠 三、安装 KVM 虚拟化支持

1. 检查 CPU 虚拟化是否启用
   ```bash
   lscpu | grep Virtualization
   ```
   若显示 VT-x 或 AMD-V 即可。

2. 安装 KVM 与相关工具
   ```bash
   sudo dnf install -y @virtualization
   sudo systemctl enable --now libvirtd
   ```
3. 验证
   ```bash
   lsmod | grep kvm
   ```
   输出包含 kvm_intel 或 kvm_amd 表示正常。

---

### 🪟 四、安装 FreeRDP（图形显示组件）

WinBoat 用它来显示 Windows 桌面。
```bash
sudo dnf install -y freerdp
```
Fedora 43 默认版本是 3.x，完全兼容 Wayland。

---

### 📦 五、安装 WinBoat 主程序

**方法一（推荐）：使用官方安装脚本**

GitHub 官方页面/官网命令任选其一：
```bash
curl -fsSL https://winboat.io/install.sh | bash
# 或
curl -fsSL https://raw.githubusercontent.com/WinBoat/installer/main/install.sh | bash
```
*如果脚本报错，可换用方法二手动部署。*

**方法二：从源码 / Docker Compose 手动部署**

1. 克隆仓库
   ```bash
   git clone https://github.com/WinBoat/WinBoat.git
   cd WinBoat
   ```
2. 启动
   ```bash
   docker compose up -d
   ```
3. 浏览器访问
   ```
   http://localhost:8080
   ```

---

### 🧰 六、第一次运行时的前置检查

启动后 WinBoat 会自动检测以下项目：

| 检测项                         | 状态要求         |
| ------------------------------ | --------------- |
| ≥4 GB RAM                      | ✔               |
| ≥2 CPU cores                   | ✔               |
| Virtualization (KVM) enabled   | ✔               |
| Docker installed               | ✔               |
| Docker Compose v2 installed    | ✔               |
| User added to docker group     | ✔（需重新登录） |
| Docker daemon is running       | ✔               |
| FreeRDP 3.x.x installed        | ✔               |

---

### 🖥 七、Wayland 环境兼容优化（推荐 KDE 用户）

Wayland 下默认光标、缩放、撕裂等可能不一致，建议设置以下环境变量：

```bash
export GDK_BACKEND=x11
export XCURSOR_SIZE=48
```
建议加入到 `~/.bashrc` 或 `~/.profile` 永久生效。

---

### 🧩 八、显示缩放设置（HiDPI 屏幕）

WinBoat → Settings → General 中推荐：

- Display Scaling → 180%～200%
- Multi-Monitor Support → None
- RDP Monitoring → Off
- Smartcard Passthrough → Off

适合 4K 屏幕和 Wayland 场景。

---

### 💥 九、常见问题解决

| 问题                 | 解决方式                                                                                                                                   |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Docker daemon 未运行 | `sudo systemctl enable --now docker`                                                                                                       |
| User not in docker group | `sudo usermod -aG docker $USER && newgrp docker`                                                                                   |
| 画面撕裂             | 关闭 KWin 中“允许画面撕裂”；执行：<br>`kwriteconfig6 --file kwinrc --group Compositing --key GLPreferBufferSwap 1`                  |
| RDP 窗口太小         | WinBoat 设置中将 Display Scaling 调至 200%                                                                                                |
| Wayland 光标太小     | 添加环境变量 `XCURSOR_SIZE=48`                                                                                                           |
| 多屏错位             | 设置 Multi-Monitor 为 “None”                                                                                                              |

---

### 🚀 十、启动与使用

1. 打开 WinBoat，选择需要的 Windows 版本（如 Windows 11 LTSC 2024）；
2. 设置内存（建议 4～8GB）与 CPU 核数；
3. 首次运行自动拉取镜像并启动虚拟机；
4. 启动完成后弹出 RDP 窗口连接 Windows 桌面。

---

### 🧭 十一、命令行快捷方式（推荐脚本）

新建脚本 `run-winboat.sh`：

```bash
#!/bin/bash
export XCURSOR_SIZE=48
export GDK_BACKEND=x11
docker start winboat || docker compose up -d
```

保存后执行：
```bash
chmod +x ~/run-winboat.sh
```
下次直接运行 `./run-winboat.sh` 即可自动启动。

---

### ✅ 十二、总结（Fedora 完整安装流程）

```bash
# 1. 安装基础组件
sudo dnf install -y moby-engine docker-compose @virtualization freerdp

# 2. 启动 Docker 与 libvirt
sudo systemctl enable --now docker libvirtd

# 3. 加入 docker 组
sudo usermod -aG docker $USER && newgrp docker

# 4. 下载并启动 WinBoat（推荐）
curl -fsSL https://winboat.io/install.sh | bash

# 5. Wayland 优化（可选）
echo 'export XCURSOR_SIZE=48' >> ~/.bashrc
echo 'export GDK_BACKEND=x11' >> ~/.bashrc

# 6. 修复撕裂（可选）
kwriteconfig6 --file kwinrc --group Compositing --key GLPreferBufferSwap 1
sudo dnf install -y qt6-tools
qdbus org.kde.KWin /KWin reconfigure
```

