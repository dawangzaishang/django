from django.shortcuts import render,redirect,HttpResponse
from django.views.generic import View
from myapp.user.models import User,Address
from myapp.order.models import OrderInfo,OrderGoods

import itsdangerous
from itsdangerous import SignatureExpired,BadSignature

# Create your views here.
def test(request):
    return render(request,'test/test.html')

def index(request):
    return render(request,'index.html')

#测试传递参数
def show_args(request,arg1):
    data = {
            'a':arg1,
            #'b':arg2,
            }
    return render(request,'args.html',context=data)

#测试传递键值对参数
def show_kwargs(request,aa):
    return render(request,'kwargs.html',{'a':aa})

#定重向
#from django.core.urlresolvers import reverse
from django.urls import reverse
def re_direct(request):
    return redirect(reverse('user:show_kwargs',kwargs ={'a':3}))

#用户注册
# def registers(request):
#     if request.method=='GET':
#          return render(request,'df_user/register.html')
#     else:
#         username = request.POST.get('username')
#         passwd = request.POST.get('pass')
#         repassword = request.POST.get('passcp')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#         print(allow)
#         if not all([username,passwd,repassword,email]):
#             return render(request,'df_user/register.html',{'errmsg':"输入的信息不完整"})
#         if allow != 'on':
#             return render(request,'df_user/register.html',{'errmsg':"请勾选协议"})
#         #进行用户注册数据库
#         user = User()
#         user.username = username
#         user.password = passwd
#         user.email = email
#         user.save()
#         #不用原始的方式，使用django内置的用户验证
#         user = User.objects.create_user(username,passwd,email)
#         user.is_active=0
#         user.save()
#         return render(request,'df_user/login.html')

#类视图
class RegisterView(View):
    def get(self, request):
        # 显示注册页面
        return render(request, 'df_user/register.html')

    def post(self, request):
        register_method = request.POST.get('')
        if register_method =='email':
            # 进行注册处理
            # 接收数据
            username = request.POST.get('username')
            password = request.POST.get('pass')
            email = request.POST.get('email')

            # 进行数据校验
            if not all([username, password, email]):
                # 数据不完整
                return render(request, 'df_user/register.html', {'errmsg': '数据不完整'})

            # 校验用户是否重复
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # 用户名不存在
                user = None

            if user:
                return render(request, 'df_user/register.html', {'errmsg': '用户已存在'})

            # 进行业务处理：进行用户注册
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = 0
            user.save()
            #print(user)
            """
            发送激活链接，包含激活链接：http://127.0.0.1:8000/user/active/5
            激活链接中需要包含用户的身份信息，并要把身份信息进行加密
            激活链接格式: /user/active/用户身份加密后的信息 /user/active/token
            加密用户的身份信息，生成激活token
            """
            # from project1 import settings
            # from django.core.mail import send_mail
            # send_mail('subject', 'message',settings.EMAIL_FROM, ['wangjiadongge@163.com']) #html_message=html_message)
            from django.conf import settings
            from celery_task.tasks import celery_send_email
            # 获取数据库中对应用户名的邮箱
            info = {'userid': user.id}
            t = itsdangerous.TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=600)
            token = t.dumps(info).decode('utf8')
            rec_email = user.email
            celery_send_email.delay(rec_email, user.username, token)
            return HttpResponse('邮件已成功发送，点击邮箱中的链接激活')
        else:
            #手机号注册
            # 获取用手手机号
            from django.http import JsonResponse
            import re
            mobile = request.POST.get('mobilenum')
            if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', mobile):
                return JsonResponse({'res':1,'errmsg':"不是正确的手机号"})
            import random
            #生成六位数验证码
            def gen_verify_code(length=6):
                code = random.randrange(10**(length-1),10**length)
                return code
            #发送短信
            from utils.sms.sendsms import send_sms
            result = send_sms(mobile_num=mobile,code=gen_verify_code(6))
            # 判断是否发送成功
            if result['code'] != '000000':
                return JsonResponse({'res':2,'errmsg':"短信未成功发送"})
            if result['mobile'] != mobile:
                return JsonResponse({'res':3,'errmsg':"手机号不一致"})
            #将验证码存入redis，过期时间设置为3分钟
            from django_redis import get_redis_connection
            conn = get_redis_connection('default')
            conn.set(mobile,gen_verify_code(6),timeout=3*60)


            #用户结果

#用户激活账号
def active(req):
    return render(req,'df_user/login.html')

