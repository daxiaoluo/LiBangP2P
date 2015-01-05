__author__ = 'taoluo'
# coding=utf8

from django.conf.urls import patterns, url

urlpatterns = patterns('core.views',
    url(r'^projects$', 'get_inverst_project'),
    url(r'^project$', 'get_single_inverstment'),
    url(r'^captcha$', 'generate_code_response'),
    url(r'^investor/register$', 'register_investor'),
    url(r'^investor/login$', 'login_investor'),
    url(r'^investor/update/(?P<pk>[0-9]+)$', 'update_investor'),
    url(r'^investor/logout$', 'logout_investor'),
    url(r'^investor/invest$', 'invest_project'),
    url(r'^investor/projects$', 'investor_info'),
    url(r'^news$', 'get_news'),
    url(r'^singleNews$', 'get_single_news'),
    url(r'^investorInfo$', 'get_investor_info'),
    url(r'^displayInfo$', 'get_display_info'),
    url(r'^versionInfo/android$', 'get_version_android'),
    url(r'^versionInfo/ios$', 'get_version_ios'),
    url(r'^csrf$', 'get_csrf'),
)
