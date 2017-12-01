import os
import sys
import paramiko

if len(sys.argv) != 3:
	print "Usage: [python "+sys.argv[0]+" <username> <password>] to Frodo machine."
	quit()

username = sys.argv[1]
password = sys.argv[2]
#server = '192.168.22.22'
server = 's22.int.contactis.pl'
port = 666
local_data_dir = 'datasets/lekta_dialogues/raw/'

print "Getting the list of directories with records."
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
ssh.connect(server, username=username, password=password, port=port)

cmd = 'ls -F /root/root_babylon'
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

dir_list = ssh_stdout.readlines()
dir_list = [dir[:-1] for dir in dir_list if dir[-2] == '/']

if ssh:
	ssh.close()

print "\nChecking if the directories exist locally."

for dir in dir_list:
	if not os.path.exists(local_data_dir+dir):
		os.mkdir(local_data_dir+dir)
		print local_data_dir+dir+" directory has been added."

print "\nSyncing the directories with remote machine."

for dir in dir_list:
	print 'Copying contents of ' + dir
	cmd = 'rsync -az -e "ssh -p ' + str(port) + '" piotr.bednarski@s22.int.contactis.pl:/root/root_babylon/'+ dir + 'Records/' + ' ' + 'datasets/lekta_dialogues/raw/' + dir
	os.system(cmd)
