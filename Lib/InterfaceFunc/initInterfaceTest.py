# coding:utf-8
# author:chenliang
# write time:2017-10-23

from Lib.MyConfig import user_saas,pwd_saas
from InterfaceConfig import V0_Interface,V1_Interface
from InterfaceSession import InterfaceSession as session
from Lib.ManageDataBase import ManageSqlite
from Lib.LogService import DB_FILE_PATH
from Lib.LogService import logger
from InterfaceConfig import LOGIN_TABLE_NAME

class Singleton(object):
    def __new__(cls,*args,**kw):
        if not hasattr(cls,'_instance'):
            orig=super(Singleton,cls)
            cls._instance=orig.__new__(cls,*args,**kw)
        return cls._instance

class InitToken(Singleton):

    def __init__(self):

        self.create_apitoken_table_str = '''CREATE TABLE %s (
                                  'providerId' varchar(20) NOT NULL,
                                  'token' varchar(20) NOT NULL,
                                  'userid' varchar(20) NOT NULL,
                                  'status' varchar(20) NOT NULL,
                                   PRIMARY KEY ('token')
                                )''' % LOGIN_TABLE_NAME

    def initTestInterface(self):

        ms = ManageSqlite(DB_FILE_PATH)
        # 判断如果数据库已有 token和providerid 就不用再次访问了
        try:
            ms.DropTable(LOGIN_TABLE_NAME)
            ms.CreateTable(self.create_apitoken_table_str)
        except:
            s = ms.Select_Sql('select providerId,token,userid from %s' % LOGIN_TABLE_NAME)
            logger.info(s)
            ms.Close()
            return s[0]
        myses = session()
        # 客服登录
        try:
            interface_dict = V0_Interface.api_login
            logger.info(interface_dict['describtion'],printstatus=True)
            myses.setBody(interface_dict['body'])
            myses.changeBody('email', user_saas)
            myses.changeBody('password', pwd_saas)
            result = myses.post(interface_dict['second_url'],printtype=True)
            # print result
            code = result['result']['code']
            user_id = result['result']['user_id']
        except Exception as e:
            logger.error("%s ERROE, please check service or http agent is open!\n" % (interface_dict['second_url']))
            raise(e)
        # 获取token
        try:
            interface_dict = V0_Interface.api_token
            logger.info(interface_dict['describtion'],printstatus=False)
            myses.setBody(interface_dict['body'])
            myses.changeBody('code', code)
            result = myses.post(interface_dict['second_url'],printtype=False)
            # print result
            token = result['result']['token']
        except Exception as e:
            logger.error("get user token ERROE, please check service!\n")
            raise e
        # 获取provider id
        interface_dict = V0_Interface.api2_OpenHelpCenterApi_getCurrentUserInfo
        logger.info(interface_dict['describtion'],printstatus=False)
        myses.setParams(interface_dict['params'])
        myses.changeParams('_token', token)
        result = myses.post(interface_dict['second_url'],printtype=False)
        # print result
        providerid = result['result']['providerId']
        myses.close()
        # 写入数据库 providerid、token
        # ms = ManageSqlite(DB_FILE_PATH)
        # ms.DropTable(LOGIN_TABLE_NAME)
        # ms.CreateTable(createtable_str)
        insert_dict = {'providerId':providerid,'token':token, 'userid':user_id, 'status':'1'}
        ms.Insert_Sql(LOGIN_TABLE_NAME,insert_dict)
        s = ms.Select_Sql('select providerId,token,userid from %s' % LOGIN_TABLE_NAME)
        logger.info(s)
        ms.Close()
        return s[0]

if __name__=='__main__':
    init = InitToken()
    init.initTestInterface()