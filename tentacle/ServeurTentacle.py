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
		print('\nWe do not accept new clients anymore (Ctrl+C)')
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
		self.x = 1
	def makeActive(self, name):
		self.active.append(name)
		self.ID[name] = self.x
		self.Parts[name] = []
		self.lock[name] = threading.Lock()
		self.x+=1
		self.size+=1
	def makeInactive(self, name):
		del self.ID[name]
		del self.lock[name]
		del self.Parts[name]
		self.active.remove(name)
		self.size-=1
		try :
			name.shutdown(1)
			name.close()
		except :
			print("already closed")
	def __str__(self):
		return(str(self.active))
	def get_sockCLI(self, id) :
		nameS = [k for k, v in list(self.ID.items()) if v == id]
		if len(nameS) == 0 :
			return(-1)
		else :
			return(nameS[0])
	def get_size(self):
		return(self.size)
	def get_nb_of_disponible_parts(self,name) :
		return(len(self.Parts[name]))
	def close(self) :
		for so in self.active :
			so.shutdown(1)
			so.close()

class Serveur(object) :
	def __init__(self):
		try :
			print("Cleaning the place.")
			system("rm -rf TMP_files")
			system("mkdir TMP_files")
		except :
			pass
		self.port1 = 6666
		self.port_b = 6667
		## gestion de l'arrêt
		global WorkingServ
		WorkingServ = True
		global WorkingComp
		WorkingComp = True
		broad_thread = threading.Thread(target = self.broadcasting, args=[self.port_b])
		broad_thread.start()
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

		while WorkingServ :
			readable = []
			while WorkingServ and not len(readable):
				time.sleep(1)
				readable, writable, errored = select.select([sock], [], [], 0)
			for s in readable :
				mysocket, myaddr = s.accept()
				statut = mysocket.recv(4)
				if "ask " == statut :
					print('Un client se connecte : %s:%d' % myaddr)
					t = threading.Thread(target=self.handlerCLI, args=[mysocket])
					self.AllThreadCLI.append(t)
					t.start()
					time.sleep(0.2)
					with self.poolCLI_lock :
						print(str(self.poolCLI.get_size())+" clients connectés.")
				elif "work" == statut :
					print('Un sous-traitant se connecte : %s:%d' % myaddr)
					t = threading.Thread(target=self.handlerSUB, args=[mysocket])
					self.AllThreadSUB.append(t)
					t.start()
					time.sleep(0.2)
					with self.poolSUB_lock :
						print(str(self.poolSUB.get_size())+" sous-traitants connectés.")
		print("Attente de la fin des thread.")
		for t in self.AllThreadCLI :
			t.join()
		WorkingComp = False
		for t in self.AllThreadSUB :
			t.join()
		print('Fin des opérations. Extinction des feux. ')

	def fractionne(self, demande_cli, id_client) :
		#transformer le string en n string dans une liste de taille n
		#chaque part est précédée de l'id_cli et d'un numéro de part.
		#["id_cli id_part demande",...]
		if "run" in demande_cli:
			frac_demande = [ str(id_client)+' 1 '+ demande_cli ]
			frac_demande[-1] = frac_demande[-1][:255]
		if "all" in demande_cli:
			frac_demande = []
			for i in xrange(6):
				frac_demande.append( str(id_client)+" %d "%(i+1)+ " ".join(demande_cli.split(" ")[:7]) + " %d"%(i+1) )
				frac_demande[-1] = frac_demande[-1][:255]
		if "explore3D" in demande_cli:
			frac_demande = []
			args = demande_cli.split(" ")
			Nessais = int(args[8])
			Dmax = int(args[4]) # de 10^(-1) à 10^(-Dmax)
			Dstep = int(args[5])
			print Nessais,"essais","Dmax=",Dmax,"Dstep=",Dstep,"soit",6*Dmax/Dstep*Nessais,"jobs au total"
			print args
			compteur = 0
			for essai in range(1,1+Nessais):
				for D in range(1, 1+Dmax, Dstep):
					
					D_str = "0."
					while len(D_str)<D+1:
						D_str = D_str + "0"
					D_str = D_str + "1"
					
					for zone in xrange(1,7):
						compteur += 1
						demande = "./main all "+" ".join(args[2:4])+" "+D_str+" "+" ".join(args[6:8])
						print "job ",str(id_client)+" %d "%(compteur), demande
						frac_demande.append( str(id_client)+" %d "%(compteur)+ demande + " %d"%(zone) )
						frac_demande[-1] = frac_demande[-1][:255]
					
		return(frac_demande, len(frac_demande))

	#gérer la relation client
	def handlerCLI(self,clientsock):
		## Lien et réception de la reuqête.
		clientsock.sendall("Request accepted")     
		with self.poolCLI_lock :    
			self.poolCLI.makeActive(clientsock) 
			ID_CLI = self.poolCLI.ID[clientsock]
		try :
			demande = clientsock.recv(255)
		except :
			print("Client N " +str(ID_CLI) +" parti sans demander son reste.")
			self.poolCLI.makeInactive(clientsock)
		else :
			if len(demande) :
				print("Client N°"+str(ID_CLI)+" demande : %s"%(demande))
				with self.poolCLI_lock :
					frac_demande, nb_of_parts = self.fractionne(demande,self.poolCLI.ID[clientsock])
				with self.Queue_lock :
					self.Queue.extend(frac_demande)
				#réception des résultats
				parts = 0
				present = True
				while WorkingComp and parts < nb_of_parts and present :
					with self.poolCLI_lock :
						parts_waiting = self.poolCLI.get_nb_of_disponible_parts(clientsock)
						if  parts_waiting != 0 :
							p_file_addr = self.poolCLI.Parts[clientsock].pop(0)
					if parts_waiting != 0 :
						print "On envoie le fichier : ",p_file_addr, " au client N°", str(ID_CLI)
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
							print('Déconnexion du client N '+str(ID_CLI))
							self.poolCLI.makeInactive(clientsock)
							break
						parts+=1
					else :
						time.sleep(2)
						print("loop")
						clientsock.settimeout(0)
						try :
							test = clientsock.recv(1)
						except :
							clientsock.settimeout(None)
							pass
						else :
							present = False
							print('Déconnexion du client N°'+str(ID_CLI))
							self.poolCLI.makeInactive(clientsock)
				if parts == nb_of_parts :
					print("Client N°"+str(ID_CLI)+" satisfait avec succès")
					self.poolCLI.makeInactive(clientsock)
			else :
				print("Client N°" +str(ID_CLI) +" parti sans demander son reste.")
				self.poolCLI.makeInactive(clientsock)

	def handlerSUB(self,subsock) :
		with self.poolSUB_lock :
			self.poolSUB.makeActive(subsock)
			ID_SUB = self.poolSUB.ID[subsock]
			ID_SUB = str(ID_SUB)
		subsock.sendall("Connection accepted.")
		while WorkingComp :
			request = ""
			try:
				with self.Queue_lock :
					request = self.Queue.pop(0)
			except IndexError:	
				subsock.settimeout(0)
				try :
					subsock.recv(1)
				except :
					pass
				else :
					print("Déconnexion du sous-traitant N "+ID_SUB)
					with self.Queue_lock :
						self.Queue = [request] + self.Queue
					with self.poolSUB_lock :
						self.poolSUB.makeInactive(subsock)
					break
				time.sleep(1)
			else :
				subsock.settimeout(None)  #comment ne pas bloquer mais sortir si il était déjà parti...?
				try :
					subsock.send(request)
				except :
					print("Déconnexion du sous-traitant N "+ID_SUB)
					with self.Queue_lock :
						self.Queue = [request] + self.Queue
					with self.poolSUB_lock :
						self.poolSUB.makeInactive(subsock)
					break
				try: #Attente de l'envoi des fichiers
					ID_mission = subsock.recv(12)
				except :
					print("Déconnexion du sous-traitant N "+ID_SUB)
					with self.Queue_lock :
						self.Queue = [request] + self.Queue
					with self.poolSUB_lock :
						self.poolSUB.makeInactive(subsock)
					break
				if len(ID_mission) > 2 :
					ID_cli = int(ID_mission.split(" ")[0])
					ID_part = int(ID_mission.split(" ")[1])
					command = "mkdir -p TMP_files/CLI"+str(ID_cli)
					system(command)
					rep_addr = "TMP_files/CLI"+str(ID_cli)
					file_addr = "TMP_files/CLI"+str(ID_cli)+"/PART"+str(ID_part)+".txt"
					out_file = open(file_addr,'w')
					results = "" 
					while WorkingComp:
						try :
							results = subsock.recv(12)
						except :
							print("Déconnexion du sous-traitant N "+ID_SUB)
							with self.Queue_lock :
								self.Queue_lock = [request] + self.Queue_lock
							out_file.close()
							with self.poolSUB_lock :
								self.poolSUB.makeInactive(subsock)
							break
						else :
							if results == "end of job !" :
								break
							out_file.write(results+'\n')
					out_file.close()
					if results == "end of job !" :
						registered = False
						while not registered :
							try :
								self.poolCLI_lock.acquire(0)
							except :
								print('poolCLI_lock indisponible') #espéré inutile. jamais vu
								time.sleep(1)
							else :
								clientsock = self.poolCLI.get_sockCLI(ID_cli)
								if clientsock >=0:
									self.poolCLI.Parts[clientsock].append(file_addr)
									self.poolCLI_lock.release()
									registered = True
									print file_addr," prêt a être envoyé au client N°",str(ID_cli)
								else :
									print("debug : the client was gone")
									self.poolCLI_lock.release()
									break
					else :
						break

	def broadcasting(self,port_b) :
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		s.bind(('', port_b))
		s.settimeout(0.1)
		print "Ecoute broadcast sur le port ", port_b,"\n"
		global WorkingServ
		while WorkingServ:
			try:
				message, address = s.recvfrom(10)
				#print "Partenaire nous recherchant : ",address
				s.sendto("Le serveur Tentacule tourne à merveille. Envoyez votre requête.",address)
			except :
				pass	
	


if __name__=="__main__":
	import sys
	system("rm -rf TMP_files")
	system("mkdir TMP_files")
	#if len(sys.argv)<2:
	#	print("usage : %s <port1>" % (sys.argv[0],))
	#	sys.exit(-1)
	signal.signal(signal.SIGINT, signal_handler_stop) #1er CTRL+C gère arrêt écoute, 2e gère arrêt clients.
	Serveur()
