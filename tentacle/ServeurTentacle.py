# -*- coding: utf-8 -*-
#https://pymotw.com/2/threading/ 
# https://docs.python.org/2.3/lib/semaphore-examples.html pour pool
# see http://www.programcreek.com/python/example/21025/signal.CTRL_BREAK_EVENT for breaking
# cf helio : https://duckduckgo.com/?q=global+variable+thread+python&atb=v37-5__&ia=qa&iax=1
#des daemons pour les ordi calculant ? interet ?

import socket
import threading
import select
import time
import signal
import sys
import time

#traiter l'arrêt
def signal_handler_stop(signal, frame):
	global WorkingServ
	global WorkingComp
	if (not WorkingServ) & WorkingComp :
		print('The subcontractors stop working (Ctrl+C)')
		WorkingComp = False #pour arrêt des thread. #essayer exemple minimal...
	if WorkingServ :
		print('We do not accept new clients anymore (Ctrl+C)')
		WorkingServ = False #pour arrêt de l'écoute

#sauvegarde de socket et suivi de leur activité.
#name désigne la socket
class ActivePool(object):
	def __init__(self):
		super(ActivePool, self).__init__()
		self.active = []
		self.activeID = {}
		self.activelock = {}
		self.activeParts = {}
		self.size = 0
		self.x = 0 #compteur d'ID
		self.acquired_parts = {}
	def makeActive(self, name):
		self.active.append(name)
		self.activeID[name] = self.x
		self.activeParts[name] = []
		self.activelock[name] = threading.Lock()
		self.acquired_parts[name] = {}
		self.x+=1
		self.size+=1
	def makeInactive(self, name):
		del self.activeID[name]
		del self.activelock[name]
		del self.activeParts[name]
		self.active.remove(name)
		self.size-=1
		name.shutdown(1)
		name.close()
	def __str__(self):
		return(str(self.active))
	def get_sockCLI(self, id) :
		nameS = [k for k, v in list(d.items()) if v == id]
		if len(nameS) == 0 :
			print("problem : unknow id")
		else :
			return(nameS[0])
	def getsize(self):
		return(self.size)
	def get_nb_of_acquired_parts(self) :
		return(len(self.acquired_parts))
	def get_acquired_parts(self) :
		return(self.acquired_parts)
	def getID(self,name):
		with self.activeID[name] :
			return(self.ac)
	def close(self) :
		for so in self.active :
			so.shutdown(1)
			so.close()

class Serveur(object) :
	def __init__(self):
		## paramètres
		self.port1 = sys.argv[1]
		self.port2 = sys.argv[2]
		self.nbcli = sys.argv[3]
		#self.TAILLE_BLOC=1024

		## gestion de l'arrêt
		global WorkingServ
		WorkingServ = True
		global WorkingComp
		WorkingComp = True

		## gestion des connexions (multiples)
		self.AllThreadCLI = []
		self.AllThreadSUB = []
		self.poolCLI = ActivePool()
		self.poolCLI_lock = threading.Lock()

		self.poolSUB = ActivePool()
		self.poolCLI_lock = threading.Lock()

		self.Queue = []
		self.Queue_lock = threading.Lock()

		sockCLI = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sockCLI.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
		sockCLI.bind(('',int(self.port1)))
		sockCLI.listen(10)
		print('Listening Clients on port %s'%self.port1)

		sockSUB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sockSUB.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
		sockSUB.bind(('',int(self.port2)))
		sockSUB.listen(10)
		print('Listening Subcontractors on port %s\n'%self.port2)

		waiting_list = [sockCLI, sockSUB]
		while WorkingServ :
			try :
				readable, writable, errored = select.select(waiting_list,[],[]) #wait for a potential connection
			except :
				print('Exeption, or no more client and subcontracctors accepted')     
				print('WorkingServ = ' + str(WorkingServ))
			for sock in readable : 
				if sock is sockCLI :
					clientsock, addr = sock.accept()
					print('A Client is connected : %s:%d' % addr)
					t = threading.Thread(target=self.handlerCLI, args=[clientsock])
					self.AllThreadCLI.append(t)
					t.start()
					print('Client currently connected are :')
					print(self.poolCLI)
				elif sock is sockSUB :
					subsock,addr = sock.accept()
					print('A subcontractor wants to work : %s:%d' %addr)
					t = threading.Thread(target=self.handlerSUB, args = [subsock])
					self.AllThreadSUB.append(t)
					t.start()
		for t in AllThreadCLI :
			t.join()
		WorkingComp = False
		for t in AllThreadSUB :
			t.join()
		print('All operations over.')

	def fractionne(self, demande_cli, id_client) :
		#transformer le string en n string dans une liste de taille n
		#chaque part est précédée de l'id_cli et d'un numéro de part.
		#["id_cli id_part demande",...]
		if "run" in demande_cli:
			demande = str(id_client)+' 1 '+ demande_cli
			return ([demande[:255]], 1)
		return(frac_demande, len(frac_demande))

	#gérer la relation client
	def handlerCLI(self,clientsock):
		## Lien et réception de la reuête.
		clientsock.sendall("Request accepted")     
		with self.poolCLI_lock :    
			self.poolCLI.makeActive(clientsock) 
		demande = clientsock.recv(255)
		print("Client asks: %s"%(demande))
		frac_demande, nb_of_parts = self.fractionne(demande,self.poolCLI.activeID[clientsock])
		with self.Queue_lock :
			self.Queue.extend(frac_demande)

		#réception des résultats
		parts = 0
		while len(self.poolCLI.activeParts[clientsock]) < nb_of_parts :
			time.sleep(2)
			pass
		print("All parts acquired for client N° : "+str(self.poolCLI.activeID[clientsock]))
		with self.poolCLI_lock :
			separated_parts = self.poolCLI.activeParts[clientsock].copy()
		result = self.assemble_parts(separated_parts)

		###ICI UNE BOUCLE POUR ENVOYER LE RESULTAT. CLIENT SUPPOSE ATTENDRE REPONSE.
		clientsock.sendall(result) 

		#Déconnection
		self.poolCLI.makeInactive(clientsock)

	def handlerSUB(self,subsock) :
		print('New subcontractor accepted.')
		self.poolSUB.makeActive(subsock)
		subsock.sendall("Connection accepted.")
		print('Subcontractors currently connected are :')
		print(self.poolSUB)
		print('\n')
		subsock.settimeout(0.5)
		while WorkingComp :
			try:
				with self.Queue_lock :
					subsock.sendall(self.Queue.pop(0)) #id_cli id_part mission
				ID_mission = subsock.recv()
				[ID_cli, ID_part] = ID_mission.split() 
				results = subsock.recv(12)  #ICI FAIRE BOUCLE DE RECEPTION DE RESULTAT
				with self.poolCLI_lock :
					poolSUB.makeInactive(subsock)
			except:
				time.sleep(0.5)
## main

if __name__=="__main__":
	import sys
	if len(sys.argv)<4:
		print("usage : %s <port1> <port2> <nbclients>" % (sys.argv[0],))
		sys.exit(-1)
	signal.signal(signal.SIGINT, signal_handler_stop) #1er CTRL+C gère arrêt écoute, 2e gère arrêt clients.
	Serveur()
##6666, 7777
