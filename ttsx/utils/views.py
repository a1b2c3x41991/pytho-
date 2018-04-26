# coding=utf-8
from django.views.generic import View
from django.contrib.auth.decorators import login_required


class LoginRequiredView(View):
    def as_view(cls, **initkwargs):
        view_fun = super().as_view(**initkwargs)
        return login_required(view_fun)


# 当一个类用于多继承时，使用Mixin作为结尾
class LoginRequiredViewMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view_fun = super().as_view(**initkwargs)
        return login_required(view_fun)

