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

```bash
# 本地预览（自动重载）
pelican --autoreload --listen -p 8001

# 本地预览（指定端口）
pelican --listen -p 8001

# 生成静态文件
pelican content

# 使用生产配置生成
pelican content -s publishconf.py

# 压缩图片（如果存在脚本）
python compress_images.py
```

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

© 2010 - Cheyan. All rights reserved.
