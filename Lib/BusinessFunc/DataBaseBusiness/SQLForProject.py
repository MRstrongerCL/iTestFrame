# coding:utf-8
from Lib.ParserConfigUnit import Parser_Config
from Lib.ManageDataBase import ManageMysqlBase


class AllSQL:

    def __init__(self):
        pass

    @classmethod
    def sql(cls, sql, methed='select', table_name=None, insert_dict=None, condition_dict=None):
        TestBed_file = Parser_Config('TestEngineConfig.ini','TestParams','TestBedName')
        ip =  Parser_Config(TestBed_file,"Mysql", 'database_ip')
        db_name =  Parser_Config(TestBed_file,'Mysql', 'dbname_saas')
        user =  Parser_Config(TestBed_file,'Mysql', 'user_saas')
        passwd =  Parser_Config(TestBed_file,'Mysql', 'password_saas')
        MysqlConnect = ManageMysqlBase(ip=ip, db_name=db_name, user=user, pwd=passwd)
        if methed == 'select':
            data = MysqlConnect.Select_Mysql_Sql(sql)
            MysqlConnect.Close()
        elif methed == 'update':
            data = MysqlConnect.Update_Mysql_Sql(table_name, insert_dict, condition_dict)
            MysqlConnect.Close()
        return data

    @classmethod
    def data(cls, name=None, provider_id=1552):
        if name == 'ticketType':
            cls.ticketType = int(
                cls.sql("SELECT MAX(id) FROM ticket_type WHERE provider_id = %s" % provider_id)[0][0])
            return cls.ticketType
        elif name == 'ticketTypeName':
            cls.ticketTypeName = cls.sql("SELECT `name` FROM ticket_type WHERE id = %s" % cls.ticketType)[0][0]
            return cls.ticketTypeName
        elif name == 'catLogId':
            cls.catLogId = int(
                cls.sql("SELECT MAX(id) FROM service_catalog WHERE provider_id = %s" % provider_id)[0][0])
            return cls.catLogId
        elif name == 'user_id':
            cls.user_id = int(
                cls.sql('SELECT user_id FROM engineer WHERE provider_id = %s AND role_id = 1' % provider_id)[0][0])
            return cls.user_id
        elif name == 'engineer_id':
            cls.engineer_id = int(cls.sql("SELECT MAX(id) FROM engineer WHERE provider_id = %s" % provider_id)[0][0])
            return cls.engineer_id
        elif name == 'serviceDesk_id':
            cls.serviceDesk_id = int(cls.sql(
                "SELECT id FROM service_desk WHERE provider_id= {} AND `name` = '默认服务台'".format(
                    provider_id).decode('utf8'))[0][0])
            return cls.serviceDesk_id
        elif name == 'userGroupId':
            cls.userGroupId = int(cls.sql(
                "SELECT MAX(id) FROM user_group WHERE provider_id = %s" % provider_id
            )[0][0])
            return cls.userGroupId
        else:
            print "stdin not in list"
