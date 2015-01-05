__author__ = 'taoluo'
# coding=utf8

from rest_framework import serializers

from models import *

from rest_framework import pagination


#投资项目系列化
class InvestmentProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentProject
        fields = ('id', 'name', 'desc', 'companyCode', 'companyDesc', \
                  'creditLevel', 'guaranteeInstitution', 'guaranteeOpinion', \
                  'fundingUsing', 'paymentSource', 'pledge', 'riskControl', \
                  'annualEarnings', 'repayDate', 'consumeTransferPeriod', \
                  'computeInvestmenmentMethod', 'financing', 'haveInvestment', \
                  'investmentStartPoint', 'addingUnit')


#投资项目分页序列化
class PaginatedInvestmentProjectSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = InvestmentProjectSerializer


#投资人序列化
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class InvestorSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='user', many=False)
    class Meta:
        model = Investor
        fields = ('user', 'id', 'phone_number', 'payment_password')

#投资人对应投资项目序列化
class InvestmentSerializer(serializers.ModelSerializer):
    project = InvestmentProjectSerializer(many=False)
    investor = InvestorSerializer(many=False)
    class Meta:
        model = Investment
        fields = ('investor', 'project', 'investMoney', 'modifiedTime')

#投资人对应的投资详情
class InvestorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorInfo
        fields = ('remainingFund', 'forzenFund', 'waittingEarning', 'waittingCost','totalEarning', 'totalInvestment',)


#投资人对应投资项目分页
class PaginatedInvestmentSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = InvestmentSerializer

#新闻报料序列化
class NewsSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.URLField(source='thumbnail.url', read_only=True)
    thumbnail_width = serializers.IntegerField(source='thumbnail.width', read_only=True)
    thumbnail_height = serializers.IntegerField(source='thumbnail.height', read_only=True)
    class Meta:
        model = News
        fields = ('id', 'title', 'abstract', 'context', 'thumbnail_url', 'thumbnail_width', 'thumbnail_height')

#新闻报料摘要序列化
class NewsShortSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.URLField(source='thumbnail.url', read_only=True)
    thumbnail_width = serializers.IntegerField(source='thumbnail.width', read_only=True)
    thumbnail_height = serializers.IntegerField(source='thumbnail.height', read_only=True)
    class Meta:
        model = News
        fields = ('id', 'title', 'abstract', 'thumbnail_url', 'thumbnail_width', 'thumbnail_height')

#新闻报料分页
class PaginatedNewsSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = NewsShortSerializer

#展示新闻单元序列化
class NewsItemSerializer(serializers.ModelSerializer):
    image_url = serializers.URLField(source='image.url', read_only=True)
    itemId = serializers.CharField(source='itemId.id', read_only=True)

    class Meta:
        model = NewsItem
        fields = ('desc', 'image_url', 'itemId')

#展示投资项单元序列化
class InvestmentItemSerializer(serializers.ModelSerializer):
    image_url = serializers.URLField(source='image.url', read_only=True)
    itemId = serializers.CharField(source='itemId.id', read_only=True)

    class Meta:
        model = InvestmentItem
        fields = ('desc', 'image_url', 'itemId')

#展示新闻列表序列化
class DisplayNewsListSerializer(serializers.ModelSerializer):
    items = NewsItemSerializer(many=True)

    class Meta:
        model = DisplayNewsList
        fields = ('refer_width', 'refer_height', 'auto_play', 'type', 'items',)

#展示投资项列表序列化
class DisplayInvestmentListSerializer(serializers.ModelSerializer):
    items = InvestmentItemSerializer(many=True)

    class Meta:
        model = DisplayInvestmentList
        fields = ('refer_width', 'refer_height', 'auto_play', 'type', 'items',)

#版本序列化
class versionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionItem
        fields = ('version', 'deviceOS', 'url')