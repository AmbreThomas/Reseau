from socket import *
from sys import argv
import threading
from os import system
from time import sleep

tentacle_ip = "127.0.0.1"

s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

print "Disponible..."
s.connect( (tentacle_ip, 7777) )
print s.recv(29)


threads = []

def normalize_file(filename, size):
	fichier = open(filename, "r")
	data = fichier.readlines()
	fichier.close()
	for i in xrange(len(data)):
		if len(data[i]) > size+1:
			data[i] = data[i][:size]+'\n'
		while len(data[i]) < size+1:
			data[i] = "0"+data[i]
	fichier = open(filename, "w")
	fichier.writelines(data)
	fichier.close()

def send_file(filename, max_size):
	print "envoi de %s..."%filename
	normalize_file(filename, max_size)
	fichier = open(filename, "r")
	data = fichier.readlines()
	fichier.close()
	for line in data:
		if len(line)>1:
			s.sendall(line[:-1])
		else:
			s.sendall(line)
	s.sendall("fin.")

def proceed(s,received):
	print "==> New job from tentacle server."
	args = " ".split(received)
	print "recu: ",received, "soit :", args
	system(received)
	send_file("mean-life-A.txt", 4)
	send_file("mean-life-B.txt", 4)

	send_file("mean-A-in-A.txt", 12)
	send_file("mean-A-in-B.txt", 12)

	send_file("mean-B-in-A.txt", 12)
	send_file("mean-B-in-B.txt", 12)

	send_file("mean-C-in-A.txt", 12)
	send_file("mean-C-in-B.txt", 12)

	send_file("mean-A-out.txt", 12)
	send_file("mean-B-out.txt", 12)
	send_file("mean-C-out.txt", 12)

	system("rm *.txt *.gif")
	print "==> One job completed.\n"
	exit()


try:
	while 1: #tant que le sous-traitant n'est pas coupe avec Ctrl+C
		received = s.recv(255)
		if received: #Accepte une demande de tentacle
			thread = threading.Thread(target=proceed, args=(s,received)) #lance un thread de calcul
			thread.start()
			threads.append(thread)


finally: #lorsque le sous-traitant est coupe avec Ctrl+C
	for t in threads:
		t.join()
	s.close()
	print "Server shut down."
s.close()
