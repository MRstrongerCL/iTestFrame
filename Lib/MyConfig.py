# coding:utf-8
import os
from ParserConfigUnit import Parser_Config
from ParserConfigUnit import iTestFrameGetTestBed

# ***************** 常量 ************************

# 登录信息
testbed = iTestFrameGetTestBed()
url_independent = Parser_Config(testbed, "Independent", "url")
service_independent = url_independent.split('//')[-1]
user_independent = Parser_Config(testbed, "Independent", "user")
pwd_independent = Parser_Config(testbed, "Independent", "password")
url_saas = Parser_Config(testbed, "Saas", "url")
service_saas = url_saas.split('//')[-1]
user_saas = Parser_Config(testbed, "Saas", "user")
pwd_saas = Parser_Config(testbed, "Saas", "password")

class MysqlInfo:
    '''数据库信息'''
    database_ip = Parser_Config(testbed, "Mysql", "database_ip")
    admin_user = Parser_Config(testbed, "Mysql", "user_admin")
    admin_pwd = Parser_Config(testbed, "Mysql", "password_admin")
    admin_dbName = Parser_Config(testbed, "Mysql", "dbname_admin")
    saas_user = Parser_Config(testbed, "Mysql", "user_saas")
    sass_pwd = Parser_Config(testbed, "Mysql", "password_saas")
    saas_dbName = Parser_Config(testbed, "Mysql", "dbname_saas")
    help_user = Parser_Config(testbed, "Mysql", "user_help")
    help_pwd = Parser_Config(testbed, "Mysql", "password_help")
    help_dbName = Parser_Config(testbed, "Mysql", "dbname_help")