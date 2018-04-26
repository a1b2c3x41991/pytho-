from django.shortcuts import render
from django.http import JsonResponse, Http404
from tt_goods.models import GoodsSKU
import json
from django_redis import get_redis_connection


# Create your views here.
def add(request):
    if request.method != 'POST':
        return Http404()
    # 接收请求的数据：商品编号、数量
    dict1 = request.POST
    sku_id = dict1.get('sku_id')
    count = dict1.get('count')

    # 验证数据的有效性
    if not all([sku_id, count]):
        return JsonResponse({'result': '参数不完整'})

    # 验证sku_id是否合法
    if GoodsSKU.objects.filter(pk=sku_id).count() != 1:
        return JsonResponse({'result': '商品编号错误'})
    # 验证count是否合法
    try:
        count = int(count)
    except:
        return JsonResponse({'result': '数量必须是整数'})
    if count < 1:
        return JsonResponse({'result': '数量必须大于1'})
    if count > 5:
        return JsonResponse({'result': '数量必须小于5'})

    if request.user.is_authenticated():
        # 如果登录，是向Redis中加入数据
        redis_client = get_redis_connection()
        # 构造购物车的键
        key = 'cart%d' % request.user.id
        # 判断此商品是否已经购买，如果有则数量相加
        count_redis = redis_client.hget(key, sku_id)
        if count_redis is not None:
            count += int(count_redis)
            if count > 5:
                count = 5
        # 向redis中加入购物车的数据
        #	键为cart用户编号
        # 属性为商品编号
        # 值为数量
        redis_client.hset(key, sku_id, count)

        # 计算总数量
        total_count = 0
        count_list = redis_client.hvals(key)
        for c in count_list:
            total_count += int(c)

        response = JsonResponse({'result': 'ok', 'total_count': total_count})
    else:
        # 获取原有购物车的数据
        cart_str = request.COOKIES.get('cart')
        # 如果购物车数据已经存在，则转换成字典，如果不存在则构造空字典
        if cart_str:
            # 将字符串转换成字典
            cart_dict = json.loads(cart_str)
        else:
            cart_dict = {}

        # 判断字典中是否包含当前商品编号
        if sku_id in cart_dict:
            # 如果商品存在则修改数量
            count = cart_dict[sku_id] + count
            if count > 5:
                count = 5
        # 如果不存在则添加商品
        cart_dict[sku_id] = count

        # 构造数据sku_id:count==>sku_id,count
        # dict_cart={sku_id:count}

        # -------此段是后加的,计算总数量，返回给浏览器
        total_count = 0
        for k, v in cart_dict.items():
            total_count += v

        # 如果未登录，则向cookie中加入数据
        response = JsonResponse({'result': 'ok', 'total_count': total_count})

        # 问题：如何将字典与字符串相互转换
        cart_str = json.dumps(cart_dict)

        # 将数据写入cookie
        response.set_cookie('cart', cart_str, expires=60 * 60 * 24 * 7)
    return response


def index(request):
    # 构造列表用于模板遍历
    cart_list = []

    # 查询所有的购物车数据
    if request.user.is_authenticated():
        # 如果登录则从redis中读取数据
        redis_client = get_redis_connection()
        # 构造键
        key = 'cart%d' % request.user.id
        # 获取所有的商品编号
        skuid_list = redis_client.hkeys(key)
        if skuid_list is not None:
            # 遍历查询商品对象
            for sku_id in skuid_list:
                try:
                    sku = GoodsSKU.objects.get(pk=int(sku_id))
                except:
                    return Http404()
                # 附加数量
                sku.cart_count = int(redis_client.hget(key, sku_id))
                # 加入列表
                cart_list.append(sku)
    else:
        # 如果未登录则从cookie中读取数据
        cart_str = request.COOKIES.get('cart')
        # 判断是否有购物车数据
        if cart_str:
            # 将字符串转换成字典
            cart_dict = json.loads(cart_str)
            # 遍历购物车中的商品
            for k, v in cart_dict.items():
                # 根据编号查询商品对象
                try:
                    sku = GoodsSKU.objects.get(pk=k)
                except:
                    return Http404()
                # 为商品对象添加购物车数量的属性
                sku.cart_count = v
                # 加入列表中
                cart_list.append(sku)

    context = {
        'title': '我的购物车',
        'cart_list': cart_list,
    }
    return render(request, 'cart.html', context)


