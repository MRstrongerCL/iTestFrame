# -*- coding:utf-8 -*-
#!usr/bin/sh
'''
Author: chenliang
Created Time: 2017/8/24
Describtion: Test Engine
'''

import os
import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf8')
    cur_dir = os.path.dirname(__file__)
    # cur_dir =cur_dir + "../.."
    cur_dir =os.path.split(cur_dir)[0]
    sys.path.append(cur_dir)
    # print('WorkSpace:',cur_dir)
except Exception as e:
    print e

import time
import datetime
import getopt
import unittest
import HTMLTestRunner
from HTMLTestRunner import _TestResult
from unittest import registerResult
from Lib import MyThread
from Lib.LogService import ROOT_DIR
from Lib.LogService import LOG_ROOT_DIR
from Lib.LogService import CreateTempTable
from Lib.LogService import WriteCaseTimeCsvTitle
from Lib.LogService import WriteCaseTimeCsvData
from Lib.LogService import Concurrent_Analysis
from Lib.LogService import logger
from Lib.ParserConfigUnit import Parser_Config
from Lib.ParserConfigUnit import Parse_config_Set
from Lib.ParserConfigUnit import TestEngineConfigName

# =========================== 常量 配置 ==============================
SCRIPTS_ROOT_DIR = 'Scripts'

# =========================== 重写python unittest 自带的方法 =====================
class MyTestLoader(unittest.TestLoader):

    def discover(self, start_dir, pattern='test*.py', top_level_dir=None):
        set_implicit_top = False
        if top_level_dir is None and self._top_level_dir is not None:
            # make top_level_dir optional if called from load_tests in a package
            top_level_dir = self._top_level_dir
        elif top_level_dir is None:
            set_implicit_top = True
            top_level_dir = start_dir

        top_level_dir = os.path.abspath(top_level_dir)

        if not top_level_dir in sys.path:
            # all test modules must be importable from the top level directory
            # should we *unconditionally* put the start directory in first
            # in sys.path to minimise likelihood of conflicts between installed
            # modules and development versions?
            sys.path.insert(0, top_level_dir)
        self._top_level_dir = top_level_dir

        is_not_importable = False
        if os.path.isdir(os.path.abspath(start_dir)):
            start_dir = os.path.abspath(start_dir)
            if start_dir != top_level_dir:
                is_not_importable = not os.path.isfile(os.path.join(start_dir, '__init__.py'))
        else:
            # support for discovery from dotted module names
            try:
                __import__(start_dir)
            except ImportError:
                is_not_importable = True
            else:
                the_module = sys.modules[start_dir]
                top_part = start_dir.split('.')[0]
                start_dir = os.path.abspath(os.path.dirname((the_module.__file__)))
                if set_implicit_top:
                    self._top_level_dir = self._get_directory_containing_module(top_part)
                    sys.path.remove(top_level_dir)

        if is_not_importable:
            raise ImportError('Start directory is not importable: %r' % start_dir)

        tests = list(self._find_tests(start_dir, pattern))
        return tests

class MyTextTestRunner(unittest.TextTestRunner):
    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None):
        unittest.TextTestRunner.__init__(self,stream=sys.stderr, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None)

    def run(self,test,loopcount=1,thread_count=1,timesleep=0,looptime=None):
        "Run the given test case or test suite."
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        startTime = time.time()
        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            if loopcount > 1:
                for i in range(loopcount):
                    thr = MyThread.thread_2()
                    thr(test,(result,),thread_count)
                    time.sleep(timesleep)
            elif loopcount <= 1 and looptime != None:
                time_s = time.time()
                use_time = 0
                while use_time <= looptime:
                    thr = MyThread.thread_2()
                    thr(test, (result,), thread_count)
                    time.sleep(timesleep)
                    time_e = time.time()
                    use_time = time_e - time_s
            else:
                thr = MyThread.thread_2()
                thr(test, (result,), thread_count)
            # test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
        stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        return result

