# Create your views here.
# coding=utf8
from django.contrib.auth.hashers import make_password
from django.core.context_processors import csrf
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from utils.utils import get_port, random_str
from validateCodeImage import create_validate_code
from serializers import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta
from models import displayType as displayType
from django.conf import settings
from django.contrib.auth import authenticate
import os
import logging

ERROR_MESSAGE = 'error message'
ERROR_CODE = 'error code'

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
MEDIA_ROOT = settings.MEDIA_ROOT
CODE_ROOT = os.path.join(MEDIA_ROOT, r'code')

CAPTCHA_OVERTIME = 5 #验证码的过期时间，单位为分钟

logger = logging.getLogger(__name__)

#得到csrf
@api_view(['GET'])
def get_csrf(request):
    c = {}
    c.update(csrf(request))
    return Response(c, status=status.HTTP_200_OK)

#验证码图片
@api_view(['GET'])
def generate_code_response(request):
    if request.DATA.get("imgName"):
        try:
            captcha = Captcha.objects.select_for_update().get(imgName=request.DATA.get("imgName"))
            os.system('rm -f ' + captcha.localPath)
            captcha.delete()
        except Captcha.DoesNotExist:
            pass

    ipAddress = get_client_ip(request)
    iphash = hashlib.md5(ipAddress).hexdigest()
    imgName = random_str(suffix=iphash)
    try:
        captcha = Captcha.objects.select_for_update().get(imgName=imgName)
        os.system('rm -f ' + captcha.localPath)
        captcha.delete()
    except Captcha.DoesNotExist:
        pass

    code, imgPath, imgURL = generate_code_image(request, imgName)
    captcha = Captcha(imgName=imgName, code=code.strip().lower(), localPath=imgPath)
    captcha.save()
    return Response({"code_image_url": imgURL, "imgName": imgName}, status=status.HTTP_200_OK)


