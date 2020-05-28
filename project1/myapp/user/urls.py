from django.urls import path,re_path
from django.conf.urls import url
from myapp.user import views
from myapp.user.views import RegisterView,Login,Logout,UserInfo,UserAdress,UserOrder  #视图类
from django.contrib.auth.decorators import login_required
urlpatterns = [
    #path('register/', views.registers),
    path('register/', RegisterView.as_view(),name='register'),  #类视图写法
    path('login/',Login.as_view(),name='login'),
    path('logout/',Logout.as_view(),name='logout'),
    url(r'active/',views.active,name='active'),
    url(r'test/',views.test,name='test'),
    #path('index/',views.index,name='index'),
    #url(r'arg/(\w+)/',views.show_args,name='show_args'),
    #url(r'kwarg/(?P<a>\d+)/',views.show_kwargs,name='show_kwargs'),
    #path('redict/',views.re_direct),
    #path('register/',views.registers,name='register'),
    # url(r'info/',login_required(UserInfo.as_view()),name='info'),
    # url(r'order/',login_required(UserOrder.as_view()),name='order'),
    # url(r'address/',login_required(UserAdress.as_view()),name='address'),
    url(r'info/',UserInfo.as_view(),name='info'),
    url(r'order/',UserOrder.as_view(),name='order'),
    url(r'address/',UserAdress.as_view(),name='address'),

]
