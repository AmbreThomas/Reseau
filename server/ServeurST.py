# -*- coding: utf-8 -*-
from socket import *
from sys import argv
import signal
from multiprocessing import *
from os import system, chdir, getcwd, mkdir, path
from time import sleep

def newsubcontractor(i):
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
					send_gif(s, "result.gif")
					#system("rm -f *.txt *.gif")
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

def send_gif(target_sock, filename):
	print "envoi de %s..."%filename
	fichier = open(filename, "rb")
	octets = path.getsize(filename)
	alert = str(octets)
	while len(alert)<9:
		alert = " "+alert
	target_sock.sendall("GIF"+alert)
	num = 0
	if octets > 1024:	# Si fichier>1024 on l'envoie par paquets
		for i in range(octets / 1024):
			fichier.seek(num, 0) # on se deplace par rapport au numero de caractere (de 1024 a 1024 octets)
			donnees = fichier.read(1024) # Lecture du fichier en 1024 octets                            
			target_sock.send(donnees) # Envoi du fichier par paquet de 1024 octets
			num = num + 1024
	donnees = fichier.read(1024)
	target_sock.send(donnees)
	fichier.close()

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
	
	system("mv ServeurST.py src/")
	system("ls | grep -v 'src' | xargs rm -r")
	chdir("src")
	system("mv ServeurST.py ../")
	system("make")
	system("make clean")
	chdir("..")
	tentacle_ip = find_tentacle()
    
	if len(argv) == 2 :
		max_cpu_to_use = int(argv[1])
        
	jobs = []
	global continuer
	global CtrlC
	global deco 
	deco = False
	CtrlC = False
	continuer = True
    
	for i in range(min(cpu_count(),max_cpu_to_use)):
		jobs.append(Process(target=newsubcontractor, args=(i,)))
		jobs[i].start()
		
	while continuer :
		try :
			if deco :
				print("Déconnexion du serveur Osiris. Veuillez réessayer.")
				sys.exit(0)
			sleep(1)
		except KeyboardInterrupt :
			print("\n Ctrl+C pressé. Arrêt de toutes les connexions.")
			break
