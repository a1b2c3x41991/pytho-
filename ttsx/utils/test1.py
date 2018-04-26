# coding=utf-8
class A(object):
    def as_view(self):
        super().as_view()
        print('a')
class B(object):
    def as_view(self):
        print('b')
class C(A,B):
    def as_view(self):
        super().as_view()
        print('c')

if __name__ == '__main__':
    c=C()
    c.as_view()

