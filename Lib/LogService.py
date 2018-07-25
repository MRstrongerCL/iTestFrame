# -*- coding: utf-8 -*-
#!usr/bin/sh
# author: chenliang
# create Time: 20180901

import os,re,sys
import datetime
import time
import logging
import threading
import traceback
from PublicMethods import Get_Current_Time
from PublicMethods import Get_Now_TimeStr
from PublicMethods import ReadCsvForList
from PublicMethods import WiteCsvForDict
from PublicMethods import WiteCsvForList
from PublicMethods import WiteCsvForLists
from ManageDataBase import ManageSqlite

# =========================== 常量 配置 ==============================
ROOT_DIR = (os.path.dirname(__file__).split('Lib')[0]).strip('\\')
LOG_ROOT_DIR = os.path.join(ROOT_DIR,"Log")
CASE_TIME_TITLE = ['CaseName','StartTime','EndTime','ExecuteTime','Result','ScriptLog']
CASE_TIME_CSV_PATH = os.path.join(ROOT_DIR,'Log\\AllCasesTime.csv')
CONCURRENT_ANALYSIS_CSV_PATH = os.path.join(ROOT_DIR,'Log\\ConcurrentReport.csv')
PASS_STR = 'Pass'
FAIL_STR = 'Failed'
DB_FILE_PATH = os.path.join(LOG_ROOT_DIR,'temple.db')
CSV_TABLE_NAME = 'sqlTempData'

eventlog = threading.Event()        # 初始化线程中Event，保持线程间简单的通信
eventlog.set()
timecsvlist = []

def CreateTempTable(c_type=False):
    # 由于加入指定日志地址后，会影响执行效率，因此无论是并行还是串行，都不记录每个脚本的日志路径（后续有需要的话就使用timecsvlist列表记录开启）
    c_type = True
    # 创建用例执行时间相关数据库
    if c_type==False:
        Create_Csv_Table = '''CREATE TABLE 'sqlTempData' (
                                  'CaseName' varchar(50) NOT NULL,
                                  'StartTime' varchar(50) NOT NULL,
                                  'EndTime' varchar(50) NOT NULL,
                                  'ExecuteTime' varchar(11) NOT NULL,
                                  'Result' varchar(50) NOT NULL,
                                  'ScriptLog' varchar(200) NOT NULL
                                )'''
    else:
        Create_Csv_Table = '''CREATE TABLE 'sqlTempData' (
                                      'CaseName' varchar(50) NOT NULL,
                                      'StartTime' varchar(50) NOT NULL,
                                      'EndTime' varchar(50) NOT NULL,
                                      'ExecuteTime' varchar(11) NOT NULL,
                                      'Result' varchar(50) NOT NULL
                                    )'''

    # PRIMARY KEY ('CaseName')    此表中不加入主键
    MS = ManageSqlite(DB_FILE_PATH)
    MS.DropTable(CSV_TABLE_NAME)
    MS.CreateTable(Create_Csv_Table)
    MS.Close()

    # 创建接口token、provider存放数据库
    # createtable_str = '''CREATE TABLE '%s' (
    #                           'providerId' varchar(20) NOT NULL,
    #                           'token' varchar(20) NOT NULL,
    #                            PRIMARY KEY ('token')
    #                         )''' % LOGIN_TABLE_NAME
    # ms = ManageSqlite(DB_FILE_PATH)
    # ms.DropTable(LOGIN_TABLE_NAME)
    # ms.CreateTable(createtable_str)
    # ms.Close()


class Singleton(object):
    def __new__(cls,*args,**kw):
        if not hasattr(cls,'_instance'):
            orig=super(Singleton,cls)
            cls._instance=orig.__new__(cls,*args,**kw)
        return cls._instance

