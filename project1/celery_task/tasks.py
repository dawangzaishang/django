from celery import Celery
from django.core.mail import send_mail
from django.conf import settings
#在任务处理者中添加
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","project1.settings")
django.setup()

#测试查看celery有没有发送邮件
#celery -A celery_task.tasks worker -l info -P eventlet
app = Celery('celery_task.tasks',broker='redis://192.168.1.223:6379/10')

@app.task
def celery_send_email(to_email,username,token):
    subject = '天天生鲜欢迎你'
    message = ''
    html_message = '''<h1>hello %s天天生鲜用户激活</h1>
                      <h3>请点击链接完成激活，激活链接在10分钟内有效</h3>
                      <a href="http://127.0.0.1:8000/test/active/%s">点击激活</a>
                      <h3>或者复制链接到浏览器中进行激活http://127.0.0.1:8000/test/active/%s</h3>''' % (username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]  # 收件人列表
    send_mail(subject, message, sender, receiver, html_message=html_message)

#生成首页静态页面需要的包
from myapp.goods.models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django.template import loader,RequestContext

@app.task
def generate_static_index_page():
    #获取商品类型
    good_type = GoodsType.objects.all()

    # 获取首页轮番图信息
    goods_banner = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销信息
    promotion_banner = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    # type_good_banner = IndexTypeGoodsBanner.objects.all()
    for type in good_type:
        image_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('-index')
        title_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
        type.image_banner = image_banner  # 给对象中的属性赋值
        type.title_banner = title_banner

    context = {
        'types': good_type,
        'goods_banner': goods_banner,
        'promotion_banner': promotion_banner,
    }
    temp = loader.get_template('static_index.html')
    # contexts = RequestContext(request,context)
    static_index_html = temp.render(context)

    # 生成首页对应静态文件
    import os
    save_path = os.path.join(settings.BASE_DIR,'static/index.html')
    with open(save_path,'w') as f:
        f.write(static_index_html .encode('gbk','ignore').decode('gbk'))

#调用时要在后面添加.delay()
#比如：generate_static_index_page.delay()