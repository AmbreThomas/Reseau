from socket import *
from sys import argv
from multiprocessing import *
from os import system, chdir
from time import sleep

tentacle_ip = "127.0.0.1"

def newsubcontractor(i):
	system("mkdir -p %d"%i)
	system("cp main %d/main"%i)
	chdir("%d"%i)
	s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	print "Sous-traitant %d disponible."%(i+1)
	s.connect( (tentacle_ip, 6666) )
	s.sendall("work")
	print s.recv(20)
	while 1: #tant que le sous-traitant n'est pas coupe avec Ctrl+C
			received = s.recv(255)
			if received: #Accepte une demande de tentacle
				print "==> New job from tentacle server."
				jobID = " ".join(received.split(" ")[:2])
				received = " ".join(received.split(" ")[2:])
				args = received.split(" ")
				print "recu sur la machine %d: "%(i+1),received,"(job ID :",jobID,")"
				system(received)
				while len(jobID)<12:
					jobID = jobID+" "
				s.sendall(jobID)
				if "run" in received:
					send_file(s, "mean-life-A.txt", 12)
					send_file(s, "mean-life-B.txt", 12)
					send_file(s, "mean-A-in-A.txt", 12)
					send_file(s, "mean-A-in-B.txt", 12)
					send_file(s, "mean-B-in-A.txt", 12)
					send_file(s, "mean-B-in-B.txt", 12)
					send_file(s, "mean-C-in-A.txt", 12)
					send_file(s, "mean-C-in-B.txt", 12)
					send_file(s, "mean-A-out.txt", 12)
					send_file(s, "mean-B-out.txt", 12)
					send_file(s, "mean-C-out.txt", 12)
					system("rm -f *.txt *.gif")
				if "all" in received:
					send_file(s, "results.txt", 12)
					system("rm -f results.txt")
				if "explore3D" in received:
					send_file(s, "results.txt", 12)
					system("rm -f results.txt")
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

def send_file(target_sock, filename, max_size):
	print "envoi de %s..."%filename
	normalize_file(filename, max_size)
	fichier = open(filename, "r")
	data = fichier.readlines()
	fichier.close()
	for line in data:
		if len(line)>1:
			target_sock.sendall(line[:-1])
		else:
			target_sock.sendall(line)
	endstring = "fin."
	while len(endstring)<max_size:
		endstring = endstring + "."
	target_sock.sendall(endstring)

if __name__ == '__main__':
	chdir("src")
	system("make")
	chdir("..")
	jobs = []
	for i in range(cpu_count()):
		system("rm -rf %d"%i)
		p = Process(target=newsubcontractor, args=(i,))
		jobs.append(p)
		p.start()



