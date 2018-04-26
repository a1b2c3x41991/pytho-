# coding=utf-8
from django.shortcuts import render
from tt_goods.models import *
from django.conf import settings
import os

#生成首页静态html文件
def gen_index():
    # 1.查询所有的分类
    category_list = GoodsCategory.objects.filter(isDelete=False)
    # 2.查询首页推荐商品,按照指定的顺序输出
    index_goods_banner_list = IndexGoodsBanner.objects.all().order_by('index')
    # 3.查询首页广告
    index_promotion_list = IndexPromotionBanner.objects.all().order_by('index')
    # 4.遍历分类，查询每个分类的标题推荐、图片推荐
    # 在分类对象上增加了属性标题推荐列表、图片推荐列表
    for category in category_list:
        # 查询指定分类的标题推荐商品
        category.title_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=0).order_by(
            'index')
        # 查询指定分类的图片推荐商品
        category.image_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=1).order_by(
            'index')

    context = {
        'category_list': category_list,
        'index_goods_banner_list': index_goods_banner_list,
        'index_promotion_list': index_promotion_list,
    }
    response = render(None, 'index.html', context)
    # 响应体
    html_str = response.content.decode()
    # 写文件
    with open(os.path.join(settings.BASE_DIR, 'static/index.html'), 'w') as html_index:
        html_index.write(html_str)