class logger(Singleton):
    cur_script_log_file = ''
    old_allstr = ''
    new_allstr = ''
    Concurrent_type = False
    log_dir_path = None
    log_file_path = None
    if log_file_path == None:
        now = datetime.datetime.now()
        logpath = '[{}-{}-{}]-{}-{}-{}-{}.log'.format(now.year, now.month, now.day, now.hour, now.minute, now.second,
                                                      now.microsecond)
        log_dir_path = os.path.join(LOG_ROOT_DIR, "sripts_log")
        log_file_path = os.path.join(log_dir_path, logpath)
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s] %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            # datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_file_path,
                            filemode='w')
        logging.info("************** Start Test Log *****************")

    @classmethod
    def initLogger(cls):
        cls.cur_script_log_file = ''
        cls.old_allstr = ''
        cls.new_allstr = ''
        cls.Concurrent_type = False
        now = datetime.datetime.now()
        logpath = '[{}-{}-{}]-{}-{}-{}-{}.log'.format(now.year, now.month, now.day, now.hour, now.minute, now.second,
                                                      now.microsecond)
        if cls.log_dir_path == None:
            cls.log_dir_path = os.path.join(LOG_ROOT_DIR, "sripts_log")
        if cls.log_file_path == None:
            cls.log_file_path = os.path.join(cls.log_dir_path, logpath)
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s] %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            # datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=cls.log_file_path,
                            filemode='w')
        logging.info("************** Start Test Log *****************")
        print("************** Start Test Log *****************")

    @classmethod
    def strEncode(cls,new_msg,code=None):
        if code != None:
            instead_status = False
            # 解码utf-8
            if instead_status == False:
                try:
                    new_msg = new_msg.decode('utf-8')
                    instead_status = True
                except:
                    pass
            # 解码utf8
            if instead_status == False:
                try:
                    new_msg = new_msg.decode('utf8')
                    instead_status = True
                except:
                    pass
            # 解码gbk
            if instead_status == False:
                try:
                    new_msg = new_msg.decode('gbk')
                    instead_status = True
                except:
                    pass
            # 解码gb2312
            if instead_status == False:
                try:
                    new_msg = new_msg.decode('gb2312')
                    instead_status = True
                except:
                    pass
            # 转码
            if code != 'unicode':
                try:
                    new_msg = new_msg.encode(code)
                except:
                    pass
        return new_msg


    @classmethod
    def opration(cls, msg, printstatus=True, code=None):
        logging.debug(msg)
        if printstatus:
            new_msg = cls.strEncode(msg,code)
            print(new_msg)
        return

    @classmethod
    def title(cls, msg, printstatus=True, code=None):
        logging.debug(msg)
        if printstatus:
            new_msg = cls.strEncode(msg,'unicode')
            print(new_msg)
        return

    @classmethod
    def debug(cls,msg, printstatus=True, code=None):
        logging.debug(msg)
        now = datetime.datetime.now()
        new_msg =  '[{}-{}-{} {}:{}:{}.{}]:'.format(now.year, now.month, now.day, now.hour,now.minute, now.second,now.microsecond) + str(msg)
        if printstatus:
            new_msg = cls.strEncode(new_msg,'unicode')
            print(new_msg)
        return

    @classmethod
    def info(cls,msg, printstatus=True, code=None):
        logging.info(msg)
        now = datetime.datetime.now()
        new_msg =  '[{}-{}-{} {}:{}:{}.{}]:'.format(now.year, now.month, now.day, now.hour,now.minute, now.second,now.microsecond) + str(msg)
        if printstatus:
            new_msg = cls.strEncode(new_msg,'unicode')
            print(new_msg)
        return

    @classmethod
    def warning(cls,msg, printstatus=True, code=None):
        logging.warning(msg)
        now = datetime.datetime.now()
        new_msg =  '[{}-{}-{} {}:{}:{}.{}]:'.format(now.year, now.month, now.day, now.hour,now.minute, now.second,now.microsecond) + str(msg)
        if printstatus:
            new_msg = cls.strEncode(new_msg,'unicode')
            print(new_msg)
        return

    @classmethod
    def error(cls,msg, printstatus=True, code=None):
        logging.error(msg)
        now = datetime.datetime.now()
        new_msg =  '[{}-{}-{} {}:{}:{}.{}]:'.format(now.year, now.month, now.day, now.hour,now.minute, now.second,now.microsecond) + str(msg)
        if printstatus:
            new_msg = cls.strEncode(new_msg,'unicode')
            print(new_msg)
        return

    @classmethod
    def DeleteScriptLog(cls):
        pth = cls.log_file_path
        mstr = '.?script_.+'
        p = re.compile(mstr)
        for one in os.listdir(pth):
            ma = p.match(one)
            if ma:
                print ma.group()
                npth = os.path.join(pth,ma.group())
                os.remove(npth)

    @classmethod
    def SplitScriptLog(cls):
        if cls.Concurrent_type == False:
            with open(cls.log_file_path,'rb+') as fr:
                cls.new_allstr = fr.read()
                newstr = cls.new_allstr.replace(cls.old_allstr,'')
                fr.close()
            if eventlog.isSet():
                eventlog.wait()
                eventlog.clear()
            # if True:
                if os.path.exists(cls.cur_script_log_file):
                    with open(cls.cur_script_log_file,'rb+') as fr1:
                        source_file_str = fr1.read()
                        more_str = cls.old_allstr.replace(source_file_str,'')
                        newstr = source_file_str + more_str + newstr
                        fr1.close()
                with open(cls.cur_script_log_file ,'wb+') as fw:
                    fw.write(newstr)
                    fw.flush()
                    fw.close()
                cls.old_allstr = cls.new_allstr
                eventlog.set()

    @classmethod
    def LogCsvDecorator(cls, f):
        def logcsv(object, self=cls):
            # global timecsvlist
            case_name = f.func_name
            if self.Concurrent_type == False:
                now = datetime.datetime.now()
                time_tile = '[{}-{}-{}_{}-{}-{}-{}]'.format(now.year, now.month, now.day, now.hour, now.minute,now.second, now.microsecond)
                logpath = '{}{}.log'.format(time_tile,case_name)
                logfilepath = os.path.join(self.log_dir_path, logpath)
                cls.cur_script_log_file = logfilepath
            startime = Get_Current_Time()
            bgaintime = time.time()
            try:
                f(object)
                status = PASS_STR
            except Exception as e:
                logger.error(e)
                traceback.print_exc()
                status = FAIL_STR
            finally:
                stoptime = Get_Current_Time()
                endtime = time.time()
                usetime = endtime - bgaintime
                # 为避免执行太快，导致usetime为0，后面计算平均时间无法被除
                if usetime == 0.0:
                    usetime = 0.00001
                self.SplitScriptLog()  # 分裂txt脚本日志
                csvdict = {}
                # 由于加入指定日志地址后，会影响执行效率，因此无论是并行还是串行，都不记录每个脚本的日志路径（后续有需要的话就使用timecsvlist列表记录开启）
                if self.Concurrent_type == False:
                    csvlist = [case_name, startime, stoptime, usetime, status, cls.cur_script_log_file]
                    for i in range(len(CASE_TIME_TITLE[:-1])):
                        csvdict[CASE_TIME_TITLE[i]] = csvlist[i]
                else:
                    csvlist = [case_name, startime, stoptime, usetime, status]
                    for i in range(len(CASE_TIME_TITLE[:-1])):
                        csvdict[CASE_TIME_TITLE[i]] = csvlist[i]
                # timecsvlist.append(csvlist)
                MS = ManageSqlite(DB_FILE_PATH)
                MS.Insert_Sql(CSV_TABLE_NAME,csvdict)
                MS.Close()
                # WiteCsvForList(CASE_TIME_CSV_PATH, csvlist)
                if status == FAIL_STR:
                    print "error in %s" % case_name
                    raise e
        return logcsv

