# -*- coding:UTF-8 -*-
# !/bin/sh
'''
Author: chenliang
Created Time: 2016/4/28
Describtion: Some Public Fuction use for Manage ConfigFile
'''

import os, yaml
import ConfigParser as cp
import re

# -------------- Varliable -------------------
TestbedFile = "TestBed.ini"
configPyPath = __file__
curpath = os.path.dirname(configPyPath)
rootDir = os.path.split(curpath)[0]
configDir = os.path.join(rootDir, "Config")
TestEngineConfigName = 'TestEngineConfig.ini'

# -------------- Function -------------------
def iTestFrameGetTestBed():
    testBed = Parser_Config(TestEngineConfigName,'TestParams','TestBedName')
    return testBed

def Get_ConfigFile(targetTittle):
    Tittle = targetTittle.lower()
    curpath = os.path.dirname(configPyPath)
    rootDir = os.path.split(curpath)[0]
    configDir = os.path.join(rootDir, "Config")
    for name in os.listdir(configDir):
        if name.lower() == Tittle:
            configPath = os.path.join(configDir, name)
        elif name.lower() == Tittle and name == os.listdir(configDir)[-1]:
            print("the targetTittle: %s is not define" % targetTittle)
    return configPath


def Get_System_Version(testbed, systype):
    if systype.lower() == "pos":
        vertitle = Parse_Pos_Version_Class(testbed)
    return vertitle


def Get_Pos_Moudle_Class(version, testfile, type):
    Cfile = Get_ConfigFile(testfile)
    conf = cp.ConfigParser()
    conf.read(Cfile)
    sectionname = "Default"
    type = type + "_"
    try:
        options = conf.options(sectionname)
        for option in options:
            if type in option and version in option:
                value = conf.get(sectionname, option)
    except Exception, error:
        print("Get Configuration Falied %s-%s-%s" % (version, testfile, type))
        return error
    return value

def Parser_TestBed_Config(TargetType, TargetOptin, vertitle=None):
    testfile = iTestFrameGetTestBed()
    Cfile = Get_ConfigFile(testfile)
    conf = cp.ConfigParser()
    conf.read(Cfile)
    try:
        value = conf.get(TargetType, TargetOptin)
    except Exception, error:
        print("Get Configuration Falied %s-%s-%s" % (testfile, TargetType, TargetOptin))
        return error
    value = value.decode('gb2312').encode('utf-8')
    return value

def Parser_Config(testfile, TargetType, TargetOptin, vertitle=None):
    Cfile = Get_ConfigFile(testfile)
    conf = cp.ConfigParser()
    conf.read(Cfile)

    if vertitle == None:
        try:
            value = conf.get(TargetType, TargetOptin)
        except Exception, error:
            print("Get Configuration Falied %s-%s-%s" % (testfile, TargetType, TargetOptin))
            return error
        value = value.decode('gb2312').encode('utf-8')

    else:
        moudlestr = "_class_module"
        if TargetType == 'Pos_keyboad_numbers':
            option = "button" + moudlestr + "_" + vertitle
        else:
            option = TargetOptin.split('_')[0] + moudlestr + "_" + vertitle
        try:
            moudle = conf.get("Default", option)
            id = conf.get(TargetType, TargetOptin)
            value = moudle + id
        except Exception, error:
            print("Get Configuration Falied %s-%s-%s" % (testfile, TargetType, TargetOptin))
            return error
    return value

def Parse_config_Set(testfile, TargetType, TargetOptin,Value):
    Cfile = Get_ConfigFile(testfile)
    conf = cp.ConfigParser()
    conf.read(Cfile)
    old_value = conf.get(TargetType, TargetOptin)
    # print(Cfile)
    # print(conf.get(TargetType, TargetOptin))
    # print("write : ----> %s %s %s %s" % (testfile,TargetType, TargetOptin,Value))
    # conf.set(TargetType,TargetOptin,Value)
    # print(conf.get(TargetType, TargetOptin))
    # 替换值
    f = open(Cfile,'r')
    all_str = f.read()
    f.close()
    new_all_str = all_str.replace(old_value,Value)
    f = open(Cfile, 'w')
    f.write(new_all_str)
    f.flush()
    f.close()
    # 这样写，注释就没有了
    # with open(Cfile,'w+') as f:
    #     conf.write(f)
    #     f.flush()
    #     f.close()

def Parse_config_to_dict(testfile, TargetType, vertitle=None):
    Cfile = Get_ConfigFile(testfile)
    conf = cp.ConfigParser()
    conf.read(Cfile)
    try:
        options = conf.options(TargetType)
        op_dict = {}
        for option in options:
            if vertitle != None:
                moudlestr = "_class_module"
                if TargetType.lower() == 'pos_keyboad_numbers':
                    n_option = "button" + moudlestr + "_" + vertitle
                else:
                    n_option = option.split('_')[0] + moudlestr + "_" + vertitle
                moudle = conf.get("Default", n_option)
                id = conf.get(TargetType, option)
                op_dict[option] = moudle + id
            else:
                op_dict[option] = conf.get(TargetType, option)
    except Exception, error:
        print("Get Configuration Falied %s-%s" % (testfile, TargetType))
        return error
    print(op_dict)
    return op_dict


def Parse_Pos_Version_Class(testfile):
    Cfile = Get_ConfigFile(testfile)
    try:
        conf = cp.ConfigParser()
        conf.read(Cfile)
        version = conf.get('Pos', 'Pos_version')
    except Exception, error:
        print("Get Configuration Falied Pos-Pos_version")
        return error
    print("the pos version is : %s" % version)
    n_version = version[:4].strip("V")
    verTitle = n_version.replace('.', '')
    return verTitle


def initYml(yaml_file, filename):
    """初始化yaml文件，获得接口相关信息
    """
    mobile_from_yaml = {}
    f = open(yaml_file, 'r')
    apis_dict = yaml.load(f)
    f.close()
    mobile_from_yaml.setdefault(filename, apis_dict['build'])
    # print "version is : %s" % apis_dict['version']
    return mobile_from_yaml

def initTargetYml(filename,option):
    dir = os.path.join(configDir,'Yaml_Data')
    yaml_file = os.path.join(dir,filename+'.yml')
    dict_from_yaml = {}
    f = open(yaml_file, 'r')
    apis_dict = yaml.load(f)
    f.close()
    dict_from_yaml.setdefault(filename, apis_dict['build'])
    return dict_from_yaml[filename][option]

def initYmlDir(dir):
    """初始化yaml文件，获得接口相关信息
    """
    yaml_dir = dir
    all_yaml_dict = {}

    for root, dirs, files in os.walk(yaml_dir):  # 遍历目录下文件
        for fn in files:
            filename = fn.split('.')[0]  # 得到文件名前缀
            yaml_file = os.path.join(yaml_dir, fn)
            file_dict = initYml(yaml_file, filename)
            all_yaml_dict[filename] = file_dict[filename]
    return all_yaml_dict


if __name__ == "__main__":
    # str1 = Parser_Config("DishesInfo.ini", "Dish_single", "name")
    # str2 = Parser_Config("StoreInfo.ini", "store1", "store_leader")
    # str3 = Parser_Config("StoreInfo.ini", "store1", "address_xx")
    # # str1 = str1.decode('gb2312')
    # # str2 = str2.decode('gb2312')
    # # str3 = str3.decode('gb2312')
    # print str1, str2, str3
    # print "可以输入中文"
    # print "IFS国际金融中心"
    # print Parser_Config("Testbed_43.ini", "Newspicyway", "password")
    #
    # Parse_Pos_Version_Class("Testbed_6.ini")
    #
    # ver = Get_System_Version("Testbed_6.ini", "Pos")
    #
    # print Parse_config_to_dict("Pos.ini", "Pos_keyboad_numbers", ver)
    #
    # print Parser_Config("Pos.ini", "Pos_keyboad_numbers", "1", ver)
    # a = initYmlDir('E:\WorkSpace\Infocare_WorkSpace\AutoTest\iTestFrame\Config\Yaml_Data')
    # print a['app'].keys()
    Parse_config_Set('TestEngineConfig.ini','TestParams','TestBedName','TestBed_beta.ini')