#todo:
# def login(request):
#     if request.method=='GET':
#         return render(request,'df_user/login.html')
#     else:
#         username = request.POST.get('username')
#         passwd = request.POST.get('pwd')
#         if username=='' or passwd == '':
#             print('u is null or pass is null')
#         # if not all([username,passwd]):
#              #return render(request,'df_user/login.html',{'errmsg':'用户名和密码不正确'})
#
#         return redirect(reverse('goods:index'))
from django.contrib.auth import authenticate,login,logout
class Login(View):
    def get(self,req):
        #判断请求的用户是否已经认证通过
        if req.user.is_authenticated:
            next_url = req.GET.get('next', reverse('goods:index'))
            return redirect(next_url)
        #浏览器中有cookie时会有username:abc01,没有cookie时username不存在
        if 'user' in req.COOKIES:
            username = req.COOKIES.get('user')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(req,'df_user/login.html',{'username':username,'checked':checked })
    def post(self,req):
        username = req.POST.get('username')
        password = req.POST.get('pwd')
        if not all([username,password]):
            return render(req,'df_user/login.html',{'errmsg':'输入信息不完整'})
        users = authenticate(username=username,password=password)
        if users is not None:
            if users.is_active:
                #记住登陆状态
                login(req,users)
                #获取登陆后要跳转的地址,如果next有值，获取next值，如果没有则=/goods/index
                next_url = req.GET.get('next',reverse('goods:index'))
                response = redirect(next_url)
                remember = req.POST.get('remember')
                if remember=='on':
                    response.set_cookie('user',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('user')
                #是否记住用户名
                return response
            else:
                return render(req,'df_user/login.html',{'errmsg':'用户未激活'})
        else:
            return render(req,'df_user/login.html',{'errmsg':'用户名或密码错误'})

#logout
class Logout(View):
    def get(self,req):
        logout(req)
        #req.user可以获取的属性
        #req.user.username
        #req.user.password
        #req.user.email
        #req.user.is_authenticated
        # if req.user.is_authenticated:
        #     return redirect(reverse('logout'))
        # else:
        #     return redirect(reverse('login'))
        return redirect(reverse('goods:index'))


#使用登陆装饰器，只有登陆的用户才可以访问这三个页面

from utils.mixin import LoginRequiredMixin
#用户中心-信息页
class UserInfo(LoginRequiredMixin,View):
    def get(self,req):
        user = req.user
        address = Address.objects.get_default_address(user=user)
        for i in address:
            if i.is_default == True:
                address = i

        #从redis中获取用户历史浏览记录
        # from redis import StrictRedis
        # str = StrictRedis(host='192.168.1.223',port=6379,db=12)
        from django_redis import get_redis_connection
        connect = get_redis_connection('default')
        history_key = 'history_%d'%user.id
        #获取用户最新浏览的5条记录
        sku_id = connect.lrange(history_key,0,4)
        from myapp.goods.models import GoodsSKU
        goods_li = []
        for his_id in sku_id:
            try:
                goods = GoodsSKU.objects.get(id = his_id)
            except GoodsSKU.DoesNotExist:
                continue
            goods_li.append(goods)
        context = {'page':'info',
                   'address':address,
                   'goods_list':goods_li}
        return render(req,'df_user/user_center_info.html',context=context)


#用户订单页
class UserOrder(LoginRequiredMixin,View):
    def get(self,req):
        user = req.user
        order_page = OrderInfo.objects.filter(user=user).order_by('-create_time')

        for i in order_page:
            order_skus = OrderGoods.objects.filter(order_id=i)
            for a in order_skus:
                amount = a.price * a.count
                a.amount = amount
            #返回两个商品
            i.order_skus = order_skus
            i.status_name = OrderInfo.ORDER_STATUS[i.order_status]
        #分页
        from django.core.paginator import Paginator
        pagenator = Paginator(order_page,1)

        return render(req,'df_user/user_center_order.html',{'order_page':order_page,'page':'order'})

#用户地址页
class UserAdress(LoginRequiredMixin,View):
    def get(self,req):
        users = req.user
        address = Address.objects.get_default_address(user=users)
        return render(req,'df_user/user_center_site.html',{'page':'address','all_address':address})
    def post(self,req):
        #接收数据
        receiver = req.POST.get('receiver')
        addr = req.POST.get('addr')
        zipcode = req.POST.get('zip_code')
        phone = req.POST.get('phone')
        #效验数据
        import re
        if not all([receiver,addr,phone]):
            return render(req,'user_center_site.html',{'errmsg':'输入信息不完整'})
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$',phone):
            return render(req, 'user_center_site.html', {'errmsg': '请填写正确的手机号'})
        #数据处理
        #如果用户已存在默认地址，则不作为默认地址
        #登陆的用户名
        user = req.user
        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default = True
        #判断地址的数量：
        cou = Address.objects.filter(user=user)
        if len(cou) >5:
            return render(req, 'user_center_site.html', {'errmsg': '地址超出上限，每隔用户最多只能添加5个地址'})
        #添加地址
        Address.objects.create(user=user,receiver=receiver,addr=addr,zip_code=zipcode,phone=phone,is_default=is_default)
        #返回应答
        return redirect(reverse('user:address'))



