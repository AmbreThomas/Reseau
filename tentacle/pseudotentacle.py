from socket import *
from time import sleep
from os import system

print "Ecoute..."
sock_clients = socket(AF_INET, SOCK_STREAM )
sock_STs = socket(AF_INET, SOCK_STREAM )
sock_STs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock_clients.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

sock_STs.bind(("", 7777))
sock_clients.bind(("", 6666))
sock_clients.listen(5)
sock_STs.listen(5)



try:
	while 1:		#tant que tentacle tourne (couper avec Ctrl+C)
		ServSocket, Servip = sock_STs.accept()
		ServSocket.sendall("Tentacle accepte ta demande.")
		print "Server %s has joined."% Servip[0]
		while 1:	#tant qu'un serveur est connecte

			print "Attente de clients..."
			CliSocket, Cliip = sock_clients.accept()
			CliSocket.sendall("Tentacle accepte ta demande.")

			demande = CliSocket.recv(255)
			print "Client %s asks: %s"%(Cliip[0], demande)
			ServSocket.sendall(demande)

			while 1: #Tant que le serveur envoie
				received = ServSocket.recv(12)
				if received=="end of job !" or not received: break
				try:
					CliSocket.sendall(received)
				except:
					print "Le client a abandonne !"
					break
			if not received:
				print "Server %s has left."% Servip[0]
				break
			print "Demande de %s terminee."%Cliip[0]


finally:
	sock_STs.close()
	sock_clients.close()
	print "Tentacle shut down."

'''
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
'''
