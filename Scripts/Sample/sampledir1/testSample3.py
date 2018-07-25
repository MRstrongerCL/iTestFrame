import time
import MyTestCase
from Lib.LogService import logger
from Lib.BusinessFunc.webOperation import webOperation
from Lib.BusinessFunc.AprFunction import AprFunction
from Lib.ParserConfigUnit import Parser_Config

TAG = 'slave'

class testSample3(MyTestCase.MyTestCase):
    def setUp(self):
        print('\n================================================>')
        before = time.ctime()
        print("testSample3 before time is : %s " % before)
        # self.driver = webOperation('Chrome')
        # self.aprurl = Parser_Config("TestBed_BetaE.ini", "Apr", "url")
        # self.user = Parser_Config("TestBed_BetaE.ini", "Apr", "user")
        # self.password = Parser_Config("TestBed_BetaE.ini", "Apr", "password")

    @logger.LogCsvDecorator
    def test_Sample_3(self):
        # AprFunction.loginApr(self.driver,self.aprurl,self.user,self.password)
        # time.sleep(2)
        # AprFunction.Into_nav(self.driver)
        time.sleep(1)
        mid = time.ctime()
        print("testSample3 mid time is : %s " % mid)
        time.sleep(1)

    def tearDown(self):
        after = time.ctime()
        print("testSample3 after time is : %s " % after)

if __name__=="__main__":
    MyTestCase.main()