#投资人注册
@api_view(['POST'])
def register_investor(request):
    serializer = InvestorSerializer(data=request.DATA)
    if serializer.is_valid():
        imgName = request.DATA.get("imgName")
        flag = validation(imgName, request.DATA.get('code'))
        if flag == 1:
            return Response(get_error_message("Captcha isn't existed", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)
        if flag == 2:
            return Response(get_error_message("Captcha is overtime", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)
        if flag == 3:
            return Response(get_error_message("Captcha error", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)

        raw_pwd = serializer.object.user.password
        serializer.object.user.set_password(raw_pwd)
        serializer.save()
        inverstor = serializer.object
        token = Token.objects.get_or_create(user=inverstor.user)
        serializer.data['Token'] = token[0].key
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.DATA.get('user'):
        username = request.DATA['user'].get('username')
        try:
            if User.objects.get(username=username):
                return Response(get_error_message("Username is existed", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            pass
    return Response(get_error_message("Data serializer error", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)


#投资人登录
@api_view(['POST'])
def login_investor(request):
    data = request.DATA
    if data:
        try:
            user = User.objects.get(username=data['username'])
            if not user:
                return Response(get_error_message("user isn't existed", status.HTTP_404_NOT_FOUND),
                                status=status.HTTP_404_NOT_FOUND)
            if not user.check_password(data['password']):
                return Response(get_error_message("password isn't right", status.HTTP_403_FORBIDDEN),
                                status=status.HTTP_403_FORBIDDEN)

            imgName = request.DATA.get("imgName")
            flag = validation(imgName, request.DATA.get('code'))
            if flag == 1:
                return Response(get_error_message("Captcha isn't existed", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)
            if flag == 2:
                return Response(get_error_message("Captcha is overtime", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)
            if flag == 3:
                return Response(get_error_message("Captcha error", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)

            token = Token.objects.get_or_create(user=user)
            investor = Investor.objects.get(user=user)
            return Response({"Token": token[0].key, "id": investor.id}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(get_error_message("User isn't exsited", status.HTTP_404_NOT_FOUND),
                            status=status.HTTP_404_NOT_FOUND)
        except Investor.DoesNotExist:
            return Response(get_error_message("Investor isn't exsited", status.HTTP_404_NOT_FOUND),
                            status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(get_error_message("Username or password haven't provided", status.HTTP_400_BAD_REQUEST),
                            status=status.HTTP_400_BAD_REQUEST)

    return Response(get_error_message("User isn't exsited", status.HTTP_404_NOT_FOUND),
                    status=status.HTTP_400_BAD_REQUEST)

#投资人信息更新
@api_view(['GET','PUT'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def update_investor(request, pk):
    try:
       investor = Investor.objects.get(pk=pk)
    except Investor.DoesNotExist:
            return Response(get_error_message("Investor isn't exsited", status.HTTP_404_NOT_FOUND),
                            status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InvestorSerializer(instance=investor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        if request.DATA.get('user'):
            username = request.DATA['user'].get('username')
            if username != investor.user.username:
                return Response(get_error_message("Username can't be updated", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)

            new_pwd = request.DATA['user'].get('new_password')
            if new_pwd: #存在新密码需要更新
                if not investor.user.check_password(request.DATA['user'].get('password')): #判断旧密码是否正确
                    return Response(get_error_message("Old password isn't right", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)

        serializer = InvestorSerializer(instance=investor, data=request.DATA)
        if serializer.is_valid():
            new_pwd = request.DATA['user'].get('new_password')
            if new_pwd:    #存在新密码需要更新
                serializer.object.user.set_password(new_pwd)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(get_error_message("Data serializer error", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)


#投资人注销
@api_view(['GET'])
def logout_investor(request):
    tokenStr = request.QUERY_PARAMS.get('Token')
    try:
        token = Token.objects.get(key=tokenStr)
        token.delete()
    except Token.DoesNotExist:
        return Response(get_error_message("token isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
    return Response({'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)


#投资人投资
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated, ))
def invest_project(request):
    (investor, investment_project, response) = invest_parameter_normalize(request)
    if response:
       return response
    try:
        money = float(request.QUERY_PARAMS.get('money'))
        investorInfo, infoCreated = InvestorInfo.objects.select_for_update().get_or_create(user=investor, defaults={'user': investor})
        if money > investor_info.remainingFund:
            return Response(get_error_message("Remaining sum isn't enough", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)

        interval = investment_project.repayDate - timezone.now()
        if interval <= 1:
            return Response(get_error_message("Inerval days aren't enough", status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)

        investment = Investment(project=investment_project, investor=investor, investMoney=money)
        investment.save()
    except ValueError, e:
        return Response(get_error_message(str(e), status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)


    investorInfo.totalInvestment += money
    investorInfo.remainingFund -= money
    investorInfo.waittingCost += money

    earning = investment_project.annualEarnings / 365 * money * (interval.days - 1)
    investorInfo.waittingEarning += earning
    investorInfo.save()

    return Response({'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)


# #投资人追加投资
# @api_view(['GET'])
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated, ))
# def add_invest_project(request):
#     (investor, investment_project, response) = invest_parameter_normalize(request)
#     if response:
#        return response
#
#     try:
#         investment =  Investment.objects.get(project=investment_project, investor=investor)
#     except Investment.DoesNotExist:
#         return Response(get_error_message("Investment isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
#
#     money = float(request.QUERY_PARAMS.get('money'))
#     investment.additionalMoneyLastTime = money * investment_project.addingUnit
#     try:
#         investment.save()
#     except ValueError, e:
#         return Response(get_error_message(str(e), status.HTTP_403_FORBIDDEN), status=status.HTTP_403_FORBIDDEN)
#
#     return Response({'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)

#投资人投资的项目
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated, ))
def investor_info(request):
    username = request.QUERY_PARAMS.get('username')
    if not username:
        return Response(get_error_message("Username isn't been provided", status.HTTP_400_BAD_REQUEST), status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        investor = Investor.objects.get(user=user)
    except Investor.DoesNotExist:
        return Response(get_error_message("Investor isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(get_error_message("Investor isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)

    queryset = Investment.objects.filter(investor=investor)
    serializer = paging(queryset, request, PaginatedInvestmentSerializer)
    return Response(serializer.data, status=status.HTTP_200_OK)


#分页投资项目
@api_view(['GET'])
def get_inverst_project(request):
    queryset = InvestmentProject.objects.order_by('name')
    serializer = paging(queryset, request, PaginatedInvestmentProjectSerializer)
    return Response(serializer.data)

#单个投资项目
@api_view(['GET'])
def get_single_inverstment(request):
    pid = request.QUERY_PARAMS.get('id')
    if not pid:
        return Response(get_error_message("Investment project id should be provided", status.HTTP_400_BAD_REQUEST), status=status.HTTP_400_BAD_REQUEST)
    try:
        investment = InvestmentProject.objects.get(pk=pid)
    except InvestmentProject.DoesNotExist:
        return Response(get_error_message("Investment project isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)

    serializer = InvestmentProjectSerializer(investment)
    return Response(serializer.data, status=status.HTTP_200_OK)

#新闻报料
@api_view(['GET'])
def get_news(request):
    queryset = News.objects.order_by('title')
    serializer = paging(queryset, request, PaginatedNewsSerializer)
    protocal = get_port(request.META['SERVER_PROTOCOL'])
    if serializer.data.get('results'):
        for item in serializer.data.get('results'):
            if item and item.get('thumbnail_url'):
                item['thumbnail_url'] = "".join([protocal, "://", str(request.META['HTTP_HOST']), item['thumbnail_url']])
    return Response(serializer.data)

#单个新闻报料
@api_view(['GET'])
def get_single_news(request):
    pid = request.QUERY_PARAMS.get('id')
    if not pid:
        return Response(get_error_message("News id should be provided", status.HTTP_400_BAD_REQUEST), status=status.HTTP_400_BAD_REQUEST)
    try:
        news = News.objects.get(pk=pid)
    except News.DoesNotExist:
        return Response(get_error_message("News isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)

    serializer = NewsSerializer(news)
    for item in serializer.data:
        if item and item == 'thumbnail_url':
            protocal = get_port(request.META['SERVER_PROTOCOL'])
            serializer.data['thumbnail_url'] = "".join([protocal, "://", str(request.META['HTTP_HOST']), serializer.data['thumbnail_url']])
    return Response(serializer.data, status=status.HTTP_200_OK)

#投资人信息
@api_view(['GET'])
def get_investor_info(request):
    username = request.QUERY_PARAMS.get('username')
    if not username:
        return Response(get_error_message("Username isn't been provided", status.HTTP_400_BAD_REQUEST), status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        investor = Investor.objects.get(user=user)
        investor_info = InvestorInfo.objects.get(user=investor)
    except Investor.DoesNotExist:
        return Response(get_error_message("Investor isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(get_error_message("Investor isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
    except InvestorInfo.DoesNotExist:
        investor_info = InvestorInfo(user=investor)

    serializer = InvestorInfoSerializer(instance=investor_info)
    return Response(serializer.data, status=status.HTTP_200_OK)



#显示轮转信息
@api_view(['GET'])
def get_display_info(request):
    type = request.QUERY_PARAMS.get('type')
    flag = False
    for item in displayType:
        if item[0] == type:
            flag = True
            break

    if not flag:
        return Response(data={}, status=status.HTTP_200_OK)

    if type == 'news':
        querySet = DisplayNewsList.objects.filter(type=type).order_by('modifiedTime')
    else:
        querySet = DisplayInvestmentList.objects.filter(type=type).order_by('modifiedTime')

    protocal = get_port(request.META['SERVER_PROTOCOL'])
    if querySet:
        if type == 'news':
            serializer = DisplayNewsListSerializer(querySet[0])
        else:
            serializer = DisplayInvestmentListSerializer(querySet[0])

        items = serializer.data.get('items')
        if items:
            for item in items:
                item['image_url'] = "".join([protocal, "://", str(request.META['HTTP_HOST']), item['image_url']])
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    return Response(data={}, status=status.HTTP_200_OK)

#版本信息
@api_view(['GET'])
def get_version_ios(request):
    return get_version_info('ios')

@api_view(['GET'])
def get_version_android(request):
    return get_version_info('Android')

def get_version_info(osType):
    versionInfo = VersionItem.objects.filter(deviceOS=osType.strip())
    if versionInfo and len(versionInfo) > 0:
        serializer = versionItemSerializer(versionInfo[0])
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(data={}, status=status.HTTP_200_OK)

#分页信息
def paging(queryset, request, pageSerializer):
    num = request.QUERY_PARAMS.get('num')
    if not num:
        num = 8
    else:
        try:
            num = int(num)
            if num <= 0 or num > 8:
                num = 8
        except ValueError:
            num = 8
    page = request.QUERY_PARAMS.get('page')
    paginator = Paginator(queryset, num)
    try:
        inverst_project_set = paginator.page(page)
    except PageNotAnInteger:
        inverst_project_set = paginator.page(1)
    except EmptyPage:
        inverst_project_set = paginator.page(paginator.num_pages)
    serializer_context = {'request': request}
    serializer = pageSerializer(inverst_project_set, context=serializer_context)
    return serializer

#投资项目参数判断
def invest_parameter_normalize(request):
    project_id = request.QUERY_PARAMS.get('project_id')
    username = request.QUERY_PARAMS.get('username')
    if not project_id:
        return None, None, Response(get_error_message("Project id isn't provided", status.HTTP_400_BAD_REQUEST), status=status.HTTP_400_BAD_REQUEST)
    if not username:
        return None, None, Response(get_error_message("Username isn't provided", status.HTTP_400_BAD_REQUEST), status=status.HTTP_400_BAD_REQUEST)

    money = request.QUERY_PARAMS.get('money')
    if not money:
        return None, None, Response(get_error_message("Invest money isn't provided", status.HTTP_400_BAD_REQUEST), status=status.HTTP_400_BAD_REQUEST)
    try:
        money = float(money)
    except ValueError:
        return None, None, Response(get_error_message("Invest money can't be convert to number", status.HTTP_400_BAD_REQUEST), status=status.HTTP_400_BAD_REQUEST)

    try:
        investment_project = InvestmentProject.objects.select_for_update().get(id=project_id)
        if not investment_project:
            return None, None, Response(get_error_message("Investment project isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
    except InvestmentProject.DoesNotExist:
        return None, None, Response(get_error_message("Investment project isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
    try:
        user = User.objects.get(username=username)
        investor = Investor.objects.get(user=user)
    except Investor.DoesNotExist:
        return None, None, Response(get_error_message("Investor isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return None, None, Response(get_error_message("Investor isn't existed", status.HTTP_404_NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
    return investor, investment_project, None

#产生验证图片
def generate_code_image(request, imgName):
    img_code = create_validate_code()
    imgName = ".".join([imgName, 'gif'])
    imgPath = os.path.join(CODE_ROOT, imgName)
    img_code[0].save(imgPath,  "GIF")
    logger.info("start generate code and image")
    logger.error("start generate code and image")
    protocal = get_port(request.META['SERVER_PROTOCOL'])
    imgURL = "".join([protocal, "://", str(request.META['HTTP_HOST']), settings.MEDIA_URL + "code/", imgName])
    return (img_code[1], imgPath, imgURL)

#验证码效验
# 0表示正确 1表示验证码不存在 2表示验证码超时 3表示验证码错误
def validation(imgName, code):
    try:
       captcha = Captcha.objects.select_for_update().get(imgName=imgName)
    except Captcha.DoesNotExist:
        return 1

    interval = timezone.now() - captcha.created
    if interval.days < 0 or interval.seconds < 0 or interval.microseconds < 0:
        return 2
    if (timezone.now() - captcha.created) > timedelta(minutes=CAPTCHA_OVERTIME):
        os.system('rm -f ' + captcha.localPath)
        captcha.delete()
        return 2

    if code and code.strip().lower() == captcha.code:
        os.system('rm -f ' + captcha.localPath)
        captcha.delete()
        return 0
    return 3


#得到客户端ip地址
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


#出错信息
def get_error_message(error_message=None, error_code=None):
    message = {}
    message[ERROR_MESSAGE] = error_message
    message[ERROR_CODE] = error_code
    return message


