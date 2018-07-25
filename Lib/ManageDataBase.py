# -*- coding: UTF-8 -*-
# author: chenliang
# create Time: 20161109

import os
import MySQLdb
import sqlite3
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB


# class ManageMysqlBase(object):
#     '''
#     Use for Manage Mysql DataBase
#     但如果多线程调用是，容易出现内存溢出、pyhton中断等问题
#     '''
#
#     def __init__(self,ip,user='pcl',pwd='11l11IllIllI11I11I',db_name='kxservicewechat',db_port=3306):
#         print "connect: %s:%s/%s %s/%s" % (ip,db_port,db_name,user,pwd)
#         self.conn= MySQLdb.connect(
#             host = ip,
#             port = int(db_port),
#             user = user,
#             passwd = pwd,
#             charset = 'gbk'
#         )
#         self.db = db_name
#         self.Select_DataBase(self.db)
#
#     def excute_sql(self,sql_str):
#         self.cur = self.conn.cursor()
#         # try:
#         #     sql_str = sql_str.decode('utf-8').encode('gbk')
#         # except:
#         #     sql_str = sql_str
#         result = self.cur.execute(sql_str)
#         return result
#
#     def Create_data_base(self,db_name):
#         self.db = db_name
#         sql_str = 'Create Database if not exists %s' % self.db
#         self.excute_sql(sql_str)
#         self.conn.select_db('%s' % self.db)
#         self.conn.commit()
#
#     def Select_DataBase(self,db_name):
#         self.conn.select_db('%s' % db_name)
#
#     def Create_table(self,table_name,title_dict):
#         sql_str1 = 'CREATE  TABLE if not exists %s ' % (table_name)
#         sql_str2 = ''
#         title_num = 500
#         for title in title_dict:
#             s_str = '%s %s(%d),' % (title,title_dict[title],title_num)
#             sql_str2 += s_str
#         sql_str2 = sql_str2.rstrip(',')
#         sql_str = sql_str1 + '(' + sql_str2 + ')'
#         self.excute_sql(sql_str)
#         self.conn.commit()
#
#     def Delele_data_base(self,db_name):
#         sql_str = 'drop database %s' % db_name
#         self.excute_sql(sql_str)
#         self.conn.commit()
#
#     def Delele_table(self,table_name):
#         sql_str = 'Drop table %s' % table_name
#         self.excute_sql(sql_str)
#         self.conn.commit()
#
#     def Delete_One_Data(self,table_name,Dete_title,condition_dict):
#         sql_str1 = 'DELETE {} From {} '.format(Dete_title,table_name)
#         options = ''
#         conditions = ''
#         for conditon in condition_dict:
#             conditions += '{}="{}"'.format(conditon, condition_dict[conditon]) + ' and '
#         sql_str = sql_str1 + ' WHERE ' + conditions.rstrip(' and ')
#         print "----> Delete CMD: %s ..." % sql_str
#         self.excute_sql(sql_str)
#         self.conn.commit()
#
#     def Delete_OneRow_Data(self,table_name,condition_dict):
#         sql_str1 = 'DELETE From {} '.format(table_name)
#         options = ''
#         conditions = ''
#         for conditon in condition_dict:
#             conditions += '{}="{}"'.format(conditon, condition_dict[conditon]) + ' and '
#         sql_str = sql_str1 + ' WHERE ' + conditions.rstrip(' and ')
#         print "----> Delete CMD: %s ..." % sql_str
#         self.excute_sql(sql_str)
#         self.conn.commit()
#
#     def Select_Mysql_Sql(self,sql_str):
#         print "----> Select CMD: %s ..." % sql_str
#         excute_result = self.excute_sql(sql_str)
#         result = self.cur.fetchmany(excute_result)
#         re_list = []
#         for one in result:
#             re_list.append(one)
#         self.conn.commit()
#         return re_list
#
#     def Insert_Mysql_Sql(self,table_name,insert_dict):
#         sql_str1 = 'INSERT INTO %s ' % table_name
#         options = ''
#         values = ''
#         for option in insert_dict:
#             options += str(option) + ','
#             values += '"' + str(insert_dict[option]) + '"'  + ','
#         options = '(' + options.rstrip(',') + ')'
#         values =  '(' + values.rstrip(',') + ')'
#         sql_str = sql_str1 + options + ' VALUES ' + values
#         print "----> Insert CMD: %s ..." % sql_str
#         self.excute_sql(sql_str)
#         self.conn.commit()
#
#     def Update_Mysql_Sql(self,table_name,insert_dict,condition_dict):
#         sql_str1 = 'UPDATE %s Set ' % table_name
#         options = ''
#         conditions = ''
#         for option in insert_dict:
#             options += str(option) + '=' + '"' + str(insert_dict[option]) + '"' + ','
#         for conditon in condition_dict:
#             conditions +=  '{}="{}"'.format(conditon,condition_dict[conditon]) + ' and '
#         sql_str = sql_str1 + options.rstrip(',') + ' WHERE ' + conditions.rstrip(' and ')
#         print "----> Update CMD: %s ..." % sql_str
#         self.excute_sql(sql_str)
#         self.conn.commit()
#
#     def Close(self):
#         self.conn.close()