class MyHTMLTestRunner(HTMLTestRunner.HTMLTestRunner):

    def __init__(self, stream=sys.stdout, verbosity=1, title=None, description=None):
        HTMLTestRunner.HTMLTestRunner.__init__(self, stream=stream, verbosity=verbosity, title=title, description=description)

    def run(self, test, loopcount=1,thread_count=1,timesleep=0,looptime=None):
        "Run the given test case or test suite."
        result = _TestResult(self.verbosity)
        # test(result)
        if loopcount > 1:
            for i in range(loopcount):
                thr = MyThread.thread_2()
                thr(test, (result,), thread_count)
                time.sleep(timesleep)
        elif loopcount <= 1 and looptime != None:
            time_s = time.time()
            use_time = 0
            while use_time <= looptime:
                thr = MyThread.thread_2()
                thr(test, (result,), thread_count)
                time.sleep(timesleep)
                time_e = time.time()
                use_time = time_e - time_s
        else:
            thr = MyThread.thread_2()
            thr(test, (result,), thread_count)
        self.stopTime = datetime.datetime.now()
        self.generateReport(test, result)
        print >>sys.stderr, '\nTime Elapsed: %s' % (self.stopTime-self.startTime)
        return result

# ========================================= 测试引擎 =======================================
class Engine(object):
    '''
    Test Engine
    :param:
    scriptsDir: 脚本所在根目录
    loopCounts: 循环执行用例集次数
    sleeptime: 循环执行时的间隔时间 单位：H、M、S
    thread_count: 用例集并发执行个数
    suite_type:  '0','1','2','3','4'  默认'0'
        '0' 默认执行scripts 下所有脚本
        '1' 执行 scripts 下的 指定的所有文件夹 使用反斜杠'/'
        '2' 执行 python文件名称 也是文件Class的名称 'testSample5','testSample1'
        '3' 执行 用例名称'test_Sample_2','test_Sample_4'
        '4' 执行 脚本的tag名称 'slave','main','smoke','master'
        '5' 非法 suite_type
    suite_params: 指定用例集列表， 与 suite_type 对应，可以是以下：
        [] : 空列表
        ['Sample/sampledir1','Sample/sampledir2'] : 文件夹列表
        ['testSample5','testSample1'] : 文件（脚本名称）列表
        ['test_Sample_2','test_Sample_4'] : 用例名称列表
        ['smoke', 'main']) : 脚本 tag 列表
    loopTime: 循环执行时间 单位：H、M、S
    '''
    Scripts_Dir = os.path.join(ROOT_DIR, SCRIPTS_ROOT_DIR)

    def __init__(self):
        # self.tests=[]
        self.scriptsDir = self.Scripts_Dir
        self.enginefile = TestEngineConfigName
        self.testBed = Parser_Config(self.enginefile,'TestParams','TestBedName')
        self.loopCounts = 1
        self.sleeptime = 0
        self.thread_count = 1
        self.suite_type = '0'
        self.suite_params = []
        self.loopTime = None
        self.responseTimeout = 20
        self.responseTimesplit = 5
        self.model = '1'

    def importLib(self,caselist):
        # get all tests from SearchProductTest and HomePageTest class
        self.caselist = caselist
        for casename in caselist:
            __import__(casename)

    def BuildTestSuite(self):
        '''
        dsc: 构造用例集
        :return:
        '''
        # Config Test Suite
        testloader = MyTestLoader()

        # Methods 1  执行Scripts下的文件夹下的所有脚本
        if self.suite_type == '0':
            # self.discoverSuite = testloader.discover(self.scriptsDir,pattern="test*.py")
            Suite = testloader.discover(self.scriptsDir,pattern="test*.py")

        # Methods 2  执行指定所有目录下的所有脚本
        elif self.suite_type == '1':
            Suite = []
            for s_dir in self.suite_params:
                dir_names = s_dir.split('/')
                target_dir = self.scriptsDir
                for name in dir_names:
                    target_dir = os.path.join(target_dir,name)
                tests = list(testloader.discover(target_dir, pattern="test*.py",top_level_dir=self.scriptsDir))
                Suite += tests
            # self.discoverSuite = testloader.suiteClass(Suite)

        # Methods 3  执行指定所有文件下的所有脚本
        elif self.suite_type == '2':
            tests = list(testloader.discover(self.scriptsDir, pattern="test*.py"))
            Suite = []
            for test in tests:
                for name in self.suite_params:
                    script_name = (str(test).split(' testMethod')[0]).split('.')[-1]
                    if name == script_name:
                        Suite.append(test)
                        break
            # self.discoverSuite = testloader.suiteClass(Suite)

        # Methods 4  执行指定所有用例名称的用例
        elif self.suite_type == '3':
            testloader = MyTestLoader()
            tests = list(testloader.discover(self.scriptsDir, pattern="test*.py"))
            Suite = []
            for test in tests:
                for name in self.suite_params:
                    # case_name = (str(test).split('=')[-1]).split('>')[0]
                    case_name = str(test)
                    # if name == case_name:
                    if name in case_name:
                        a_tests = test._tests
                        for _tests in a_tests:
                            for _test in _tests._tests:
                                if name == _test._testMethodName:
                                    Suite.append(_test)
                        # Suite.append(test)
            # self.discoverSuite = testloader.suiteClass(Suite)

        # Methods 5  执行指定所有tag的用例
        elif self.suite_type == '4':
            tests = list(testloader.discover(self.scriptsDir, pattern="test*.py"))
            Suite = []
            for test in tests:
                if ' testMethod' in str(test):
                    moudle_name = SCRIPTS_ROOT_DIR + '.' + (str(test).split(' testMethod')[0]).split('<')[-1]
                    moudle_name_list = moudle_name.split('.')
                    class_name = moudle_name_list[-1]
                    script_moudle_name = '.'.join(moudle_name_list[:-1])
                    __import__(script_moudle_name)
                    moudle = sys.modules[script_moudle_name]
                    for name in self.suite_params:
                        # if name.lower() == moudle.TAG.lower():
                        if hasattr(moudle,'TAG'):
                            if name in moudle.TAG and test not in Suite:
                                Suite.append(test)
                                break
            # self.discoverSuite = testloader.suiteClass(Suite)
        else:
            raise Exception('Has No this suite_type : "%s" not in ["0","1","2","3","4"]' % self.suite_type)
        # Methods 6  （测试文件名 与类名 一致）
        # for casename in caselist:
        #     test = unittest.TestLoader().loadTestsFromTestCase(getattr(sys.modules[casename],casename))
        #     self.tests.append(test)
        # self.runtests = unittest.TestSuite(self.tests)
        # Methods 7  (测试文件与引擎在同一目录)
        # self.runtests = unittest.TestSuite()
        #
        # for moudle_name in self.caselist:
        #     t_moudle = sys.modules[moudle_name]
        #     for class_name in dir(t_moudle):
        #         t_class = getattr(t_moudle,class_name)
        #         for case_name in dir(t_class):
        #             matcher = re.compile("^test.*")
        #             if matcher.search(case_name):
        #                 self.runtests.addTest(t_class(case_name))
        # Methods 8  （测试文件在引擎所在目录下的文件夹下）
        # if int(self.loopCounts) > 1 and self.sleeptime==0:
        #     Suite = Suite * int(self.loopCounts)
        self.discoverSuite = testloader.suiteClass(Suite)
        return True


    def loghtml(self,logdir=None):

        # get the directory path to output report file
        if logdir == None:
            result_dir = LOG_ROOT_DIR
        else:
            result_dir = os.path.abspath(logdir)
        # open the report file
        outfile = open(result_dir + '\TestReport.html', 'w')

        # configure HTMLTestRunner options
        # 单线程不调用多线程功能
        # self.runner = HTMLTestRunner.HTMLTestRunner(stream=outfile,
        #                                        title='Test Report',
        #                                        description='Smoke Tests')
        # 调用多线程功能
        self.runner = MyHTMLTestRunner(stream=outfile,title='Test Report',description='Smoke Tests')

    def logtext(self):
        # 单线程不调用多线程功能
        # self.runner = unittest.TextTestRunner()
        # 调用多线程功能
        self.runner = MyTextTestRunner()

    def run(self):
        # run the suite
        self.runner.run(self.discoverSuite,self.loopCounts,self.thread_count,self.sleeptime,self.loopTime)

