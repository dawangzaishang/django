from django.contrib import admin
from myapp.goods.models import Goods,GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner,GoodsSKU
from django.core.cache import cache
# Register your models here.

#自定义当管理后台用户修改数据库时，更新静态首页和首页清除缓存
class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新表中的数据时调用"""
        super().save_model(request, obj, form, change)

        # 发出任务，让celery worker 重新生成首页静态页
        # 为何在顶部导入不可以，执行celery会出错
        from celery_task.tasks import generate_static_index_page
        generate_static_index_page.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表中的数据时调用"""
        super().delete_model(request, obj)
        # 发出任务，让celery worker 重新生成首页静态页
        from celery_task.tasks import generate_static_index_page
        generate_static_index_page.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')


class GoodsTypeAdmin(BaseModelAdmin):
    pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass


class GoodsSPUAdmin(BaseModelAdmin):
    pass


class GoodsSKUAdmin(BaseModelAdmin):
    pass


admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(Goods, GoodsSPUAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)



