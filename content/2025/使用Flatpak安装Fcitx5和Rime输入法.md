---
title: 使用 Flatpak 安装 Fcitx5 和 Rime 输入法
slug: 2025-11-03-使用Flatpak安装Fcitx5和Rime输入法
datetime: 2025-11-03 00:00
date: 2025-11-03 00:00
summary: 介绍如何在 Linux 下使用 Flatpak 安装 Fcitx5 输入法框架和 Rime（中州韵）输入法，并详细说明配置方法。
tags: Linux, Flatpak, Fcitx5, Rime, 输入法

---

本文介绍如何在 Linux 系统下使用 Flatpak 安装 Fcitx5 输入法框架和 Rime（中州韵）输入法。Flatpak 版本的 Fcitx5 Rime 由 Fcitx5 的作者亲自维护，包含 librime-lua 依赖，可以避免一些依赖问题。

## 为什么使用 Flatpak 版本

- **维护良好**：Flatpak 版本的 fcitx5-rime 由 Fcitx5 作者维护
- **依赖完整**：包含 librime-lua 依赖，避免编译和依赖问题
- **跨发行版**：不依赖发行版特定的包管理器，通用性更好
- **隔离环境**：Flatpak 应用运行在沙箱环境中，不影响系统其他部分

## 1. 安装 Flatpak

### Debian/Ubuntu 系统

```bash
# 安装 Flatpak
sudo apt update
sudo apt install flatpak

# 添加 Flathub 仓库
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# 如果使用 GNOME 桌面环境，安装 Gnome-Software 的 Flatpak 插件（可选）
sudo apt install gnome-software-plugin-flatpak
```

### 配置国内镜像源（可选）

如果 Flatpak 下载速度慢，可以使用国内镜像源：

```bash
# 使用上海交大镜像（推荐）
flatpak remote-modify flathub --url=https://mirror.sjtu.edu.cn/flathub

# 或者手动添加镜像源
flatpak remote-add --if-not-exists flathub https://mirror.sjtu.edu.cn/flathub
```

重启系统或注销重新登录，使 Flatpak 配置生效。

## 2. 安装 Fcitx5 和 Rime

### 安装 Fcitx5

```bash
flatpak install flathub org.fcitx.Fcitx5
```

### 安装 Fcitx5 Rime 插件

```bash
flatpak install flathub org.fcitx.Fcitx5.Addon.Rime
```

### 验证安装

```bash
# 查看已安装的 Flatpak 应用
flatpak list | grep fcitx
```

应该能看到：
- `org.fcitx.Fcitx5`
- `org.fcitx.Fcitx5.Addon.Rime`

## 3. 配置环境变量

为了让系统应用程序能够使用 Fcitx5，需要设置环境变量。

### 方法一：使用 `.pam_environment`（推荐）

创建或编辑 `~/.pam_environment` 文件：

```bash
nano ~/.pam_environment
```

添加以下内容：

```
GTK_IM_MODULE DEFAULT=fcitx
QT_IM_MODULE  DEFAULT=fcitx
XMODIFIERS    DEFAULT=@im=fcitx
```

这种方式在系统级别设置环境变量，对所有用户会话都有效。

### 方法二：使用 `.xprofile`（X11 环境）

如果使用 X11 显示服务器，可以在 `~/.xprofile` 中添加：

```bash
nano ~/.xprofile
```

添加以下内容：

```bash
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx

# 启动 Fcitx5（Flatpak 版本）
flatpak run org.fcitx.Fcitx5 &
```

### 方法三：使用 `.profile` 或 `.bashrc`（终端环境）

如果只在终端环境中需要，可以添加到 `~/.profile` 或 `~/.bashrc`：

```bash
nano ~/.profile
```

添加：

```bash
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
```

## 4. 启动 Fcitx5

### 手动启动

```bash
# 启动 Flatpak 版本的 Fcitx5
flatpak run org.fcitx.Fcitx5

# 或者后台运行
flatpak run org.fcitx.Fcitx5 &
```

### 自动启动

#### 使用 systemd 用户服务（推荐）

创建服务文件 `~/.config/systemd/user/fcitx5.service`：

```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/fcitx5.service
```

添加以下内容：

```ini
[Unit]
Description=Fcitx5 Input Method Framework
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/flatpak run --branch=stable --arch=x86_64 --command=fcitx5 org.fcitx.Fcitx5
Restart=on-failure

[Install]
WantedBy=default.target
```

启用并启动服务：

```bash
# 重新加载 systemd 用户配置
systemctl --user daemon-reload

# 启用服务（开机自启）
systemctl --user enable fcitx5.service

# 启动服务
systemctl --user start fcitx5.service

# 查看状态
systemctl --user status fcitx5.service
```

#### 使用桌面环境自动启动

对于 GNOME、KDE 等桌面环境，可以在"启动应用程序"中添加：

**命令：**
```bash
flatpak run org.fcitx.Fcitx5
```

**工作目录：** 留空或设置为 `$HOME`

## 5. 配置 Fcitx5

### 打开配置工具

```bash
# 使用 Flatpak 版本的配置工具
flatpak run org.fcitx.Fcitx5 org.fcitx.Fcitx5 -c

# 或者直接运行（如果已启动 Fcitx5）
fcitx5-configtool
```

### 添加 Rime 输入法

1. 打开 Fcitx5 配置工具
2. 点击 **"输入法"** 标签
3. 点击下方的 **"+"** 按钮
4. 取消勾选 **"只显示当前语言"**
5. 在列表中找到 **"Rime"** 并添加
6. 点击 **"确定"** 保存

### 配置快捷键

在 Fcitx5 配置工具的 **"全局选项"** 中可以设置：

