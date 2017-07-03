###############################################
### GCP agent installation application v1.0 ###
###############################################
import os, re, paramiko, sys
from colored import fg, bg, attr
from time import sleep
#
# Define Colors & attributes
#
okStatus = fg('white') + bg('green') + attr('bold')
errStatus = fg('white') + bg('red') + attr('bold')
warStatus = fg('white') + bg('dark_orange') + attr('bold')
normalText = attr('reset')
boldText = attr('bold')
infoText = fg('white') + bg('grey_39')
#
# Greatings Message
#
os.system('clear')
print(infoText + boldText + "\t\t\t\t\t\t\t" + normalText)
print(infoText + boldText + "\tGCP agent installation application v=0.1\t" + normalText)
print(infoText + boldText + "\t\t\t\t\t\t\t" + normalText)
print(boldText + """\n[Greatings humans! I'll help you to install GCP monitoring
agent on your instances at once!]
Are you ready(type \'y\' or \'n\')?""" + normalText)
answer = input()
result = True
while result == True:
    if answer == 'y':
        print(boldText + infoText + '\nMoving on...\n' + normalText)
        result = False
    elif answer == 'n':
        print(boldText + infoText + '\nSee ya!' + normalText)
        exit()
    else:
        print(warStatus + '\nINCORRECT INPUT:' + normalText + boldText + ' (Type \'y\' or \'n\')' + normalText)
        answer = input()
#
# Open file with IPs in binary
#
print("Enter name of the hosts file:", end = ' ')
while result == False:
    hostsFile = input()
    if hostsFile == 'q':
        exit()
    print(boldText + infoText + '\nOpening hosts file...' + normalText)
    try:
        openHosts = open(hostsFile)
        print(okStatus + "\nFile opened. Getting hosts IPs to connect with..." + normalText)
        result = True
        sleep(1)
    except FileNotFoundError:
        print(errStatus + "\nHosts file '" + hostsFile + "' doesn't exist. Make sure you've specified an existing one and enter it or press 'q' for exit" + normalText)
hostsList = openHosts.readlines()
openHosts.close()
if len(hostsList) == 0:
    print(warStatus + '\nHosts file is empty. Come back when you\'ll add\nat least one host. See ya!' + normalText)
    exit()
else:
    count = 0
    for host in hostsList:
        count = count + 1
    print(infoText + '\nHosts counted:' + boldText, count, normalText)
#
# Enter Username & key_filename
#
print("Enter username:", end = ' ')
userName = input()
print("Enter ssh key filename:", end = ' ')
keyFileName = input()
#
# Check SSH availability and print out. Calculate opened and closed ports
#
print(boldText + infoText + '\nChecking SSH availability on every host...' + normalText + "\n")
print('      HOST \t|   SSH')
print('-' * 26)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
countOpened = 0
countClosed = 0
availableHosts = open('availableHosts','w')
availableHosts.write('')
availableHosts.close()
unavailableHosts = open('unavailableHosts','w')
unavailableHosts.write('')
unavailableHosts.close()
for host in hostsList:
    host = host.rstrip()
    try:
        ssh.connect(hostname = host, username = userName, key_filename = keyFileName, timeout = 3)
        print(host + '\t: ' + okStatus + " OPENED " + normalText)
        countOpened = countOpened + 1
        availableHosts = open('availableHosts','a')
        availableHosts.write(host + '\n')
    except :
        print(host + '\t: ' + errStatus + " CLOSED " + normalText)
        countClosed = countClosed + 1
        unavailableHosts = open('unavailableHosts','a')
        unavailableHosts.write(host + '\n')
print('\n')
print("SSH is " + boldText + "Opened" + normalText + " on " + boldText + str(countOpened) + normalText + " host(s)")
print("SSH is " + boldText + "Closed" + normalText + " on " + boldText + str(countClosed) + normalText + " host(s)")
#
# Creating validation directory and copy json config
#
print(boldText + infoText + '\nDeploying JSON validation file...' + normalText + "\n")
availableHosts = open('availableHosts')
availableHostsList = availableHosts.readlines()
print('      HOST \t|     jsonStatus')
print('-' * 36)
for host in availableHostsList:
    ssh.connect(hostname = host, username = userName, key_filename = keyFileName, timeout = 3)
    stdin, stdout, stderr = ssh.exec_command('sudo cat /etc/google/auth/application_default_credentials.json')
    destPath = '/etc/google/auth/application_default_credentials.json'
    jsonName = 'application_default_credentials.json'
    data = stderr.readlines()
    host = host.rstrip()
    if len(data) != 0:
        print(host + "\t: " + errStatus + str(data) + normalText)
        print("\t\t  " + warStatus + "Creating directory..." + normalText)
        stdin, stdout, stderr = ssh.exec_command('sudo mkdir -p /etc/google/auth/ && sudo chmod 777 -R /etc/google/auth/')
        sleep(0.5)
        print("\t\t  " + okStatus + "Done!" + normalText)
        print("\t\t  " + warStatus + "Uploading JSON configuration file..." + normalText)
        sftp = ssh.open_sftp()
        sftp.put(jsonName, destPath)
        sleep(0.5)
        print("\t\t  " + okStatus + "Uploaded!" + normalText)
        sftp.close()
    else:
        print(host + "\t: " + okStatus + " JSON is at place " + normalText)
    ssh.close()
#
# Check if GCP agent is installed and running otherwize - install it
#
print(boldText + infoText + '\nChecking GCP agent...' + normalText + "\n")
availableHosts = open('availableHosts')
availableHostsList = availableHosts.readlines()
print('      HOST \t|     agentStatus')
print('-' * 36)
for host in availableHostsList:
    ssh.connect(hostname = host, username = userName, key_filename = keyFileName, timeout = 3)
    stdin, stdout, stderr = ssh.exec_command('systemctl status stackdriver-agent | grep \'Unit stackdriver-agent.service could not be found\'')
    data = stdout.read() + stderr.read()
    data = str(data)
    dataRegex = re.compile(r'Unit stackdriver-agent.service could not be found')
    matchingObject = dataRegex.search(data)
    if matchingObject != None:
        print(host.strip() + "\t: " + warStatus + 'Installing GCP agent...' + normalText)
        stdin, stdout, stderr = ssh.exec_command('curl -O "https://repo.stackdriver.com/stack-install.sh" && sudo sh stack-install.sh --write-gcm && sudo systemctl restart stackdriver-agent')
        error = stderr.readlines()
        if len(error) != 0 and len(error) != 3:
            print(host.strip() + "\t: " + errStatus + str(error) + normalText)
        else:
            print("\t\t  " + okStatus + "Agent was installed and started!" + normalText)
    else:
        print(host.strip() + "\t: " + okStatus + " Agent was installed and started! " + normalText)
    ssh.close()
print(okStatus + "\nAll done!" + normalText + "\n")
