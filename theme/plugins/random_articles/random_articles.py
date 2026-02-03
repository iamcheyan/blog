# -*- coding: utf-8 -*-

"""
Copyright (c) cheyan (http://iamcheyan.com)
"""

import json
import os.path
import shutil
from pelican import signals

def export_articles(generator):
    articles = []
    for article in generator.articles:
        articles.append({
            'title': article.title,
            'url': article.url,
        })

    # 获取主题所在的路径，以及 static 目录所在的路径
    theme_path = generator.settings.get('THEME')
    # print(f'当前主题所在路径{theme_path}')

    # 生成文件的完整路径
    file_path = os.path.join(theme_path, 'articles.js')
    print(f'> {file_path}')

    with open(file_path, 'w') as f:
        f.write('var articlesData = ')
        json.dump(articles, f)
        f.write(';')

    # 将文件复制到 pelican 的 OUTPUT_PATH 根目录下
    output_path = generator.settings.get('OUTPUT_PATH')
    shutil.copy(file_path, output_path)
    print(f'> {output_path}/articles.js')

def register():
    signals.article_generator_finalized.connect(export_articles)