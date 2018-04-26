# coding=utf-8
from haystack import indexes
from tt_goods.models import GoodsSKU

#指定在哪个表中查询数据，在django中模型类对应着表
class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    """建立索引时被使用的类"""
    #这段代码不能改
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """从哪个表中查询"""
        #这个值可以修改
        return GoodsSKU

    def index_queryset(self, using=None):
        """从指定表中的哪些行中进行查询"""
        #这个值可以改，添加自己的过滤条件
        return self.get_model().objects.filter(isDelete=False)