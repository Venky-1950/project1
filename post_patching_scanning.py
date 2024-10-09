#!/usr/bin/env python3
############Authors###############
#Venkat Revanth 
##################################

import subprocess

Server_name=subprocess.getoutput("hostname")

OS_Version=subprocess.getoutput("rpm -qf --queryformat '%{VERSION}' /etc/os-release")
UPTIME=subprocess.getoutput("uptime | awk '{print $3 $4}' | cut -d ',' -f 1")
kernel=subprocess.getoutput("uname -r")
glibc_version=subprocess.getoutput("rpm -q glibc")
patch=subprocess.getoutput("zypper lu | egrep -i 'kernel|glibc' | wc -l")
print(Server_name,OS_Version,UPTIME,kernel,glibc_version,patch)
