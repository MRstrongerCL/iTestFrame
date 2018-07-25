# coding:utf-8
# chenliang 20171026

from Lib.ManageDataBase import ManageMysqlBase
from Lib.ParserConfigUnit import Parser_Config
from Lib.ParserConfigUnit import iTestFrameGetTestBed

class Singleton(object):
    def __new__(cls,*args,**kw):
        if not hasattr(cls,'_instance'):
            orig=super(Singleton,cls)
            cls._instance=orig.__new__(cls,*args,**kw)
        return cls._instance

class ManageAdminDB(Singleton):

    def __init__(self):
        testbed = iTestFrameGetTestBed()
        ip = Parser_Config(testbed, "Mysql", "database_ip")
        user = Parser_Config(testbed, "Mysql", "user_admin")
        password = Parser_Config(testbed, "Mysql", "password_admin")
        dbName = Parser_Config(testbed, "Mysql", "dbname_admin")
        self.MysqlAdmin = ManageMysqlBase(ip, user, password, dbName)

    def __del__(self):
        self.MysqlAdmin.Close()

class ManageHelpDB(Singleton):

    def __init__(self):
        testbed = iTestFrameGetTestBed()
        ip = Parser_Config(testbed, "Mysql", "database_ip")
        user = Parser_Config(testbed, "Mysql", "user_help")
        password = Parser_Config(testbed, "Mysql", "password_help")
        dbName = Parser_Config(testbed, "Mysql", "dbname_help")
        self.MysqlHelp = ManageMysqlBase(ip, user, password, dbName)

    def __del__(self):
        self.MysqlHelp.Close()

