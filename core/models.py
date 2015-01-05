# coding=utf8

from django.db import models
from django.contrib.auth.models import User
import hashlib

#信用级别
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from DjangoUeditor.models import UEditorField

levels = [(0.5, u'0.5等级'), (1.0, u'1等级'), (1.5, u'1.5等级'), (2.0, u'2等级'), (2.5, u'2.5等级'), (3.0, u'3等级'), (3.5, u'3.5等级'), (4.0, u'4等级'), (4.5, u'4.5等级'), (5.0, u'5等级')]

displayType = [('news', u'新闻'), ('investment', u'投资项目')]
deviceOSChoice = [('ios', 'ios'), ('Android', 'Android')]

#投资项目
class InvestmentProject(models.Model):
    name = models.CharField(max_length=50, verbose_name=u'项目名称')
    desc = models.CharField(max_length=150, verbose_name=u'项目描述')
    companyCode = models.CharField(max_length=20, verbose_name=u'企业编码')
    companyDesc = models.CharField(max_length=150, verbose_name=u'企业描述')
    creditLevel = models.FloatField(choices=levels, max_length=15, verbose_name=u'信用等级')
    guaranteeInstitution = models.CharField(max_length=50, verbose_name=u'担保机构')
    guaranteeOpinion = models.CharField(max_length=150, verbose_name=u'担保意见')
    fundingUsing = models.CharField(max_length=100, verbose_name=u'资金用途')
    paymentSource = models.CharField(max_length=100, verbose_name=u'还款来源')
    pledge = models.CharField(max_length=150, verbose_name=u'抵押物')
    riskControl = models.CharField(max_length=100, verbose_name=u'风险控制')
    annualEarnings = models.FloatField(verbose_name=u'年化收益')
    repayDate = models.DateField(verbose_name=u'还款日期')
    consumeTransferPeriod = models.FloatField(verbose_name=u'消费周转周期')
    computeInvestmenmentMethod = models.CharField(max_length=150, verbose_name=u'计息方式')
    financing = models.FloatField(verbose_name=u'融资金额')
    haveInvestment = models.FloatField(verbose_name=u'已投金额')
    investmentStartPoint = models.FloatField(verbose_name=u'投资起点')
    addingUnit = models.FloatField(verbose_name=u'递增单位')

    createdTime = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    modifiedTime = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    status = models.BooleanField(verbose_name=u'状态', default=True, blank=True, editable=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'投资项目'
        verbose_name_plural = u'投资项目'
        ordering = ('name',)


#投资人
class Investor(models.Model):
    user = models.OneToOneField(User, related_name='user')
    phone_number = models.TextField(max_length=20, verbose_name='手机号码')
    payment_password = models.TextField(max_length=128, verbose_name='支付密码')

    createdTime = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    modifiedTime = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    status = models.BooleanField(verbose_name=u'状态', default=True, blank=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.payment_password = hashlib.md5(self.payment_password).hexdigest()
        super(Investor, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None):
        self.user.delete()
        super(Investor, self).delete(using)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = u'投资人'
        verbose_name_plural = u'投资人'
        ordering = ('user',)

#投资人对应的项目
class Investment(models.Model):
    project = models.ForeignKey(InvestmentProject, verbose_name=u'项目名称', related_name='project')
    investor = models.ForeignKey(Investor, verbose_name=u'投资人', related_name='investor')
    investMoney = models.FloatField(verbose_name=u'投入资金', default=0, blank=True)
    createdTime = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    modifiedTime = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    status = models.BooleanField(verbose_name=u'状态', default=True, blank=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.status:
            super(Investment, self).save(force_insert, force_update, using, update_fields)
            return
        if self.investMoney + self.project.haveInvestment > self.project.financing:
            raise ValueError("The invest finance surplus project's limited financing")

        if self.investMoney < self.project.investmentStartPoint:
            raise ValueError("The invest finance isn't enough")

        self.project.haveInvestment += self.investMoney
        self.project.save()
        super(Investment, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return "(%s, %s, %s)" % (self.project.name, self.investor.user.username, self.investMoney)

    class Meta:
        verbose_name = u'投资人对应的项目'
        verbose_name_plural = u'投资人对应的项目'
        ordering = ('project', 'createdTime', 'modifiedTime',)

#投资人投资与收益情况
class InvestorInfo(models.Model):
    user = models.ForeignKey(Investor, verbose_name=u'投资人', related_name='investorForInfo')
    remainingFund = models.FloatField(verbose_name=u'余额', blank=True, default=0)
    forzenFund = models.FloatField(verbose_name=u'冻结资金', blank=True, default=0)
    waittingEarning = models.FloatField(verbose_name=u'待收收益', blank=True, default=0)
    waittingCost = models.FloatField(verbose_name=u'待收成本', blank=True, default=0)
    totalEarning = models.FloatField(verbose_name=u'累计收益', blank=True, default=0)
    totalInvestment = models.FloatField(verbose_name=u'累计投资', blank=True, default=0)

    createdTime = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    modifiedTime = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    status = models.BooleanField(verbose_name=u'状态', default=True, blank=True, editable=False)

    def __unicode__(self):
        return self.user.user.username

    class Meta:
        verbose_name = u'投资人收益信息'
        verbose_name_plural = u'投资人收益信息'
        ordering = ('user',)



#验证码
class Captcha(models.Model):
    imgName = models.CharField(max_length=100, verbose_name=u'文件名')
    code = models.CharField(max_length=10, verbose_name=u'验证码')
    localPath = models.CharField(max_length=150, verbose_name=u'存放位置')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'生成时间')
    class Meta:
        verbose_name = u'验证码'
        verbose_name_plural = u'验证码'
        ordering = ('created',)

#新闻报料
class News(models.Model):
    title = models.CharField(max_length=30, verbose_name=u'标题')
    abstract = models.TextField(max_length=100, verbose_name=u'摘要')
    context = UEditorField(u'新闻内容',height=200,width=500, default='',imagePath='upload/img',imageManagerPath="upload/imglib",toolbars="normal",options={"elementPathEnabled":True},filePath='upload/file',blank=False)
    thumbnail = models.ImageField(upload_to='upload/thumbnail', verbose_name=u'缩略图')

    createdTime = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    modifiedTime = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    status = models.BooleanField(verbose_name=u'状态', default=True, blank=True, editable=False)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'新闻报料'
        verbose_name_plural = u'新闻报料'
        ordering = ('title',)




#展示列表
class DisplayList(models.Model):
    refer_width = models.IntegerField(verbose_name=u'参考宽度', blank=True, default=0)
    refer_height = models.IntegerField(verbose_name=u'参考高度', blank=True, default=0)
    auto_play = models.BooleanField(verbose_name=u'自动轮播', blank=True, default=False)

    createdTime = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    modifiedTime = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    status = models.BooleanField(verbose_name=u'状态', default=True, blank=True, editable=False)

    class Meta:
        abstract = True

#展示新闻列表
class DisplayNewsList(DisplayList):
    type = models.CharField(verbose_name=u'展示类型', max_length=15, auto_created=True, default='news')

    def __unicode__(self):
        return self.type

    class Meta:

        verbose_name = u'展示新闻列表'
        verbose_name_plural = u'展示新闻列表'
        ordering = ('type', 'modifiedTime',)

#展示投资项列表
class DisplayInvestmentList(DisplayList):
    type = models.CharField(verbose_name=u'展示类型', max_length=15, auto_created=True, default='investment')

    def __unicode__(self):
        return self.type

    class Meta:

        verbose_name = u'展示投资项列表'
        verbose_name_plural = u'展示投资项目列表'
        ordering = ('type', 'modifiedTime',)

#展示单元
class Item(models.Model):
    desc = models.CharField(max_length=30, verbose_name=u'描述', blank=True, default=None)
    image = models.ImageField(upload_to='upload/image', verbose_name=u'显示图')

    createdTime = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    modifiedTime = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    status = models.BooleanField(verbose_name=u'状态', default=True, blank=True, editable=False)

    def __unicode__(self):
        return self.desc

    class Meta:
        abstract = True

#展示新闻
class NewsItem(Item):
    displayTo = models.ForeignKey(DisplayNewsList, verbose_name=u'展示新闻列表', related_name='items')
    itemId = models.ForeignKey(News, verbose_name=u'展示新闻', related_name='news')

    class Meta:
        verbose_name = u'展示新闻'
        verbose_name_plural = u'展示新闻'

#展示投资项
class InvestmentItem(Item):
    displayTo = models.ForeignKey(DisplayInvestmentList, verbose_name=u'展示投资项列表', related_name='items')
    itemId = models.ForeignKey(InvestmentProject, verbose_name=u'展示投资项', related_name='investment')

    class Meta:
        verbose_name = u'展示投资项'
        verbose_name_plural = u'展示投资项'
#版本
class VersionItem(models.Model):
    version = models.CharField(max_length=20, verbose_name=u'版本号')
    deviceOS = models.CharField(max_length=30, choices=deviceOSChoice, verbose_name=u'设备操作系统')
    url = models.URLField(verbose_name=u'版本更新链接', blank=True)
    createdTime = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    modifiedTime = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    status = models.BooleanField(verbose_name=u'状态', default=True, blank=True, editable=False)

    def __unicode__(self):
        return "os: %s, version: %s" % (self.deviceOS, self.version)

    class Meta:
        verbose_name = u'版本信息'
        verbose_name_plural = u'版本信息'
        ordering = ('deviceOS', 'modifiedTime',)

#删除投资人
@receiver(post_delete, sender=Investor)
def trans_post_delete(sender, instance, *args, **kwargs):
    if instance.user:
        instance.user.delete()

@receiver(pre_delete, sender=Investor)
def trans_pre_delete(sender, instance, *args, **kwargs):
    investor = Investor.objects.get(pk=instance.id)
    for investment in Investment.objects.filter(investor=investor):
        investment.project.haveInvestment -= investment.investMoney
        investment.project.save()