class ManageSqlite(object):
    '''python 自带轻量级快速数据库，此处默认存放在内存中，也可以指定.db文件'''

    createtable_str = '''CREATE TABLE 'sqlTempData' (
                          'id' int(11) NOT NULL,
                          'name' varchar(20) NOT NULL,
                          'gender' varchar(4) DEFAULT NULL,
                          'age' int(11) DEFAULT NULL,
                          'address' varchar(200) DEFAULT NULL,
                          'phone' varchar(20) DEFAULT NULL,
                           PRIMARY KEY ('id')
                        )'''

    def __init__(self,dbname=':memory:'):
        self.db_name = dbname
        self.table_name = 'sqlTempData'
        self.conn = sqlite3.connect(self.db_name)

    def execute_sql(self,sql):
        co = self.conn.cursor()
        try:
            co.execute(sql)
            self.conn.commit()
        except Exception as e:
            raise e
        co.close()

    def CreateTable(self,sqlstr=createtable_str):
        self.execute_sql(sqlstr)

    def DropTable(self,tablename):
        sql_str = 'DROP TABLE IF EXISTS ' + tablename
        self.execute_sql(sql_str)

    def Delete_Sql(self,table_name,condition_dict):
        sql_str1 = 'DELETE From {} '.format(table_name)
        options = ''
        conditions = ''
        for conditon in condition_dict:
            conditions += "{}='{}'".format(conditon, condition_dict[conditon]) + ' and '
        sql_str = sql_str1 + ' WHERE ' + conditions.rstrip(' and ')
        print "----> Delete CMD: %s ..." % sql_str
        self.execute_sql(sql_str)

    def Select_Sql(self,select_sql):
        print "----> Select CMD: %s ..." % select_sql
        co = self.conn.cursor()
        co.execute(select_sql)
        result_list = co.fetchall()
        co.close()
        return result_list

    def Insert_Sql(self,table_name,insert_dict):
        sql_str1 = 'INSERT INTO %s ' % table_name
        options = ''
        values = ''
        for option in insert_dict:
            options += str(option) + ','
            values +="'" + str(insert_dict[option]) + "'"  + ","
        options = '(' + options.rstrip(',') + ')'
        values =  '(' + values.rstrip(',') + ')'
        sql_str = sql_str1 + options + ' VALUES ' + values
        print "----> Insert CMD: %s ..." % sql_str
        co = self.conn.cursor()
        co.execute(sql_str)
        self.conn.commit()
        co.close()

    def Update_Sql(self,table_name,update_dict,condition_dict):
        sql_str1 = 'UPDATE %s Set ' % table_name
        options = ''
        conditions = ''
        for option in update_dict:
            options += str(option) + "=" + "'" + str(update_dict[option]) + "'" + ","
        for conditon in condition_dict:
            conditions +=  "{}='{}'".format(conditon,condition_dict[conditon]) + " and "
        sql_str = sql_str1 + options.rstrip(',') + ' WHERE ' + conditions.rstrip(' and ')
        print "----> Update CMD: %s ..." % sql_str
        co = self.conn.cursor()
        co.execute(sql_str)
        self.conn.commit()
        co.close()

    def Close(self):
        self.conn.close()

