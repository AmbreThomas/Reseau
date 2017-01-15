from socket import *
from time import sleep
from os import system

print "Ecoute..."
s = socket(AF_INET, SOCK_STREAM )
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

s.bind(("", 7777))
s.listen(5)

def clean_file(filename):
	fichier = open(filename, "r")
	data = fichier.readlines()
	fichier.close()
	for i in xrange(len(data)):
		while data[i][0] == '0' and len(data[i]) > 2:
			data[i] = data[i][1:]
	fichier = open(filename, "w")
	fichier.writelines(data[:-2]+['\n'])
	fichier.close()

def receive_file(newSocket, filename, max_size):
	print "reception de %s..."%filename
	r = ""
	output = []
	while "fin." not in r:
		r = newSocket.recv(max_size)
		output.append(r+'\n')
		if not r: break
	fichier = open(filename, "w")
	fichier.writelines(output)
	fichier.close()
	clean_file(filename)
	return r


try:
	while 1:
		newSocket, ip = s.accept()
		newSocket.sendall("Tentacle accepte ta demande.")
		print "%s has joined."% ip[0]
		while 1:# tant que le client est connecte
			demande = raw_input("Demande:")
			newSocket.sendall(demande)

			if "run" in demande:
				received = receive_file(newSocket, "mean-life-A.txt", 4)
				if received: received = receive_file(newSocket,"mean-life-B.txt", 4)
				if received: received = receive_file(newSocket,"mean-A-in-A.txt", 12)
				if received: received = receive_file(newSocket,"mean-A-in-B.txt", 12)
				if received: received = receive_file(newSocket,"mean-B-in-A.txt", 12)
				if received: received = receive_file(newSocket,"mean-B-in-B.txt", 12)
				if received: received = receive_file(newSocket,"mean-C-in-A.txt", 12)
				if received: received = receive_file(newSocket,"mean-C-in-B.txt", 12)
				if received: received = receive_file(newSocket,"mean-A-out.txt", 12)
				if received: received = receive_file(newSocket,"mean-B-out.txt", 12)
				if received: received = receive_file(newSocket,"mean-C-out.txt", 12)
				if received:
					system("Rscript Analyse.R")
					system("evince Rplots.pdf")
				system("rm *.txt")





			if not received: break
		print "%s has left."% ip[0]


finally:
	s.close()
	print "Server shut down."
