# coding=utf8
__author__ = 'taoluo'

import xadmin
from core import models
from django.db.models import TextField
from xadmin.views import BaseAdminPlugin, ModelFormAdminView, DetailAdminView, ModelAdminView
from DjangoUeditor.models import UEditorField
from DjangoUeditor.widgets import UEditorWidget
from django.conf import settings

class XadminUEditorWidget(UEditorWidget):
    def __init__(self,**kwargs):
        self.ueditor_options=kwargs
        self.Media.js = None
        super(UEditorWidget,self).__init__(kwargs)

class UeditorPlugin(BaseAdminPlugin):
    def get_field_style(self, attrs, db_field, style, **kwargs):
        if style == 'ueditor':
            if isinstance(db_field, UEditorField):
                return {'widget': XadminUEditorWidget(**db_field.formfield().widget.ueditor_options)}
            if isinstance(db_field, TextField):
                return {'widget': XadminUEditorWidget}
        return attrs

    def block_extrahead(self, context, nodes):
        js = '<script type="text/javascript" src="%s"></script>' % (settings.STATIC_URL + "ueditor/editor_config.js")
        js += '<script type="text/javascript" src="%s"></script>' % (settings.STATIC_URL + "ueditor/editor_all_min.js")
        nodes.append(js)

    def init_request(self, *args, **kwargs):
        return True

class NewsAdmin(object):
    style_fields = {"context": "ueditor"}


class NewsItemInLine(object):
    model = models.NewsItem
    extra = 3
    style = 'tab'

class NewsItemsAdmin(object):
    inlines = [NewsItemInLine,]

class InvestmentItemInLine(object):
    model = models.InvestmentItem
    extra = 3
    style = 'tab'

class InvestmentItemsAdmin(object):
    inlines = [InvestmentItemInLine,]

xadmin.site.register_plugin(UeditorPlugin, DetailAdminView)
xadmin.site.register_plugin(UeditorPlugin, ModelFormAdminView)
xadmin.site.register_plugin(UeditorPlugin, ModelAdminView)

xadmin.site.register(models.Investor)
xadmin.site.register(models.InvestmentProject)
xadmin.site.register(models.Investment)
xadmin.site.register(models.News, NewsAdmin)
xadmin.site.register(models.InvestorInfo)
xadmin.site.register(models.DisplayNewsList, NewsItemsAdmin)
xadmin.site.register(models.DisplayInvestmentList, InvestmentItemsAdmin)
xadmin.site.register(models.VersionItem)




