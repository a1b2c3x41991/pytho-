from django.db import models
#使用django提供的用户系统进行二次开发
from django.contrib.auth.models import AbstractUser
from utils.models import BaseModel


class User(AbstractUser, BaseModel):
    """用户"""
    class Meta:
        #指定表的名称
        db_table = "df_users"

class AreaInfo(models.Model):
    atitle=models.CharField(max_length=30)#名称
    aParent=models.ForeignKey('self',null=True,blank=True)#关系
    class Meta:
        db_table='df_areainfo'

class Address(BaseModel):
    """地址"""
    user = models.ForeignKey(User, verbose_name="所属用户")
    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    #省,选项related_name的作用是：因为三个属性关联的是同一个类，默认生成的属性是同名，导致报错，所以需要指定不同的名称
    province=models.ForeignKey(AreaInfo,related_name='provice')
    #市
    city=models.ForeignKey(AreaInfo,related_name='city')
    #区
    district=models.ForeignKey(AreaInfo,related_name='district')
    #详细地址
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, verbose_name="邮政编码")

    class Meta:
        db_table = "df_address"