- **切换激活/非激活：** 默认 `Ctrl+Space`
- **切换到上一个输入法：** 默认 `Shift+Shift`
- **切换到下一个输入法：** 默认 `Ctrl+Shift`

## 6. 配置 Rime 输入法

### Rime 配置目录

Flatpak 版本的 Rime 配置目录位于：

```bash
~/.var/app/org.fcitx.Fcitx5/config/fcitx5/rime/
```

### 初始化 Rime

首次使用时，Rime 会自动创建默认配置。如果需要手动初始化：

```bash
# 进入 Rime 配置目录
cd ~/.var/app/org.fcitx.Fcitx5/config/fcitx5/rime/

# 运行部署工具（如果存在）
# 或者直接重启 Fcitx5
```

### 配置输入方案

编辑 `default.custom.yaml` 文件来自定义输入方案：

```bash
nano ~/.var/app/org.fcitx.Fcitx5/config/fcitx5/rime/default.custom.yaml
```

示例配置：

```yaml
patch:
  # 默认输入方案列表
  schema_list:
    - schema: luna_pinyin          # 朙月拼音
    - schema: luna_pinyin_simp     # 朙月拼音·简化字
    - schema: double_pinyin_flypy  # 小鹤双拼
    - schema: wubi_pinyin          # 五笔拼音混输
  
  # 切换输入方案的快捷键
  switcher:
    save_options:
      - full_shape
      - ascii_mode
      - simplification
      - extended_charset
```

### 常用 Rime 输入方案

| 输入方案 | 说明 | 适合人群 |
|---------|------|---------|
| `luna_pinyin` | 朙月拼音（全拼） | 习惯拼音的用户 |
| `double_pinyin_flypy` | 小鹤双拼 | 双拼用户 |
| `wubi_pinyin` | 五笔拼音混输 | 五笔用户 |
| `cangjie5` | 仓颉五代 | 仓颉用户 |

### 重新部署 Rime

修改配置后需要重新部署：

```bash
# 方法一：在 Fcitx5 托盘图标右键选择"重新部署"
# 方法二：使用命令行
flatpak run org.fcitx.Fcitx5 fcitx5-remote -r
```

或者重启 Fcitx5：

```bash
# 停止 Fcitx5
flatpak run org.fcitx.Fcitx5 fcitx5-remote -e

# 启动 Fcitx5
flatpak run org.fcitx.Fcitx5 &
```

## 7. 验证和测试

### 检查 Fcitx5 状态

```bash
# 检查 Fcitx5 是否运行
flatpak run org.fcitx.Fcitx5 fcitx5-diagnose

# 或者
ps aux | grep fcitx5
```

### 测试输入法

1. 打开任意文本编辑器（如 Gedit、Firefox 浏览器等）
2. 按 `Ctrl+Space` 切换到 Fcitx5 输入法
3. 尝试输入中文，应该能看到 Rime 输入法的候选词

### 常见问题排查

#### 输入法无法切换

1. **检查环境变量：**
   ```bash
   echo $GTK_IM_MODULE
   echo $QT_IM_MODULE
   echo $XMODIFIERS
   ```
   应该显示 `fcitx`

2. **检查 Fcitx5 是否运行：**
   ```bash
   flatpak run org.fcitx.Fcitx5 fcitx5-diagnose
   ```

3. **重启 Fcitx5：**
   ```bash
   flatpak run org.fcitx.Fcitx5 fcitx5-remote -r
   ```

#### 某些应用无法使用输入法

某些应用（特别是 Flatpak 应用）可能需要额外配置：

```bash
# 为 Flatpak 应用配置输入法
flatpak override --env=GTK_IM_MODULE=fcitx --env=QT_IM_MODULE=fcitx --env=XMODIFIERS=@im=fcitx --user
```

#### 配置不生效

1. **注销并重新登录**（推荐）
2. **重启系统**
3. **检查配置文件语法**（YAML 文件对缩进敏感）

## 8. 高级配置

### 自定义主题

Fcitx5 支持多种主题，可以通过配置工具在 **"外观"** 标签中选择。

### 词库管理

Rime 支持自定义词库，可以在配置目录中添加：

```bash
# 词库文件位置
~/.var/app/org.fcitx.Fcitx5/config/fcitx5/rime/
```

### 同步配置

可以将 Rime 配置目录同步到其他设备：

```bash
# 备份配置
cp -r ~/.var/app/org.fcitx.Fcitx5/config/fcitx5/rime/ ~/fcitx5-rime-backup/

# 恢复配置
cp -r ~/fcitx5-rime-backup/* ~/.var/app/org.fcitx.Fcitx5/config/fcitx5/rime/
```

## 9. 卸载（如果需要）

```bash
# 卸载 Fcitx5 Rime 插件
flatpak uninstall org.fcitx.Fcitx5.Addon.Rime

# 卸载 Fcitx5
flatpak uninstall org.fcitx.Fcitx5

# 删除配置（可选）
rm -rf ~/.var/app/org.fcitx.Fcitx5/
rm -f ~/.pam_environment
```

## 总结

使用 Flatpak 安装 Fcitx5 和 Rime 的优势：

- ✅ **安装简单**：不需要编译，直接安装
- ✅ **依赖完整**：包含所有必要的依赖
- ✅ **维护良好**：由官方维护
- ✅ **跨发行版**：在大多数 Linux 发行版上都可用

配置要点：

1. ✅ 正确设置环境变量
2. ✅ 配置自动启动
3. ✅ 添加 Rime 输入法
4. ✅ 自定义输入方案

按照以上步骤，你就能在 Linux 系统上使用功能强大的 Fcitx5 + Rime 输入法组合了。

---

**参考资源：**

- [Fcitx5 官方文档](https://fcitx-im.org/)
- [Rime 输入法官网](https://rime.im/)
- [Flatpak 官方文档](https://flatpak.org/)