def WriteCaseTimeCsvTitle():
    if os.path.exists(CASE_TIME_CSV_PATH):
        os.remove(CASE_TIME_CSV_PATH)
    # 由于加入指定脚本日志地址后，会影响执行效率，因此无论是并行还是串行，都不记录每个脚本的日志路径（后续有需要的话就使用timecsvlist列表记录开启）
    # if logger.Concurrent_type == False:
    #     WiteCsvForList(CASE_TIME_CSV_PATH,CASE_TIME_TITLE)
    # else:
    #     WiteCsvForList(CASE_TIME_CSV_PATH, CASE_TIME_TITLE[:-1])
    WiteCsvForList(CASE_TIME_CSV_PATH, CASE_TIME_TITLE[:-1])

def WriteCaseTimeCsvData():
    # 由于加入指定脚本日志地址后，会影响执行效率，因此无论是并行还是串行，都不记录每个脚本的日志路径（后续有需要的话就使用timecsvlist列表记录开启）
    # 注释掉数据库操作，即采用缓存的形式写入csv
    MS = ManageSqlite(DB_FILE_PATH)
    timecsvlist = MS.Select_Sql("Select * From %s" % CSV_TABLE_NAME)
    MS.Close()
    WiteCsvForLists(CASE_TIME_CSV_PATH, timecsvlist)
    time.sleep(1)

def LogCsvDecorator(f):
    def logcsv(self):
        global timecsvlist
        case_name = f.func_name
        startime = Get_Current_Time()
        bgaintime = time.time()
        try:
            f(self)
            status = PASS_STR
        except Exception as e:
            logging.error(e)
            status = FAIL_STR
        finally:
            stoptime = Get_Current_Time()
            endtime = time.time()
            usetime = endtime - bgaintime
            csvlist = [case_name, startime, stoptime, usetime, status]
            timecsvlist.append(csvlist)
            # WiteCsvForList(CASE_TIME_CSV_PATH, csvlist)
            if status == FAIL_STR:
                print "Traceback Error in : %s" % case_name
                raise e
    return logcsv

def Concurrent_Analysis(timeout=10,split_time=2):
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter
    # 获取相同用例执行信息字典
    analysis_dict = {}
    if os.path.exists(CASE_TIME_CSV_PATH):
        all_lists = ReadCsvForList(CASE_TIME_CSV_PATH)
        all_dict = {}
        # 由于加入指定脚本日志地址后，会影响执行效率，因此无论是并行还是串行，都不记录每个脚本的日志路径（后续有需要的话就使用timecsvlist列表记录开启）
        # if logger.Concurrent_type == False:
        #     casetime_TITLE = CASE_TIME_TITLE
        # else:
        #     casetime_TITLE = CASE_TIME_TITLE[:-1]
        casetime_TITLE = CASE_TIME_TITLE[:-1]
        keys_indexs = len(casetime_TITLE)
        for key in casetime_TITLE:
            all_dict[key] = []
        for one_case in all_lists[1:]:
            for i in range(keys_indexs):
                key = casetime_TITLE[i]
                single = one_case[i]
                all_dict[key].append(single)
        # print all_dict
    else:
        raise Exception('There is no file: %s ' % CASE_TIME_CSV_PATH)

    # 生产性能报告csv字段
    casename_key = casetime_TITLE[0]
    diff_casenames = []
    compare_casename = ''
    for casename in all_dict[casename_key]:
        if casename not in diff_casenames:
            diff_casenames.append(casename)
    # print diff_casenames

    if os.path.exists(CONCURRENT_ANALYSIS_CSV_PATH):
        os.remove(CONCURRENT_ANALYSIS_CSV_PATH)
    for diff_casename in diff_casenames:
        analysis_dict_key_names = ['casename', 'Concurrent_counts', 'usetime_list', 'pass_counts', 'failed_counts',\
                         'all_Success_rate','average_time','throughput','Maximum_time','Minimum_time']
        analysis_dict[analysis_dict_key_names[0]] = diff_casename
        analysis_dict[analysis_dict_key_names[1]] = 0
        analysis_dict[analysis_dict_key_names[2]] = []
        analysis_dict[analysis_dict_key_names[3]] = 0
        analysis_dict[analysis_dict_key_names[4]] = 0
        cur_big_timeout_count = 0
        for i in range(len(all_dict[casename_key])):
            if all_dict[casename_key][i] == diff_casename:
                analysis_dict[analysis_dict_key_names[1]] += 1
                analysis_dict[analysis_dict_key_names[2]].append(all_dict[casetime_TITLE[3]][i])
                if all_dict[casetime_TITLE[4]][i] == PASS_STR:
                    analysis_dict[analysis_dict_key_names[3]] += 1
                if all_dict[casetime_TITLE[4]][i] == FAIL_STR:
                    analysis_dict[analysis_dict_key_names[4]] += 1
        analysis_dict[analysis_dict_key_names[5]] = "%{:.2f}".format(float(analysis_dict[analysis_dict_key_names[3]])/(analysis_dict[analysis_dict_key_names[1]]) * 100)
        all_times = sum(float(t) for t in analysis_dict[analysis_dict_key_names[2]])
        analysis_dict[analysis_dict_key_names[6]] = "{:.6f}".format(all_times/analysis_dict[analysis_dict_key_names[1]])
        throughput = float(analysis_dict[analysis_dict_key_names[1]]) / all_times
        analysis_dict[analysis_dict_key_names[7]] = "{:.6f} TPS".format(throughput)
        max_time = max(float(t) for t in analysis_dict[analysis_dict_key_names[2]])
        analysis_dict[analysis_dict_key_names[8]] = "{:.6f}".format(max_time)
        min_time = min(float(t) for t in analysis_dict[analysis_dict_key_names[2]])
        analysis_dict[analysis_dict_key_names[9]] = "{:.6f}".format(min_time)

        #计算梯度响应时间比
        for j in range(timeout / split_time)[1:]:
            split_time_new = j * split_time
            dt_timeout_count = 0
            key_name = '%sS_Success_rate' % split_time_new
            analysis_dict_key_names.append(key_name)
            for use_time in analysis_dict[analysis_dict_key_names[2]]:
                use_time = float(use_time)
                if use_time <= split_time_new:
                    dt_timeout_count += 1
            analysis_dict[key_name] = "%{:.2f}".format(float(dt_timeout_count)/analysis_dict[analysis_dict_key_names[1]] * 100)
        #最大超时时间的成功率
        for use_time in analysis_dict[analysis_dict_key_names[2]]:
            use_time = float(use_time)
            if use_time <= timeout:
                cur_big_timeout_count += 1
        key_name = '%sS_Success_rate' % timeout
        analysis_dict_key_names.append(key_name)
        analysis_dict[key_name] = "%{:.2f}".format(float(cur_big_timeout_count)/analysis_dict[analysis_dict_key_names[1]] * 100)
        # print analysis_dict

        # 输出性能图
        picture_dir = os.path.join(LOG_ROOT_DIR,'pic_dir\\performance')
        time_str = Get_Now_TimeStr()
        picture_name = diff_casename + '({}).png'.format(time_str)
        picture_path = os.path.join(picture_dir,picture_name)
        if os.path.exists(picture_path):
            os.remove(picture_path)
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        new_usetime_list = []
        for utime in analysis_dict['usetime_list']:
            n_utime = '{:.4f}'.format(float(utime))
            new_usetime_list.append(float(n_utime))
        time_array = np.array(new_usetime_list)
        time_name = str(int(all_times) / 3600) + " H " + str(int(all_times) % 3600 / 60) + ' M ' + str(int(all_times) % 3600 % 60) + ' S '
        ax.set_title(diff_casename + ' performance ' + time_name)
        ax.plot(time_array,color='red')

        # 设置纵坐标刻度
        ymajorLocator = MultipleLocator(1)  # 将y轴主刻度标签设置为0.5的倍数
        ymajorFormatter = FormatStrFormatter('%1.1f')  # 设置y轴标签文本的格式
        yminorLocator = MultipleLocator(0.2)  # 将此y轴次刻度标签设置为0.1的倍数

        # 设置主刻度标签的位置,标签文本的格式
        ax.yaxis.set_major_locator(ymajorLocator)
        ax.yaxis.set_major_formatter(ymajorFormatter)

        # 显示次刻度标签的位置,没有标签文本
        ax.yaxis.set_minor_locator(yminorLocator)
        # ax.yaxis.set_minor_formatter(ymajorFormatter)

        ax.yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度

        # 存为图片
        plt.savefig(picture_path)
        plt.close()

        # 写入性能报告csv
        analysis_dict_key_names.remove('usetime_list')
        usetime_list = analysis_dict.pop('usetime_list')
        if diff_casenames.index(diff_casename) == 0:
            WiteCsvForList(CONCURRENT_ANALYSIS_CSV_PATH,analysis_dict_key_names)
        WiteCsvForDict(CONCURRENT_ANALYSIS_CSV_PATH,analysis_dict,analysis_dict_key_names)

