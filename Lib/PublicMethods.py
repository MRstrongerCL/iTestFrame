# -*- coding: UTF-8 -*-
#!/bin/sh
'''
Author: chenliang
Created Time: 2016/5/31
Describtion: Public method Manage
'''

import sys
import os
from time import time
import datetime
import subprocess
from time import sleep
import json
from requests import *
import re,csv
from random import Random
from ftplib import FTP
# from MyTelnet import do_telnet
from exceptions import AssertionError

def take_screenshot(browser, save_fn="capture.png"):
    browser.save_screenshot(save_fn)

def Sys_path_append(path):
    if not os.path.exists(r"C:\Python27\Lib\site-packages\pos.pth"):
        f = file(r"C:\Python27\Lib\site-packages\pos.pth","w")
        f.write(path)
        f.flush()
        f.close()
    print(path)
    sys.path.append(path)

def ReadCsvForList(csvPath):
    read_list = []
    with open(csvPath, 'rb+') as csvfile:
        read = csv.reader(csvfile)
        for line in read:
            read_list.append(line)
        csvfile.close()
    return read_list

def WiteCsvForList(csvPath,list):
    writelist = []
    # if os.path.exists(csvPath):
    #     with open(csvPath, 'r') as csvfile:
    #         for line in csvfile:
    #             newline = line.strip('\r\n').split(',')
    #             writelist.append(newline)
    # writelist.append(lists)
    # print writelist
    # with open(csvPath,'wb+') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows(writelist)
    with open(csvPath, 'ab+') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list)
        csvfile.close()

def WiteCsvForLists(csvPath,lists):
    writelist = []
    # if os.path.exists(csvPath):
    #     with open(csvPath, 'r') as csvfile:
    #         for line in csvfile:
    #             newline = line.strip('\r\n').split(',')
    #             writelist.append(newline)
    # writelist.append(lists)
    # print writelist
    # with open(csvPath,'wb+') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows(writelist)
    with open(csvPath, 'ab+') as csvfile:
        writer = csv.writer(csvfile)
        for line in lists:
            writer.writerow(line)
        csvfile.close()

def WiteCsvForDict(csvPath,dicts,keys_list):
    with open(csvPath, 'ab+') as csvfile:
        writer = csv.DictWriter(csvfile,keys_list)
        writer.writerow(dicts)
        csvfile.close()

def Ascii2Chinese(str1):
    if str1==None:
        return None
    if type(str1)==int:
        str1=str(str1)
    return str1.decode("gb2312")

def Connect_AndroidDevice(device_ip_port,timeout=20):
    try:
        adb_env_path = os.environ['ANDROID_HOME']
    except KeyError,key:
        raise("adb connect device Failed,Have No the Environ,KeyError:%s" % key)
    adb_path = os.path.join(adb_env_path,'platform-tools\\adb.exe')
    connect_cmd_str = "%s connect %s" % (adb_path,device_ip_port)
    adbdevicecmd = "%s devices" % (adb_path)
    con = subprocess.Popen(connect_cmd_str,stdout=subprocess.PIPE)
    now_time = time()
    end_time = now_time + int(timeout)
    r_str = con.stdout
    status = 0
    return_faild_info = ''
    while now_time < end_time:
        result_str = str(r_str.readline())
        print result_str
        if len(result_str) > 5:
            return_faild_info = result_str
        matchstr = '%s\tdevice' % device_ip_port
        matchstr1 = 'connected to %s' % device_ip_port
        matchstr2 = 'already connected to %s' % device_ip_port
        if matchstr1 in result_str or matchstr2 in result_str:
            print "adb Conect %s Success !!!" % device_ip_port
            for i in range(5):
                adbdevices = subprocess.check_output(adbdevicecmd,shell=True)
                if matchstr in adbdevices:
                    status = 1
                    break
                else:
                    sleep(1)
            if status == 1:
                adbdvicesinfo = Ascii2Chinese(adbdevices)
                print adbdvicesinfo
                print(adbdvicesinfo)
                return True
        else:
            print "Connect failed:, Go on ..."
            sleep(0.5)
        now_time = time()
    if status == 0:
        print "Connect Failed, And timeout.Failed info:\n%s\nPlease check:\n\t1,adb environment;\n\t2,android device's adbwireless tool has start server;\n\t3,adb's port 5073 has used;\n\t4,the androied device had not authorisation " % return_faild_info
        raise("Connect %s Failed, And timeout %sS .Failed info:\n%s\nPlease check:\n\t1,adb environment;\n\t2,android device's adbwireless tool has start server;\n\t3,adb's port 5073 has used;\n\t4,the androied device had not authorisation" % (device_ip_port,timeout,return_faild_info))

