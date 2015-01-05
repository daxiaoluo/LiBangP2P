# coding=utf8

from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, routers
from django.contrib import admin


from django.conf import settings



admin.autodiscover()

import xadmin
xadmin.autodiscover()

from xadmin.views.base import CommAdminView
CommAdminView.site_title = _(u'利邦资产投资平台管理系统')
CommAdminView.apps_label_title = {'core': u'核心业务', 'auth': u'权限控制'}

# # version模块自动注册需要版本控制的 Model
# from xadmin.plugins import xversion
# xversion.registe_models()

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    model = User


class GroupViewSet(viewsets.ModelViewSet):
    model = Group


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)


urlpatterns = patterns(
    '',
    url(r'^$', 'libangp2p.views.home', name='home'),
    url(r'^admin/', include(xadmin.site.urls)),
    url(r'invest/', include('core.urls')),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^ueditor/',include('DjangoUeditor.urls')),
    # url(r'^libangp2p/', include('libangp2p.foo.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )