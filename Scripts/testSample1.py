import time
import MyTestCase
from Lib.LogService import logger

TAG = ['MMoke','Qilo']

class testSample1(MyTestCase.MyTestCase):
    def setUp(self):
        print('\n================================================>')
        before = time.ctime()
        logger.info("testSample1 before time is : %s " % before)

    @logger.LogCsvDecorator
    def test_Sample_1(self):
        self.logCaseID( MyTestCase.get_current_function_name())
        # self.url_apr = 'http://10.40.10.154:8091/apr/login'
        # self.user = '12200056'
        # self.password = 'cl123456'
        # ses = MyTestCase.requests.session()
        # # ses.
        # dict_data = {}
        # r = ses.post(self.url_apr,dict_data)
        # logger.info(r.url + " : %s" % r.status_code)
        # ss = r.content
        # print r.text
        # ses.close()
        mid = time.ctime()
        logger.info("testSample1 mid time is : %s " % mid)
        time.sleep(1)

    def tearDown(self):
        after = time.ctime()
        logger.info("testSample1 after time is : %s " % after)

if __name__=='__main__':
    MyTestCase.main()