# 初始化日志
class MyLog(object):
    def __init__(self):
        self.scriptLogFile = None
        # self.case_name = ''
        self.cur_script_log_file = ''
        self.old_allstr = ''
        self.new_allstr = ''
        self.old_allstr_list = []
        self.new_allstr_list = []
        self.logDirpath = os.path.join(ROOT_DIR,"Log\sripts_log")

    def initScriptLog(self):
        now = datetime.datetime.now()
        logpath = '[scriptLog_{}-{}-{}]-{}-{}-{}-{}.log'.format(now.year, now.month, now.day, now.hour,now.minute, now.second,now.microsecond)
        logfilepath = os.path.join(self.logDirpath,logpath)
        i = 0
        while True:
            if os.path.exists(logfilepath):
                logpath = '[scriptLog_{}-{}-{}]-{}-{}-{}-{}_({}).log'.format(now.year, now.month, now.day, now.hour,now.minute, now.second, now.microsecond, i)
                logfilepath = os.path.join(self.logDirpath,logpath)
                i += 1
            else:
                break
        self.scriptLogFile = logfilepath

    def WriteScriptLog(self,text):
        with open(self.scriptLogFile,'ab+') as f:
            newtext = '[' + time.ctime() + '] ' + text + '\r\n'
            f.write(newtext)
            f.flush()
            f.close()

    def getListAandB(self,listA,listB):
        listC = []
        for one in listA:
            if one in listB and ("--------->" not in one or "SetUp" not in one or "TearDown" not in one):
                listC.append(one)
        return listC

    def getListAmoreB(self,listA,listB):
        listC = []
        if len(listA) > len(listB):
            for one in listA:
                if one not in listB or ("--------->" in one or "SetUp" in one or "TearDown" in one):
                    listC.append(one)
        else:
            for one in listB:
                if one not in listA or ("--------->" in one or "SetUp" in one or "TearDown" in one):
                    listC.append(one)
        return listC

    def getListAorB(self,listA,listB):
        listC = listA + listB
        return listC

    def findListLastIndext(self,theList, target):
        for i in xrange(len(theList)):
            if target == theList[i]:
                return i


if __name__ == '__main__':
    pass