# -*- coding: utf-8 -*-
##############################  IMPORTATIONS  ##################################
from Tkinter import *
from ttk import *
from tkMessageBox import *
import sys
import tkFont
import matplotlib.pyplot as plt
from numpy import *
import socket
import os
import string
from tkFileDialog import *
import signal
from PIL import Image, ImageTk
import pygame
import time
import select
from msgbox import *
from gif import *

################################  MUSIQUE  #####################################
pygame.mixer.init()
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.set_volume(1.5)
pygame.mixer.music.play(-1)

#######################  GESTION FERMETURE SYSTEME  ############################
def intercepte(fenetre):
	fenetre.destroy()

def intercepte2(fenetre):
	exit()
	fenetre.quit()

###########################  TROUVER IP SERVEUR  ###############################
def find_osiris_ip(timeout = 15) :
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.bind(('', 6664))
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

tentacle_ip = find_osiris_ip()

########################  TRACER COURBES REQUETE 3  ############################
def heatphases(D, N, resolT, resolA):
	plt.clf()
	plt.cla()
	ncol = 1500/resolT
	nrow = 51/resolA
	data = []
	print "\nouverture de %d fichiers..."%N
	for i in xrange(1,N+1):
		file_list = open("essai%d/results-D%d.txt"%(i, D), "r")
		data.append(file_list.readlines())
		file_list.close()
	matrix = zeros((nrow+1, ncol+1))
	print "\nmixing the %d runs..."%N
	for point in xrange(len(data[0])):
		l = []
		for essai in xrange(N):
			l.append( data[essai][point].split(' ') )
		matrix[ int(l[0][0])/resolA, int(l[0][1])/resolT] = sum([ int(l[k][2]) for k in xrange(N) ])/float(N)
	print "> OK"
	print "\ngenerating heatmap for D=%f..."%(10**(-D))
	X = zeros((nrow+1, ncol+1))
	Y = zeros((nrow+1, ncol+1))

	for i in xrange(nrow+1):
		for j in xrange(ncol+1):
			X[i,j] = resolT*j+1
			Y[i,j] = resolA*i
	print "\n",shape(X),"\n",shape(Y),"\n",shape(matrix),"\n"


	plt.pcolor(X,Y,matrix)
	plt.title("Diagramme de phases des colonies satellites")
	plt.suptitle("pour D = %f"%(10**(-D)))
	plt.xlim(0,1500)
	plt.ylim(0, 50)
	plt.xlabel("Temps avant de repiquer la culture")
	plt.ylabel("[Glucose] initiale")
	print "saving %d.png..."%D
	plt.savefig("%d.png"%D)

########################  TROUVE TAILLE FENETRES TK  ###########################
def geoliste(g):
	r = [i for i in range (0, len(g)) if not g[i].isdigit()]
	return [int(g[0:r[0]]), int(g[r[0]+1:r[1]])]

#######################  ASSEMBLE FICHIERS REQUETE 3  ##########################
def assembler(liste, nom, dossier):
	fichier = open("essai"+str(dossier)+"/results-D"+str(nom)+".txt", "w")
	for i in range (liste[0], liste[1] + 1):
		ecrire = open(str(i)+".txt", "r")
		fichier.writelines(ecrire.readlines()[:-1])
		ecrire.close()
	fichier.close()

####################  DEBARASSE FICHIERS LIGNES INUTILES  ######################
def clean_file(filename, a = 1):
	fichier = open(filename, "r")
	data = fichier.readlines()
	fichier.close()
	for i in xrange(len(data)):
		while data[i][0] == '#':
			data[i] = data[i][1:]
	fichier = open(filename, "w")
	if (a == 1):
		fichier.writelines(data[1:-1]+['\n'])
	else :
		fichier.writelines(data[:-1]+['\n'])
	fichier.close()

