# -*- coding: UTF-8 -*-
# chenliang 20170710

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from Lib.LogService import ROOT_DIR
from Lib.LogService import logger
from Lib.PublicMethods import Get_Now_TimeStr
from Lib.PublicMethods import random_strs

import re,time,os

# driver = webdriver.Chrome()
# driver.page_source()

class webOperation(object):
    def __init__(self,browername='Chrome',brower_path=None):
        self.url_apr = 'http://10.40.10.158:8091/apr/login'
        self.browername = browername
        if brower_path == None:
            self.driver = getattr(webdriver,browername)()
        else:
            self.driver = getattr(webdriver, browername)(brower_path)
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)
        self.driver.set_page_load_timeout(30)
        self.pic_dir = os.path.join(ROOT_DIR,'Log\pic_dir')
        return self

    def take_screenshot(self, save_fn="capture.png"):
        picpath = os.path.join(self.pic_dir, "{}_({}){}.png".format(Get_Now_TimeStr(), random_strs(6),save_fn))
        logger.info("log picture at; %s" % (picpath))
        self.save_screenshot(picpath)

    def WaitForElement(self,ByObj,locate,time=5,splittime=0.5):
        return WebDriverWait(self.driver, time, splittime).until(expected_conditions.presence_of_element_located((ByObj, locate)))

    def MouseOver(self,mouse_ele,type=None):
        if type==None:
            ActionChains(self.driver).move_to_element(mouse_ele).perform()
        else:
            id = mouse_ele.get_attribute('id')
            JavascriptStr = "$('#%s').trigger('mouseover')" % id
            self.driver.execute_script(JavascriptStr)

    def Select_Nav(self,nav_1,nav_2):
        # nav1_ele = self.WaitForElement(By.LINK_TEXT,nav_1)
        self.WaitForElement(By.TAG_NAME, 'iframe', 20)
        time.sleep(1)
        nav1_ele = self.WaitForElement(By.XPATH,"//*[text()='%s']" % nav_1)
        # mouse_ele = self.driver.find_element_by_class('pulldown app-url')
        self.MouseOver(nav1_ele)
        # self.MouseOver(mouse_ele,type='js')
        time.sleep(1)
        nav2_ele = self.WaitForElement(By.LINK_TEXT,nav_2).click()
        self.WaitForElement(By.LINK_TEXT, nav_2)

    def Select_Request_No(self,Request_No):
        # 进入iframe
        self.WaitForElement(By.TAG_NAME, 'iframe', 20)
        self.WaitForElement(By.ID, '贷款审批质检', 20)
        self.driver.switch_to.frame(self.driver.find_element_by_id('贷款审批质检'))
        self.driver.save_screenshot('E:\\WorkSpace\\自研小工具\\TestsTool\\ReviewAprInfo\\cap1.png')

        # 等待工单列表显示
        table_moudle_xpath = '//*[@id="gdApplygrid"]/div[4]/div[2]/div/table/tbody'
        self.WaitForElement(By.XPATH,table_moudle_xpath,30)

        # 查找并双击目标工单号
        requests = self.driver.find_elements_by_class_name('l-grid-row')
        for request in requests:
            new_request = request.find_element_by_class_name('l-grid-row-cell-inner')
            if new_request.text == Request_No:
                request_ele = new_request
                break
        # request_ele = self.driver.find_element_by_xpath("//*[text()='%s']" % Request_No)
        # request_ele = self.WaitForElement(By.LINK_TEXT, Request_No)   #此方法无法定位
        print("--------------> %s" % request_ele.text)
        ActionChains(self.driver).double_click(request_ele).perform()
        time.sleep(5)
        self.driver.save_screenshot('E:\\WorkSpace\\自研小工具\\TestsTool\\ReviewAprInfo\\cap1.png')

        # 等待审核iframe出现
        self.driver.switch_to.default_content()
        iframes = self.driver.find_elements_by_tag_name("iframe")
        for frame in iframes:
            print frame
            print frame.get_attribute('id')
        iframe_father = self.WaitForElement(By.CLASS_NAME,'l-dialog-content-nopadding',20)
        # iframe_father = self.WaitForElement(By.CLASS_NAME,'l-dialog-content-noimage')
        iframe = iframe_father.find_element_by_tag_name('iframe')
        self.driver.switch_to.frame(iframe)
        company_name = self.WaitForElement(By.ID,'companyName').text
        print company_name
        name = self.WaitForElement(By.XPATH,'//*[@id="identity"]/table/tbody/tr[1]/td[2]').text
        print name

        # 进入家庭电核岗
        iframe_father = self.WaitForElement(By.ID,'approve')
        self.driver.execute_script("arguments[0].scrollIntoView();", iframe_father)
        iframe3 = iframe_father.find_element_by_tag_name('iframe')
        print iframe3.get_attribute('src')
        self.driver.switch_to.frame(iframe3)

        home_ele = self.WaitForElement(By.XPATH,"//*[text()='家庭电核岗'")
        ActionChains(self.driver).double_click(home_ele).perform()
        time.sleep(2)
        self.driver.save_screenshot('E:\\WorkSpace\\自研小工具\\TestsTool\\ReviewAprInfo\\cap2.jpg')

        # 等待家庭审核iframe出现
        self.driver.switch_to.default_content()
        iframe_fathers = self.driver.find_elements_by_class_name('l-dialog-content-noimage')
        iframe_father2 = iframe_fathers[1]
        iframe = iframe_father2.find_element_by_tag_name('iframe')
        self.driver.switch_to.frame(iframe)
        img = self.driver.find_element_by_xpath('/html/body/div[2]/img')
        print img.get_attribute('src')


    def __close__(self):
        self.driver.close()
        os.system('taskkill /f /im phantomjs.exe')
        # os.system('taskkill /f /im %s.exe' % self.browername.lower())


if __name__=='__main__':
    # AR = AprReview('Chrome')
    AR = webOperation('PhantomJS','phantomjs.exe')
    AR.Select_Nav('业务处理','贷款审批质检')
    AR.Select_Request_No('23060201707130000')
    time.sleep(5)
    AR.__close__()