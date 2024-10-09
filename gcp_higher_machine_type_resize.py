#!/usr/bin/env python3

##Author Details##
#Name - Venkat Revanth#
##################

import subprocess
import sys
from termcolor import colored
from terminaltables import AsciiTable
import time
import re
import os
import logging
import logging.config

logging.basicConfig(filename='/test/higher_machinetype.log',level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

user_name=subprocess.getoutput("ldapsearch -x uid=$(whoami) | grep -i givenName | awk '{print$2}'")
user_id=subprocess.getoutput("whoami")
user_mail=subprocess.getoutput("ldapsearch -x uid=$(whoami) | grep -i mail | awk '{print $2}'")
logging.info("Script user {} {}".format(user_name,user_id))

##Mail Function##
def send_mail():
       #var_message = 'Success'
       global var_message
       global approval_details
       color = '#FF0000'
       to_list = f'{user_mail}'
       #cc_list = 'DL_'
       #cc_list = ''
       subject = "Higher Machine type resize"
       if ( rs == '0' or ps == '0' ):
           cc_list = 'DL_'
       else:
           cc_list = 'DL_'

       sendmail = subprocess.run(f'perl /home/adminhosts/mail/dlm_mail.pl --template /home/adminhosts/mail/dlm_template.html  --subject \'{subject}\' --var headline={ServerName}  --var \'Machine_type={reqd_machine_type}\' --var \'Approval Details= {approval_details}\' --var \'Resize_Status={resize_status}\' --var \'Status={var_message}\'  --from \'DLM_cloud_VM_Resize\' --to=\'{to_list}\' --cc=\"{cc_list}\"', shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


print(colored(f"Hello {user_name}", 'yellow'))
print()
#print("        Hope you are doing Good!!")
print(colored('       Hope you are doing Good!!', 'green'))
print()
#print("                          " "\033[4mWELCOME TO SP UPGRADATION\033[0m")
print(colored('                          ' '\033[4mWELCOME TO GCP Higher Machine Type resize\033[0m', 'red'))
print("")
user_check=subprocess.getoutput("id $(whoami) | grep -i 'sm_admin' | wc -l")
if int(user_check) == 0:

    print(f"You're not  SM Team Member")
    logging.info("User {} isn't part of SM_ADMIN".format(user_name))
    sys.exit()
else:
    print(f"You're the authorized person")
    print("")

#print(f"Log path - /test/higher_machinetype.log")
data_1=[['Log path','/test/higher_machinetype.log']]
table = AsciiTable(data_1)
print(table.table)

print("")
ServerName=str(input(colored("Enter the Server Name : ", 'magenta')))
logging.info("{} - Entered server name is {}".format(user_id,ServerName))
#To check SSH connection
def ssh_check():
    check_server_exist=subprocess.getoutput(['nc -zvw 10 ' f'{ServerName}' ' 22'])
    final_ssh_port_again_check = re.search("succeeded", check_server_exist)
    if final_ssh_port_again_check:
       print(colored("           Able to connect via SSH for host {}".format(ServerName),'cyan'))
       logging.info("{} is reachable.. Proceeding further".format(ServerName))
    else:
       print(colored(f"               **********{ServerName} is not REACHABLE/Please check manually***************",'blue', attrs=['bold']))
       logging.error("{} isn't reachable.. Script Exited".format(ServerName))
       sys.exit()
ssh_check()

#To check the platform of the server and to call respective snapshot creation function
'''Server_type=subprocess.run("sudo -iu rcuser ssh {} /usr/sbin/dmidecode -s system-manufacturer | cut -d ',' -f 1".format(ServerName),shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
check_Server_type=Server_type.stdout.strip()
if (check_Server_type == "Google"):
    print(f"Entered Server is GCP...... proceeding further...!")
else:
    print(f"Server isn't GCP... Please check once")
'''
#if ServerName[0:3] == "vlg" or hostname[0:3] == "vwg":
print("")
if ServerName[0:3] == "vlg":
    print(f"Entered Server is GCP Linux Server")
    logging.info("{} is a GCP Linux Server".format(ServerName))
else:
    print(f"Entered Server Name isn't GCP Linux")
    logging.error("{} isn't a GCP Linux Server... Script exited".format(ServerName))
    sys.exit()


#To check Server Zone#
print("")
print("Fetching server details... Please wait")
awk = "awk '{print $2}'"
cmd_server_check=subprocess.run("sudo gcloud compute instances list | grep -i {} | {}" .format(ServerName,awk), shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#cmd_server_check=subprocess.run("sudo gcloud compute instances list --filter='name~{}' --format='value(ZONE)'"  .format(ServerName), shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
zone=cmd_server_check.stdout.strip()
if cmd_server_check.returncode == 0:
    print(f"Server Exist in GCP")
    logging.info("{} exist in GCP".format(ServerName))
else:
    print(f"Server not exist in GCP")
    logging.error("{} not Exist in GCP".format(ServerName))
    sys.exit()

#To check current machine type of server##
table_fmt = "'table(machineType.basename())'"
cmd_server_check=subprocess.run("sudo gcloud compute instances describe {} --zone={} --format={}  | tail -1" .format(ServerName,zone,table_fmt), shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
machine_type=cmd_server_check.stdout.strip()
#print("Currently {} is in ZONE {} & Machine Type is {}".format(ServerName,zone,machine_type))

#To check node affinity label of a Server##
cmd_nodeaffinity=subprocess.run("sudo gcloud compute instances describe {}  --zone={} --format=flattened | grep -q 'nodeAffinities'" .format(ServerName,zone), shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if cmd_nodeaffinity.returncode == 0:
   fmt_cmd = "'csv(scheduling.nodeAffinities[0].values[0])'"
   cmd_nodeaffinity_name=subprocess.run("sudo gcloud compute instances describe {} --zone={} --format={} | tail -1" .format(ServerName,zone,fmt_cmd), shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   check_cmd_nodeaffinity_name=cmd_nodeaffinity_name.stdout.strip()
   print(f"Server is in Sole-tenant - {check_cmd_nodeaffinity_name} ... Please, perform resize manually")
   logging.info(f"Server is in Sole-tenant - {check_cmd_nodeaffinity_name} ... Please, perform resize manually")
   sys.exit()
   #print("Server is in {} Sole-tenancy" .format(check_cmd_nodeaffinity_name))
else:
   #print(f"Server isn't in sole-tenancy node")
   check_cmd_nodeaffinity_name = '---none---'
data=[['Server Name','Zone','Machine Type','Sole-tenancy'],[f'{ServerName}',f'{zone}',f'{machine_type}',f'{check_cmd_nodeaffinity_name}']]
table = AsciiTable(data)
print(table.table)
print("")
#print("     Server Name                  Zone                     Machine Type                              Sole-tenancy ")
#print(f"     {ServerName}                {zone}                {machine_type}                       {check_cmd_nodeaffinity_name}   ")
logging.info(f"{ServerName} {zone} {machine_type} sole-tenancy - {check_cmd_nodeaffinity_name}")

#Taking required machine type input#
reqd_machine_type=str(input(colored("Enter the required machine type : ", 'cyan'))).lower()
logging.info(f"Entered Machine type is {reqd_machine_type}")
if (reqd_machine_type == machine_type):
    print(f"Current machine type & Enter Machine type is same")
    logging.error(f"Current machine type {machine_type} & Enter Machine type {reqd_machine_type} is same...exited")
    sys.exit()
else:
    print(f"Current machine type & Entered Machine type isn't same. Hence, proceeding further...")


#Taking approval details from User##
print("")
approval_details=str(input(colored("Enter the approval mail sub or Ticket No. : ", 'yellow')))
if approval_details:
    logging.info(f"{user_id}Entered Approval Details  -  {approval_details}")
else:
    print(f"Approval details empty..")
    logging.error(f"Approval details empty.. exited")
    sys.exit()


##Checking entered machine type is exist or not in Zone#
check_machine_type=subprocess.run("sudo gcloud compute machine-types list --zones={} | grep -i '{}'" .format(zone,reqd_machine_type),shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if check_machine_type.returncode != 0:
    print(f"Entered machine type not exist in zone... Please, check & try again")
    logging.error(f"Entered machine type not exist in zone...Exited")
    sys.exit()
else:
    print(f"Entered machine type exist in Zone... Proceeding further")
    print("")

###Taking user confirmation to proceed further##
confrm=str(input(colored(f"Server going to resize from {machine_type} to {reqd_machine_type}... Please, confirm (yes/no) : ", 'cyan'))).lower()
if (confrm == "yes"):
    print(f"Proceeding further....")
else:
    print(f"User aborted")
    logging.error(f"User not confirmed resize.. Aborted")
    sys.exit()

print("")
if reqd_machine_type[0:2] == "m3":
    print(f"M3 machine type selected... Hence proceeding with pre-checks")
    script_m3='"/test/M3_compatibility_check.sh 1> /dev/null 2>&1"'
    cmd_precheck_m3=subprocess.run("sudo -i -u rcuser ssh -q -o StrictHostKeyChecking=no {} {}" .format(ServerName,script_m3), shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cmd_precheck_m3.returncode != 0:
        print(f"Pre-checks for M3 machine type has failed... Please, check & run below pre-check script in server manually & come back")
        print("M3_Check_Script = /test/M3_compatibility_check.sh")
        logging.error(f"M3 machine type pre-checks failed... Hence exited")
        sys.exit()
    else:
        print("M3 Machine type pre-checks are successful... Proceeding further......")
        logging.info(f"M3 pre-checks successful...")
else:
    print(f"M3 Pre-checks not required")

###Power-off Server##
print(f"Server is going to power off....")
poweroff=subprocess.run("sudo gcloud compute instances stop {} --zone={}" .format(ServerName,zone),shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if poweroff.returncode == 0:
    print(f"Server has been Powered off")
    logging.info(f"{ServerName} powered off successfully")
else:
    print(f"poweroff.stdoout")
    print(f"Unable to Power off server.... Please, check once!")
    logging.error(f"Server unable to power off due to {poweroff.stdoout}")


###Resizing the server##
print("")
resize=subprocess.getoutput("sudo gcloud compute instances set-machine-type {} --machine-type={} --zone={}" .format(ServerName,reqd_machine_type,zone))
check_resize=re.search("Updated", resize)
if check_resize:
    print(f"Server machine type changed to {reqd_machine_type}")
    logging.info("Server machine type changed")
    resize_error = 0
else:
    print(f"Failed to change machine type {resize.stderr}")
    logging.error("Server machine type failed to change")
    resize_error = 1

##Power On Server##
if resize_error == 0:
    poweron=subprocess.run("sudo gcloud compute instances start {} --zone={}" .format(ServerName,zone),shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if poweron.returncode == 0:
        print(f"Server Powered on successfully")
        logging.info("Server Powered on successfully post resize")
        resize_status='Success'
        rs = 1
    else:
        print(f"Server unable to Power On post resize. Due to {poweron.stderr}")
        print(f"Reverting server to old machine type.... please wait")
        logging.info(f"Server unable to Power on post resize.... Due to {poweron.stderr}")
        logging.info("Reverting server to old machine type")
        resize_old=subprocess.run("sudo gcloud compute instances set-machine-type {} --machine-type={} --zone={}" .format(ServerName,machine_type,zone),shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        poweron=subprocess.run("sudo gcloud compute instances start {} --zone={}" .format(ServerName,zone),shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("Reverted server to old machine type & powered on server")
        print(f"Hence, reverted to old machine type & power on server. Please, check error & try again")
        resize_status='Unable to start Power on server post resize.... Hence,Reverted to old machine type'
        rs = 0
else:
    print(f"Unable to change Machine type... Please, check above error messages")
    var_message='Unable to change Machine type..Please, check logs & try again!.. Currently Server is in power-off state'
    resize_status='Failed'
    rs = 0
    send_mail()
    sys.exit()


print(f"")
print(f"Waiting for server to come up...")
print(f"")
time.sleep(200)
check_server_accessible=subprocess.getoutput(['nc -zvw 10 ' f'{ServerName}' ' 22'])
check_server_accessible_re = re.search("succeeded", check_server_accessible)
if check_server_accessible_re:
    if poweron.returncode == 0:
        print(colored("Resize completed succesfully... Server is now accessible via SSH".format(ServerName),'cyan'))
        logging.info("Server is accessible after resize")
        var_message='Server Succesfully resized & accessible post resize'
        ps = 1
        send_mail()
    else:
        print(colored("Server not resized...Server is now accessible via SSH with old machine type".format(ServerName),'cyan'))
        logging.info("Server is accessible with old machine type")
        var_message='Unable to resize server & accessible with old machine type..Please check logs'
        ps = 0
        send_mail()

else:
       #print('{} port 22 is not open - error {}'.format(ServerName,check_server_exist))
    print(colored(f"**********{ServerName} is not accessible after resize... Please check manually***************",'blue', attrs=['bold']))
    logging.error("Server isn't accessible via SSH after resize...")
    var_message='Server resized but not accessible via SSH post resize... Please,check logs'
    ps = 0
    send_mail()
    sys.exit()