########################  RECOIT FICHIERS REQUETE 3  ###########################
def receive_gif(conn, filename):
	received = conn.recv(12) #GIF + size
	octets = int(received.split(" ")[-1])
	print "reception de %s..."%filename
	fichier = open(filename, "wb")
	for i in range(octets/1024):
		received = conn.recv(1024)
		fichier.write(received)
	fichier.write(conn.recv(octets%1024))
	fichier.close()

#######################  RECOIT FICHIERS REQUETES 1/2  #########################
def receive_file(newSocket, filename, max_size, a = 1):
	print "reception de %s..."%filename
	r = ""
	output = []
	while "fin." not in r:
		r = newSocket.recv(max_size)
		if (len(r) < max_size):
			r = r + newSocket.recv(max_size - len(r))
		output.append(r+'\n')
		if not r: break
	fichier = open(filename, "w")
	fichier.writelines(output)
	fichier.close()
	clean_file(filename, a)
	return r

#######################  ASSEMBLE FICHIERS REQUETE 2  ##########################
def add_file(newSocket, max_size, fichier):
	print "reception de donnees..."
	r = ""
	output = []
	while "fin." not in r:
		r = newSocket.recv(max_size)
		if (len(r) < max_size):
			r = r + newSocket.recv(max_size - len(r))
		output.append(r+'\n')
		if not r: break
	fichier.writelines(output[1:-1])
	return r

##############################  GESTION BOUTONS  ###############################
def clickvalue1(event):
	listeCombobox = ["[Glucose] extracellulaire", "[Acetate] extracellulaire", "[Ethanol] extracellulaire", "[Glucose] intracellulaire", "[Acetate] intracellulaire", "[Ethanol] intracellulaire", "Cellules vivantes", "Cellules A vs B", "Fitness des cellules"]
	if (valueGif.get() == 0 or selectGif.get() == "Choisissez"):
		selection = "0"
	else:
		selection = str(listeCombobox.index(selectGif.get())+1)
	envoyer("./main run "+valueLargeur.get()+" "+valueHauteur.get()+" "+valueD.get()+" "+valueA0.get()+" "+valueT.get()+" "+valueiterMax.get()+" "+selection, fenetre2)

def clickbutton1(event):
	global valueRequest
	ParamRequest(valueRequest.get(), fenetre)

def clickvalue2(event):
	envoyer("./main all "+valueLargeur.get()+" "+valueHauteur.get()+" "+valueD.get()+" "+valueT.get()+" "+valueA0.get(), fenetre2)

def clickvalue3(event):
	envoyer("./main explore3D "+valueLargeur.get()+" "+valueHauteur.get()+" "+valueDmax.get()+" "+valueDstep.get()+" "+valueT.get()+" "+valueA0.get()+" "+valueNessai.get(), fenetre2)

##########################  GESTION MENU DEROULANT  ############################
def afficherBox():
	if (valueGif.get()):
		global selectGif
		global c
		selectGif = StringVar()
		selectGif.set("Choisissez")
		listeCombobox = ("[Glucose] extracellulaire", "[Acetate] extracellulaire", "[Ethanol] extracellulaire", "[Glucose] intracellulaire", "[Acetate] intracellulaire", "[Ethanol] intracellulaire", "Cellules vivantes", "Cellules A vs B", "Fitness des cellules")
		c = Combobox(textvariable = selectGif, values = listeCombobox, width = 200)
		c.pack()
	elif (valueGif.get() == 0):
		c.destroy()

