from django.shortcuts import render,redirect,reverse
from django.views.generic import View
from myapp.goods.models import GoodsType,Goods,GoodsSKU,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django_redis import get_redis_connection
from django.core.cache import cache

#商品首页
class IndexView(View):
    def get(self,req):
        #获取缓存，如果不存在则设置缓存
        context = cache.get('index_page_data')
        #cache.delete('index_page_data')
        if context is None:
            #获取商品种类
            good_type =  GoodsType.objects.all()

            #获取首页轮番图信息
            goods_banner = IndexGoodsBanner.objects.all().order_by('index')

            #获取首页促销信息
            promotion_banner = IndexPromotionBanner.objects.all().order_by('index')

            #获取首页分类商品展示信息
            #type_good_banner = IndexTypeGoodsBanner.objects.all()
            for type in good_type:
                image_banner = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by('-index')
                title_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
                type.image_banner = image_banner  #给对象中的属性赋值
                type.title_banner = title_banner
            context = {
                'types': good_type,
                'goods_banner': goods_banner,
                'promotion_banner': promotion_banner,
            }
            cache.set('index_page_data', context, 60)

            print('设置缓存')
        #获取购物车数量
        user = req.user
        if user.is_authenticated:
            connect = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = connect.hlen(cart_key)
        else:
            cart_count = 0
        # 设置缓存数据,缓存的名字，内容，过期的时间
        context.update(cart_count=cart_count)
        return render(req,'df_goods/index.html',context=context)


#商品详情页
from myapp.order.models import OrderGoods
class DetailView(View):
    def get(self,req,goods_id):
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            #商品不存在
            return render(req,'404.html')
        #获取商品分类信息
        #在前端通过外键sku.type.name获取
        #获新品推荐
        new_sku = GoodsSKU.objects.filter(type_id = sku.type.id ).order_by('-create_time')

        #获取评论,是所有商品的评论
        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取同一个SPU的其他规格商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        # 获取登录用户的额购物车中的商品的数量
        user = req.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已经登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id

            # 获取用户购物车中的商品条目数
            cart_count = conn.hlen(cart_key)  # hlen hash中的数目

            # 添加用户的历史记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除列表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的5条信息
            conn.ltrim(history_key, 0, 4)
        data = {'sku': sku,
                'new_skus': new_sku,
                'comments':sku_orders,
                'same_spu_skus':same_spu_skus,
                'cart_count':cart_count,
                'types':GoodsType.objects.all()
                }
        return render(req,'df_goods/detail.html',context=data)

#种类id 页码 排序方式
class ListView(View):
    def get(self,req,type_id,page):
        #/list/type_id/page
        #获取商品类型：
        try:
            type = GoodsType.objects.get(id=int(type_id))
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))
        #获取商品分类信息
        types = GoodsType.objects.all()
        # 获取单个种类的全部商品
        #获取排序方式
        # sort = default
        # sort = price
        # sort = sale
        sort = req.GET.get('sort')
        if sort == 'price':
            type_good = GoodsSKU.objects.filter(type=type).order_by('-price')
        elif sort == 'hot':
            type_good = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            type_good = GoodsSKU.objects.filter(type=type).order_by('-id')
        #分页
        from django.core.paginator import Paginator
        paginator = Paginator(type_good,2)
        # print(paginator)
        # #按2个一页分多少页：
        # print(paginator.num_pages)
        # #指定页的内容
        # content = paginator.page(2)
        # for i in content:
        #     print(i)
        # #打印当前页的上一页内容和下一页内容
        # print(content.previous_page_number)
        # print(content.next_page_number)
        # #获取当前总页数取件
        # print(content.paginator.page_range)
        # #当前页面是第几页
        # print(content.number)
        #获取第page页内容
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        page_content = paginator.page(page)
        print(page_content.number)
        #todo:进行页码控制，页面上显示5个页面，当前页码的前两个和后两个
        #1、总页数小于5页，显示所有页码
        #2、如果当前页是前3页，显示1-5页
        #3、如果当前页是后3页，显示后5页
        #4、其他情况，显示当前页的前2页和后2页
        all_num = paginator.num_pages

        if all_num < 5:
            pages = range(1,all_num+1)
        elif page <= 3:
            pages = range(1,6)
        elif all_num-page<=2:
            pages = range(all_num-4,all_num+1)
        else:
            pages = range(page-2,page+3)
        print(pages)
        #获取新品信息
        new_sku = GoodsSKU.objects.filter(type_id=type.id).order_by('-create_time')
        #获取购物车数据
        user = req.user
        cart_count = 0
        if user.is_authenticated:
            #用户已经登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            #获取用户购物车中的商品条目数
            cart_count = conn.hlen(cart_key)  # hlen hash中的数目
        #组织上下文
        data = {
                'type':type,
                'types':types,
                'skus_page':page_content,
                'new_skus':new_sku,
                'cart_count':cart_count,
                'sort':sort,
                'pages':pages,
            }

        return render(req,'df_goods/list.html',context=data)
