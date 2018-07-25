# coding:utf-8
#!usr/bin/sh
# chenliang
# 20170907 18:41

import paramiko

# # 杀死打印日志进程
# ssh.exec_command("pid=`ps -ef |grep '/home/pcl/tomcat/kxweixinuser_tomcat/logs/catalina.out' | awk '{print $2}'|sed -n '1p'`;kill -9 $pid")
# ssh.exec_command("pid=`ps -ef |grep '/home/pcl/tomcat/kxweixinuser_tomcat/logs/catalina.out' | awk '{print $2}'|sed -n '1p'`|xargs kill -9 $pid")

# trans.close()

class RemoteOperationLinux(object):

    def __init__(self,ip,port):
        self.ip = str(ip)
        self.port = int(port)

    def connect(self,user,password,connectType='ssh'):
        self.user = user
        self.password = password
        self.transport = paramiko.Transport((self.ip,self.port))
        self.transport.connect(username=self.user, password=self.password)
        if connectType.lower()=='ssh':
            self.ssh_protocol()
        else:
            self.sftp_protocol()

    def ssh_protocol(self):
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = self.transport

    def sftp_protocol(self):
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def exe_cmd(self,cmd):
        if self.transport.is_alive():
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
        else:
            self.connect(self.user,self.password)
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
        kxwein_log = stdout.read().decode('utf8')
        return kxwein_log

    def get_ftp(self):
        return self.sftp

    def close(self):
        self.transport.close()

if __name__ == '__main__':
    r = RemoteOperationLinux('10.40.10.158', 52119)
    r.connect('chenliang','cl123')
    r_str = r.exe_cmd('pwd')
    print r_str
    r.exe_cmd('tail -f /home/pcl/tomcat/public-wechat-tomcat/logs/catalina.out > /home/chenliang/log.txt &')
    r.exe_cmd("ps -ef |grep '/home/pcl/tomcat/kxweixinuser_tomcat/logs/catalina.out' | awk '{print $2}'|sed -n '1p'|xargs kill -9 ")
    r.sftp_protocol()
    r.sftp.get('/home/chenliang/log.txt','log.txt')
    r.close()
    r_str = r.exe_cmd('df -l')
    print r_str
    r.close()
