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
from os import system

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
		self.ID = {}
		self.lock = {}
		self.Parts = {}
		self.size = 0
		self.x = 0 #compteur d'ID
		self.acquired_parts = {}
	def makeActive(self, name):
		self.active.append(name)
		self.ID[name] = self.x
		self.Parts[name] = []
		self.lock[name] = threading.Lock()
		self.acquired_parts[name] = {}
		self.x+=1
		self.size+=1
	def makeInactive(self, name):
		del self.ID[name]
		del self.lock[name]
		del self.Parts[name]
		del self.acquired_parts[name] #putain Charles arrête les copier-coller foireux ! :P
		self.active.remove(name)
		self.size-=1
		name.shutdown(1)
		name.close()
	def __str__(self):
		return(str(self.active))
	def get_sockCLI(self, id) :
		nameS = [k for k, v in list(self.ID.items()) if v == id]
		if len(nameS) == 0 :
			print("problem : unknow id")
		else :
			return(nameS[0])
	def get_size(self):
		return(self.size)
	def get_nb_of_disponible_parts(self) :
		return(len(self.acquired_parts))
	def get_acquired_parts(self) :
		return(self.acquired_parts)
	def close(self) :
		for so in self.active :
			so.shutdown(1)
			so.close()

class Serveur(object) :
	def __init__(self):
		try :
			print("Cleaning the place.")
			system("rd /s /q TMP_files")
			system("md TMP_files")
		except :
			pass
		self.port1 = 6666
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
		self.poolSUB_lock = threading.Lock()

		self.Queue = []
		self.Queue_lock = threading.Lock()

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
		sock.bind(('',int(self.port1)))
		sock.listen(20)
		print('Listening on port %s'%self.port1)
		print ""

		while WorkingServ :
			readable = []
			while WorkingServ and not len(readable):
				time.sleep(1)
				readable, writable, errored = select.select([sock], [], [], 0)
			for s in readable :
				mysocket, myaddr = s.accept()
				statut = mysocket.recv(4)
				if "ask " == statut :
					print('\nA Client is connected : %s:%d' % myaddr)
					t = threading.Thread(target=self.handlerCLI, args=[mysocket])
					self.AllThreadCLI.append(t)
					t.start()
					time.sleep(0.2)
					with self.poolCLI_lock :
						print(str(self.poolCLI.get_size())+" client(s) actually connected.")
				elif "work" == statut :
					print('A subcontractor is connected : %s:%d' % myaddr)
					t = threading.Thread(target=self.handlerSUB, args=[mysocket])
					self.AllThreadSUB.append(t)
					t.start()
					time.sleep(0.2)
					with self.poolSUB_lock :
						print(str(self.poolSUB.get_size())+" subcontractor(s) actually connected.")
		for t in self.AllThreadCLI :
			t.join()
		WorkingComp = False
		for t in self.AllThreadSUB :
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
		## Lien et réception de la reuqête.
		clientsock.sendall("Request accepted")     
		with self.poolCLI_lock :    
			self.poolCLI.makeActive(clientsock) 
		try :
			demande = clientsock.recv(255)
		except :
			print("CLI is gone.")
			#handle...
		else :
			print("Client asks: %s"%(demande))
			with self.poolCLI_lock :
				frac_demande, nb_of_parts = self.fractionne(demande,self.poolCLI.ID[clientsock])
			with self.Queue_lock :
				self.Queue.extend(frac_demande)
			#réception des résultats
			parts = 0
			while WorkingComp and parts < nb_of_parts :
				with self.poolCLI_lock :
					parts_waiting = self.poolCLI.get_nb_of_disponible_parts()
					if  parts_waiting != 0 :
						p_file_addr = ""
						while WorkingComp and p_file_addr == "":
							try:
								p_file_addr = self.poolCLI.Parts[clientsock].pop(0)
							except IndexError:
								pass
				if parts_waiting != 0 :
					p_file = open(p_file_addr,'r')
					part = p_file.readlines()
					p_file.close()
					try :
						for line in part:
							if len(line)>1:
								clientsock.sendall(line[:-1])
							else:
								clientsock.sendall(line)
					except :
						print('CLI does not receive well')
					parts+=1
				else :
					time.sleep(2)
					pass
			print("All parts acquired for client N° : "+str(self.poolCLI.ID[clientsock]))

		#~ self.poolCLI.makeInactive(clientsock)
		self.poolCLI.makeInactive(clientsock)

	def handlerSUB(self,subsock) :
		print('New subcontractor accepted.')
		self.poolSUB.makeActive(subsock)
		subsock.sendall("Connection accepted.")
		print('Subcontractors currently connected are :')
		print(self.poolSUB)
		while WorkingComp :
			request = ""
			while WorkingComp and not len(request):
				try:
					with self.Queue_lock :
						request = self.Queue.pop(0)
				except IndexError:
					time.sleep(1)
			try:
				subsock.sendall(request) #id_cli id_part mission
			except :
				print("SUB is gone")
				with self.Queue_lock :
					self.Queue = [request] + self.Queue
				self.poolSUB.makeInactive(subsock)
				break
			subsock.settimeout(None)  #comment ne pas bloquer mais sortir si il était déjà parti...?
			try: #Attente de l'envoi des fichiers
				ID_mission = subsock.recv(12)
			except :
				print("SUB is gone")
				with self.Queue_lock :
					self.Queue = [request] + self.Queue
				self.poolSUB.makeInactive(subsock)
				break
			ID_cli = int(ID_mission.split(" ")[0])
			ID_part = int(ID_mission.split(" ")[1])
			rep_addr = "TMP_files\CLI"+str(ID_cli)
			file_addr = "TMP_files\CLI"+str(ID_cli)+"\PART"+str(ID_part)+".txt"

			out_file = open(file_addr,'w')
			results = "" 
			while WorkingComp:
				try :
					results = subsock.recv(12)
				except :
					print('The subcontactor stopped emitting.')
					with self.Queue_lock :
						self.Queue_lock = [request] + self.Queue_lock
					out_file.close()
					self.poolSUB.makeInactive(subsock)
					break
				if results == "end of job !" :
					break
				out_file.write(results+'\n')
			out_file.close()
			clientsock = self.poolCLI.get_sockCLI(ID_cli)
			self.poolCLI.Parts[clientsock].append(file_addr)
		self.poolSUB.makeInactive(subsock)
	
	

if __name__=="__main__":
	import sys
	#if len(sys.argv)<2:
	#	print("usage : %s <port1>" % (sys.argv[0],))
	#	sys.exit(-1)
	signal.signal(signal.SIGINT, signal_handler_stop) #1er CTRL+C gère arrêt écoute, 2e gère arrêt clients.
	Serveur()
