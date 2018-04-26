# coding=utf-8
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FdfsStorage(Storage):
    # 只要进行文件保存，就会调用这个方法
    # 保存成功后，需要返回文件的名称，用于保存到表中
    def save(self, name, content, max_length=None):
        # 添加文件格式的验证

        try:
            # 根据配置文件，创建fdfs的客户端，通过这个对象上传文件到fdfs
            client = Fdfs_client(conf_path=settings.FDFS_CLIENT)
            # content表示上传文件的内容，以bytes类型进行上传
            result = client.upload_by_buffer(content.read())
            # 判断是否上传成功
            if result.get('Status') == 'Upload successed.':
                # 上传成功后，返回文件的名称
                return result.get('Remote file_id')
            else:
                return ''
        except:
            return ''
        '''
        {'Group name': 'group1', 'Remote file_id': 'group1/M00/00/00/wKi7hVrX_OuAOfX6AAA2pLUeB60110.jpg', 'Uploaded size': '13.00KB', 'Status': 'Upload successed.', 'Local file name': '/home/python/Desktop/images/adv01.jpg', 'Storage IP': '192.168.187.133'}
        '''

    # 提供访问这个文件的地址
    def url(self, name):
        return settings.FDFS_URL + name
