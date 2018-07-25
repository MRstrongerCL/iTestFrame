# coding:utf-8
# !/bin/sh
# chenliang 2017-08-29
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass
import inspect
import unittest
import requests         #不能删除，子用例中会用到
from unittest import main             #不能删除，用例继承时会用到
from Lib.LogService import logger
from Lib.InterfaceFunc.initInterfaceTest import InitToken
from Lib.InterfaceFunc.InterfaceSession import InterfaceSession
from Lib.InterfaceFunc.InterfacePublicMethods import InterfacePublicMethods as Interface
from Lib.InterfaceFunc.InterfaceConfig import V0_Interface

class SqliteManager(object):
    '''存放用户信息，当前用于存放token和providerid'''
    inToken = InitToken()
    info = inToken.initTestInterface()
    provider_id = int(info[0])
    token = info[1]
    user_id = info[2]

def get_current_function_name():
        return inspect.stack()[1][3]

def setUpModule():
   pass

class MyTestCase(unittest.TestCase):
    '''
    根据项目特点自己重新封装TestCase类
    '''

    def logCaseID(self,casename):
         logger.info('[CaseID]:'+ casename)

    def logStep(self,msg):
        logger.info("[Step]:" + msg)

    def SetCaseExecuteSuccess(self):
        self.exe_status = 1

    @classmethod
    def setUpClass(cls):
        # 单个用例unittest调试时，将必须初始化logger
        # logger.initLogger()
        logger.info("======================= SetUp Class Start =====================")

    def setUp(self):
        logger.info("------------------------- SetUp Start -------------------------")
        self.exe_status = 0

    def tearDown(self):
        logger.info("------------------------ tearDown Start -----------------------")
        # logger.SplitScriptLog()

    @classmethod
    def tearDownClass(cls):
        logger.info("==================== TearDown Class Start =====================")

def tearDownModule():
    pass

if __name__=="__main__":
    unittest.main()
