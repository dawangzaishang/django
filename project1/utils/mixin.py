from django.contrib.auth.decorators import login_required

#让视图中的类继续此类
class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        # 调用父类的as_view
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return login_required(view)
