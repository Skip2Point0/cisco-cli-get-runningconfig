# ############################################     PARAMETERS    #######################################################
# Fill in variables below. Usernames, passwords, and enable passwords.
# Use text file switches.txt and paste in ip addresses of the devices. One per line.
# Alternatively, comment out lines 11-13 and use line 14 instead, if number of devices is relatively small.
# By default, only cisco platform is supported.
# ######################################################################################################################
user = 'cisco'
password = 'password'
enable_password = 'password'
# ######################################################################################################################
switchhosts = 'switches.txt'
with open(switchhosts) as f:
    switchhosts = f.read().splitlines()
# switchhosts = ['192.168.56.21', '192.168.56.20', '192.168.56.40', '192.168.56.23']
# ######################################################################################################################
platform = 'cisco_ios'
errors = []


def netmiko_show_run(usr, passw, en_passw, swh, plat):
    from netmiko import ConnectHandler
    print("SWITCHES IN THE HOSTS FILE: ")
    print(swh)
    for host in swh:
        print("ESTABLISHING SSH SESSION TO SWITCH: " + str(host))
        try:
            net_connect = ConnectHandler(device_type=plat,
                                         ip=host, username=usr,
                                         password=passw,
                                         secret=en_passw,
                                         )
            net_connect.enable()
            output = net_connect.send_command("show run", delay_factor=6)
            print(output)
            readoutput = output
            saveoutput = open(host + "_show_run.txt", "w")
            saveoutput.write(readoutput)
            saveoutput.write("\n")
        except:
            errors.append(host)


def tellib_show_run(usr, passw, en_passw, swh):
    import telnetlib
    incr = 0
    for host in swh:
        try:
            tn = telnetlib.Telnet(host)
            tn.read_until(b"Username: ")
            tn.write(usr.encode('ascii') + b"\n")
            if password:
                tn.read_until(b"Password: ")
                tn.write(passw.encode('ascii') + b"\n")
                tn.write(b"enable\n")
                tn.write(en_passw.encode('ascii') + b"\n")
                tn.write(b"terminal length 0\n")
                print("PULLING SHOW RUN FROM HOST " + host)
                print("===============")
                print("===============")
                print("===============")
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


netmiko_show_run(user, password, enable_password, switchhosts, platform)
# tellib_show_run(user, password, enable_password, switchhosts)

for e in errors:
    print("##############################################")
    print("ERRORS WERE FOUND ON THIS HOST: " + e)
