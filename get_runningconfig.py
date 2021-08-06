# ############################################     PARAMETERS    #######################################################
# Fill in variables below. Usernames, passwords, and enable passwords. Script supports different usernames and passwords
# across devices. For telnet, it is able to detect whether Username has been set, or password only.
# Use text file switches.txt and paste in ip addresses of the devices. One per line.
# Alternatively, comment out lines 12-14 and use line 15 instead, if number of devices is relatively small.
# By default, only cisco platform is supported.
# ######################################################################################################################
user = ['cisco', 'admin']
password = ['cisco', 'password']
enable_password = ['password', 'cisco']
# ######################################################################################################################
switchhosts = 'switches.txt'
with open(switchhosts) as f:
    switchhosts = f.read().splitlines()
# switchhosts = ['192.168.56.40', '192.168.56.23', '192.168.56.48']
# ######################################################################################################################
prompt_list = [b'Username: ', b'Password: ']
platform = 'cisco_ios'
errors = []
authentication_errors = []


def tellib_find_password(ls, usr, pasw, en_pasw, swh):
    import telnetlib
    import re
    tn = telnetlib.Telnet(swh)
    auth = tn.expect(ls)
    prompt_parser = re.compile(r'Username:|Password:')
    prompt_type = prompt_parser.search(auth[1].group(0).decode('ascii'))
    tn.close()
    if prompt_type[0] == 'Password:':
        for p in pasw:
            tn = telnetlib.Telnet(swh)
            tn.read_until(b"Password: ")
            tn.write(p.encode('ascii') + b"\n")
            try:
                response = tn.read_until(b">", timeout=1)
            except EOFError as e:
                print("Connection closed: %s" % e)
            if b">" in response:
                tn.write(b"enable\n")
                for ep in en_pasw:
                    tn.write(ep.encode('ascii') + b"\n")
                    try:
                        response = tn.read_until(b"#", timeout=1)
                    except EOFError as e:
                        print("Connection closed: %s" % e)
                    if b"#" in response:
                        return tn

    elif prompt_type[0] == 'Username:':
        for u in usr:
            for p in pasw:
                tn = telnetlib.Telnet(swh)
                tn.read_until(b"Username: ")
                tn.write(u.encode('ascii') + b"\n")
                tn.read_until(b"Password: ")
                tn.write(p.encode('ascii') + b"\n")
                try:
                    response = tn.read_until(b">", timeout=1)
                except EOFError as e:
                    print("Connection closed: %s" % e)
                if b">" in response:
                    tn.write(b"enable\n")
                    for ep in en_pasw:
                        tn.write(ep.encode('ascii') + b"\n")
                        try:
                            response = tn.read_until(b"#", timeout=1)
                        except EOFError as e:
                            print("Connection closed: %s" % e)
                        if b"#" in response:
                            return tn


def netmiko_show_run(usr, passw, en_passw, swh, plat):
    from netmiko import ConnectHandler
    from paramiko.ssh_exception import AuthenticationException
    print("SWITCHES IN THE HOSTS FILE: ")
    print(swh)
    for host in swh:
        print("ESTABLISHING SSH SESSION TO SWITCH: " + str(host))

        def inner_func():
            for u in usr:
                for p in passw:
                    for ep in en_passw:
                        try:
                            net_connect = ConnectHandler(device_type=plat,
                                                         ip=host, username=u,
                                                         password=p,
                                                         secret=ep,
                                                         )
                            net_connect.enable()
                            print("Authentication Success!" + " - " + host + ": " + u + "/" + p + "/" + ep)
                            output = net_connect.send_command("show run", delay_factor=6)
                            print(output)
                            readoutput = output
                            saveoutput = open(host + "_show_run.txt", "w")
                            saveoutput.write(readoutput)
                            saveoutput.write("\n")
                            return

                        except:
                            if AuthenticationException:
                                authentication_errors.append("Authentication Failure" + " - " + host + ": " + u + "/" +
                                                             p + "/" + ep)
                            else:
                                errors.append(host)

        inner_func()


def tellib_show_run(usr, passw, en_passw, swh):
    incr = 0
    for host in swh:
        try:
            tn = tellib_find_password(prompt_list, usr, passw, en_passw, host)
            tn.write(b"terminal length 0\n")
            print("============================================")
            print("PULLING SHOW RUN FROM HOST " + host)
            print("============================================")
            tn.write(b"show run" + b"\n")
            incr = incr + 1
            tn.write(b"terminal length 24\n")
            tn.write(b"exit\n")
            # print(tn.read_all().decode('ascii'))
            saveoutput = open(host + "_show_run.txt", "w")
            readoutput = tn.read_all().decode('ascii')
            saveoutput.write(readoutput)
            saveoutput.write("\n")
        except:
            errors.append(host)


# ############################################     PARAMETERS    #######################################################
netmiko_show_run(user, password, enable_password, switchhosts, platform)
# tellib_show_run(user, password, enable_password, switchhosts)
# ######################################################################################################################

for e in errors:
    print("##############################################")
    print("ERRORS WERE FOUND ON THIS HOST: " + e)
