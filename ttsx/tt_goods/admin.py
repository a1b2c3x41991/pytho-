from django.contrib import admin
from .models import GoodsCategory,Goods,IndexGoodsBanner,IndexCategoryGoodsBanner,IndexPromotionBanner
from django.core.cache import cache
# from utils import gen_html
from utils import celery_tasks
# Register your models here.
class BaseAdmin(admin.ModelAdmin):
    #当保存模型时，会调用这个方法
    def save_model(self, request, obj, form, change):
        super().save_model(request,obj,form,change)
        #当数据被删除时，需要重新生成静态首页
        celery_tasks.gen_index.delay()
        #删除首页数据的缓存
        cache.delete('index_data')
    #当删除模型时，会调用这个方法
    def delete_model(self, request, obj):
        #实现逻辑删除
        # obj.isDelete=True
        # obj.save()
        #物理删除
        # obj.delete()
        super().delete_model(request,obj)
        #当数据被删除时，需要重新生成静态首页
        celery_tasks.gen_index.delay()
        #删除首页数据的缓存
        cache.delete('index_data')


class GoodsCategoryAdmin(BaseAdmin):
    list_display = ['id','name','logo']
class IndexGoodsBannerAdmin(BaseAdmin):#(admin.ModelAdmin):
    pass
    # list_display = ['id','name','logo']
    #当保存模型时，会调用这个方法
    # def save_model(self, request, obj, form, change):
    #     super().save_model(request,obj,form,change)
    #     #当数据被删除时，需要重新生成静态首页
    #     gen_html.gen_index()
    # #当删除模型时，会调用这个方法
    # def delete_model(self, request, obj):
    #     #实现逻辑删除
    #     # obj.isDelete=True
    #     # obj.save()
    #     #物理删除
    #     # obj.delete()
    #     super().delete_model(request,obj)
    #     #当数据被删除时，需要重新生成静态首页
    #     gen_html.gen_index()
class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    pass
    # list_display = ['id','name','logo']
class IndexPromotionBannerAdmin(BaseAdmin):
    pass
    # list_display = ['id','name','logo']

admin.site.register(GoodsCategory,GoodsCategoryAdmin)
admin.site.register(IndexGoodsBanner,IndexGoodsBannerAdmin)
admin.site.register(IndexCategoryGoodsBanner,IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner,IndexPromotionBannerAdmin)
admin.site.register(Goods)