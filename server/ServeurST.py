# -*- coding: utf-8 -*-
from socket import *
from sys import argv
import signal
from multiprocessing import *
from os import system, chdir, getcwd, getpid, listdir, mkdir
from time import sleep

def newsubcontractor(i):
	#~ i = 1
	nom_machine = str(gethostname())+"-"+str(i+1)
	try:
		mkdir(nom_machine)
	except OSError:
		pass
	system("cp main %s/main"%nom_machine)
	chdir(nom_machine)
	s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	print "Sous-traitant %s disponible."%nom_machine
	s.connect( (tentacle_ip, 6666) )
	s.sendall("work")
	global continuer
	continuer = True
	global CtrlC
	deco = False
	global deco
	
	try :
		print s.recv(20)
	except KeyboardInterrupt:
		CtrlC = True
		continuer = False
	s.settimeout(0.5)
	try:
		while continuer : #tant que le sous-traitant n'est pas coupe avec Ctrl+C
			received = ""
			try :
				received = s.recv(255)
			except KeyboardInterrupt :
				CtrlC = True
				continuer = False
				break
			except timeout :
				pass
			else :
				if len(received) <2 :
					deco = True
					continuer = False
					break
			if received: #Accepte une demande de tentacle
				print "==> New job from tentacle server."
				jobID = " ".join(received.split(" ")[:2])
				received = " ".join(received.split(" ")[2:])
				args = received.split(" ")
				print "recu sur la machine %s"%nom_machine,"(job ID :",jobID,") : ",received.split("  ")[0]
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
	except :
		print "Arrêt du sous-traitant %d."%i
	try :
		s.shutdown()
		s.close()
	except : 
		pass

def normalize_file(filename, size):
	fichier = open(getcwd()+"/"+filename, "r")
	data = fichier.readlines()
	fichier.close()
	for i in xrange(len(data)):
		if len(data[i]) > size+1:
			data[i] = data[i][:size]+'\n'
		while len(data[i]) < size+1:
			data[i] = "#"+data[i]
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

def find_tentacle(timeout = 15) :
	s = socket(AF_INET, SOCK_DGRAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	s.bind(('', 6665))
	s.sendto("test", (('<broadcast>',6667)))
	t = 0
	s.settimeout(0.1)
	while t < timeout :
		s.sendto("test", (('<broadcast>',6667)))
		try :
			message, addr = s.recvfrom(8149)
		except :
			sleep(1)
			t+=1
		else :
			print "L'adresse du serveur est : ", addr[0]
			print "Message du serveur : ", message
			s.close()
			return(addr[0])
	print(str(timeout)+" secondes écoulées... Aucun serveur ne semble disponible.")
	s.close()
	return(0)

if __name__ == '__main__':
	
	chdir("src")
	system("make")
	chdir("..")
	tentacle_ip = find_tentacle()
	jobs = []
	global continuer
	global CtrlC
	global deco 
	deco = False
	CtrlC = False
	continuer = True
	for i in range(cpu_count()):
		jobs.append(Process(target=newsubcontractor, args=(i,)))
		jobs[i].start()
	while continuer :
		try :
			if deco :
				print("Déconnexion du serveur Osiris. Pressez Ctrl+C et réessayez.")
				sys.exit(0)
			
			sleep(1)
		except KeyboardInterrupt :
			print("\n Ctrl+C pressé. Arrêt de toutes les connexions.")
			break