def disconnect_Android_device(device_ip_port):
    try:
        adb_env_path = os.environ['ANDROID_HOME']
    except KeyError,key:
        key = Ascii2Chinese(key)
        raise("adb connect device Failed,Have No the Environ,KeyError:%s" % key)
    adb_path = os.path.join(adb_env_path,'platform-tools\\adb.exe')
    disconnect_cmd_str = "%s disconnect %s" % (adb_path,device_ip_port)
    try:
        print("At first,if the pc had device connected, disconnect it ...")
        result = subprocess.call(disconnect_cmd_str,shell=True)
    except:
        pass
    if result==0:
        print "disconnect %s Success !" % device_ip_port
    elif result==1:
        print "has no connected %s, don't need disconnect !" % device_ip_port

def Start_Appium_Server(timeout=30,AppiumHome_path=None,port=4723,bootstrap_port=4724):
    timeout = int(timeout)
    p = os.getcwd()
    subprocess.call("taskkill /F /IM node.exe")

    if AppiumHome_path==None:
        try:
            AppiumHome_path = os.environ['APPIUM_HOME'].split(';')[0]
        except KeyError,key:
            raise("Start Appium Server Failed,Have No the Environ,KeyError:%s" % key)

    print "Appium Path: %s" % AppiumHome_path
    appium_log_dir = os.path.join(AppiumHome_path,"RobotLog")
    if not os.path.exists(appium_log_dir):
        os.makedirs(appium_log_dir)
    appium_log_path = os.path.join(AppiumHome_path,"RobotLog\log_%s.txt" % Get_Now_TimeStr())
    appiumcmd_path = os.path.join(AppiumHome_path,'node_modules\\.bin\\appium.cmd')
    # cmd_str ='start appium.cmd ' +'-a 127.0.0.1 -p ' + str(port) +' --bootstrap-port ' + str(bootstrap_port) + ' --session-override'+ ' --log "' + appium_log_path +'" --command-timeout 600'
    cmd_str =appiumcmd_path +' -a 127.0.0.1 -p ' + str(port) +' --bootstrap-port ' + str(bootstrap_port) + ' --session-override'+ ' --log "' + appium_log_path +'" --command-timeout 600'
    print cmd_str

    # 创建cmd执行启动appium
    startAppiumCmd_path = os.path.join(p,'StartAppium.cmd')
    if os.path.exists(startAppiumCmd_path):
        os.system('del /f/q %s' % startAppiumCmd_path)
    f = open(startAppiumCmd_path,"a")
    f.write(cmd_str)
    f.flush()
    f.close()

     #创建vbs执行appium后台程序
    startAppiumVbs_path = os.path.join(p,'startAppiumVbs.VBS')
    if not os.path.exists(startAppiumVbs_path):
        startbackVbs_str = 'Set ws = CreateObject("Wscript.Shell")\nws.run "cmd /c StartAppium",vbhide'
        f = open(startAppiumVbs_path,'a')
        f.write(startbackVbs_str)
        f.flush()
        f.close()
    # 监控appium启动成功
    app = subprocess.call(startAppiumVbs_path,shell=True,stdout=subprocess.PIPE)
    # app = os.system(startAppiumVbs_path)
    now_time = time()
    end_time = now_time + timeout
    status = 0
    result = 'Init Null'
    while now_time < end_time:
        linshifile = os.path.join(p,'linshi.txt')
        cmdstr = 'netstat -ano | findstr "4723" > %s' % linshifile
        os.system(cmdstr)
        f = open(linshifile,'r')
        rlinelist = f.readlines()
        f.close()
        if rlinelist != []:
            result = rlinelist[0]
            if 'LISTENING' in result:
                print result
                status = 1
                os.system('del /s/q %s' % linshifile)
                break
            else:
                sleep(0.5)
        now_time = time()
    if status ==1 :
        print "Start Appium Success !!!"
        print('Start Appium Success,%s' % result)
        sleep(2)
        return True
    else:
        print "Start Appium Failed !!!"
        os.system('del /s/q %s' % linshifile)
        raise('Start Appium Failed and Timeout %sS, Please Check:\n\t1,APPIUM_HOME environ Path;\n\t2,the port 4073 had used;\n\t3,wait time is not enough' % (timeout,result))

def Numbers_Should_Bigthan(num1,num2):
    '''
    num1 >  num2
    '''
    try:
        if '.' in str(num1) or '.' in str(num2):
            num1 = float(num1)
            num2 = float(num2)
        else:
            num1 = int(num1)
            num2 = int(num2)
        if num1>num2:
            return True
        else:
            return False
    except:
        print "This Time Compare Failed"
        return False

def Numbers_Should_Smallthan(num1,num2):
    '''
    num1 <  num2
    '''
    try:
        if '.' in str(num1) or '.' in str(num2):
            num1 = float(num1)
            num2 = float(num2)
        else:
            num1 = int(num1)
            num2 = int(num2)
        if num1<num2:
            return True
        else:
            return False
    except:
        print "This Time Compare Failed"
        return False

def Numbers_Should_Equal(num1,num2):
    '''
    num1 ==  num2
    '''
    try:
        print "num1:{} -- num2:{}".format(num1,num2)
        print "type1:{} -- type2:{}".format(type(num1),type(num2))
        if '.' in str(num1) or '.' in str(num2):
            num1 = float(num1)
            num2 = float(num2)
        else:
            num1 = int(num1)
            num2 = int(num2)
        print "num1:{} -- num2:{}".format(num1,num2)
        print "type1:{} -- type2:{}".format(type(num1),type(num2))
        if num1 == num2:
            return True
        else:
            return False
    except:
        print "This Time Compare Failed"
        return False

def Numbers_Eval(numbers_str):
    result = False
    try:
        numbers_str = str(numbers_str)
        result = eval(numbers_str)
        return result
    except Exception,e:
        print e
        print("Eval Failed: %s" % e)
        return result


class CompareException(Exception):
    pass
    # def __init__(self, first, second):
    #     Exception.__init__(self)
    #     self.first = first
    #     self.second = second
    #     print "Compare Error: first-%s, second-%s" % (self.first,self.second)

def assert_Bigthan(arg1,arg2, msg=None):
    '''
    arg1 > arg2
    '''
    try:
        if arg1 > arg2:
            return True
        else:
            print msg
            return False
    except Exception as e:
        print "Compare Failed: "
        raise e

def assert_Smallthan(arg1,arg2, msg=None):
    '''
    arg1 < arg2
    '''
    try:
        if arg1 < arg2:
            return True
        else:
            print msg
            return False
    except Exception as e:
        print "Compare Failed: "
        raise e

def assert_Equal(arg1,arg2, msg=None):
    '''
    arg1 = arg2
    '''
    try:
        # print arg1,type(arg1),arg2,type(arg2)
        if arg1 == arg2:
            return True
        else:
            print msg
            return False
    except Exception as e:
        print "Compare Failed: "
        raise e