##########################  DEMANDE DES PARAMETRES  ############################
def ParamRequest(value, fen):
	fen.destroy()
	global fenetre2
	fenetre2 = Tk()
	fenetre2.protocol("WM_DELETE_WINDOW", lambda: intercepte(fenetre2))
	fenetre2.resizable(width = False, height = False)
	fenetre2.iconbitmap("@../icone.xbm")
	h = fenetre2.winfo_screenheight()
	w = fenetre2.winfo_screenwidth()
	frame = Frame(fenetre2, borderwidth=2, relief=GROOVE).pack(padx=1, pady=1)
	Label(frame, text = "Merci de rentrer les paramètres de la simulation").pack()
	global valueD
	valueD = StringVar()
	valueD.set(1)
	global valueA0
	valueA0 = StringVar()
	valueA0.set(10)
	global valueiterMax
	valueiterMax = StringVar()
	valueiterMax.set(10000)
	global valueT
	valueT = StringVar()
	valueT.set(100)
	global valueDmax
	valueDmax = StringVar()
	valueDmax.set(5)
	global valueDstep
	valueDstep = StringVar()
	valueDstep.set(1)
	global valueNessai
	valueNessai = StringVar()
	valueNessai.set(10)
	global valueLargeur
	valueLargeur = StringVar()
	valueLargeur.set(32)
	global valueHauteur
	valueHauteur = StringVar()
	valueHauteur.set(32)
	Label(frame, text = "Hauteur de la boîte", font="bold").pack()
	EntryHauteur = Entry(frame, textvariable=valueHauteur, width=30).pack()
	Label(frame, text = "Largeur de la boîte", font="bold").pack()
	EntryLargeur = Entry(frame, textvariable=valueLargeur, width=30).pack()
	if value == 1:
			fenetre2.title("Realiser une simulation")
			Label(frame, text = "Coefficient de diffusion", font="bold").pack()
			valueD.set(0.1)
			EntryD = Entry(frame, textvariable=valueD, width=30).pack()
			Label(frame, text = "Concentration initiale en glucose", font="bold").pack()
			valueA0.set(20)
			EntryA0 = Entry(frame, textvariable=valueA0, width=30).pack()
			Label(frame, text = "Pas des temps entre les repiquages", font="bold").pack()
			valueT.set(1000)
			EntryT = Entry(frame, textvariable=valueT, width=30).pack()
			Label(frame, text = "Durée de l'expérience", font = "bold").pack()
			valueiterMax.set(5000)
			EntryiterMax = Entry(frame, textvariable=valueiterMax, width=30).pack()
			global valueGif
			valueGif = IntVar()
			valueGif.set(0)
			check = Checkbutton(frame, text="Visualiser ?", variable=valueGif, command=afficherBox).pack()
			bvalue1 = Button(fenetre2, text="Valider", command=lambda: clickvalue1(1))
			bvalue1.pack(side = LEFT, anchor=SW)
			bvalue1.focus_set()
			bvalue1.bind('<Return>', clickvalue1)
			Button(fenetre2, text="Fermer", command=fenetre2.destroy).pack(side = RIGHT, anchor=SE)
			L = 300
			H = 325
			fenetre2.geometry("%dx%d+"%(L, H) + str(w/2-L/2) + "+"+ str(h/2-H/2))
	elif value == 2:
			fenetre2.title("Exploration parametrique (T et A0)")
			Label(frame, text = "Coefficient de diffusion", font="bold").pack()
			valueD.set(0.1)
			EntryD = Entry(frame, textvariable=valueD, width=30).pack()
			Label(frame, text = "Pas des concentrations en glucose (entre 0 et 50)", font="bold").pack()
			EntryA0 = Entry(frame, textvariable=valueA0, width=30).pack()
			Label(frame, text = "Pas de temps entre les repiquages (entre 1 et 1500)", font="bold").pack()
			EntryT = Entry(frame, textvariable=valueT, width=30).pack()
			bvalue2 = Button(fenetre2, text="Valider", command=lambda: clickvalue2(1))
			bvalue2.pack(side = LEFT, anchor=SW)
			bvalue2.focus_set()
			bvalue2.bind('<Return>', clickvalue2)
			Button(fenetre2, text="Fermer", command=fenetre2.destroy).pack(side = RIGHT, anchor=SE)
			L = 420
			H = 265
			fenetre2.geometry("%dx%d+"%(L, H) + str(w/2-L/2) + "+"+ str(h/2-H/2))
	elif value == 3:
			fenetre2.title("Exploration parametrique (T, A0 et Dmax)")
			Label(frame, text = "Coefficient de diffusion maximum", font="bold").pack()
			EntryDmax = Entry(frame, textvariable=valueDmax, width=30).pack()
			Label(frame, text = "Pas des coefficients de diffusion", font="bold").pack()
			EntryDstep = Entry(frame, textvariable=valueDstep, width=30).pack()
			Label(frame, text = "Pas des concentrations en glucose", font="bold").pack()
			EntryA0 = Entry(frame, textvariable=valueA0, width=30).pack()
			Label(frame, text = "Pas de temps entre les repiquages", font="bold").pack()
			EntryT = Entry(frame, textvariable=valueT, width=30).pack()
			Label(frame, text = "Nombres d'essais à réaliser", font="bold").pack()
			EntryNessai = Entry(frame, textvariable=valueNessai, width=30).pack()
			bvalue3 = Button(fenetre2, text="Valider", command=lambda: clickvalue3(1))
			bvalue3.pack(side = LEFT, anchor=SW)
			bvalue3.focus_set()
			bvalue3.bind('<Return>', clickvalue3)
			Button(fenetre2, text="Fermer", command=fenetre2.destroy).pack(side = RIGHT, anchor = SE)
			L = 380
			H = 350
			fenetre2.geometry("%dx%d+"%(L, H) + str(w/2-L/2) + "+"+ str(h/2-H/2))
	return;

