# coding:utf-8
# author:chenliang
# write time:2017-10-23
from Lib.ParserConfigUnit import initYmlDir
from Lib.LogService import ROOT_DIR
import os

LOGIN_TABLE_NAME = 'login'


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


class ParserYamlConfig(Singleton):
    """
    解析yml配置文件
    """
    init_type = False
    ymal_dict = {}

    @classmethod
    def __init(cls):
        interface_dir = os.path.join(ROOT_DIR, 'Config\\Yaml_data')
        cls.ymal_dict = initYmlDir(interface_dir)
        cls.init_type = True

    @classmethod
    def get(cls, filename):
        if not cls.init_type:
            cls.__init()
        file_dict = cls.ymal_dict[filename]
        # for key,dictvalue in file_dict.items():
        #     for s_key,s_value in dictvalue.items():
        #         if s_key.lower() == 'doc':
        #             s_value = s_value.encode('GBK')
        #             dictvalue[s_key] = s_value
        return file_dict


class V0_Interface(object):
    """
    存放v0版本的相应接口，路径及参数
    """
    login = {
        'describtion': 'Web用户登录接口',
        'second_url': '/login',
        'params': {
            'email': None,
            'password': None,
            'remember_me': True,
            'captcha': None,
            'provider.id': None
        },
        'body': None,
        'retsult': {
            'status': 0
        }
    }

    api_login = {
        'describtion': '用户登录接口',
        'second_url': '/api/login',
        'params': None,
        'body': {
            'display': 'json',
            'email': None,
            'password': None,
            'app_id': '1',
            'engineer_login': 'true'
        },
        'retsult': {
            'status': 200
        }
    }

    api_token = {
        'describtion': '获取token接口',
        'second_url': '/api/token',
        'params': None,
        'body': {
            'app_secret': '123',
            'code': None
        },
        'retsult': {
            'status': 200
        }
    }

    api2_OpenHelpCenterApi_getCurrentUserInfo = {
        'describtion': '获取provider ID接口',
        'second_url': '/api2/OpenHelpCenterApi.getCurrentUserInfo',
        'params': {
            '_token': None,
            '_app_key': 'pc_helpcenter'
        },
        'body': None,
        'retsult': {
            'status': 200
        }
    }

    UpdateHelpCenter = {
        'describtion': '更新帮助中心所需服务商信息',
        'second_url': '/updateHelpCenter.json',
        'params': None,
        'body': None,
        'retsult': {
            'status': 200
        }
    }


class V1_Interface(object):
    '''
    存放v1版本的相应接口，路径及参数
    '''
    api_ticket_save = {
        'describtion': '客服界面创建工单',
        'second_url': '/api/v1/ticket/save.json',
        'params': {
            '_token': None,
            'provider_id': None
        },
        'body': {
            "ccs": [{
                "user": {"id": 55679, "name": "lklkdsfn"}
            }],
            "ticketComment": {
                "content": "这是iTestFrame自动化测试工单的描述",
                "attachments": []
            },
            "engineer": {"id": 5617},
            "serviceDesk": {
                "id": 2022,
                "name": "DEFAULT_SERVICE_DESK_NAME"
            },
            "ticketCustomFields": [],
            "requester": {
                "id": 55685,
                "name": "haoren"
            },
            "subject": "这是iTestFrame自动化测试工单",
            "status": "assigned",
            "via": {
                "channel": "console",
                "channelName": "客服界面 ",
                "source": "陈亮"
            }
        },
        'retsult': {
            'status': 200
        }
    }
	
	
    api_notify_logs = {
         'describtion': '消息列表v1版接口，app在用',
        'second_url': '/api/v1/users/24744/notify_logs.json',
        'params': {
            '_token': None,
            'provider_id': None
        },
         'retsult': {
            'status': 200
        }
    }


class V2_Interface(object):
    '''
    存放v2版本的相应接口，路径及参数
    '''

    OpenAutomationApi_save = {
        'describtion': '创建更新自动化会话/工单',
        'second_url': '/api2/OpenAutomationApi.save',
        'params': {
            '_token': None
        },
        'body': {
            "automation": {
                "type": "chat",
                "andConditions": [{
                    "orderKey": 1,
                    "attribute": "customerLastReply",
                    "compare": "$gt_hours",
                    "tally": "and",
                    "value": 50
                }],
                "orConditions": [],
                "operations": [{
                    "orderKey": 1,
                    "attribute": "chatComment",
                    "value": "{\"value\":\"快速答复！\"}"}],
                "name": "6.2.1会话自动化2"
            }
        }
    }

    OpenTicketExportApi_ticketExportById = {
        'describtion':'导出PDF格式工单详情',
        'second_url':'/api2/OpenTicketExportApi.ticketExportById',
         'params': {
            '_token': None
        },
        'body_PDF':{
            "ticketId":416475,"exportType":"TYPE_PDF"
        },
         'body_DOC':{
            "ticketId":416475,"exportType":"TYPE_DOC"
        }

    }


    OpenTicketExportApi_ticketExportClean = {
        'describtion': '删除导出附件',
        'second_url': '/api2/OpenTicketExportApi.ticketExportClean',
        'params': {
            '_token': None
        },
        'body':{
            "days":7
        }
    }

    OpenNotifyLogApi_listAllByUserId = {
        'describtion': '通知消息列表',
        'second_url': '/api2/OpenNotifyLogApi.listAllByUserId',
        'params': {
            '_token': None
        },
        'body':{"page":{"pageNumber":1,"pageSize":10},"userId":43352}
    }
    OpenTicketExportApi_ticketExportClean = {
        'describtion': '删除导出附件',
        'second_url': '/api2/OpenTicketExportApi.ticketExportClean',
        'params': {
            '_token': None
        },
        'body':{
            "days":7
        }
    }
	
if __name__ == '__main__':
    print ParserYamlConfig.get('app')['getEngineerPermissions']

