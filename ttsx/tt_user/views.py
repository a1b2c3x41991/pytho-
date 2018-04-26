from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
# 引入django中定义的类视图基类
from django.views.generic import View
import re
from .models import User, AreaInfo, Address
# 引入django发送邮件的函数，相关的配置都写在settings中
from django.core.mail import send_mail
from django.conf import settings
# 对json数据进行有时效性的加密
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from utils import celery_tasks
# django提供的用户验证功能
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from utils.views import LoginRequiredView, LoginRequiredViewMixin
from django_redis import get_redis_connection
from tt_goods.models import GoodsSKU
import json


# Create your views here.
# 接收get方式的请求，用于展示注册页面
# 接收post方式的请求，用于注册处理
# def register(request):
#     if request.method == 'GET':
#         return render(request, 'register.html')
#     elif request.method == 'POST':
#         return HttpResponse('ok')
# 接收post方式的请求，用于注册处理
# def register_handle(request):
#     return HttpResponse('ok')
# 类视图：可以根据请求方式查找对应的处理函数
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 1.接收所有请求的数据
        dict1 = request.POST
        user_name = dict1.get('user_name')
        pwd = dict1.get('pwd')
        cpwd = dict1.get('cpwd')
        email = dict1.get('email')
        allow = dict1.get('allow')
        # 	是否接受协议:对于checkbox如果选中则提交，如果不选中则不提交，此时的值为None
        if allow == None:
            return render(request, 'register.html')
        # 2.验证数据的完整性
        # all([])：迭代列表，判断列表中每个元素的值，如果其中某个值为false，则直接返回false，如果没有返回false，则最终返回true
        if not all([user_name, pwd, cpwd, email]):
            return render(request, 'register.html')
        # 3.验证数据的正确性
        # 	邮箱格式是否正确
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html')
        # 密码是否一致
        if pwd != cpwd:
            return render(request, 'register.html')
        # 用户名是否存在
        if User.objects.filter(username=user_name).count() >= 1:
            return render(request, 'register.html')
        # 4.保存用户对象
        user = User.objects.create_user(user_name, email, pwd)
        # 4.1默认用户创建后是激活状态，此处逻辑为需要用户手动激活，则设置为非激活
        user.is_active = False
        user.save()

        # 5.提示
        celery_tasks.send_active_mail.delay(user.email, user.id)

        return HttpResponse('请到邮箱中激活')


def user_name(request):
    # 接收用户名
    uname = request.GET.get('uname')
    # 查询判断是否存在
    result = User.objects.filter(username=uname).count()
    # 返回提交信息
    return JsonResponse({'result': result})


def send_active_mail(request):
    # 查找邮箱
    user = User.objects.get(pk=1)
    # # user.id
    # # user.email
    # # 定义邮件内容
    #
    # # 加逻辑：对用户编号进行加密
    # user_dict = {'user_id': user.id}
    # serializer = Serializer(settings.SECRET_KEY, expires_in=5)
    # str1 = serializer.dumps(user_dict).decode()
    #
    # # 需要指定激活账号的编号
    # mail_body = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % str1
    # # http://127.0.0.1:8000/user/active/1
    # # 发邮件
    # # 参数2表示message，内容是纯文本
    # # 参数html_message，内容是html
    # # 注意：如果内容是html，则将第二个参数设置成'',再设置html_message参数
    # send_mail('用户激活', '', settings.EMAIL_FROM, [user.email], html_message=mail_body)
    # 提示


    # delay()将celery的任务加到队列中
    celery_tasks.send_active_mail.delay(user.email, user.id)

    return HttpResponse('请到邮箱中激活')


def user_active(request, user_str):
    # 1.从地址中接收用户编号(见url配置)

    # 加逻辑：解密
    serializer = Serializer(settings.SECRET_KEY)
    # 如果时间超过规定的时间则会抛异常
    try:
        user_dict = serializer.loads(user_str)
        user_id = user_dict.get('user_id')
        print('----------------%s' % user_id)
    except:
        return HttpResponse('地址无效')

    # 2.根据编号查询用户对象
    user = User.objects.get(pk=user_id)
    # 3.修改is_active属性为True
    user.is_active = True
    user.save()
    # 4.提示：转到登录页
    return redirect('/user/login')


