# coding=utf-8
# 对json数据进行有时效性的加密
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from tt_goods.models import *
import os
#引入Celery类
from celery import Celery
#创建celery对象，通过broker指定存储队列的数据库(redis)
app = Celery('celery_tasks', broker='redis://127.0.0.1:6379/4')

#将函数设置成celery的任务
@app.task
def send_active_mail(user_email,user_id):
    # 对用户编号进行加密
    user_dict = {'user_id': user_id}
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    str1 = serializer.dumps(user_dict).decode()
    #发邮件
    mail_body = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % str1
    send_mail('用户激活', '', settings.EMAIL_FROM, [user_email], html_message=mail_body)

#生成首页静态html文件
@app.task
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
    with open('/home/python/Desktop/index.html', 'w') as html_index:
        html_index.write(html_str)