def assert_Not_Equal(arg1,arg2, msg=None):
    '''
    arg1 = arg2
    '''
    try:
        if arg1 != arg2:
            return True
        else:
            print msg
            return False
    except Exception as e:
        print "Compare Failed: "
        raise e

def assert_isNone(arg,msg=None):
    try:
        if arg == None:
            return True
        else:
            print msg
            return False
    except Exception as e:
        print "Compare Failed: "
        raise e

def assert_isnotNone(arg,msg=None):
    try:
        if arg != None:
            return True
        else:
            print msg
            return False
    except Exception as e:
        print "Compare Failed: "
        raise e

def int_2_strlist(input):
    new = list(str(input))
    int_list = []
    for i in new:
        int_list.append(int(i))
    print(int_list)
    return int_list

def Get_Date(timetype='today'):
    now=datetime.datetime.now()
    if timetype.lower()=='today':
        r_str="%s-%s-%s" % (now.year,now.month,now.day)
    elif timetype.lower()=='tomorrow':
        tomo = now - 24
        r_str="%s-%s-%s" % (tomo.year,tomo.month,tomo.day)
    else:
        r_str=False
    return r_str

def Get_Now_TimeStr():
    now=datetime.datetime.now()
    r_str = ("%s-%s-%s_%s-%s-%s" % (now.year,now.month,now.day,now.hour,now.minute,now.second))
    return r_str

def Get_Current_Time():
    now=datetime.datetime.now()
    r_str = ("%s-%s-%s %s:%s:%s:%s" % (now.year,now.month,now.day,now.hour,now.minute,now.second,now.microsecond))
    return r_str

def Get_Tomrrow_Time():
    now=datetime.datetime.now()
    tomrrow = now + datetime.timedelta(days=-1)
    r_str = '{:%Y-%m-%d %X}'.format(tomrrow)
    return r_str

def Run_exe_or_bat(path):
   subprocess.Popen(path)

def random_nums(randomlength=12):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random()
    try:
        randomlength = int(randomlength)
    except:
        pass
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def random_strs(randomlength=12):
    str = ''
    chars = 'AaBbCcDdEeFf0123456789'
    length = len(chars) - 1
    random = Random()
    try:
        randomlength = int(randomlength)
    except:
        pass
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def Utf8_To_GBK(strs):
    try:
        print type(strs)
        strs = strs.decode('utf-8').encode('gbk')
    except Exception,e:
        print e
    return strs

def Utf8_To_Unicode(strs):
    try:
        print type(strs)
        strs = strs.decode('utf-8')
    except Exception,e:
        print e
    return strs

def parse_json(arg):
    new_arg = json.loads(arg)
    return new_arg

def str_decode_uicode(arg):
    try:
        arg = str(arg)
        newarg = arg.decode('utf-8')
    except:
        newarg = arg
    return newarg

def list_decode_uicode(arg):
    new_arg = []
    for i in arg:
        new_arg.append(i.decode('utf-8'))
    return new_arg

def dict_decode_uicode(arg):
    new_arg = {}
    for key,value in arg.items():
        new_arg[key]=value.decode('utf-8')
    return new_arg

def str_encode_utf8(strs):
    try:
        newstr = strs.encode('utf-8')
    except:
        newstr = strs
    return newstr

def str_encode_utf8_butCh(strs):
    try:
        strs = strs.decode('utf8')
    except:
        pass
    #matcher = re.compile(u'[\u4e00-\u9fa5]+')
    newstr = ''
    for one in strs:
        #match = matcher.search(ustrs)
        #if match:
        print "Star Print uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"
        print one
        if one >= u'\u4e00' and one<=u'\u9fa5':
            # newstr = ''
            # for uchar in strs:
            #     if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
            #         uchar = uchar.encode("utf8")
            #     else:
            #         uchar = uchar.encode('utf-8')
            #     newstr = newstr + uchar
            newone = one.encode('gb2312')
            print "--------------------------"
            print newone
        else:
            newone = one.encode('utf-8')
        newstr = newstr + newone
    return newstr

