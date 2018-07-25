# -*- coding:gbk -*-

def do_telnet(Host, username, password, commands, finish = 'Administrator>',time_out = None):
    import telnetlib
    import datetime
    import time
    '''
    Telnet远程登录：Windows客户端连接Linux服务器
    运行前提是，服务端 已开启telnet服务
    '''
    print "\n####################### Telnet START ######################"
    print "====> Target PC Info : %s %s %s" % (Host,username,password)

    # 连接Telnet服务器
    tn = telnetlib.Telnet(Host, port=23, timeout=10)
    time.sleep(1)
    tn.write('\r\n')
    # tn.set_debuglevel(0)
    # tn.set_debuglevel(2)

    # 输入登录用户名
    tn.read_until('login: ',timeout=10)
    tn.write(username + '\r\n')

    # 输入登录密码
    tn.read_until('password: ',timeout=10)
    tn.write(password + '\r\n')
    tn.read_until(finish)

    # 登录完毕后执行命令
    for command in commands:
        start = datetime.datetime.now()
        print "----> Cmd: %s" % command
        tn.write('%s\r\n' % command)
        for i in range(20):
            if tn.read_until(finish,1):
                break
            elif tn.read_until('[N]:',1):
                tn.write('Y\r\n')
                tn.read_until(finish)
        if time_out != None:
            time.sleep(time_out)
        end = datetime.datetime.now()
        use = end - start
        print "----> Excute Cmd Use Time: %s " % use

    #执行完毕后，终止Telnet连接（或输入exit退出）
    tn.close() # tn.write('exit\n')
    print "######################## Telnet END #######################\n"

if __name__=='__main__':
     # 配置选项
    Host = '10.66.21.6' # Telnet服务器IP
    username = 'administrator'   # 登录用户名
    password = '123'  # 登录密码
    finish = 'Administrator> '      # 命令提示符
    commands = 'echo "test"'
    do_telnet(Host, username, password, commands)