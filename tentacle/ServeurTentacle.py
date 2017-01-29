# -*- coding: utf-8 -*-

import socket
import threading
import select
import time
import signal
import sys
import time
from os import system

################### TRAITER L'ARRET PAR CTRL+C #########################
def signal_handler_stop(signal, frame):
	global WorkingServ
	global WorkingComp
	if (not WorkingServ) & WorkingComp :
		print('\nLes sous-traitants arrêtent le travail (Ctrl+C pressé une deuxième fois)')
		WorkingComp = False #pour arrêt des thread. #essayer exemple minimal...
	if WorkingServ :
		print("\nNous n'acceptons plus de nouveaux clients (Ctrl+C pressé une fois)")
		WorkingServ = False #pour arrêt de l'écoute

################### DEFINITION DES CLASSES #############################
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
			pass
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
	################### CREATION DU SERVEUR ############################
	def __init__(self):
		print("Bienvenue dans le serveur de calcul distribué Osiris.")
		try :
			print("Nous faisons le ménage dans les dossiers.")
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
		print('Ecoute sur le port %s'%self.port1)

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

	################### FRACTIONNEMENT D'UN JOB ########################
	def fractionne(self, demande_cli, id_client) :
		#transformer le string en n strings dans une liste
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
						frac_demande.append( str(id_client)+" %d "%(compteur)+ demande + " %d"%(zone) )
						frac_demande[-1] = frac_demande[-1][:255]
					
		return(frac_demande, len(frac_demande))

	################### RELATION AU CLIENT #############################
	def handlerCLI(self,clientsock):
		########### ACCEPTER LA CONNEXION ##############################
		with self.poolSUB_lock :
			nb_sub_dispo = self.poolSUB.get_size()
		clientsock.sendall("Requête acceptée ("+ str(nb_sub_dispo)+"ST)")     
		with self.poolCLI_lock :    
			self.poolCLI.makeActive(clientsock) 
			ID_CLI = self.poolCLI.ID[clientsock]
		########### ATTENDRE UN JOB ####################################
		try :
			demande = clientsock.recv(255)
		except :
			print("Client N " +str(ID_CLI) +" parti sans demander son reste.")
			self.poolCLI.makeInactive(clientsock)
		else :
			if len(demande) :
				############### METTRE LE JOB EN ATTENTE ###############
				print("Client N°"+str(ID_CLI)+" demande : %s"%(demande))
				with self.poolCLI_lock :
					frac_demande, nb_of_parts = self.fractionne(demande,self.poolCLI.ID[clientsock])
					GIF_to_send = False
				if int(demande.split()[8])>0 and nb_of_parts == 1:
					nb_of_parts+=1
					GIF_to_send = True
				with self.Queue_lock :
					self.Queue.extend(frac_demande)
				############### RENVOYER LES RESULTATS #################
				parts = 0
				present = True
				while WorkingComp and parts < nb_of_parts and present:
					########### TESTER SI FICHIER DISPONIBLE ###########
					with self.poolCLI_lock :
						parts_waiting = self.poolCLI.get_nb_of_disponible_parts(clientsock)
						if  parts_waiting != 0 :
							p_file_addr = self.poolCLI.Parts[clientsock].pop(0)
					########### SI OUI : ENVOYER FICHIER ###############
					if parts_waiting != 0:
						########### ENVOYER FICHIER TEXTE ##############
						if not (parts ==1 and GIF_to_send) :
							print "On envoie le fichier : ",p_file_addr, " au client N°", str(ID_CLI)
							p_file = open(p_file_addr,'r')
							part = p_file.readlines()
							final_line = part[-1]
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
						########## ENVOYER FICHIER GIF #################
						else :
							print "On envoie le fichier : ",p_file_addr, " au client N°", str(ID_CLI)
							p_file = open(p_file_addr,'rb')
							octets = int(final_line.split()[-1])
							surplus = octets%1024
							nb_of_blocks = (octets-surplus)/1024
							blocks_got = 0
							while blocks_got<nb_of_blocks :
								try :
									print "Block sent to cli :"+str(blocks_got)
									p = p_file.read(1024)
									clientsock.sendall(p)
									blocks_got+=1
									p_file.seek(blocks_got*1024)
								except :
									print('Déconnexion du client N°'+str(ID_CLI))
									self.poolCLI.makeInactive(clientsock)
									p_file.close()
									break
							if blocks_got == nb_of_blocks :
								clientsock.sendall(p_file.read(surplus))
								p_file.close()
						parts+=1
					######### SI NON : TESTER SI CLIENT TOUJOURS LA ####
					else :
						time.sleep(2)
						clientsock.settimeout(0)#provoque erreur de recv si client
						try :
							test = clientsock.recv(1)#le client n'envoie jamais rien
						except :
							clientsock.settimeout(None)
							pass
						else :
							clientsock.settimeout(None)
							present = False
							print('Déconnexion du client N°'+str(ID_CLI))
							self.poolCLI.makeInactive(clientsock)
				############# QUAND TOUS LES FICHIERS SONT RECUS #######
				if parts == nb_of_parts :
					print("Client N°"+str(ID_CLI)+" satisfait avec succès")
					self.poolCLI.makeInactive(clientsock)
			################### SI PAS DE DEMANDE DU CLIENT ############
			else :
				print("Client N°" +str(ID_CLI) +" parti sans demander son reste.")
				self.poolCLI.makeInactive(clientsock)

	################ RELATION AU SERVEUR SOUS-TRAITANT #################
	def handlerSUB(self,subsock) :
		############### ACCEPTER CONNEXION #############################
		with self.poolSUB_lock :
			self.poolSUB.makeActive(subsock)
			ID_SUB = self.poolSUB.ID[subsock]
			ID_SUB = str(ID_SUB)
		subsock.sendall("Connexion acceptée.")
		while WorkingComp :
			############## ATTENDRE UN JOB #############################
			request = ""
			try:
				with self.Queue_lock :
					request = self.Queue.pop(0)
			except IndexError:
				time.sleep(1)
			else :
				########## ENVOYER LE JOB ##############################
				subsock.settimeout(None) 
				try :
					s = subsock.send(request)
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
				########## RECEPTIONNER LES RESULTATS ##################
				if len(ID_mission) > 2 :
					###### PREPARER LES DOSSIERS/FICHIERS PART.TXT #####
					ID_cli = int(request.split(" ")[0])
					ID_part = int(request.split(" ")[1])
					command = "mkdir -p TMP_files/CLI"+str(ID_cli)
					system(command)
					rep_addr = "TMP_files/CLI"+str(ID_cli)
					file_addr = "TMP_files/CLI"+str(ID_cli)+"/PART"+str(ID_part)+".txt"
					file_name = str(ID_part)+".txt"
					while len(file_name)<12:
						file_name = " " + file_name 
					out_file = open(file_addr,'w')
					out_file.write(file_name+'\n')
					results = "" 
					GIF_to_get = False
					while WorkingComp:
						########### RECEVOIR FICHIERS TEXTE ############
						try :
							results = subsock.recv(12)
						except :
							print("Déconnexion du sous-traitant N "+ID_SUB)
							with self.Queue_lock :
								self.Queue = [request] + self.Queue
							with self.poolSUB_lock :
								self.poolSUB.makeInactive(subsock)
							break
						if "end of job !" == results:
							break
							out_file.write(results+"\n")
						if results[0:3] == "GIF" :
							nb_octets = int(results.split()[-1])
							surplus = nb_octets%1024
							nb_of_blocs = (nb_octets-surplus)/1024
							GIF_to_get = True
							blocks_got = 0
							break
					out_file.close()
					if GIF_to_get :
						########### RECEVOIR FICHIERS GIF ##############
						file_addr_gif = "TMP_files/CLI"+str(ID_cli)+"/GIF"+str(ID_part)+".gif"
						out_file = open(file_addr_gif,'wb')		
						while WorkingComp and blocks_got<nb_of_blocs :
							try :
								results = subsock.recv(1024)
							except :
								print("Déconnexion du sous-traitant N "+ID_SUB)
								with self.Queue_lock :
									self.Queue = [request] + self.Queue
								out_file.close()
								with self.poolSUB_lock :
									self.poolSUB.makeInactive(subsock)
								break
							out_file.write(results)
							blocks_got+=1
						try :
							results = subsock.recv(surplus)
							out_file.write(results)
						except :
							print("Déconnexion du sous-traitant N "+ID_SUB)
							with self.Queue_lock :
								self.Queue = [request] + self.Queue
							with self.poolSUB_lock :
								self.poolSUB.makeInactive(subsock)
							break	
						out_file.close()
					####### DECLARER LES FICHIERS COMME DISPONIBLES ####
					registered = False
					while not registered:
						try :
							self.poolCLI_lock.acquire(0)
						except :
							print('poolCLI_lock indisponible') #espéré inutile. jamais vu
							time.sleep(1)
						else :
							clientsock = self.poolCLI.get_sockCLI(ID_cli)
							if clientsock >=0:
								self.poolCLI.Parts[clientsock].append(file_addr)
								print file_addr," prêt a être envoyé au client N°",str(ID_cli)
								if GIF_to_get :
									self.poolCLI.Parts[clientsock].append(file_addr_gif)
									print file_addr_gif," prêt a être envoyé au client N°",str(ID_cli)
								self.poolCLI_lock.release()
								registered = True
							else :
								clientsock = self.poolCLI.get_sockCLI(ID_cli)
								if clientsock >=0: #si il existe toujours...
									self.poolCLI.Parts[clientsock].append(file_addr)
									print file_addr,"prêt a être envoyé au client N°",str(ID_cli)
									if GIF_to_get :
										self.poolCLI.Parts[clientsock].append(file_addr_gif)
										print file_addr_gif,"prêt a être envoyé au client N°",str(ID_cli)
									self.poolCLI_lock.release()
									registered = True
								else :
									print("Le client N°"+str(ID_cli)+" est parti sauvagement...")
									self.poolCLI_lock.release()
									break
					else :
						break

	############# REPONDRE A LA RECHERCHE D'OSIRIS ####################
	def broadcasting(self,port_b) :
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		s.bind(('', port_b))
		s.settimeout(0.1)
		print("\nEcoute broadcast sur le port "+ str(port_b) +"\n")
		time.sleep(0.1)
		global WorkingServ
		while WorkingServ:
			try:
				message, address = s.recvfrom(10)
				s.sendto("Le serveur Tentacule tourne à merveille. Envoyez votre requête.",address)
			except :
				pass

if __name__=="__main__":
    
	signal.signal(signal.SIGINT, signal_handler_stop) #1er CTRL+C gère arrêt écoute, 2e gère arrêt clients.
	Serveur()
