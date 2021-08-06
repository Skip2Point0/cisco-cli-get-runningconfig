# cisco-cli-get-runningconfig

Summary:

With this script you will be able to quickly download running configurations from Cisco equipment (routers/switches or 
other devices that support "show run" command). This was tested primarily in virtual Cisco environment and might have 
different effect on specific physical Cisco models. 

Requirements:

1) Interpreter: Python 3.8.0+
2) Python Packages: telnetlib, netmiko, paramiko, re

How to run:

1) Open get_runningconfig.py file with a text editor of your choice. Replace example configurations in the PARAMETERS
   section. Lines 7-9. By default, ip addresses must be added to switches.txt file, one per line in the same directory 
   with the script. Fo small number of devices, comment out lines 11-13 and uncomment line 14. 
   

2) By default, script will use SSH to establish connection. Telnet is supported.
    1) To disable SSH, comment out Line 135.
    2) To enable Telnet, uncomment Line 136.
   

3) Run python3 get_runningconfig.py in the terminal. If connection has been successful, <ip_address>_show_run.txt files
will appear in the same directory from which this script was ran.