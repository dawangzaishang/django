
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/',include('haystack.urls')),
    path('user/', include(('myapp.user.urls','user'), namespace='user')),  # 用户模块
    path('cart/', include(('myapp.cart.urls','cart'), namespace='cart')),  # 购物车模块
    path('order/', include(('myapp.order.urls','order'), namespace='order')),  # 订单模块
    path('goods/', include(('myapp.goods.urls','goods'), namespace='goods')),  # 商品模块


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
