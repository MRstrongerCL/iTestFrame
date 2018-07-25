# coding:utf-8
# author:chenliang
# write time:2017-10-23

import json
import requests
from InterfaceConfig import *
from Lib.MyConfig import url_independent
from Lib.MyConfig import url_saas
from Lib.LogService import logger
from Lib.PublicMethods import Unicode_Encode_Utf8_Json

class InterfaceSession():

    def __init__(self):
        self.ses = requests.session()
        self.headers = {}
        self.params = {}
        self.body = {}
        self.first_url_independent = url_independent
        self.first_url_saas = url_saas

    def setHeaders(self,headers):
        self.headers = headers

    def addHeaders(self,key,value):
        self.headers.setdefault(key,value)

    def changeHeaders(self,key,value):
        self.headers.update({key:value})

    def setParams(self,params):
        self.params = params

    def addParams(self,key,value):
        self.params.setdefault(key,value)

    def changeParams(self,key,value):
        self.params.update({key:value})

    def setBody(self,body):
        self.body = body

    def addBody(self,key,value):
        self.body.setdefault(key,value)

    def changeBody(self,key,value):
        self.body.update({key:value})

     #用session登录，获得cookie
    def holdCookie(self,body,platfom='SAAS'):
        #判断是独立平台还是saas
        if platfom.upper() == 'SAAS':
           url = self.first_url_saas + '/login'
        else:
           url = self.first_url_independent + '/login'

        #请求接口
        try:
           print('登录地址是：：：：：：%s '% url)
           result = self.ses.post(url,body)
           print ('登录结果：：：：：：：%s' % result.content)
        except Exception as e:
           raise e
        self.result = result
        self.url = result.url



    def get(self,second_url,params=None,bodyType=None,platfom='SAAS'):
        #判断是独立平台、还是sass
        if platfom.upper() == 'SAAS':
            url = self.first_url_saas + second_url
        else:
            url = self.first_url_independent + second_url

        #判断有无params
        if  params is not None and self.params == {}:
            new_url = url + '?'
            for key, value in params.items():
                new_url = new_url + '%s=%s&' % (key, value)
            new_url.rstrip('&')
        elif params is None and self.params != {}:
            new_url = url + '?'
            for key,value in self.params.items():
                new_url = new_url + '%s=%s&' % (key,value)
            new_url.rstrip('&')
        elif params is None and self.params == {}:
            new_url = url
        else:
            raise Exception('Params Wrrong !')

        # 请求接口
        try:
            logger.debug(new_url)
            result = self.ses.get(new_url)
        except Exception as e:
            raise e

        self.result = result
        self.url = result.url
        try:
            result_json = result.json()
            return result_json
        except:
            return result.content
        else:
            return result


    def post(self,second_url,body=None,params=None,bodyType='form',platfom='SAAS',printtype=True):
        # 判断是独立平台、还是sass
        if platfom.upper() == 'SAAS':
            url = self.first_url_saas + second_url
        else:
            url = self.first_url_independent + second_url

        # 判断有无params
        if  params is not None:
            new_url = url + '?'
            for key, value in params.items():
                new_url = new_url + '%s=%s&' % (key, value)
            new_url = new_url.rstrip('&')
        elif params is None and self.params != {}:
            new_url = url + '?'
            for key,value in self.params.items():
                new_url = new_url + '%s=%s&' % (key,value)
            new_url = new_url.rstrip('&')
        elif params is None and self.params == {}:
            new_url = url
        else:
            raise Exception('Params Wrrong !')

        #请求接口
        try:
            result = {}
            if body is not None:
                if bodyType.lower() == 'json':
                    body = json.dumps(body)
                else:
                    body = body
                result = self.ses.post(new_url, body)
                if printtype:
                    logger.debug(new_url)
                    logger.debug('body:{}'.format(body))
            elif body is None and self.body != {}:
                if bodyType.lower() == 'json':
                    body = json.dumps(self.body)
                else:
                    body = self.body
                result = self.ses.post(new_url,body)
                if printtype:
                    logger.debug(new_url)
                    logger.debug('body:{}'.format(body))
            elif body is None and self.body == {}:
                result = self.ses.post(new_url,self.body)
                if printtype:
                    logger.debug(new_url)
                    logger.debug('body:{}'.format(self.body))
        except Exception as e:
            raise e
        self.result = result
        self.url = result.url
        try:
            result_json = result.json()
            return result_json
        except:
            return result.content
        else:
            return result

    def delete(self,second_url,body=None,params=None,bodyType='form',platfom='SAAS'):
        # 判断是独立平台、还是sass
        if platfom.upper() == 'SAAS':
            url = self.first_url_saas + second_url
        else:
            url = self.first_url_independent + second_url

        # 判断有无params
        if  params is not None:
            new_url = url + '?'
            for key, value in params.items():
                new_url = new_url + '%s=%s&' % (key, value)
            new_url = new_url.rstrip('&')
        elif params is None and self.params != {}:
            new_url = url + '?'
            for key,value in self.params.items():
                new_url = new_url + '%s=%s&' % (key,value)
            new_url = new_url.rstrip('&')
        elif params is None and self.params == {}:
            new_url = url
        else:
            raise Exception('Params Wrrong !')

        #请求接口
        try:
            result = {}
            if body is not None:
                if bodyType.lower() == 'json':
                    body = json.dumps(body)
                else:
                    body = body
                result = self.ses.delete(new_url, body)
            elif body is None and self.body != {}:
                if bodyType.lower() == 'json':
                    body = json.dumps(self.body)
                else:
                    body = self.body
                result = self.ses.delete(new_url,body)
            elif body is None and self.body == {}:
                result = self.ses.delete(new_url)
                logger.debug(new_url)
                logger.debug('body:' + str(body))
        except Exception as e:
            raise e
        self.result = result
        self.url = result.url
        try:
            result_json = result.json()
            return result_json
        except:
            return result.content
        else:
            return result

    def close(self):
        self.ses.close()

class InterfaceMethods():

    @classmethod
    def user_Login(cls,user,pwd):
        myses = InterfaceSession()
        # 登录
        interface_dict = V0_Interface.api_login
        logger.info(interface_dict['describtion'])
        myses.setBody(interface_dict['body'])
        myses.changeBody('email', user)
        myses.changeBody('password', pwd)
        result = myses.post(interface_dict['second_url'])
        # print result
        code = result['result']['code']
        # 获取token
        interface_dict = V0_Interface.api_token
        logger.info(interface_dict['describtion'])
        myses.setBody(interface_dict['body'])
        myses.changeBody('code', code)
        result = myses.post(interface_dict['second_url'])
        # print result
        token = result['result']['token']
        # 获取provider id
        interface_dict = V0_Interface.api2_OpenHelpCenterApi_getCurrentUserInfo
        logger.info(interface_dict['describtion'])
        myses.setParams(interface_dict['params'])
        myses.changeParams('_token', token)
        result = myses.post(interface_dict['second_url'])
        # print result
        providerid = result['result']['providerId']
        myses.close()
        return {'token':token,'provider_id':providerid}

if __name__=='__main__':
    from Lib.ParserConfigUnit import Parser_Config
    myses = InterfaceSession()
    interface_dict = V0_Interface.api_login
    print interface_dict['describtion']
    myses.setBody(interface_dict['body'])
    user = Parser_Config("TestBed_Beta.ini", "Saas", "user")
    pwd = Parser_Config("TestBed_Beta.ini", "Saas", "password")
    myses.changeBody('email',user)
    myses.changeBody('password',pwd)
    r = myses.post(interface_dict['second_url'])
    print r
    myses.close()