def list_encode_utf8(arg):
    new_arg = []
    for i in arg:
        new_arg.append(i.encode('utf-8'))
    return new_arg

def dict_encode_utf8(arg):
    new_arg = {}
    for key,value in arg.items():
        new_arg[key]=value.encode('utf-8')
    return new_arg

def Rnum_to_Numstr(r_num):
    typearg = type(r_num)
    if typearg == list:
        n_list = []
        for dit in r_num:
            if type(dit) == dict:
                n_dit = {}
                for key,value in dit.items():
                    new_value = Rnum_to_Numstr(value)
                    n_dit[key] = new_value
            elif type(dit) == list:
                n_dit = []
                for itm in dit:
                    n_dit.append(Rnum_to_Numstr(itm))
            else:
                n_dit = rnumber_parse_str(dit)
            n_list.append(n_dit)
        new_arg = n_list
    elif typearg == dict:
        n_dict = {}
        for key,value in r_num.items():
            if type(value) == dict:
                n_dit = {}
                for key1,value1 in value.items():
                    new_value1 = Rnum_to_Numstr(value1)
                    n_dit[key1] = new_value1
            elif type(value) == list:
                n_dit = []
                for itm in value:
                    n_dit.append(Rnum_to_Numstr(itm))
            else:
                 n_dit = rnumber_parse_str(value)
            n_dict[key] = n_dit
        new_arg = n_dict
    else:
        new_arg = rnumber_parse_str(r_num)
    return new_arg

def str_to_listordict(strs):
    list1 = eval(strs)
    return list1

def is_number(strs):
    """判断一串字符或数字是否是数字"""
    print "*** This is is_number Function ***"
    if type(strs)==str:
        try:
            strs = strs.encode('utf-8')
        except Exception as e:
            print "Can't encode strs : %s " % strs
    try:
        if strs != '':
            # if strs[0] != '0':
            #     uchar = float(strs)
            #     return True
            if len(str(strs)) > 1:
                if strs[0] == '0':
                    return False
            uchar = float(strs)
            return True
    except Exception as e:
        return False

def str_parse_number(num_strs):
    try:
        number = int(num_strs)
        return number
    except:
        number = float(num_strs)
        return number

def rnumber_parse_str(r_num):
    try:
        matcher = re.compile('r[0-9]+[\.]?[0-9]*')
        match = matcher.search(r_num)
        if match:
            new_strs = r_num.strip("r")
        else:
            new_strs = r_num
        return new_strs
    except:
        print "number_parse_str error : %s ,%s" % (r_num,type(r_num))
        return r_num

def Repair_DataType_FromStr(strs):
    try:
        strs = str_encode_utf8(strs)
    except:
        pass
    if is_number(strs):
        new_1 = str_parse_number(strs)
    elif strs != '' and type(strs) == str:
        if (strs[0]=='{' or strs[0]=='[') :
            new_1 = str_to_listordict(strs)
            new_1 = Unicode_Encode_Utf8(new_1)               # 有可能字典或列表中 还有unicode编码
        else:
            new_1 = strs
    else:
        new_1 = strs
    new_1 = Rnum_to_Numstr(new_1)
    return new_1

def Unicode_Encode_Utf8(arg):
    type_arg = type(arg)
    new_arg = False
    if type_arg == str or type_arg == unicode:
        new_arg = Repair_DataType_FromStr(arg)
    elif type_arg == list:
        new_arg = []
        for option in arg:
            new_arg.append(Repair_DataType_FromStr(option))
    elif type_arg == dict:
        new_arg = {}
        for key,value in arg.items():
            key = str_encode_utf8(key)               #有可能key也是Unicode
            new_arg[key]=Repair_DataType_FromStr(value)
    return new_arg

