from django.conf.urls import url
from myapp.goods.views import IndexView,DetailView, ListView

from myapp.goods import views
app_name = 'myapp.goods'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),  # 商品页作为首页
    url(r'index/', IndexView.as_view(), name='index'),  # 商品页作为首页
    url(r'goods/(?P<goods_id>\d+)$', DetailView.as_view(), name='detail'),  # 详情页
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$', ListView.as_view(), name='list'),  # 列表页
    #url(r'^list/', ListView.as_view(), name='list'),
]


