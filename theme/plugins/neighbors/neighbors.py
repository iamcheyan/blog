# -*- coding: utf-8 -*-
"""
Neighbor Articles Plugin for Pelican
====================================

This plugin adds ``next_article`` (newer) and ``prev_article`` (older)
variables to the article's context
"""
from pelican import signals


def iter3(seq):
    """Generate one triplet per element in 'seq' following PEP-479."""
    nxt, cur = None, None
    for prv in seq:
        if cur:
            yield nxt, cur, prv
        nxt, cur = cur, prv
    # Don't yield anything if empty seq
    if cur:
        # Yield last element in seq (also if len(seq) == 1)
        yield nxt, cur, None


def get_translation(article, prefered_language):
    if not article:
        return None
    for translation in article.translations:
        if translation.lang == prefered_language:
            return translation
    return article


def set_neighbors(articles, next_name, prev_name):
    for nxt, cur, prv in iter3(articles):
        setattr(cur, next_name, nxt)
        setattr(cur, prev_name, prv)

        for translation in cur.translations:
            setattr(translation, next_name,
                    get_translation(nxt, translation.lang))
            setattr(translation, prev_name,
                    get_translation(prv, translation.lang))

def neighbors(generator):
    # Pelican 的 generator.articles 已经是按日期排序的，直接使用
    # 但为了避免修改原始列表，创建一个副本
    articles_list = list(generator.articles)
    set_neighbors(articles_list, 'next_article', 'prev_article')

    for category, articles in generator.categories:
        # 确保按日期排序，使用安全的排序方法
        try:
            articles.sort(key=lambda x: x.date if hasattr(x, 'date') and x.date is not None else None, reverse=True)
        except (TypeError, AttributeError):
            # 如果排序失败，跳过该分类
            continue
        set_neighbors(
            articles, 'next_article_in_category', 'prev_article_in_category')

    if hasattr(generator, 'subcategories'):
        for subcategory, articles in generator.subcategories:
            # 确保按日期排序，使用安全的排序方法
            try:
                articles.sort(key=lambda x: x.date if hasattr(x, 'date') and x.date is not None else None, reverse=True)
            except (TypeError, AttributeError):
                # 如果排序失败，跳过该子分类
                continue
            index = subcategory.name.count('/')
            next_name = 'next_article_in_subcategory{}'.format(index)
            prev_name = 'prev_article_in_subcategory{}'.format(index)
            set_neighbors(articles, next_name, prev_name)


def register():
    signals.article_generator_finalized.connect(neighbors)
