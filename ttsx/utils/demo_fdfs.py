# coding=utf-8
from fdfs_client.client import Fdfs_client
from django.conf import settings
#根据配置文件，创建fdfs的客户端，通过这个对象上传文件到fdfs
client=Fdfs_client(conf_path='/etc/fdfs/client.conf')
#调用方法上传文件
result=client.upload_by_file('/home/python/Desktop/images/adv01.jpg')
print(result)
'''
{'Group name': 'group1', 'Remote file_id': 'group1/M00/00/00/wKi7hVrX_OuAOfX6AAA2pLUeB60110.jpg', 'Uploaded size': '13.00KB', 'Status': 'Upload successed.', 'Local file name': '/home/python/Desktop/images/adv01.jpg', 'Storage IP': '192.168.187.133'}
'''