###############################  GESTION CTR+C  ################################
def signal_handler(signal, frame):
	print 'You pressed Ctrl+C !'

######################  GESTION ENVOI/RECEPTION REQUETES  ######################
def envoyer(params, fenetre):
	fenetre.destroy()
	fenetre2=Tk()
	fenetre2.protocol("WM_DELETE_WINDOW", lambda: intercepte(fenetre2))
	fenetre2.resizable(width = False, height = False)
	fenetre2.iconbitmap("@../icone.xbm")
	h = fenetre2.winfo_screenheight()
	w = fenetre2.winfo_screenwidth()
	L, H = geoliste(fenetre2.geometry())
	fenetre2.geometry("%dx%d+"%(L,H) + str(w/2-L/2) + "+" + str(h/2-H/2))
	signal.signal(signal.SIGINT, signal_handler)
	print 'Press Ctrl+C pour arreter le client'
	for i in range(len(params), 255):
		params += " "
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.connect((tentacle_ip, 6666))
		s.sendall("ask ")
		print s.recv(29)
		mbox('Les calculs sont prêts à être effectués.\nCliquez sur OK pour continuer.')
		s.sendall(params)
		if "run" in params:
			received = receive_file(s, "mean-life-A.txt", 12)
			if received: received = receive_file(s,"mean-life-B.txt", 12, 3)
			if received: received = receive_file(s,"mean-A-in-A.txt", 12, 3)
			if received: received = receive_file(s,"mean-A-in-B.txt", 12, 3)
			if received: received = receive_file(s,"mean-B-in-A.txt", 12, 3)
			if received: received = receive_file(s,"mean-B-in-B.txt", 12, 3)
			if received: received = receive_file(s,"mean-C-in-A.txt", 12, 3)
			if received: received = receive_file(s,"mean-C-in-B.txt", 12, 3)
			if received: received = receive_file(s,"mean-A-out.txt", 12, 3)
			if received: received = receive_file(s,"mean-B-out.txt", 12, 3)
			if received: received = receive_file(s,"mean-C-out.txt", 12, 3)
			if received: receive_gif(s, "result.gif")
			if received:
				os.system("Rscript Analyse.R")
				afficher(1, fenetre2)
				os.system("rm *.txt")
				global enregistrer
				if (not enregistrer):
					os.system("rm th.png")
				else:
					os.system("cp th.png "+rep+"/th.png")
					if rep != os.getcwd():
						os.system("rm -f th.png")
		if "all" in params:
			fichier = open("results.txt", "w")
			received = add_file(s, 12, fichier)
			i = 1
			while (received and i < 6):
				received = add_file(s, 12, fichier)
				i += 1
			fichier.close()
			clean_file("results.txt")
			if (received):
				os.system("Rscript phases.R")
				afficher(2, fenetre2)
				os.system("rm *.txt")
				if (not enregistrer):
					os.system("rm th2.png")
				else:
					os.system("cp th2.png "+rep+"/th2.png")
					if rep != os.getcwd():
						os.system("rm -f th2.png")
		if "explore" in params:
			compteur = 0;
			params = params.split(" ")
			Dmax = int(params[4])
			Dstep = int(params[5])
			Nessai = int(params[8])
			nb_fichiers = 6*Dmax/Dstep*Nessai
			received = receive_file(s, s.recv(12).lstrip(), 12, 3)
			while (received and compteur < nb_fichiers - 1):
				received = receive_file(s, s.recv(12).lstrip(), 12, 3)
				compteur += 1
			if (received):
				#creer les dossiers
				for i in range (0, Nessai):
					os.system("mkdir essai"+str(i+1))
				#assembler les fichiers entre eux
				i = 1
				j = 1
				N = 1
				while (i < nb_fichiers/6 + 1):
					assembler([i, i+5], j, N)
					i += 1
					j += Dstep
					if (j > Dmax):
						j = 1
						N += 1
				os.system("rm *.txt")
				for D in range(1, 1+Dmax, Dstep):
					heatphases(D, Nessai, int(params[6]), int(params[7]))
				os.system("convert -delay 100 -loop 0 *.png phases-3D-logscale.gif")
				afficher(3, fenetre2)
				for i in range (0, Nessai):
					os.system("rm -rf essai"+str(i+1))
				os.system("rm -f *.png")
				if (not enregistrer):
					os.system("rm *.gif")
				else:
					os.system("cp phases-3D-logscale.gif "+rep+"/phases-3D-logscale.gif")
					if rep != os.getcwd():
						os.system("rm *.gif")
	except socket.error, e:
		print "erreur dans l'appel a une methode de la classe socket : %s"%e
		sys.exit(1)
	finally:
		s.shutdown(1)
		s.close()
	os.system("rm -f *.pyc")
	print "fin"
	return;