class ManageMysqlBase(object):
    '''
    可以满足多线程调用
    '''
    # 连接池对象 先创建了最大40个连接 
    __pool = None

    def __init__(self,ip,user='pcl',pwd='11l11IllIllI11I11I',db_name='kxservicewechat',db_port=3306):
        print "connect: %s:%s/%s %s/%s" % (ip,db_port,db_name,user,pwd)
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        # self.conn = self.__getConn(ip,user,pwd,db_name,db_port)
        if self.__pool is None:
            self.__pool=PooledDB(creator=MySQLdb,mincached=1,maxcached=20,host=ip,port=int(db_port),user=user,passwd=pwd,db=db_name,use_unicode=False,charset='utf8') # 查询返回元祖
        #     # __pool=PooledDB(creator=MySQLdb,mincached=1,maxcached=20,host=ip,port=int(db_port),user=user,passwd=pwd,db=db_name,use_unicode=False,charset='gbk',cursorclass=DictCursor) # 查询返回字典

    def __getConn(self):
        """ 
        @summary: 静态方法，从连接池中取出连接 
        @return MySQLdbconnection 
        """
        # if ManageMysqlBase.__pool is None:
        #     __pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=40, host=ip, port=int(db_port),
        #                                       user=user, passwd=pwd, db=db_name, use_unicode=False,
        #                                       charset='gbk')  # 查询返回元祖
            # __pool=PooledDB(creator=MySQLdb,mincached=1,maxcached=20,host=ip,port=int(db_port),user=user,passwd=pwd,db=db_name,use_unicode=False,charset='gbk',cursorclass=DictCursor) # 查询返回字典
        return self.__pool.connection()

    def begin(self,conn):
        """
        @summary: 开启事务
        """
        conn.autocommit(0)

    def end(self, conn, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            conn.commit()
        else:
            conn.rollback()

    def dispose(self, conn, cur=None, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end(conn, 'commit')
        else:
            self.end(conn, 'rollback')
        if cur is not None:
            cur.close()
        conn.close()

    def excute_sql(self,sql_str):
        conn = self.__getConn()
        cur = conn.cursor()
        result = cur.execute(sql_str)
        conn.commit()
        self.dispose(conn, cur)
        return result

    def Create_data_base(self,db_name):
        self.db = db_name
        sql_str = 'Create Database if not exists %s' % self.db
        conn = self.__getConn()
        cur = conn.cursor()
        result = cur.execute(sql_str)
        conn.select_db('%s' % self.db)
        conn.commit()
        self.dispose(conn,cur)

    def Select_DataBase(self,db_name):
        conn = self.__getConn()
        conn.select_db('%s' % db_name)
        conn.commit()
        self.dispose(conn)

    def Create_table(self,table_name,title_dict):
        sql_str1 = 'CREATE  TABLE if not exists %s ' % (table_name)
        sql_str2 = ''
        title_num = 500
        for title in title_dict:
            s_str = '%s %s(%d),' % (title,title_dict[title],title_num)
            sql_str2 += s_str
        sql_str2 = sql_str2.rstrip(',')
        sql_str = sql_str1 + '(' + sql_str2 + ')'
        conn = self.__getConn()
        cur = conn.cursor()
        result = cur.execute(sql_str)
        conn.commit()
        self.dispose(conn, cur)

    def Delele_data_base(self,db_name):
        sql_str = 'drop database %s' % db_name
        conn = self.__getConn()
        cur = conn.cursor()
        result = cur.execute(sql_str)
        conn.commit()
        self.dispose(conn, cur)

    def Delele_table(self,table_name):
        sql_str = 'Drop table %s' % table_name
        conn = self.__getConn()
        cur = conn.cursor()
        result = cur.execute(sql_str)
        conn.commit()
        self.dispose(conn, cur)

    def Delete_One_Data(self,table_name,Dete_title,condition_dict):
        sql_str1 = 'DELETE {} From {} '.format(Dete_title,table_name)
        options = ''
        conditions = ''
        for conditon in condition_dict:
            conditions += '{}="{}"'.format(conditon, condition_dict[conditon]) + ' and '
        sql_str = sql_str1 + ' WHERE ' + conditions.rstrip(' and ')
        print "----> Delete CMD: %s ..." % sql_str
        conn = self.__getConn()
        cur = conn.cursor()
        result = cur.execute(sql_str)
        conn.commit()
        self.dispose(conn, cur)

    def Delete_OneRow_Data(self,table_name,condition_dict):
        sql_str1 = 'DELETE From {} '.format(table_name)
        options = ''
        conditions = ''
        for conditon in condition_dict:
            conditions += '{}="{}"'.format(conditon, condition_dict[conditon]) + ' and '
        sql_str = sql_str1 + ' WHERE ' + conditions.rstrip(' and ')
        print "----> Delete CMD: %s ..." % sql_str
        conn = self.__getConn()
        cur = conn.cursor()
        result = cur.execute(sql_str)
        conn.commit()
        self.dispose(conn, cur)

    def Select_Mysql_Sql(self,sql_str):
        print "----> Select CMD: %s ..." % sql_str
        conn = self.__getConn()
        cur = conn.cursor()
        excute_result = cur.execute(sql_str)
        result = cur.fetchmany(excute_result)
        re_list = []
        for one in result:
            re_list.append(one)
        conn.commit()
        self.dispose(conn, cur)
        return re_list

    def Insert_Mysql_Sql(self,table_name,insert_dict):
        sql_str1 = 'INSERT INTO %s ' % table_name
        options = ''
        values = ''
        for option in insert_dict:
            options += str(option) + ','
            values += '"' + str(insert_dict[option]) + '"'  + ','
        options = '(' + options.rstrip(',') + ')'
        values =  '(' + values.rstrip(',') + ')'
        sql_str = sql_str1 + options + ' VALUES ' + values
        print "----> Insert CMD: %s ..." % sql_str
        conn = self.__getConn()
        cur = conn.cursor()
        result = cur.execute(sql_str)
        conn.commit()
        self.dispose(conn, cur)

    def Update_Mysql_Sql(self,table_name,insert_dict,condition_dict):
        sql_str1 = 'UPDATE %s SET ' % table_name
        options = ''
        conditions = ''
        for option in insert_dict:
            options += str(option) + '=' + '"' + str(insert_dict[option]) + '"' + ','
        for conditon in condition_dict:
            conditions += '{}="{}"'.format(conditon, condition_dict[conditon]) + ' and '
        sql_str = sql_str1 + options.rstrip(',') + ' WHERE ' + conditions.rstrip(' and ')
        print "----> Update CMD: %s ..." % sql_str
        conn = self.__getConn()
        cur = conn.cursor()
        result = cur.execute(sql_str)
        conn.commit()
        self.dispose(conn, cur)

    def Close(self):
        # self.conn.close()
        pass

if __name__=='__main__':
    # ------------ Test Mysql -------------------
    # ip='127.0.0.1'
    # db_name='testcash'
    # edtion_mysql=ManageMysqlBase(ip)
    # # edtion_mysql.Delele_data_base(db_name)
    # # edtion_mysql.Create_data_base(db_name)
    # edtion_mysql.Select_DataBase(db_name)
    # # edtion_mysql.Delele_table('user')
    # # edtion_mysql.Create_table(['user','name','password','backup'])
    # # sql_dict = {'name':'"chenliang"','password':'"123456"','backup':'"888"'}
    # # edtion_mysql.Insert_Mysql_Sql('user',sql_dict)
    # sql_str = "Select order_price from t_cash"
    # print edtion_mysql.Select_Mysql_Sql(sql_str)
    # edtion_mysql.Close()

    # ---------------- Test Oracle -------------------
    # ip = '10.40.10.174'
    # oracle = ManageOracleBase(ip)
    # sql = "select cust_no From t_loan_base_info ww  where ww.aprov_result='013005' and ww.loan_no='51010201410130064'"
    # result = oracle.Select_Sql(sql)
    # print result
    # update_dict = {'LOGIN_IP':'10.1.4.224'}  #10.1.4.224
    # condition_dict = {'USER_ID':'01230004'}
    # oracle.Update_Sql('T_TEMP_LOGIN_INFO',update_dict,condition_dict)
    # insert_sql_dict = {'USER_ID':'0000001','LOGIN_IP':'10.1.4.255'}
    # oracle.Insert_Sql('T_TEMP_LOGIN_INFO',insert_sql_dict)
    # oracle.Close()
    sql = ManageSqlite()
    sql.CreateTable()
    insert_sql_dict = {'id': 1, 'name': '10.1.4.255','gender':'man','age':25,'address':'chengdu','phone':'15263524152'}
    sql.Insert_Sql('sqlTempData',insert_dict=insert_sql_dict)
    a = sql.Select_Sql('Select * From sqlTempData')
    sql.Close()
    print a


