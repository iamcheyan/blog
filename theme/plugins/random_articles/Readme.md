# Pelican Random Article Loader Plugin 随机加载文章插件
After installing this plugin, Pelican will randomly load the titles and links of 10 articles on each page refresh.  
As the Pelican website is static, in order to implement the functionality of displaying random articles on the page, this plugin first generates a "articles.js" file in the root directory.  
This file includes the titles and links of all the blog articles.  
Then, using "random_articles.js", 10 articles are randomly selected and inserted into the <ul id="random-articles"></ul> element on the page.
Please note that when browsing locally, there may be cross-domain issues preventing the JavaScript from loading. In order to see the effect, it is necessary to access the website through a web environment.

安装本插件后，pelican 会在每次页面刷新时，随机加载10篇文章的标题和链接  
原理：
因为页面是静态的，所以为了实现随机文章，插件会先在根目录生成一个 articles.js
该文件包含了全部日志的标题和链接
再通过 random_articles.js 随机调用 10 篇文章  
插入到页面的 #random-articles 中，实现每次刷新页面加载不同文章的功能  
注意：在本地浏览时因为涉及到跨域问题，所以 js 无法在本地加载，需要通过 web 环境访问才能看到效果

[效果预览：http://iamcheyan.com/](http://iamcheyan.com/)

## Usage
-----
Copy the project folder to the plugin directory of Pelican. 
Copy the random_articles/static folder to the theme directory of your Pelican project. 
In the templates/base.html file, include the newly added JavaScript code: 

把本项目文件夹拷贝到 pelican 的插件目录下 
把 random_articles/static 文件夹拷贝到 pelican 的主题目录下 
在 templates/base.html 中引入刚刚添加的 js 

```html
{# Random Articles #}
<script src="{{ SITEURL }}/theme/js/random_articles.js"></script>
```
In the templates/include/sidebar.html file, add the following HTML structure: 
在 templates/include/sidebar.html 中添加一段 HTML 结构 
```html
<h3>Random</h3>
<ul id="random-articles"></ul>
</nav>
```

## 注意
本仓库`https://github.com/iamcheyan/Pelican-Random-Article-Loader-Plugin.git`是包含在 Pelican 博客主仓库中，做为子模块存在

##  Licence
GNU AFFERO GENERAL PUBLIC LICENSE Version 3

Copyright (c) cheyan (http://iamcheyan.com)