class ManageSassDB(Singleton):

    connection_pool = 0 #连接池个数
    def __init__(self):
        testbed = iTestFrameGetTestBed()
        ip = Parser_Config(testbed, "Mysql", "database_ip")
        user = Parser_Config(testbed, "Mysql", "user_saas")
        password = Parser_Config(testbed, "Mysql", "password_saas")
        dbName = Parser_Config(testbed, "Mysql", "dbname_saas")
        dbport = Parser_Config(testbed, "Mysql", "database_port")
        if self.connection_pool == 0:
            self.MysqlSaas = ManageMysqlBase(ip, user, password, dbName, dbport)
            self.connection_pool += 1

    def getProviderIdFromDomain(self,domain_str):
        domain = domain_str.split('.')[0]
        select_str = 'Select id from provider where sub_domain="%s"' % (domain)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getProviderIdFromUser(self,useremail):
        if "@" in useremail:
            select_str = 'Select provider_id from user where email="%s"' % (useremail)
        else:
            select_str = 'Select provider_id from user where mobile_phone="%s"' % (useremail)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getServiceDeskFromID(self,id):
        select_str = "Select id,name from service_desk where id=%s" % (id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getServiceDeskFromProviderid(self,providerID,limit_count=1):
        select_str = "Select id,name from service_desk where provider_id=%s limit %s" % (providerID,limit_count)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list

    def getDefaultServiceDeskIDFromProviderid(self,providerID):
        select_str = u'Select id from service_desk where (name="默认服务台" or name="DEFAULT_SERVICE_DESK_NAME") and provider_id=%s and deleted=0' % (providerID)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getUserFromProviderid(self,providerID,type='customer',limit_count=1,valid=1):
        if type=='customer':
            select_str = "Select id,name,nickname,mobile_phone,email from user where provider_id=%s and type='customer' and deleted=0 and valid=%s limit %s" % (providerID, valid, limit_count)
        else:
            select_str = "Select id,name,nickname,mobile_phone,email from user where provider_id=%s and type='engineer' and deleted=0  and valid=%s limit %s" % (providerID, valid, limit_count)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list

    def getUserPwdFromID(self,id):
        select_str = "Select password from user where id=%s" % (id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        if result_list != []:
            if result_list[0][0] == None:
                return "123456"
            else:
                return result_list[0][0]

    def getUserFromID(self,id):
        select_str = "Select id,name,nickname,mobile_phone,email from user where id=%s" % (id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getUserFromName(self,Name):
        select_str = "Select id,name,nickname,mobile_phone,email from user where name=%s" % (Name)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getUserFromEmailPid(self, email, providerid):
        if "@" in email:
            select_str = 'Select id,name,nickname,mobile_phone,email from user where email="%s" and provider_id=%s' % (email, providerid)
        else:
            select_str = 'Select id,name,nickname,mobile_phone,email from user where mobile_phone="%s" and provider_id=%s' % (email, providerid)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getEngineerFromProviderid(self,providerID,default_service_desk=None,limit_count=1):
        if default_service_desk==None:
            select_str = "Select id,nickname,user_id from engineer where provider_id=%s limit %s" % (providerID, limit_count)
        else:
            select_str = "Select id,nickname,user_id from engineer where provider_id=%s and default_service_desk_id=%s limit %s" % (providerID,default_service_desk,limit_count)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list

    def getEengineerfromID(self,id):
        select_str = "Select id,nickname,user_id from engineer where id=%s" % (id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getEengineerfromNickname(self,Nickname):
        select_str = "Select id,nickname,user_id from engineer where nickname=%s" % (Nickname)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getEengineerIDfromServiceDesk(self,service_desk_id):
        select_str = "Select engineer_id from engineer_r_service_desk where service_desk_id=%s" % (service_desk_id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list

    def getWebFormFromProviderid(self,providerID,limit_count=1):
        select_str = "Select id,name,type,deleted from custom_webform where provider_id=%s limit %s" % (providerID, limit_count)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list

    def getServiceIdFromEngineerID(self,engineer_id):
        select_str = "Select id from engineer_r_service_desk where engineer_id=%s" % (engineer_id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getEngineerIDFromServiceID(self,service_id,limit_count=1):
        select_str = "Select engineer_id from engineer_r_service_desk where id=%s limit %s" % (service_id, limit_count)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list

    def getChannelIDFromTypeName(self,providerID,type,namelike=None,enable=None,delete=None,limit_count=1):
        select_str = "Select id from channel where provider_id={} and type='{}' and enabled={} and deleted={} and name like '{}%' limit {}".format(providerID, type, enable, delete, namelike, limit_count)
        if namelike == None:
            select_str = select_str.replace(" and name like '{}%'".format(namelike), '')
        if delete == None:
            select_str = select_str.replace(' and deleted={}'.format(delete),'')
        if enable == None:
            select_str = select_str.replace(' and enabled={}'.format(enable), '')
        try:
            select_str = select_str.decode('utf8')
        except:
            pass
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list

    def getChannelUidFromId(self,id):
        select_str = "Select uid from channel where id={}".format(id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getChannelNameFromId(self,id):
        select_str = "Select name from channel where id={}".format(id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getChannelKeyFromId(self,id,key):
        select_str = "Select {0} from channel where id={1}".format(key,id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        value = result_list[0][0]
        if value == '\x00':
            return 0
        elif value == '\x01':
            return 1
        else:
            return value

    def getChannelChartUidFromUid(self,uid,type='web'):
        select_str = "Select chat_form_uid from channel_{}_config where channel_uid='{}'".format(type,uid)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getChannelTickeUidFromUid(self,uid,type='web'):
        select_str = "Select ticket_form_uid from channel_{}_config where channel_uid='{}'".format(type,uid)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getChannelConfigIDFromUid(self,uid,type='web'):
        select_str = "Select id from channel_{}_config where channel_uid='{}'".format(type,uid)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getChannelConfigOldIDFromUid(self,uid,type='web'):
        select_str = "Select old_id from channel_{}_config where channel_uid='{}'".format(type,uid)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getChannelConfigEmailFromUid(self,uid,type='web'):
        select_str = "Select email from channel_{}_config where channel_uid='{}'".format(type,uid)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getChannelConfigTargetKeyFromUid(self,uid,key='id',type='web'):
        select_str = "Select {0} from channel_{1}_config where channel_uid='{2}'".format(key,type,uid)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getFormIDFromTypeName(self,providerID,type,namelike=None,enable=None,delete=None,limit_count=1):
        select_str = "Select id from form where provider_id={} and type='{}' and enabled={} and deleted={} and name like '{}%' limit {}".format(providerID, type, enable, delete, namelike, limit_count)
        if namelike == None:
            select_str = select_str.replace(" and name like '{}%'".format(namelike), '')
        if delete == None:
            select_str = select_str.replace(' and deleted={}'.format(delete),'')
        if enable == None:
            select_str = select_str.replace(' and enabled={}'.format(enable), '')
        try:
            select_str = select_str.decode('utf8')
        except:
            pass
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list

    def getFormUidFromId(self,id):
        select_str = "Select uid from form where id={}".format(id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getFormNameFromId(self,id):
        select_str = "Select name from form where id={}".format(id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list[0]

    def getFormKeyFromId(self,id,key):
        select_str = "Select {0} from form where id={1}".format(key,id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        value = result_list[0][0]
        if value == '\x00':
            return 0
        elif value == '\x01':
            return 1
        else:
            return value

    def getAssignRuleIDFromTypeName(self,providerID,type,namelike=None,active=None,delete=None,limit_count=1):
        select_str = "Select id from assign_Rule where provider_id={} and type='{}' and active={} and deleted={} and name like '{}%' limit {}".format(providerID, type, active, delete, namelike, limit_count)
        if namelike == None:
            select_str = select_str.replace(" and name like '{}%'".format(namelike), '')
        if delete == None:
            select_str = select_str.replace(' and deleted={}'.format(delete),'')
        if active == None:
            select_str = select_str.replace(' and active={}'.format(active), '')
        try:
            select_str = select_str.decode('utf8')
        except:
            pass
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        return result_list

    def getAssignRuleKeyFromId(self,id,key):
        select_str = "Select {0} from assign_Rule where id={1}".format(key,id)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        value = result_list[0][0]
        if value == '\x00':
            return 0
        elif value == '\x01':
            return 1
        else:
            return value

    def getTicketidFromProviderIdAndStatus(self,providerId,status='open',limit_count=1,delete=0):
        select_str = "Select id from ticket where provider_id={} and status='{}' and deleted='{}' limit {}".format(providerId, status, delete,limit_count)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        ticket_id_list = []
        for one in result_list:
            ticket_id_list.append(one[0])
        return ticket_id_list

    def getAttachmentid(self,providerId,deleted=0,limit_count=1):
        select_str = "Select id from attachment where provider_id={} and deleted='{}' limit {}".format(providerId, deleted,
                                                                                                  limit_count)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        attachment_id_list = []
        for one in result_list:
            attachment_id_list.append(one[0])
        return attachment_id_list

    def deleteChannelOnlyOneFromName(self,channel_name_like,providerId):
        select_str = 'Select id from channel where provider_id={} and deleted=0 and name like "%{}%" ORDER BY created_at ASC'.format(providerId,channel_name_like)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        if result_list!=[]:
            channel_id_last = result_list[-1][0]   #排除最后一条渠道
            update_str = 'UPDATE channel SET deleted=1 WHERE provider_id={0} and id!={1} and name like "%{2}%"'.format(providerId,channel_id_last,channel_name_like)
            print("----> Udate CMD: %s" % update_str)
            self.MysqlSaas.excute_sql(update_str)

    def deleteAssignRuleOnlyOneFromName(self,rule_name_like,providerId):
        select_str = "Select id from assign_rule where provider_id={} and deleted=0 and name like '%{}%' ORDER BY created_at ASC".format(
            providerId, rule_name_like)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        if result_list != []:
            rule_id_last = result_list[-1][0]  # 排除最后一条规则
            update_str = 'UPDATE assign_rule SET deleted=1 WHERE provider_id={0} and id!={1} and name like "%{2}%"'.format(providerId,rule_id_last,rule_name_like)
            print("----> Udate CMD: %s" % update_str)
            self.MysqlSaas.excute_sql(update_str)

    def close(self):
        print('**************** Close DB ****************')
        self.MysqlSaas.Close()

    def dispose(self):
        self.MysqlSaas.dispose()

class ManageSassChatDB(Singleton):

    def __init__(self):
        testbed = iTestFrameGetTestBed()
        ip = Parser_Config(testbed, "Mysql", "database_ip")
        user = Parser_Config(testbed, "Mysql", "user_saas_chat")
        password = Parser_Config(testbed, "Mysql", "password_saas_chat")
        dbName = Parser_Config(testbed, "Mysql", "dbname_saas_chat")
        dbport = Parser_Config(testbed, "Mysql", "database_port")
        self.MysqlSaas = ManageMysqlBase(ip, user, password, dbName, dbport)

    def getChatKeyFromStatusAndProviderID(self,key,providerid,status_str='new',istype=True, limit_count=1):
        if istype:
            select_str = "Select %s from module_talk_chat where status='%s' and provider_id=%s limit %s" % (key, providerid,status_str ,limit_count)
        else:
            select_str = "Select %s from module_talk_chat where status!='%s' and provider_id=%s limit %s" % (key, providerid, status_str, limit_count)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        if result_list != []:
            value = result_list[0][0]
            if value == '\x00':
                return 0
            elif value == '\x01':
                return 1
            else:
                return value
        else:
            return result_list

    def getChatKeyFromChatid(self,key,chatid,istype=True):
        if istype:
            select_str = "Select {0} from moudle_talk_chat where id={1}".format(key, chatid)
        else:
            select_str = "Select {0} from moudle_talk_chat where id!={1}".format(key, chatid)
        result_list = self.MysqlSaas.Select_Mysql_Sql(select_str)
        if result_list != []:
            value = result_list[0][0]
            if value == '\x00':
                return 0
            elif value == '\x01':
                return 1
            else:
                return value
        else:
            return result_list

    def close(self):
        print('**************** Close DB ****************')
        self.MysqlSaas.Close()

if __name__=='__main__':
    msDB = ManageSassDB()
    # print msDB.getServiceDeskFromProviderid('1656')
    # print msDB.getUserFromProviderid('1656')
    # print msDB.getEngineerFromProviderid('1656',2022)
    # print msDB.getServiceDeskFromID(2025)
    # print msDB.getUserFromID(40716)
    # print msDB.getEengineerfromID(5617)
    # print msDB.getEengineerIDfromServiceDesk(2022)
    # user = Parser_Config("TestBed_Beta.ini", "Saas", "user")
    # print msDB.getProviderIdFromUser(user)
    # print msDB.getUserPwdFromID(44148)
    # print msDB.getServiceIdFromEngineerID(12)
    # print msDB.getEngineerIDFromServiceID(6)
    # print msDB.getDefaultServiceDeskIDFromProviderid(1160)
    id = msDB.getChannelIDFromTypeName('1656','web','网页组件')
    print id
    print msDB.getChannelUidFromId(id[0][0])

    mscdb = ManageSassChatDB()
    chatid = mscdb.getChatKeyFromStatusAndProviderID('id', 'new', 1160)
    mscdb.close()
    print chatid