class LoginView(View):
    def get(self, request):
        # 从cookie中读取用户名，并显示在界面上
        username = request.COOKIES.get('username', '')
        context = {
            'username': username
        }
        return render(request, 'login.html', context)

    def post(self, request):
        # 1.接收
        dict1 = request.POST
        username = dict1.get('username')
        pwd = dict1.get('pwd')
        remember = dict1.get('remember')

        # 2.验证完整性:可以不传递remember
        if not all([username, pwd]):
            return render(request, 'login.html')

        # 3.验证正确性：查询用户名与密码对应的用户是否存在
        # 如果用户名与密码正确，则返回user对象，如果错误，则返回None
        user = authenticate(username=username, password=pwd)
        # 判断是否正确
        if user is None:
            return render(request, 'login.html', {'msg': '用户名或密码错误'})

        # ---加逻辑1：状态保持
        login(request, user)

        # 获取response对象
        # ---加逻辑3：如果有来源页面，则转到那个页面，如果没有，则转到登录页面
        login_url = request.GET.get('next', '/')
        response = redirect(login_url)

        # ---加逻辑2：记住用户名，存储到cookie中
        if remember is None:
            response.delete_cookie('username')
        else:
            response.set_cookie('username', username, expires=60 * 60 * 24 * 7)

        # 扩展代码：将cookie中的购物车数据，存入redis中
        # 读取cookie中的购物车信息
        cart_str = request.COOKIES.get('cart')
        # 判断是否存在购物车信息
        if cart_str is not None:
            # 获取redis的连接
            redis_client = get_redis_connection()
            # 创建购物车的键
            key = 'cart%d' % request.user.id
            # 将购物车字符串转换成字典
            cart_dict = json.loads(cart_str)
            # 逐个遍历购物车中的商品编号k与数量v
            for k, v in cart_dict.items():
                # 从redis中获取商品k的数量，如果没有这个商品则返回None
                count_redis = redis_client.hget(key, k)
                # 如果这个商品在redis中存在，则数量相加
                if count_redis is not None:
                    # 数量相加，注意从redis中读取的数据类型为bytes，需要改为int
                    v += int(count_redis)
                    # 上限判断
                    if v > 5:
                        v = 5
                # 将当前用户的购物车中商品编号与对应的数量写入redis中
                redis_client.hset(key, k, v)
            # 删除cookie中的购物车信息
            response.delete_cookie('cart')

        # 如果用户正确则返回首页
        return response


def user_logout(request):
    # django提供了登出功能
    logout(request)
    return redirect('/user/login')


@login_required
def info(request):
    # 判断用户是否登录，如果未登录则转到登录页
    # if not request.user.is_authenticated():
    #     return redirect('/user/login')

    # 查询最近浏览的信息
    browser_key = 'browser%d' % request.user.id
    # 获取redis的连接
    redis_client = get_redis_connection()
    # 获取列表数据
    skuid_list = redis_client.lrange(browser_key, 0, -1)
    # 根据编号查询商品对象
    sku_list = []
    for skuid in skuid_list:
        sku_list.append(GoodsSKU.objects.get(pk=skuid))

    # 查询收货地址的第一条数据显示
    addr_list = request.user.address_set.all()
    mobile = ''
    addr = ''
    if addr_list is not None:
        addr1 = addr_list[0]
        mobile = addr1.receiver_mobile
        addr = '%s %s %s %s' % (addr1.province.atitle,
                                addr1.city.atitle,
                                addr1.district.atitle,
                                addr1.detail_addr)

    context = {
        'title': '个人信息',
        'sku_list': sku_list,
        'mobile': mobile,
        'addr': addr,
    }
    return render(request, 'user_center_info.html', context)


@login_required
def order(request):
    context = {}
    return render(request, 'user_center_order.html', context)


# @login_required
# def site(request):
# class SiteView(LoginRequiredView):#(View):
class SiteView(LoginRequiredViewMixin, View):
    def get(self, request):
        # 获取当前登录的用户
        user = request.user
        # 查找当前用户的所有收货地址
        addr_list = user.address_set.all()

        context = {
            'addr_list': addr_list,
            'title': '收货地址'
        }
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        # 2.接收数据
        dict1 = request.POST
        receiver_name = dict1.get('receiver_name')
        province_id = dict1.get('province')
        city_id = dict1.get('city')
        district_id = dict1.get('district')
        detail_addr = dict1.get('detail_addr')
        zip_code = dict1.get('zip_code')
        receiver_mobile = dict1.get('receiver_mobile')
        # 3.创建对象
        addr = Address()
        addr.receiver_name = receiver_name
        addr.province_id = province_id
        addr.city_id = city_id
        addr.district_id = district_id
        addr.detail_addr = detail_addr
        addr.zip_code = zip_code
        addr.receiver_mobile = receiver_mobile
        addr.user_id = request.user.id
        # 4.保存
        addr.save()
        return redirect('/user/site')


def area(request):
    # 接收请求的地址编号，查询这个编号作为父级编号的地区
    pid = request.GET.get('pid')
    if pid is None:
        # 查询省信息
        area_list = AreaInfo.objects.filter(aParent__isnull=True)
    else:
        # 如果pid是省的编号则查询市
        # 如果pid是市的编号则查询区县
        area_list = AreaInfo.objects.filter(aParent_id=pid)
    # 重新整理数据格式为{id:**,title:***}
    list1 = []
    for a in area_list:
        list1.append({'id': a.id, 'title': a.atitle})
    # 返回数据{list1:[{},{},...]}
    return JsonResponse({'list1': list1})