def Unicode_Encode_Utf8_Json(arg):
    new = Unicode_Encode_Utf8(arg)
    new_arg = json.dumps(new)
    return new_arg

def Create_My_Dictionary(*args):
    '''
    create dictionary
    :param args: a='abc',b=[1,2,3]
    :return: new_dict:{"a"='abc';'b':[1 2 3]}
    '''
    try:
        new_dict = {}
        for eachone in args:
            l = eachone.split('=')
            key = l[0]
            value = eval(l[1])
            new_dict[key]=value
        return new_dict
    except Exception as e:
        raise e

def Arg1_Contain_Arg2(arg1,arg2):
    try:
        if arg2 in arg1:
            return True
        else:
            return False
    except Exception as e:
        raise e

def Remove_Str_From_List(l,rs,count=None):
    if count==None:
        c = l.count(rs)
        for i in range(c):
            l.remove(rs)
    else:
        c = int(count)
        sc = l.count(rs)
        if sc <= c:
            tc = sc
        else:
            tc = c
        for i in range(tc):
            l.remove(rs)
    return l

def Post_Http(url,RFdict1):
    jsons = Unicode_Encode_Utf8_Json(RFdict1)
    https = post(url,jsons)
    return https.text

def Ftp_Put_PadLog(dirpath,store_url_port):
    store_ip = store_url_port.split(':')[0]
    if os.path.exists(dirpath):
        ftp_ip = '10.66.161.36'
        ftp_port = 21
        ftp_user = 'robot'
        ftp_passwd = '123456'
        ftp=FTP()
        # ftp.set_debuglevel(2)
        ftp.connect(host=ftp_ip,port=ftp_port,timeout=999)
        ftp.login(user=ftp_user,passwd=ftp_passwd)
        print ftp.getwelcome()
        newpath = os.path.join(dirpath,os.listdir(dirpath)[0])
        newfilename = '[%s]_' % store_ip + os.path.split(dirpath)[1]
        filename = newfilename + '.txt'
        ftp.cwd("PadLog")
        ftp.storbinary('STOR %s' % filename, open(newpath,'rb'))
        # print ftp.dir()
        # ftp.set_debuglevel(0)
        ftp.quit()
        print('put the pad log to ftp server Success !!!')
    else:
        raise("Has no the file path : %s" % dirpath)

def Parse_Decimal_SqlData(sqldata):
    data = str(sqldata)
    match_str ='\(\(([a-zA-z]+.?[a-zA-z]*\((.+)\)),\),\)'
    p = re.compile(match_str)
    m = p.match(data)
    if m:
        print("this str should parse sql tuple data ...")
        old_s = m.group(1)
        new_s = m.group(2)
        data = data.replace(old_s,new_s)
    re_str = eval(data)
    return re_str

def Re_Get_Html_Str(htmlstr,t_re):
    '''
    Get target str From html strs Use Re Function

    :param htmlstr:  all html strs

    :param t_re:  target re

    :return: math_str
    '''
    t_xiaofei = '.+id="amount">([0-9]+.[0-9]+)<.+'
    t_xf =  '.+id="serviceCharge-tip">([0-9]+.[0-9]+)<.+'
    t_service =  '.+id="tip-amount">([0-9]+.[0-9]+)<.+'
    t_youhui =  '.+id="discount-amount">([0-9]+.[0-9]+)<.+'
    t_yingshou =  '.+id="should-amount">([0-9]+.[0-9]+)<.+'
    # t_re = t_yingshou
    htmllist = htmlstr.split('\n')
    p = re.compile(t_re)
    for line in htmllist:
        math = p.match(line)
        if math:
            print line
            return math.group(1)


if __name__=='__main__':
    # f = open(r"C:\Users\chenliang\Desktop\testhtml.html","r")
    # all = f.read()
    # f.close()
    # print Re_Get_Html_Str(all)
    print "1111111111111111"