#########################  GESTION ENREGISTREMENTS  ############################
def enregistrer_gif_req1():
	global enregistrer_gif
	enregistrer_gif = 1
	global rep_gif
	rep_gif = askdirectory(title="Choisissez un répertoire")

def enregistrer_image():
	global enregistrer
	enregistrer = 1
	global rep
	rep = askdirectory(title="Choisissez un répertoire")

#########################  AFFICHAGE GIF REQUETE 1  ############################
def afficherGifRequete1():
	fenetrex = Tk()
	fenetrex.protocol("WM_DELETE_WINDOW", lambda: intercepte(fenetrex))
	fenetrex.resizable(width = False, height = False)
	Button(fenetrex, text="Cliquez ici pour enregistrer l'image", command=enregistrer_gif_req1).pack(side = LEFT, anchor = SW)
	Button(fenetrex, text="Fermer", command=fenetrex.destroy).pack(side=RIGHT, anchor = SE)
	fenetrex.mainloop()

############################  AFFICHAGE RESULTATS  #############################
def afficher(nb, fenetre):
	path = os.getcwd()
	fenetre.iconbitmap("@../icone.xbm")
	fenetre.resizable(width = False, height = False)
	h = fenetre.winfo_screenheight()
	w = fenetre.winfo_screenwidth()
	fenetre.title('Résultats')
	if (nb == 1):
		L = 480
		H = 510
		fenetre.geometry('%dx%d+'%(L, H) + str(w/2-L/2) + '+'+ str(h/2-H/2))
		monimage = Image.open(path+'/th.png')
		photo = ImageTk.PhotoImage(monimage)
		lab = Label(image = photo)
		lab.image=photo
		lab.pack()
	if (nb == 2):
		L = 480
		H = 510
		fenetre.geometry('%dx%d+'%(L, H) + str(w/2-L/2) + '+' + str(h/2-H/2))
		monimage = Image.open(path+'/th2.png')
		photo = ImageTk.PhotoImage(monimage)
		lab = Label(image = photo)
		lab.image=photo
		lab.pack()
	if (nb == 3):
		L = 750
		H = 630
		fenetre.geometry("%dx%d+"%(L,H) + str(w/2-L/2) + "+"+str(h/2-H/2))
		path = os.getcwd()
		image = App(fenetre, path+"/phases-3D-logscale.gif", 750, 600)
	global enregistrer
	enregistrer = 0
	global enregistrer_gif
	enregistrer_gif = 0
	Button(fenetre, text="Cliquez ici pour enregistrer l'image", command=enregistrer_image).pack(side = LEFT, anchor = SW)
	if (nb == 1):
		Button(fenetre, text="Voir Gif", command=afficherGifRequete1).pack(side=LEFT, anchor = S)
	if (nb == 3):
		fenetre.protocol("WM_DELETE_WINDOW", lambda: intercepte2(fenetre))
		boutonchiant = Button(fenetre, text="Fermer", command=lambda: intercepte2(fenetre))
		boutonchiant.pack(side=RIGHT, anchor = SE)
	else:
		fenetre.protocol("WM_DELETE_WINDOW", lambda: intercepte(fenetre))
		Button(fenetre, text="Fermer", command=fenetre.destroy).pack(side=RIGHT, anchor = SE)
	fenetre.mainloop()
	fenetre.destroy()

