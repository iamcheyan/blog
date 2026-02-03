# 澈言的个人博客

这是澈言（iamcheyan）的个人博客源码仓库，使用 Pelican 静态站点生成器构建，并通过 GitHub Actions 自动部署到 GitHub Pages。

**博客地址：** [https://blog.iamcheyan.com](https://blog.iamcheyan.com)

## 技术栈

- **静态站点生成器：** Pelican (Python)
- **部署平台：** GitHub Pages
- **自动化部署：** GitHub Actions
- **自定义域名：** blog.iamcheyan.com

## 项目结构

```
blog.iamcheyan.com/
├── content/          # 博客文章源文件（Markdown）
│   ├── 2007/        # 按年份组织的文章目录
│   ├── 2008/
│   ├── ...
│   └── assets/      # 文章中的图片资源
├── theme/           # Pelican 主题文件
│   ├── templates/   # HTML 模板
│   ├── static/      # CSS、JS 等静态资源
│   └── plugins/     # Pelican 插件
├── .github/
│   └── workflows/
│       └── publish.yml  # GitHub Actions 工作流配置
├── pelicanconf.py   # Pelican 开发环境配置
├── publishconf.py   # Pelican 生产环境配置
├── requirements.txt # Python 依赖包
└── venv/            # Python 虚拟环境（不提交到 Git）
```

## 自动化部署流程

### GitHub Actions 自动构建和部署

当代码推送到 `master` 分支时，GitHub Actions 会自动：

1. **检出代码**：从仓库拉取最新代码
2. **安装依赖**：安装 Python 3.11 和项目依赖
3. **构建静态站点**：运行 `pelican content -s publishconf.py` 生成静态 HTML
4. **创建 CNAME 文件**：自动生成自定义域名配置
5. **部署到 GitHub Pages**：将构建产物部署到 `github-pages` 环境

**工作流程：**
```
推送代码到 master → GitHub Actions 自动触发 → 构建 Pelican 博客 → 部署到 GitHub Pages → 网站自动更新
```

### 发布新文章

1. 在 `content/` 目录下创建 Markdown 文件（按年份组织）
2. 提交并推送：
   ```bash
   git add content/
   git commit -m "Add new post: 文章标题"
   git push origin master
   ```
3. 等待 2-5 分钟，文章会自动发布到网站

## 本地开发环境

### 环境要求

- Python 3.7+ （推荐 Python 3.11）
- 虚拟环境工具（venv 或 conda）

### 设置本地开发环境

#### 方法一：使用 venv（推荐）

`venv` 是 Python 标准的虚拟环境命名，用于隔离项目依赖。

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境（macOS/Linux）
source venv/bin/activate

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

**注意：** 虚拟环境目录 `venv/` 已添加到 `.gitignore`，不会被提交到仓库。

#### 方法二：使用 conda

```bash
# 创建虚拟环境
conda create -n pelican python=3.11
conda activate pelican

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 本地预览

#### 使用 app.py（推荐）

```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux（venv）
# 或
conda activate pelican    # conda

# 一键启动（自动构建 + 自动重载 + 本地服务器）
python app.py -p 8001

# 访问 http://localhost:8001 查看预览
```

#### 手动命令

```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux（venv）
# 或
conda activate pelican    # conda

# 启动开发服务器（自动重载）
pelican content --ignore-cache --autoreload --listen -p 8001

# 访问 http://localhost:8001 查看预览
```

### 本地构建

```bash
# 生成静态文件到 blog/ 目录（开发环境）
pelican content

# 生成静态文件（生产环境配置）
pelican content -s publishconf.py
```

## 编写新文章

### 文章格式

1. **文件命名：** `YYYY-MM-DD-文章标题.md`
2. **存放位置：** `content/YYYY/` 目录（按年份组织）
3. **文件头部：** 包含 Pelican 元数据（Front Matter）

### 文章模板

```markdown
---
title: 文章标题
slug: 2025-01-01-文章标题
datetime: 2025-01-01 00:00
date: 2025-01-01 00:00
summary: 文章摘要
tags: 标签1, 标签2
cover_image_url: 
---

正文内容...
```

### 图片处理

- **图片存放位置：** `content/assets/` 目录
- **引用方式：** `![图片描述](../assets/图片文件名.jpg)`
- **Typora 设置：** 拖拽图片到 Typora 编辑器，会自动使用相对路径

需要在 Typora 里做如下设置

```markdown
![示例图片](../assets/@20240926205808.jpg)
```

如果你使用 Typora 或其他编辑器，也推荐将图片拖入文档，让编辑器自动生成正确的相对路径。

## 配置文件说明

### pelicanconf.py

开发环境配置文件，用于本地预览：
- `RELATIVE_URLS = True`：使用相对 URL，适合本地预览
- `OUTPUT_PATH = 'blog/'`：输出目录

### publishconf.py

生产环境配置文件，用于 GitHub Pages 部署：
- `RELATIVE_URLS = False`：使用绝对 URL
- `SITEURL = 'https://blog.iamcheyan.com'`：生产环境域名
- `DELETE_OUTPUT_DIRECTORY = True`：构建前清空输出目录

## 常用命令

### 方式一：使用 app.py（推荐，最简单）

`app.py` 是一个便捷脚本，可以自动完成构建和启动本地服务器的全部流程。

#### 基本用法

```bash
# 激活虚拟环境
source venv/bin/activate

# 自动构建并启动服务器（默认端口 8000，启用自动重载）
python app.py

# 指定端口
python app.py -p 8001

# 禁用自动重载
python app.py --no-reload

# 跳过构建步骤，直接启动服务器（适用于已构建的情况）
python app.py --skip-build

# 使用生产环境配置构建并启动
python app.py --config publishconf.py
```

#### 完整参数说明

```bash
python app.py [选项]

选项:
  -p, --port PORT       指定服务器端口号（默认: 8000）
  --no-reload          禁用自动重载模式（文件变化时不自动重新构建）
  --skip-build          跳过构建步骤，直接启动服务器
  --config CONFIG       指定 Pelican 配置文件（默认: pelicanconf.py）
  -h, --help           显示帮助信息
```

#### 使用场景

1. **日常开发预览（推荐）**：
   ```bash
   python app.py -p 8001
   ```
   自动构建并启动服务器，文件变化时自动重新构建，最适合日常开发。

2. **快速预览（已构建）**：
   ```bash
   python app.py --skip-build -p 8001
   ```
   如果已经构建过，可以直接启动服务器，节省时间。

3. **生产环境测试**：
   ```bash
   python app.py --config publishconf.py -p 8000
   ```
   使用生产环境配置构建，测试部署前的最终效果。

4. **稳定模式（不自动重载）**：
   ```bash
   python app.py --no-reload -p 8001
   ```
   禁用自动重载，适合在演示或长时间查看时使用。

### 方式二：手动命令

```bash
# 激活虚拟环境
source venv/bin/activate

# 生成静态文件（开发环境）
pelican content

# 本地预览（指定端口，需要先构建）
# 先运行: pelican content
# 然后运行: pelican --listen -p 8001

# 本地预览（自动重载）
# 这会自动构建并监听文件变化
pelican --autoreload --listen -p 8001

# 使用生产配置生成（用于部署）
pelican content -s publishconf.py

# 压缩图片（如果存在脚本）
python compress_images.py
```

## 内容管理工具（目录树 + Markdown 编辑器）

项目内置了一个轻量的内容管理工具，启动后：
- 左侧显示 `content/` 的目录树（只显示 Markdown 文件和文件夹）
- 右侧为 Markdown 编辑器（基于 EasyMDE）
- 右上角有「新建」按钮，可在当前年份目录自动创建带 Front Matter 的新文章

### 启动

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖（需要 Flask）
pip install Flask

# 启动管理工具（默认端口 5000）
python tools/content_manager.py

# 指定端口
python tools/content_manager.py -p 5500

# 访问
open http://127.0.0.1:5000
```

### 使用说明

- 在左侧目录树点击任意 `.md` 文件即可在右侧打开编辑
- 点击「保存」按钮保存当前文件内容
- 点击「新建」会依次询问标题/标签/摘要，并在 `content/<当前年份>/` 下创建
- 新建后的文件会自动加载到编辑器中

注意：若浏览器无法加载 EasyMDE 的 CDN，可替换为本地资源或切换网络。

### 开发服务器警告说明

运行 `pelican --listen` 时如果看到类似这样的警告：
```
WARNING  Unable to find `/theme/css/theme.css` or variations:
```

这是因为开发服务器需要从输出目录（`blog/`）提供静态文件。解决方法：

1. **推荐方式**：使用 `--autoreload` 选项，它会自动构建：
   ```bash
   pelican --autoreload --listen -p 8001
   ```

2. **手动方式**：先构建再启动服务器：
   ```bash
   pelican content          # 先构建
   pelican --listen -p 8001  # 再启动服务器
   ```

这些警告不会影响网站功能，但如果想消除警告，按上述方式操作即可。

## 注意事项

1. **不要提交生成的文件：** `blog/` 目录已添加到 `.gitignore`，不应提交到仓库
2. **虚拟环境：** `venv/` 目录已添加到 `.gitignore`，是标准的 Python 虚拟环境目录，不应提交到仓库
3. **图片优化：** 建议在提交前压缩大图片
4. **文章命名：** 使用英文或拼音，避免特殊字符

## 部署状态

可以在以下位置查看部署状态：

- **GitHub Actions：** [仓库 Actions 页面](https://github.com/iamcheyan/blog/actions)
- **GitHub Pages 设置：** Settings → Pages

## 相关链接

- **博客网站：** https://blog.iamcheyan.com
- **GitHub 仓库：** https://github.com/iamcheyan/blog
- **Pelican 文档：** https://docs.getpelican.com/

---

© Cheyan. All rights reserved.
