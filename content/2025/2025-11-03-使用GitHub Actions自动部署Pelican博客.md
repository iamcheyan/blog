---
title: 使用GitHub Actions自动部署Pelican博客到GitHub Pages
slug: 2025-11-03-使用GitHub Actions自动部署Pelican博客到GitHub Pages
datetime: 2025-11-03 00:00
date: 2025-11-03 00:00
summary: 记录如何将Pelican静态博客部署到GitHub Pages，并通过GitHub Actions实现自动化构建和部署流程。
tags: GitHub Pages GitHub Actions Pelican 博客部署
cover_image_url: 
---

## 背景

想要将现有的Pelican博客从手动部署改为自动化部署，利用GitHub Pages的免费托管和GitHub Actions的自动构建能力。

## 准备工作

### 1. 创建GitHub仓库

首先在GitHub上创建一个新仓库（或使用现有仓库），例如：`iamcheyan/blog`

### 2. 初始化Git仓库

```bash
git init
git remote add origin git@github.com:iamcheyan/blog.git
```

## 配置GitHub Actions

### 创建工作流文件

创建 `.github/workflows/publish.yml` 文件：

```yaml
name: Publish Pelican Blog

on:
  push:
    branches:
      - master
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Build Pelican site
        run: |
          pelican content -s publishconf.py

      - name: Create CNAME file for custom domain
        run: |
          echo "blog.iamcheyan.com" > blog/CNAME

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        if: github.ref == 'refs/heads/master'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./blog
```

## 配置文件调整

### publishconf.py

更新 `publishconf.py` 中的 `SITEURL`，使其指向你的GitHub Pages地址或自定义域名：

```python
# Custom domain: https://blog.iamcheyan.com
SITEURL = 'https://blog.iamcheyan.com'
RELATIVE_URLS = False
```

### .gitignore

确保 `.gitignore` 忽略生成的静态文件目录：

```
# Pelican 生成的静态文件
blog/
output/
```

但保留 `content/` 目录，因为这是源代码。

## 配置自定义域名（可选）

如果你想使用自定义域名（如 `blog.iamcheyan.com`），需要：

1. **在DNS中添加CNAME记录**：
   - 主机记录：`blog`
   - 记录类型：`CNAME`
   - 记录值：`iamcheyan.github.io`

2. **GitHub Actions会自动创建CNAME文件**（已在工作流中配置）

## 启用GitHub Pages

1. 进入仓库的 **Settings** → **Pages**
2. 选择 **Source**: `Deploy from a branch`
3. 选择 **Branch**: `gh-pages`，文件夹：`/ (root)`
4. 在 **Custom domain** 中输入你的域名并保存

## 自动化工作流程

配置完成后，工作流程变得非常简单：

1. **编写文章**：在 `content/` 目录下创建Markdown文件
2. **提交推送**：
   ```bash
   git add content/
   git commit -m "Add new post: 文章标题"
   git push origin master
   ```
3. **自动完成**：
   - GitHub Actions自动触发构建
   - Pelican自动生成静态页面
   - 自动部署到 `gh-pages` 分支
   - 网站自动更新（通常2-5分钟）

## 关键要点

### GitHub Actions的优势

- **免费虚拟机**：GitHub为公开仓库提供免费的构建环境
- **完全自动化**：无需手动操作，推送代码即自动部署
- **环境一致**：每次构建都是全新的干净环境，避免本地环境问题

### gh-pages分支

- `gh-pages` 分支是GitHub Pages专用的发布分支
- GitHub Actions会自动创建和维护这个分支
- 你不需要手动操作这个分支

### CNAME文件

- CNAME文件告诉GitHub Pages使用哪个自定义域名
- 文件必须放在发布目录的根目录（即 `blog/CNAME`）
- GitHub会自动为自定义域名配置SSL证书

## 遇到的问题

### 子模块错误

如果遇到子模块相关的错误，需要：
1. 移除子模块配置：`git rm --cached <submodule-path>`
2. 删除子模块中的 `.git` 目录
3. 重新添加为普通文件

### DNS配置

如果使用自定义域名，确保DNS记录正确配置，并等待DNS生效（通常几分钟到几小时）。

## 总结

通过GitHub Actions自动化部署Pelican博客，大大简化了发布流程：

- ✅ 只需推送代码，无需手动构建
- ✅ 利用GitHub的免费资源（公开仓库完全免费）
- ✅ 支持自定义域名和HTTPS
- ✅ 每次部署都是干净一致的环境

现在，写博客只需要专注于内容创作，技术细节都由自动化流程处理了！

