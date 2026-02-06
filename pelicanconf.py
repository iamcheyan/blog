RELATIVE_URLS = True   # True时启用文档相对 URL，如果关闭，则在本地无法正常预览链接文件

AUTHOR = 'cheyan'
SITENAME = 'iamcheyan.com'
SITEURL = 'http://iamcheyan.com/app/pelican/blog'
PATH = 'content'
TIMEZONE = 'Asia/Shanghai'
LOCALE = 'C.UTF-8'  # 设置语言环境为英文
DEFAULT_LANG = 'en'
DEFAULT_PAGINATION = 20 # 每页所列出的文章数量的最大值

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# ARTICLE_URL = '{slug}/index.html'
# ARTICLE_SAVE_AS = '{slug}/index.html'
# PAGE_URL = '{slug}/index.html'
# PAGE_SAVE_AS = '{slug}/index.html'

# 不生成作者页面，因为只有一个作者
AUTHOR_SAVE_AS = ''
AUTHORS_SAVE_AS = ''

# 不生成分类页面，因为统一使用tag
CATEGORY_URL = ''
CATEGORY_SAVE_AS = ''

# 设置tag页为一级目录
TAG_URL = 'tag-{slug}.html'
TAG_SAVE_AS = 'tag-{slug}.html'

# 标签列表页面
TAGS_URL = 'tags.html'
TAGS_SAVE_AS = 'tags.html'

THEME = "theme"    # 主题
OUTPUT_PATH = 'blog/'   # 生成文件的输出位置
STATIC_PATHS = [
                "assets",
                ] # 生成时将img目录拷贝到 output/static/

# 插件
PLUGIN_PATHS = ['theme/plugins/', ]
PLUGINS=['tipue_search',    # 静态搜索
         'sitemap', # 站点地图
         "pelican_comment_system",  # 静态评论
         "neighbors",  # 相邻文章
         "random_articles",  # 随机文章
         # "minify_file",  # 压缩文件
         # "css_html_js_minify",  # 压缩
         # "yuicompressor",  # 在构建步骤中使用 YUI 压缩器最小化 CSS/JS 文件
         # "optimize_images", # 图片压缩
         ]

DIRECT_TEMPLATES = ['index', 'archives', 'search', 'tags']
# YUICOMPRESSOR_EXECUTABLE = 'yui-compressor'

# 静态评论
PELICAN_COMMENT_SYSTEM = True
# PELICAN_COMMENT_SYSTEM_DIR = ['comments',]
PELICAN_COMMENT_SYSTEM_EMAIL_USER = "me@iamcheyan.com"

# 站点地图
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}


# 友情连接
LINKS = (
         ('寒泥', 'http://www.imhan.com'),
         ('钉子の次元', 'http://blog.dimpurr.com/'),
         ('Plumz', 'https://plumz.me/'),
         ('RandyBlog', 'https://lutaonan.com/'),
         ('丁宇 | DING Yu', 'https://dingyu.me/blog'),
         ('Mr.Zan', 'https://mrzan.xyz'),
         ('HOUGE MADNESS BLOG', 'https://litterhougelangley.life/blog'),
         ('S31BZ','https://www.s31bz.com/'),
        )


