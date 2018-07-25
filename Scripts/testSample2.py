import time
import MyTestCase
from Lib.LogService import logger


TAG = 'smoke'

class testSample2(MyTestCase.MyTestCase):

    def setUp(self):
        print('\n================================================>')
        before = time.ctime()
        logger.info("testSample2 before time is : %s " % before)

    # @MyTestCase.LogCsvDecorator
    @logger.LogCsvDecorator
    def test_Sample_2(self):
        time.sleep(1)
        mid = time.ctime()
        self.assertEqual(4,5,"4,5 Not equal")
        logger.info("testSample2 mid time is : %s " % mid)
        time.sleep(1)

    def tearDown(self):
        after = time.ctime()
        logger.info("testSample2 after time is : %s " % after)


if __name__=='__main__':
    MyTestCase.main()