def EngineRun():
    '''
       Test Engine
       :param:
       -l: 循环执行用例集次数 >=1
       -w: 循环执行时的间隔wait时间 >=0，单位：H、M、S 例如 ： 2H,20M,100S
       -e: 用例集并发执行个数
       -t: 用例集类型 '0','1','2','3','4'  默认'0'
           '0' 默认执行scripts 下所有脚本
           '1' 执行 scripts 下的 指定的所有文件夹 使用反斜杠'/'
           '2' 执行 python文件名称 也是文件Class的名称 'testSample5','testSample1'
           '3' 执行 用例名称'test_Sample_2','test_Sample_4'
           '4' 执行 脚本的tag名称 'slave','main','smoke','master'
           '5' 非法 suite_type
       -s: 指定用例集， 与 suite_type 对应，采用逗号','分割：
           : 可以为空
           'Sample/sampledir1','Sample/sampledir2' : 文件夹(相对Scripts目录)
           'testSample5','testSample1': 文件（脚本名称）
           'test_Sample_2','test_Sample_4' : 用例名称
           'smoke', 'main' : 脚本tag
        -o: 分析性能时，最大超时 单位：S
        -c: 分析性能时，间隔分析递增时间 单位：S
        -L: 循环执行多长时间>=0 单位：H、M、S, 例如 ： 2H,20M,100S
        -B: 测试床配置文件名成，默认 TestBed.ini
       '''
    suite_type_dict = {'0':"scripts 下所有脚本",'1':"指定文件夹",'2':"指定脚本文件",'3':"指定用例名称",'4':"指定脚本Tag",}
    help_str = u'''python %s **args
        -f: 测试引擎配置文件名称，默认请填写：TestEngineConfig.ini
        -m: 运行模式，0：调试模式（输出到控制台）， 1：正式模式（有html报告）;默认为 1
        -L: 循环执行多长时间>=0 单位：H、M、S, 例如 ： 2H,20M,100S，默认为0S
        -l: 循环执行用例集次数 >=1，默认为1
        -w: 循环执行时的间隔wait时间 >=0 单位：H、M、S ,例如 ： 2H,20M,100S，默认为0S
        -e: 用例集并发执行个数 >=1
        -t: 用例集类型 '0','1','2','3','4'  默认'0'
            '0': 默认执行scripts 下所有脚本
            '1': 执行 scripts 下的 指定的所有文件夹 使用反斜杠'/'
            '2': 执行 python文件名称 也是文件Class的名称 'testSample5','testSample1'
            '3': 执行 用例名称'test_Sample_2','test_Sample_4'
            '4': 执行 脚本的tag名称 'slave','main','smoke','master'
        -s: 指定用例集， 与 suite_type 对应，采用逗号','分割， 默认为空
            : 为空，当-t选择‘0’时，执行Scripts目录下所有脚本，否则不执行任何脚本
            Sample/sampledir1,Sample/sampledir2 : 文件夹(相对Scripts目录)
            testSample5,testSample1: 文件（脚本名称）
            test_Sample_2,test_Sample_4 : 用例名称
            smoke, main : 脚本tag
        -o: 分析性能时，最大超时 单位：S ,默认20S
        -c: 分析性能时，间隔分析递增时间 单位：S ,默认5S
        -B: 测试床配置文件名成，默认 TestBed.ini
       ''' % __file__
    opts, args = getopt.getopt(sys.argv[1:], "hf:m:t:s:e:l:w:o:c:L:W:B:")
    #初始话日志
    logger.initLogger()
    #初始化引擎
    eg = Engine()
    if opts != []:
        for op, value in opts:
            if op == '-h':
                logger.opration(help_str,code='gb2312')
                return
            elif op == '-t':
                eg.suite_type = str(value)
            elif op == '-s':
                try:
                    eg.suite_params = value.split(',')
                except:
                    eg.suite_params = value.split(' ')
            elif op == '-e':
                try:
                    value = int(value)
                except Exception as e:
                    logger.error(e)
                if value <= 1:
                    logger.Concurrent_type = False
                else:
                    logger.Concurrent_type = True
                    eg.thread_count = value
            elif op == '-l':
                    eg.loopCounts = int(value)
            elif op == '-w':
                    wait_time_str = str(value)
                    if 'H' in wait_time_str or 'h' in wait_time_str:
                        eg.sleeptime = int(wait_time_str.lower().split('h')[0]) * 60 * 60
                    if 'M' in wait_time_str or 'm' in wait_time_str:
                        eg.sleeptime = int(wait_time_str.lower().split('m')[0]) * 60
                    if 'S' in wait_time_str or 's' in wait_time_str:
                        eg.sleeptime = int(wait_time_str.lower().split('s')[0])
            elif op == '-o':
                eg.responseTimeout = int(value)
            elif op == '-c':
                eg.responseTimesplit = int(value)
            elif op == '-L':
                exe_time_str = str(value)
                if 'H' in exe_time_str or 'h' in exe_time_str:
                    eg.loopTime = int(exe_time_str.lower().split('h')[0]) * 60 * 60
                if 'M' in exe_time_str or 'm' in exe_time_str:
                    eg.loopTime = int(exe_time_str.lower().split('m')[0]) * 60
                if  'S' in exe_time_str or 's' in exe_time_str:
                    eg.loopTime = int(exe_time_str.lower().split('s')[0])
            elif  op == '-m':
                eg.model = value
            elif op == '-f':
                enginefile = value
                # enginefile = 'TestEngineConfig.ini'
                eg.model = Parser_Config(enginefile, 'TestParams', 'runModel')
                eg.suite_type = Parser_Config(enginefile, 'TestParams', 'suiteType')
                eg.suite_params = Parser_Config(enginefile, 'TestParams', 'suiteParams').split(',')
                TestBedConfigName = Parser_Config(enginefile,'TestParams','TestBedName')
                eg.testBed = TestBedConfigName
                exeLoop_time_str = Parser_Config(enginefile, 'TestParams', 'loopTime')
                if 'H' in exeLoop_time_str or 'h' in exeLoop_time_str:
                    eg.loopTime = int(exeLoop_time_str.lower().split('h')[0]) * 60 * 60
                if 'M' in exeLoop_time_str or 'm' in exeLoop_time_str:
                    eg.loopTime = int(exeLoop_time_str.lower().split('m')[0]) * 60
                if 'S' in exeLoop_time_str or 's' in exeLoop_time_str:
                    eg.loopTime = int(exeLoop_time_str.lower().split('s')[0])
                eg.loopCounts = int(Parser_Config(enginefile, 'TestParams', 'loopCounts'))
                wait_time_str = Parser_Config(enginefile, 'TestParams', 'sleeptime')
                if 'H' in wait_time_str or 'h' in wait_time_str:
                    eg.sleeptime = int(wait_time_str.lower().split('h')[0]) * 60 * 60
                if 'M' in wait_time_str or 'm' in wait_time_str:
                    eg.sleeptime = int(wait_time_str.lower().split('m')[0]) * 60
                if 'S' in wait_time_str or 's' in wait_time_str:
                    eg.sleeptime = int(wait_time_str.lower().split('s')[0])
                eg.responseTimeout = int(Parser_Config(enginefile, 'TestParams', 'responseTimeOut'))
                eg.responseTimesplit = int(Parser_Config(enginefile, 'TestParams', 'responseSplitTime'))
                threadvalue = int(Parser_Config(enginefile, 'TestParams', 'threadCount'))
                if threadvalue <= 1:
                    logger.Concurrent_type = False
                else:
                    logger.Concurrent_type = True
                    eg.thread_count = threadvalue
                break
            elif op == '-B':
                eg.testBed = value
                Parse_config_Set(eg.enginefile,'TestParams','TestBedName',value)
            else:
                raise Exception('Has No this option : "%s" ' % op)
        logger.opration(u'\n^^^^^^^^^^^^^^^^^ 本次测试执行参数 ^^^^^^^^^^^^^^^^',code='gb2312')
        if eg.model == '1':
            logger.opration(u'------>  *** 正式模式（输出html报告）***',code='gb2312')
        else:
            logger.opration(u'------>  *** 调试模式（输出到控制台）***',code='gb2312')
        logger.opration(u'------> 注意：同时有参数循环执行次数、循环执行时间时，优先选择循环执行次数！',code='gb2312')
        if eg.loopCounts > 1 or eg.loopTime == None or eg.loopTime == 0:
            logger.opration(u'------> 循环执行 %s 次，每次间隔等待时间为 %s S' % (eg.loopCounts,eg.sleeptime),code='gb2312')
        else:
            logger.opration(u'------> 循环执行 %s S，每次间隔等待时间为 %s S' % (eg.loopTime, eg.sleeptime),code='gb2312')
        logger.opration(u'------> 并发线程数为： %s 个' % (eg.thread_count),code='gb2312')
        logger.opration(u'------> 执行用例集类型为： %s ' % (suite_type_dict[eg.suite_type]).decode('utf-8'),code='gb2312')
        if eg.suite_params == []:
            logger.opration(u'------> 用例集： Scripts目录下所有脚本 ',code='gb2312')
        else:
            logger.opration(u'------> 用例集： %s ' % (eg.suite_params),code='gb2312')
        logger.opration(u'------> 性能分析最大超时： %s S' % (eg.responseTimeout),code='gb2312')
        logger.opration(u'------> 性能分析时间间隔： %s S' % (eg.responseTimesplit),code='gb2312')
        logger.opration(u'------> 测试床配置文件为： %s ' % (eg.testBed),code='gb2312')
    else:
        eg.model = Parser_Config(eg.enginefile,'TestParams','runModel')
        eg.suite_type = Parser_Config(eg.enginefile,'TestParams','suiteType')
        eg.suite_params = Parser_Config(eg.enginefile,'TestParams','suiteParams').split(',')
        exeLoop_time_str = Parser_Config(eg.enginefile, 'TestParams', 'loopTime')
        if 'H' in exeLoop_time_str or 'h' in exeLoop_time_str:
            eg.loopTime = int(exeLoop_time_str.lower().split('h')[0]) * 60 * 60
        if 'M' in exeLoop_time_str or 'm' in exeLoop_time_str:
            eg.loopTime = int(exeLoop_time_str.lower().split('m')[0]) * 60
        if 'S' in exeLoop_time_str or 's' in exeLoop_time_str:
            eg.loopTime = int(exeLoop_time_str.lower().split('s')[0])
        eg.loopCounts = int(Parser_Config(eg.enginefile, 'TestParams', 'loopCounts'))
        wait_time_str = Parser_Config(eg.enginefile, 'TestParams', 'sleeptime')
        if 'H' in wait_time_str or 'h' in wait_time_str:
            eg.sleeptime = int(wait_time_str.lower().split('h')[0]) * 60 * 60
        if 'M' in wait_time_str or 'm' in wait_time_str:
            eg.sleeptime = int(wait_time_str.lower().split('m')[0]) * 60
        if 'S' in wait_time_str or 's' in wait_time_str:
            eg.sleeptime = int(wait_time_str.lower().split('s')[0])
        eg.responseTimeout = int(Parser_Config(eg.enginefile,'TestParams','responseTimeOut'))
        eg.responseTimesplit = int(Parser_Config(eg.enginefile,'TestParams','responseSplitTime'))
        threadvalue = int(Parser_Config(eg.enginefile,'TestParams','threadCount'))
        eg.testBed = Parser_Config(eg.enginefile,'TestParams','TestBedName')
        if threadvalue <= 1:
            logger.Concurrent_type = False
        else:
            logger.Concurrent_type = True
            eg.thread_count = threadvalue
        logger.opration('\n^^^^^^^^^^^^^^^^^ 本次测试执行参数 ^^^^^^^^^^^^^^^^')
        if eg.model == '1':
            logger.opration('------>  *** 正式模式（输出html报告）***')
        else:
            logger.opration('------>  *** 调试模式（输出到控制台）***')
        logger.opration('------> 注意：同时有参数循环执行次数、循环执行时间时，优先选择循环执行次数！')
        if eg.loopCounts > 1 or eg.loopTime == None or eg.loopTime == 0:
            logger.opration('------> 循环执行 %s 次，每次间隔等待时间为 %s S' % (eg.loopCounts, eg.sleeptime))
        else:
            logger.opration('------> 循环执行 %s S，每次间隔等待时间为 %s S' % (eg.loopTime, eg.sleeptime))
        logger.opration('------> 并发线程数为： %s 个' % (eg.thread_count))
        logger.opration('------> 执行用例集类型为： %s ' % (suite_type_dict[eg.suite_type]))
        if eg.suite_params == []:
            logger.opration('------> 用例集： Scripts目录下所有脚本 ')
        else:
            logger.opration('------> 用例集： %s ' % (eg.suite_params))
        logger.opration('------> 性能分析最大超时： %s S' % (eg.responseTimeout))
        logger.opration('------> 性能分析时间间隔： %s S' % (eg.responseTimesplit))
        logger.opration('------> 测试床配置文件为： %s ' % (eg.testBed))
    # 初始日志csv的title
    WriteCaseTimeCsvTitle()
    # 初始化数据库表
    CreateTempTable()
    #获取token和providerid并写入数据库
    # initTestInterface()   # 放到Mytestcase中执行
    # 引擎启动执行
    eg.BuildTestSuite()
    # 报告模式
    if eg.model == '1':
        eg.loghtml()
    else:
        eg.logtext()
    # 开始执行
    eg.run()
    # 收集case执行时间
    WriteCaseTimeCsvData()
    # 执行分析
    Concurrent_Analysis(eg.responseTimeout,eg.responseTimesplit)
    if opts != []:
        logger.opration(u'\n====================== 执行完毕 ！=======================',code='gb2312')
    else:
        logger.opration('\n====================== 执行完毕 ！=======================')

if __name__=="__main__":
    EngineRun()
    # Concurrent_Analysis(10,2)