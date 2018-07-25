# coding:utf-8
# author:chenliang
# write time:2018-04-12

from Lib.LogService import logger
from Lib.InterfaceFunc.InterfaceSession import InterfaceSession
from Lib.PublicMethods import assert_Bigthan
from Lib.PublicMethods import assert_Smallthan
from Lib.PublicMethods import assert_Equal
from Lib.PublicMethods import assert_Not_Equal
from Lib.PublicMethods import assert_isNone
from Lib.PublicMethods import assert_isnotNone
from InterfaceConfig import V0_Interface
from Lib.MyConfig import user_saas,pwd_saas
from exceptions import AssertionError
from websocket import create_connection
import json


class InterfacePublicMethods(object):

    '''
    接口公共方法，在具体的接口脚本中引用
    脚本中将定义params、body ：可选参数、必传可为空参数 的黎彬
    body_CanCompatibility_object_key  可以兼容不同类型的参数，例如整型传入字符型也可成功
    '''
    params_CanLost_object_key = []
    params_MustAndCanEmpty_object_key = []
    body_CanLost_object_key = []
    body_MustAndCanEmpty_object_key = []
    body_CanCompatibility_object_key = []
    ses = InterfaceSession()

    def assert_Equal(self,arg1,arg2, msg=None):
        status = assert_Equal(arg1,arg2, msg)
        if not status:
            raise AssertionError("Compare Equal Failed: %s != %s , %s" % (arg1,arg2,msg))

    def assert_Not_Equal(self,arg1,arg2, msg=None):
        status = assert_Not_Equal(arg1,arg2, msg)
        if not status:
            raise AssertionError("Compare not Equal Failed: %s == %s , %s" % (arg1,arg2,msg))

    def assert_isNone(self,arg1,msg=None):
        status = assert_isNone(arg1,msg)
        if not status:
            raise AssertionError("Compare is None Failed: %s is not None , %s" % (arg1,msg))

    def assert_isnotNone(self,arg1,arg2, msg=None):
        status = assert_isnotNone(arg1, msg)
        if not status:
            raise AssertionError("Compare is not None Failed: %s is None , %s" % (arg1,msg))

    def assert_Bigthan(self,arg1,arg2, msg=None):
        status = assert_Bigthan(arg1,arg2, msg)
        if not status:
            raise AssertionError("Compare Bigthan Failed: %s <= %s , %s" % (arg1,arg2,msg))

    def assert_Smallthan(self,arg1,arg2, msg=None):
        status = assert_Smallthan(arg1,arg2, msg)
        if not status:
            raise AssertionError("Compare Smallthan Failed: %s >= %s , %s" % (arg1,arg2,msg))

    def assert_Contain(self,arg1,arg2, msg=None):
        if arg2 not in arg1:
            raise AssertionError("Compare Smallthan Failed: %s >= %s , %s" % (arg1,arg2,msg))

    def engineerLogin(self,providerid,user_id):
        # 客服登录并建立长连接传到push上（主要保证会话发起能成功）
        logger.info('ws://push.itkeeping.com/cometd; providerid:%s, userid:%s' % (providerid,user_id))
        ws = create_connection('ws://push.itkeeping.com/cometd',timeout=600)
        msg = [{
            'user': {
                'id': user_id,
                'providerId': providerid,
                'platform': "web_console"
            },
            'advice': {
                'timeout': 60000,
                'interval': 0
            },
            'supportedConnectionTypes': ["websocket", "long-polling", "callback-polling"],
            'channel': "/meta/handshake",
            'id': "1",
            'minimumVersion': "1.0",
            'version': "1.0"
        }]
        ws.send(json.dumps(msg))
        # ws.send(msg)
        logger.info("Receiving...")
        result = ws.recv()
        logger.info(str(result))
        new_result = json.loads(result)
        self.assert_Equal(new_result[0]['successful'],True)
        session_id = new_result[0]['clientId']
        return session_id

    def returnTargetEmptyObject(self, targetObject):
        t_type = type(targetObject)
        if t_type == int or t_type == float or t_type == long:
            return None
        elif t_type == str or t_type == unicode:
            return ''
        elif t_type == bool:
            return None
        elif t_type == list:
            return []
        elif t_type == dict:
            return {}
        else:
            return None

    def returnTargetNullObject(self, targetObject):
        return None

    def returnTargetWrongType(self, targetObject):
        t_type = type(targetObject)
        if t_type == int or t_type == float or t_type == long:
            return str(targetObject)+"abc"
        elif t_type == str or t_type == unicode:
            try:
                new_object = int(targetObject)
            except:
                new_object = 999999999
            return new_object
        elif t_type == bool:
            return 0
        elif t_type == list:
            return {}
        elif t_type == dict:
            return []
        else:
            return ''

    def NormalTestInterface(self, second_url,body,params={},bodyType='form',platfom='SAAS',request_type='post',interface_Type='v1v2',login_body={}):
        logger.debug('*** 正常参数请求，请求成功 ***')
        if login_body != {}:
           self.ses.holdCookie(login_body)
        self.ses.setParams(params)
        self.ses.setBody(body)
        requstsFunc = getattr(self.ses, request_type)
        result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
        logger.debug(self.ses.result.text)
        self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
        if request_type == 'get':
            if interface_Type == 'v1v2':
                self.assert_Equal(result['status'], 0, self.ses.result.content)
            else:
                self.assert_Equal(result['success'],True,self.ses.result.content)
        else:
            if interface_Type == 'v1v2':
                self.assert_Equal(result['status'], 0, self.ses.result.content)
            else:
                self.assert_Equal(result['success'],True,self.ses.result.content)
        return result

    def NormalTestInterface_compatibilityObject(self, second_url,body,params={},bodyType='form',platfom='SAAS',request_type='post',interface_Type='v1v2'):
        logger.debug('*** 正常参数请求，请求成功 ***')
        if self.body_CanCompatibility_object_key !=[]:
            self.ses.setParams(params)
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key in self.body_CanCompatibility_object_key:
                value = body[key]
                new_value = str(value)
                new_body = body
                new_body[key] = new_value
                self.ses.setBody(new_body)
                requstsFunc = getattr(self.ses, request_type)
                result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                logger.debug('body:%s 为可兼容的数据类型' % key)
                logger.debug(self.ses.result.text)
                self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
                if request_type == 'get':
                    if interface_Type == 'v1v2':
                        self.assert_Equal(result['status'], 0, self.ses.result.content)
                    else:
                        self.assert_Equal(result['success'],True,self.ses.result.content)
                else:
                    if interface_Type == 'v1v2':
                        self.assert_Equal(result['status'], 0, self.ses.result.content)
                    else:
                        self.assert_Equal(result['success'],True,self.ses.result.content)
        return result

    def NormalTestInterface_lostObject(self, second_url,body,params={},bodyType='form',platfom='SAAS',request_type='post'):
        logger.debug('*** Body缺少可选参数，请求成功 ***')
        if self.body_CanLost_object_key != []:
            self.ses.setParams(params)
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key in self.body_CanLost_object_key:
                value = body[key]
                new_body = body
                new_body.pop(key)
                self.ses.setBody(new_body)
                requstsFunc = getattr(self.ses, request_type)
                result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                logger.debug('body:%s 缺少' % key)
                logger.debug(self.ses.result.text)
                new_body[key] = value
                try:
                    self.assert_Equal(self.ses.result.status_code, 200, '---> 缺少参数 %s 请求失败!\n' % key)
                    if request_type == 'get':
                        self.assert_Equal(result['status'], 0, '---> 缺少参数 %s 请求返回不正确!\n' % key)
                    else:
                        self.assert_Equal(result['status'], 0, '---> 缺少参数 %s 请求返回不正确!\n' % key)
                except Exception as e:
                    wrong_count += 1
                    wrong_key.append(key)
                    exceptions += str(e) + self.ses.result.text + '\n'
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.debug(second_url)
            logger.debug("可选参数为空，不进行部分可选参数不传的验证！")

    def NormalTestInterface_lostParamsObject(self, second_url,body,params,bodyType='form',platfom='SAAS',request_type='post',interface_Type='v1v2',login_body={}):
        logger.debug('*** Params缺少可选参数，请求成功 ***')
        if self.params_CanLost_object_key != []:
            if login_body != {}:
                self.ses.holdCookie(login_body)
            self.ses.setBody(body)
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key in self.params_CanLost_object_key:
                value = params[key]
                new_params = params
                new_params.pop(key)
                self.ses.setParams(new_params)
                requstsFunc = getattr(self.ses, request_type)
                result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                logger.debug('params:%s 缺少' % key)
                logger.debug(self.ses.result.text)
                new_params[key] = value
                try:
                    self.assert_Equal(self.ses.result.status_code, 200, '---> 缺少可选参数 %s 请求不应该失败!\n' % key)
                    if request_type == 'get':
                        if interface_Type == 'v1v2':
                            self.assert_Equal(result['status'], 0, '---> 缺少可选参数 %s 请求不应该失败!\n' % key)
                        else:
                            self.assert_Equal(result['success'], True,  '---> 缺少可选参数 %s 请求不应该失败!\n' % key)
                    else:
                        if interface_Type == 'v1v2':
                            self.assert_Equal(result['status'], 0,  '---> 缺少可选参数 %s 请求不应该失败!\n' % key)
                        else:
                            self.assert_Equal(result['success'], True,  '---> 缺少可选参数 %s 请求不应该失败!\n' % key)
                except Exception as e:
                    wrong_count += 1
                    wrong_key.append(key)
                    exceptions += str(e) + self.ses.result.text + '\n'
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.debug(second_url)
            logger.debug("可选参数为空，不进行部分可选参数不传的验证！")

    def NormalTestInterface_ReTry(self, second_url,body,params={},bodyType='form',platfom='SAAS',request_type='post',interface_Type='v1v2',login_body={}):
        logger.debug('*** 重复相同参数请求，请求成功 ***')
        if login_body != {}:
            self.ses.holdCookie(login_body)
        self.ses.setParams(params)
        self.ses.setBody(body)
        requstsFunc = getattr(self.ses, request_type)
        result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
        self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
        if request_type == 'get':
            if interface_Type == 'v1v2':
                self.assert_Equal(result['status'], 0, self.ses.result.content)
            else:
                self.assert_Equal(result['success'],True,self.ses.result.content)
        else:
            if interface_Type == 'v1v2':
                self.assert_Equal(result['status'], 0, self.ses.result.content)
            else:
                self.assert_Equal(result['success'],True,self.ses.result.content)
        logger.debug(self.ses.result.content)
        #重复请求
        result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
        self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
        if request_type == 'get':
            if interface_Type == 'v1v2':
                self.assert_Equal(result['status'], 0, self.ses.result.content)
            else:
                self.assert_Equal(result['success'],True,self.ses.result.content)
        else:
            if interface_Type == 'v1v2':
                self.assert_Equal(result['status'], 0, self.ses.result.content)
            else:
                self.assert_Equal(result['success'],True,self.ses.result.content)

        logger.debug(self.ses.result.content)
        return result

    def AbNormalTestInterface(self, second_url,body,params={},bodyType='form',platfom='SAAS',request_type='post'):
        logger.debug('*** 异常请求，请求失败 ***')
        self.ses.setParams(params)
        self.ses.setBody(body)
        requstsFunc = getattr(self.ses, request_type)
        result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
        logger.debug(self.ses.result.text)
        self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
        if request_type == 'get':
            self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
        else:
            self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
        return result

    def AbNormalTestInterface_ReTry(self, second_url,body,params={},bodyType='form',platfom='SAAS',request_type='post'):
        logger.debug('*** 所有参数完整且格式正确 ***')
        self.ses.setParams(params)
        self.ses.setBody(body)
        requstsFunc = getattr(self.ses, request_type)
        result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
        self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
        if request_type == 'get':
            self.assert_Equal(result['status'], 0, self.ses.result.content)
        else:
            self.assert_Equal(result['status'], 0, self.ses.result.content)
        logger.debug(self.ses.result.content)
        #重复请求
        result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
        self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
        if request_type == 'get':
            self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
        else:
            self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
        logger.debug(self.ses.result.content)
        return result

    def AbNormalTestInterface_ParamsIsNone(self, second_url,body,params={},bodyType='form',platfom='SAAS',request_type='post'):
        logger.debug('*** Params为{}，请求失败 ***')
        params.pop('_token')
        self.ses.setParams(params)
        self.ses.setBody(body)
        requstsFunc = getattr(self.ses, request_type)
        result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
        logger.debug(self.ses.result.text)
        self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
        if request_type == 'get':
            self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
        else:
            self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
        return result

    def AbNormalTestInterface_isEmptyObject(self, second_url,body,params={},bodyType='form',platfom='SAAS',liwai=[],request_type='post'):
        logger.debug('*** Body中参数分别为Empty，请求失败 ***')
        self.ses.setParams(params)
        if body != {} and body != None:
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key,value in body.items():
                if key not in self.body_CanLost_object_key and key not in liwai:
                    new_value = self.returnTargetEmptyObject(value)
                    new_body = body
                    new_body[key] = new_value
                    self.ses.setBody(new_body)
                    requstsFunc = getattr(self.ses, request_type)
                    result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                    logger.debug('body:%s 为Empty' % key)
                    logger.debug(self.ses.result.text)
                    new_body[key] = value
                    try:
                        self.assert_Equal(self.ses.result.status_code, 200, '---> 参数 %s 为Empty 请求失败!\n' % key)
                        if key in self.body_MustAndCanEmpty_object_key:
                            if request_type == 'get':
                                pass
                            else:
                                self.assert_Equal(result['status'], 0, '---> 参数 %s 可以为Empty 请求返回不正确!\n' % key)
                        else:
                            if request_type == 'get':
                                self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为Empty 请求返回不正确!\n' % key)
                                self.assert_isnotNone(result['result']['error_description'],
                                                     '---> 参数 %s 为Empty 请求返回不正确！\n' % key)
                            else:
                                self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为Empty 请求返回不正确!\n' % key)
                                self.assert_isnotNone(result['result']['error_description'], '---> 参数 %s 为Empty 请求返回不正确！\n' % key)
                    except Exception as e:
                        wrong_count += 1
                        wrong_key.append(key)
                        exceptions += str(e) + self.ses.result.text + '\n'
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.info('body 为空，无需再进行部分必传参数为空的验证！')

    def AbNormalTestInterface_isParamsEmptyObject(self, second_url,body,params,bodyType='form',platfom='SAAS',liwai=[],request_type='post',login_body={}):
        logger.debug('*** Params中参数分别为Empty，请求失败 ***')
        if login_body != {}:
            self.ses.holdCookie(login_body)
        self.ses.setBody(body)
        if params != {} and params != None:
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key,value in params.items():
                if key not in self.params_CanLost_object_key and key not in liwai:
                    new_value = self.returnTargetEmptyObject(value)
                    new_params = params
                    new_params[key] = new_value
                    self.ses.setParams(new_params)
                    requstsFunc = getattr(self.ses, request_type)
                    result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                    logger.debug('params:%s 为Empty' % key)
                    logger.debug(self.ses.result.text)
                    new_params[key] = value
                    try:
                        self.assert_Equal(self.ses.result.status_code, 200, '---> 参数 %s 为Empty 请求失败!\n' % key)
                        if key in self.params_MustAndCanEmpty_object_key:
                            if request_type == 'get':
                                self.assert_Equal(result['status'], 0, '---> 参数 %s 可以为Empty 请求返回不正确!\n' % key)
                            else:
                                self.assert_Equal(result['status'], 0, '---> 参数 %s 可以为Empty 请求返回不正确!\n' % key)
                        else:
                            if request_type == 'get':
                                self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为Empty 请求返回不正确!\n' % key)
                                self.assert_isnotNone(result['result']['error_description'],
                                                     '---> 参数 %s 为Empty 请求返回不正确！\n' % key)
                            else:
                                self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为Empty 请求返回不正确!\n' % key)
                                self.assert_isnotNone(result['result']['error_description'], '---> 参数 %s 为Empty 请求返回不正确！\n' % key)
                    except Exception as e:
                        wrong_count += 1
                        wrong_key.append(key)
                        exceptions += str(e) + self.ses.result.text + '\n'
                else:
                    logger.info('params: %s 可以空，无需再进行部分必传参数为空的验证！' % key)
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.info('params 为空，无需再进行部分必传参数为空的验证！')

    def AbNormalTestInterface_isParamsEmptyObject_500(self, second_url,body,params,bodyType='form',platfom='SAAS',liwai=[],request_type='post',login_body={}):
        logger.debug('*** Params中参数分别为Empty，请求失败 ***')
        if login_body != {}:
            self.ses.holdCookie(login_body)
        self.ses.setBody(body)
        if params != {} and params != None:
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key,value in params.items():
                if key not in self.params_CanLost_object_key and key not in liwai:
                    new_value = self.returnTargetEmptyObject(value)
                    new_params = params
                    new_params[key] = new_value
                    self.ses.setParams(new_params)
                    requstsFunc = getattr(self.ses, request_type)
                    result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                    logger.debug('params:%s 为Empty' % key)
                    logger.debug(self.ses.result.text)
                    new_params[key] = value
                    try:

                        if key in self.params_MustAndCanEmpty_object_key:
                            self.assert_Equal(self.ses.result.status_code, 200, '---> 参数 %s 为Empty 不应该请求失败!\n' % key)
                        else:
                            self.assert_Equal(self.ses.result.status_code, 500, '---> 参数 %s 为Empty 应该请求失败!\n' % key)
                    except Exception as e:
                        wrong_count += 1
                        wrong_key.append(key)
                        exceptions += str(e) + self.ses.result.text + '\n'
                else:
                    logger.info('params: %s 可以空，无需再进行部分必传参数为空的验证！' % key)
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.info('params 为空，无需再进行部分必传参数为空的验证！')

    def AbNormalTestInterface_isNullObject(self, second_url,body,params={},bodyType='form',platfom='SAAS',liwai=[],request_type='post'):
        logger.debug('*** Body中参数分别为Null，请求失败 ***')
        self.ses.setParams(params)
        if body != {} and body != None:
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key,value in body.items():
                if key not in self.body_CanLost_object_key and key not in liwai:
                    new_value = self.returnTargetNullObject(value)
                    new_body = body
                    new_body[key] = new_value
                    self.ses.setBody(new_body)
                    requstsFunc = getattr(self.ses, request_type)
                    result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                    logger.debug('body:%s 为null' % key)
                    logger.debug(self.ses.result.text)
                    new_body[key] = value
                    try:
                        self.assert_Equal(self.ses.result.status_code, 200, '---> 参数 %s 为null 请求失败!\n' % key)
                        if request_type == 'get':
                            self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为null 请求返回不正确!\n' % key)
                            self.assert_isnotNone(result['result']['error_description'],
                                                 '---> 参数 %s 为null 请求返回不正确！\n' % key)
                        else:
                            self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为null 请求返回不正确!\n' % key)
                            self.assert_isnotNone(result['result']['error_description'], '---> 参数 %s 为null 请求返回不正确！\n' % key)
                    except Exception as e:
                        wrong_count += 1
                        wrong_key.append(key)
                        exceptions += str(e) + self.ses.result.text + '\n'
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.info('body 为空，无需再进行部分必传参数为空的验证！')

    def AbNormalTestInterface_isParamsNullObject(self, second_url,body,params,bodyType='form',platfom='SAAS',liwai=[],request_type='post',interface_type='v1v2',login_body={}):
        logger.debug('*** Params中参数分别为Null，请求失败 ***')
        if login_body != {}:
           self.ses.holdCookie(login_body)
        self.ses.setBody(body)
        if params != {} and params != None:
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key,value in params.items():
                if key not in self.params_CanLost_object_key and key not in liwai:
                    new_value = self.returnTargetNullObject(value)
                    new_params = params
                    new_params[key] = new_value
                    self.ses.setParams(new_params)
                    requstsFunc = getattr(self.ses, request_type)
                    result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                    logger.debug('params:%s 为null' % key)
                    logger.debug(self.ses.result.text)
                    new_params[key] = value
                    try:
                        if interface_type == 'v1v2':
                            self.assert_Equal(self.ses.result.status_code, 200, '---> 参数 %s 为null 请求失败!\n' % key)
                        else:
                            self.assert_Equal(self.ses.result.status_code, 500, '---> 非v1v2接口，参数 %s 为null 返回错误！\n' % key)
                        if interface_type == 'v1v2':
                            if request_type == 'get':
                                self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为null 请求返回不正确!\n' % key)
                                self.assert_isnotNone(result['result']['error_description'],
                                                 '---> 参数 %s 为null 请求返回不正确！\n' % key)
                            else:
                                self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为null 请求返回不正确!\n' % key)
                                self.assert_isnotNone(result['result']['error_description'], '---> 参数 %s 为null 请求返回不正确！\n' % key)
                    except Exception as e:
                        wrong_count += 1
                        wrong_key.append(key)
                        exceptions += str(e) + self.ses.result.text + '\n'
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.info('body 为空，无需再进行部分必传参数为空的验证！')

    def AbNormalTestInterface_isWrongType(self, second_url,body,params={},bodyType='form',platfom='SAAS',liwai=[],request_type='post'):
        logger.debug('*** Body中参数分别为错误的数据类型，请求失败 ***')
        self.ses.setParams(params)
        if body != {} and body != None:
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key,value in body.items():
                if key not in self.body_CanLost_object_key and key not in liwai:
                    new_value = self.returnTargetWrongType(value)
                    new_body = body
                    new_body[key] = new_value
                    self.ses.setBody(new_body)
                    requstsFunc = getattr(self.ses, request_type)
                    result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                    logger.debug('body:%s 为错误的数据类型' % key)
                    logger.debug(self.ses.result.text)
                    new_body[key] = value
                    try:
                        self.assert_Equal(self.ses.result.status_code, 200, '---> 参数 %s 为错误的数据类型 请求失败!\n' % key)
                        if request_type == 'get':
                            self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为错误的数据类型 请求返回不正确!\n' % key)
                            self.assert_isnotNone(result['result']['error_description'],
                                                 '---> 参数 %s 为错误的数据类型 请求返回不正确！\n' % key)
                        else:
                            self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为错误的数据类型 请求返回不正确!\n' % key)
                            self.assert_isnotNone(result['result']['error_description'], '---> 参数 %s 为错误的数据类型 请求返回不正确！\n' % key)
                    except Exception as e:
                        wrong_count += 1
                        wrong_key.append(key)
                        exceptions += str(e) + self.ses.result.text + '\n'
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.info('body 为空，无需再进行部分参数类型不正确的验证！')

    def AbNormalTestInterface_isParamsWrongType(self, second_url,body,params={},bodyType='form',platfom='SAAS',liwai=[],request_type='post',interface_type='v1v2',login_body={}):
        logger.debug('*** Params中参数分别为错误的数据类型，请求失败 ***')
        if login_body != {}:
           self.ses.holdCookie(login_body)
        self.ses.setBody(body)
        if params != {} and params != None:
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key,value in params.items():
                if key not in self.params_CanLost_object_key and key not in liwai:
                    new_value = self.returnTargetWrongType(value)
                    new_params = params
                    new_params[key] = new_value
                    self.ses.setParams(new_params)
                    requstsFunc = getattr(self.ses, request_type)
                    result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                    logger.debug('params:%s 为错误的数据类型' % key)
                    logger.debug(self.ses.result.text)
                    new_params[key] = value
                    try:
                        if interface_type == 'v1v2':
                            self.assert_Equal(self.ses.result.status_code, 200, '---> 参数 %s 为null 请求失败!\n' % key)
                        else:
                            self.assert_Equal(self.ses.result.status_code, 500, '---> 非v1v2接口，参数 %s 为null 返回错误！\n' % key)
                        if interface_type == 'v1v2':
                            if request_type == 'get':
                                self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为null 请求返回不正确!\n' % key)
                                self.assert_isnotNone(result['result']['error_description'],
                                                 '---> 参数 %s 为null 请求返回不正确！\n' % key)
                            else:
                                self.assert_Not_Equal(result['status'], 0, '---> 参数 %s 为null 请求返回不正确!\n' % key)
                                self.assert_isnotNone(result['result']['error_description'], '---> 参数 %s 为null 请求返回不正确！\n' % key)
                    except Exception as e:
                        wrong_count += 1
                        wrong_key.append(key)
                        exceptions += str(e) + self.ses.result.text + '\n'
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.info('body 为空，无需再进行部分参数类型不正确的验证！')

    def AbNormalTestInterface_LostObject(self, second_url,body,params={},bodyType='form',platfom='SAAS',liwai=[],request_type='post'):
        logger.debug('*** Body中缺少必传参数，请求失败 ***')
        self.ses.setParams(params)
        if body != {} and body != None:
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key,value in body.items():
                if key not in self.body_CanLost_object_key and key not in liwai:
                    new_body = body
                    new_body.pop(key)
                    self.ses.setBody(new_body)
                    requstsFunc = getattr(self.ses, request_type)
                    result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                    logger.debug('body:%s 缺少' % key)
                    logger.debug(self.ses.result.text)
                    new_body[key] = value
                    try:
                        self.assert_Equal(self.ses.result.status_code, 200, '---> 缺少参数 %s 请求失败!\n' % key)
                        if request_type == 'get':
                            self.assert_Not_Equal(result['status'], 0, '---> 缺少参数 %s 请求返回不正确!\n' % key)
                        else:
                            self.assert_Not_Equal(result['status'], 0, '---> 缺少参数 %s 请求返回不正确!\n' % key)
                    except Exception as e:
                        wrong_count += 1
                        wrong_key.append(key)
                        exceptions += str(e) + self.ses.result.text + '\n'
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.info('body 为空，无需再进行不传部分必传的验证！')

    def AbNormalTestInterface_LostParamsObject(self, second_url,body,params={},bodyType='form',platfom='SAAS',liwai=[],request_type='post',login_body={}):
        logger.debug('*** Params中缺少必传参数，请求失败 ***')
        if login_body != {}:
           self.ses.holdCookie(login_body)
        self.ses.setBody(body)
        if params != {} and params != None:
            wrong_count = 0
            wrong_key = []
            exceptions = 'EXCEPTION List ... \n'
            for key,value in params.items():
                if key not in self.params_CanLost_object_key and key not in liwai:
                    new_params = params
                    new_params.pop(key)
                    self.ses.setParams(new_params)
                    requstsFunc = getattr(self.ses, request_type)
                    result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
                    logger.debug('params:%s 缺少' % key)
                    logger.debug(self.ses.result.text)
                    new_params[key] = value
                    try:
                        self.assert_Equal(self.ses.result.status_code, 200, '---> 缺少参数 %s 请求失败!\n' % key)
                        if request_type == 'get':
                            self.assert_Not_Equal(result['status'], 0, '---> 缺少参数 %s 请求返回不正确!\n' % key)
                        else:
                            self.assert_Not_Equal(result['status'], 0, '---> 缺少参数 %s 请求返回不正确!\n' % key)
                    except Exception as e:
                        wrong_count += 1
                        wrong_key.append(key)
                        exceptions += str(e) + self.ses.result.text + '\n'
            if wrong_count > 0:
                raise Exception(exceptions)
        else:
            logger.info('params 为空，无需再进行不传部分必传的验证！')

    def AbNormalTestInterface_LostAllObject(self, second_url,params={},body={},bodyType='form',platfom='SAAS',request_type='post'):
        logger.debug('*** Body缺少所有参数，请求失败 ***')
        self.ses.setBody({})
        if body != {} and body != None:
            self.ses.setParams(params)
            requstsFunc = getattr(self.ses, request_type)
            result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
            logger.debug(self.ses.result.text)
            self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
            if request_type == 'get':
                self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
            else:
                self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
            return result
        else:
            logger.info('body 本就为空，无需再进行不传所有参数的验证！')

    def AbNormalTestInterface_LostParamsAllObject(self, second_url,params={},body={},bodyType='form',platfom='SAAS',request_type='post'):
        logger.debug('*** Params缺少所有参数，请求失败 ***')
        self.ses.setParams({})
        if params != {} and params != None:
            self.ses.setBody(body)
            requstsFunc = getattr(self.ses, request_type)
            result = requstsFunc(second_url, bodyType=bodyType, platfom=platfom)
            logger.debug(self.ses.result.text)
            self.assert_Equal(self.ses.result.status_code, 200, self.ses.result.url)
            if request_type == 'get':
                self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
            else:
                self.assert_Not_Equal(result['status'], 0, self.ses.result.content)
            return result
        else:
            logger.info('body 本就为空，无需再进行不传所有参数的验证！')

    def __del__(self):
        self.ses.close()