# -*- coding:utf-8 -*-
# chanliang
# 20170320 16:35
import thread
import threading
import multiprocessing
import time


# ******************   多线程1 ：简单调用多线程 ***********************
class thread_1(object):

    def __init__(self):
        pass

    @staticmethod
    def music(funcName,loop):
        for i in range(loop):
            print('This music is %s th: %s,%s\n' % ((i+1),funcName,time.ctime()) )
            time.sleep(2)

    @staticmethod
    def movie(funcName,loop):
        for i in range(loop):
            print("This is movie %s th: %s,%s\n" % ((i+1),funcName,time.ctime()))
            time.sleep(3)

    @staticmethod
    def creatThreadList():
        thread_list = []
        t1 = threading.Thread(target=thread_1.music,args=("我只在乎你",2))
        thread_list.append(t1)
        t2 = threading.Thread(target=thread_1.movie,args=("金刚",2))
        thread_list.append(t2)
        return thread_list

    @staticmethod
    def threads_run(threadsList):
        print("start Time: %s" % time.ctime())
        # 启动线程
        for thr in threadsList:
            thr.start()
        # 守护线程 (即是 等待所有线程 结束后，再往下执行, start 和 join方法不能放在一个循环执行，不然就变成串行了，失去了多线程并发的目的)
        for thr in threadsList:
            thr.join()
        print("end Time: %s" % time.ctime())

    @staticmethod
    def test_thread_1():
        thr_list = thread_1.creatThreadList()
        thread_1.threads_run(thr_list)

# *************************** 多线程2：多进程并发 ************************
class thread_2(threading.Thread):

    def __init__(self):
        '''@summary: 初始化对象。

        @param lock: 琐对象。
        @param threadName: 线程名称。
        '''
        super(thread_2, self).__init__()  # 注意：一定要显式的调用父类的初始
        self.thread_list = []

    def __call__(self,func,args_tuple,counts):
        self.build_func_loop(func,args_tuple,counts)
        self.run()

    def Count(self,id,num):
        for i in xrange(num):
            print "Thread id is : %s  ,num is : %s ;    time: %s \n" % (id, i,time.ctime())
            time.sleep(1)

    def build_func_loop(self,func,func_args,counts):
        for i in xrange(int(counts)):
            thread_func = threading.Thread(target=func, args=func_args)
            self.thread_list.append(thread_func)
            thread_func.start()

    def add_func_to_thread_list(self,func,func_arg):
        thread_func = threading.Thread(target=func, args=func_arg)
        self.thread_list.append(thread_func)
        thread_func.start()

    def run(self):
        # for t in self.thread_list:
        #     t.start()
        for t in self.thread_list:
            t.join()

    def test_thread_2(self):
        num = 1
        t1 = threading.Thread(target=self.Count, args=('A',2))
        t2 = threading.Thread(target=self.Count, args=('B',3))
        self.thread_list.append(t1)
        self.thread_list.append(t2)
        for t in self.thread_list:
            t.start()
        for t in self.thread_list:
            t.join()


if __name__ == '__main__':
    # thread_1.test_thread_1()
    thr2 = thread_2()
    # thr2.test_thread_2()
    # thr2.build_func_loop(thread_1.movie,("hi , girl",2),4)
    # thr2.run()
    thr2(thread_1.movie, ("hi , girl", 2), 4)