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

