# coding=utf8
__author__ = 'taoluo'

import os
import time
import threading
from django.utils import timezone
from datetime import tzinfo, datetime, timedelta
from models import *
from rest_framework.authtoken.models import Token
from django.db import transaction
from utils.utils import get_crontab_configuration

import logging

rootPath = os.path.dirname(os.path.realpath(__file__))
filePath = rootPath + "/../configuration/"

logger = logging.getLogger(__name__)


class UTC(tzinfo):
    """UTC"""
    def __init__(self,offset = 0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)

class ComputeInterest(threading.Thread):
    def __init__(self, fileName):
        threading.Thread.__init__(self)
        self.isRun = True
        currentTime = timezone.now()
        self.currentTime = datetime(currentTime.year, currentTime.month, currentTime.day, 0, 0, 0)
        self.setDaemon(False)
        self.fileName = fileName

    @transaction.commit_manually
    def run(self):
        logger.info("start ComputeInterest threading...")
        path = filePath + self.fileName
        while self.isRun:
            flag = get_crontab_configuration(path, "ComputeInterest")
            if not flag or flag.strip() == "False":
                break
            currentTime = timezone.now()
            curTime = timezone.now()
            interval = currentTime - self.currentTime

            #每天00时刻左右更新
            if interval.days >= 1:
                self.currentTime = currentTime
                investments = Investment.objects.filter(status=True)
                for investment in investments:
                    invest_project = investment.project
                    investor = investment.investor

                    #到达还款日期
                    if curTime >= invest_project.repayDate:
                        try:
                            inverstorInfo = InvestorInfo.objects.select_for_update().get(user=investor)
                            inverstorInfo.remainingFund += investment.investMoney #更新余额
                            inverstorInfo.waittingCost -= investment.investMoney #更新待收成本
                            interval_days = invest_project.repayDate - investment.modifiedTime

                            #计算利息
                            if interval_days.days <= 0:
                                transaction.commit()
                                continue
                            money = interval_days.days * invest_project.annualEarnings / 365 * investment.investMoney
                            # investment.modifiedTime = curTime

                            inverstorInfo.remainingFund += money #更新余额
                            inverstorInfo.waittingEarning -= money #更新待收收益
                            inverstorInfo.totalEarning += money #更新累计收益
                            inverstorInfo.save()

                        except InvestorInfo.DoesNotExist:
                            transaction.rollback()
                            continue
                        investment.investMoney = 0
                        investment.status = False
                        investment.save()
                        transaction.commit()
                        continue

                    transferPeriodDays = invest_project.consumeTransferPeriod * 30
                    interval_days = curTime - investment.modifiedTime

                    #到达周转周期
                    if interval_days.days >= transferPeriodDays:
                        try:
                            inverstorInfo = InvestorInfo.objects.select_for_update().get(user=investor)
                            money = interval_days.days * invest_project.annualEarnings / 365 * investment.investMoney
                            investment.modifiedTime = curTime
                            investment.save()
                            inverstorInfo.remainingFund += money #更新余额
                            inverstorInfo.waittingEarning -= money #更新待收收益
                            inverstorInfo.totalEarning += money #更新累计收益
                            inverstorInfo.save()
                        except InvestorInfo.DoesNotExist:
                            transaction.rollback()
                            continue
                        else:
                            transaction.commit()
            time.sleep(3)

        logger.info("close ComputeInterest threading...")


class ClearCaptcha(threading.Thread):
    def __init__(self, fileName):
        threading.Thread.__init__(self)
        self.isRun = True
        self.setDaemon(False)
        self.fileName = fileName

    @transaction.commit_manually
    def run(self):
        logger.info("start ClearCaptcha thread ...")
        path = filePath + self.fileName
        while self.isRun:
            flag = get_crontab_configuration(path, "ClearCaptcha")
            if not flag or flag.strip() == "False":
                break
            try:
                captchas = Captcha.objects.filter(created__lt=(timezone.now()-timedelta(minutes=5)))
                for captcha in captchas:
                    os.system('rm -f ' + captcha.localPath)
                    captcha.delete()
                    transaction.commit()
            except:
                transaction.rollback()
            else:
                transaction.commit()
            time.sleep(6*60)
        logger.info("close ClearCaptcha thread ...")

class ClearToken(threading.Thread):
    def __init__(self, fileName):
        threading.Thread.__init__(self)
        self.isRun = True
        self.fileName = fileName
        self.setDaemon(False)

    @transaction.commit_manually
    def run(self):
        logger.info("start ClearToken thread ...")
        path = filePath + self.fileName
        while self.isRun:
            flag = get_crontab_configuration(path, "ClearToken")
            if not flag or flag.strip() == "False":
                break
            try:
                tokens = Token.objects.filter(created__lt=(timezone.now()-timedelta(days=7)))
                for token in tokens:
                    token.delete()
                    transaction.commit()
            except:
                transaction.rollback()
            else:
                transaction.commit()
            time.sleep(6*60)
        logger.info("close ClearToken thread...")

def openCrontab(fileName):
    computeInterest = ComputeInterest(fileName)
    computeInterest.start()
    clearCaptcha = ClearCaptcha(fileName)
    clearCaptcha.start()
    clearToken = ClearToken(fileName)
    clearToken.start()