#########################  AFFICHAGE FENETRE ACCUEIL  ##########################
def main():
	global fenetre
	fenetre = Tk()
	f1 = Frame(fenetre).pack(padx = 1, pady = 1)
	fenetre.resizable(width = False, height = False)
	path = os.getcwd()
	fenetre.iconbitmap("@../icone.xbm")
	monimage = Image.open(path+"/../logo.png")
	photo = ImageTk.PhotoImage(monimage)
	lab = Label(image = photo)
	lab.image = photo
	lab.pack()
	fenetre.title('Osiris')
	label = Label(f1, text = "Merci de choisir la requête à envoyer", style="BW.TLabel", font = "bold").pack()
	global valueRequest
	valueRequest = IntVar()
	valueRequest.set(1)
	Radiobutton(f1, text="Realiser une simulation", variable=valueRequest, value=1).pack(anchor=W, padx=(27,8))
	Radiobutton(f1, text="Exploration parametrique (T et A0)", variable=valueRequest, value=2).pack(anchor=W, padx=(27,8))
	Radiobutton(f1, text="Exploration parametrique (T, A0 et Dmax)", variable=valueRequest, value=3).pack(anchor=W, padx=(27,8))
	valider = Button(f1, text="Valider", command=lambda: clickbutton1(1))
	valider.pack(side = LEFT, anchor = SW)
	Button(f1, text="Fermer", command=fenetre.destroy).pack(side = RIGHT, anchor = SE)
	h = fenetre.winfo_screenheight()
	w = fenetre.winfo_screenwidth()
	L = 350
	H = 185
	valider.focus_set()
	valider.bind('<Return>', clickbutton1)
	fenetre.geometry("%dx%d+"%(L, H) + str(w/2-L/2) + "+"+ str(h/2-H/2))
	fenetre.protocol("WM_DELETE_WINDOW", lambda: intercepte(fenetre))
	fenetre.mainloop()

main()
