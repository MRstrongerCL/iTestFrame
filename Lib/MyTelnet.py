# -*- coding:gbk -*-

def do_telnet(Host, username, password, commands, finish = 'Administrator>',time_out = None):
    import telnetlib
    import datetime
    import time
    '''
    TelnetԶ�̵�¼��Windows�ͻ�������Linux������
    ����ǰ���ǣ������ �ѿ���telnet����
    '''
    print "\n####################### Telnet START ######################"
    print "====> Target PC Info : %s %s %s" % (Host,username,password)

    # ����Telnet������
    tn = telnetlib.Telnet(Host, port=23, timeout=10)
    time.sleep(1)
    tn.write('\r\n')
    # tn.set_debuglevel(0)
    # tn.set_debuglevel(2)

    # �����¼�û���
    tn.read_until('login: ',timeout=10)
    tn.write(username + '\r\n')

    # �����¼����
    tn.read_until('password: ',timeout=10)
    tn.write(password + '\r\n')
    tn.read_until(finish)

    # ��¼��Ϻ�ִ������
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

    #ִ����Ϻ���ֹTelnet���ӣ�������exit�˳���
    tn.close() # tn.write('exit\n')
    print "######################## Telnet END #######################\n"

if __name__=='__main__':
     # ����ѡ��
    Host = '10.66.21.6' # Telnet������IP
    username = 'administrator'   # ��¼�û���
    password = '123'  # ��¼����
    finish = 'Administrator> '      # ������ʾ��
    commands = 'echo "test"'
    do_telnet(Host, username, password, commands)