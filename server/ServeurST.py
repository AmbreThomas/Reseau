from socket import *
from sys import argv
from multiprocessing import *
from os import system
from time import sleep

tentacle_ip = "192.168.0.46"

def newsubcontractor(i):
	s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	print "Sous-traitant %d disponible."%i
	s.connect( (tentacle_ip, 6666) )
	s.sendall("work")
	print s.recv(20)
	while 1: #tant que le sous-traitant n'est pas coupe avec Ctrl+C
			received = s.recv(255)
			if received: #Accepte une demande de tentacle
				print "==> New job from tentacle server."
				received = " ".join(received.split(" ")[2:])
				args = received.split(" ")
				print "recu sur la machine %d: "%i,received, "soit :", args
				system(received)
				if "run" in received:
					send_file("mean-life-A.txt", 12)
					send_file("mean-life-B.txt", 12)
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
				s.sendall("end of job !")
				print "==> One job completed.\n"


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
	endstring = "fin."
	while len(endstring)<max_size:
		endstring = endstring + "."
	s.sendall(endstring)

if __name__ == '__main__':
	jobs = []
	for i in range(cpu_count()):
		p = Process(target=newsubcontractor, args=(i,))
		jobs.append(p)
		p.start()



