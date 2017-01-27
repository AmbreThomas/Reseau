# -*- coding: utf-8 -*-
from Tkinter import *
from tkMessageBox import *
import sys
import socket
import os
import string
import signal
from PIL import Image, ImageTk
import time
import select

tentacle_ip = "127.0.0.1"

global enregistrer;

def geoliste(g):
	r = [i for i in range (0, len(g)) if not g[i].isdigit()]
	return [int(g[0:r[0]]), int(g[r[0]+1:r[1]])]

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
		if (len(r) < max_size):
		    r = r + newSocket.recv(max_size - len(r))
		output.append(r+'\n')
		if not r: break
	fichier = open(filename, "w")
	fichier.writelines(output)
	fichier.close()
	clean_file(filename)
	return r

def add_file(newSocket, max_size, fichier):
	print "reception de fichier..."
	r = ""
	output = []
	while "fin." not in r:
		r = newSocket.recv(max_size)
		if (len(r) < max_size):
			r = r + newSocket.recv(max_size - len(r))
		output.append(r+'\n')
		if not r: break
	fichier.writelines(output)
	return r

def ParamRequest(value, fen):
    fen.destroy()
    fenetre2 = Tk()
    frame = Frame(fenetre2, borderwidth=2, relief=GROOVE).pack(padx=1, pady=1)
    Label(frame, text = "Merci de rentrer les paramètres de la simulation").pack()
    valueLargeur = StringVar() 
    valueLargeur.set(32)
    valueHauteur = StringVar() 
    valueHauteur.set(32)
    Label(frame, text = "Hauteur de la boîte").pack()
    EntryHauteur = Entry(frame, textvariable=valueHauteur, width=30).pack()
    Label(frame, text = "Largeur de la boîte").pack()
    EntryLargeur = Entry(frame, textvariable=valueLargeur, width=30).pack()
    if value == 1:
            fenetre2.title("Realiser une simulation")
            valueD = StringVar()
            valueD.set(0.1)
            valueA0 = StringVar() 
            valueA0.set(20)
            valueT = StringVar() 
            valueT.set(500)
            valueiterMax = StringVar() 
            valueiterMax.set(10000)
            Label(frame, text = "Valeur du coefficient de diffusion").pack()
            EntryD = Entry(frame, textvariable=valueD, width=30).pack()
            Label(frame, text = "Valeur de la concentration initiale en glucose").pack()
            EntryA0 = Entry(frame, textvariable=valueA0, width=30).pack()
            Label(frame, text = "Intervalle de temps entre les repiquages").pack()
            EntryT = Entry(frame, textvariable=valueT, width=30).pack()
            Label(frame, text = "Durée de l'expérience").pack()
            EntryiterMax = Entry(frame, textvariable=valueiterMax, width=30).pack()
            Button(fenetre2, text="Valider", command=lambda: envoyer("./main run "+valueLargeur.get()+" "+valueHauteur.get()+" "+valueD.get()+" "+valueA0.get()+" "+valueT.get()+" "+valueiterMax.get()+" 0", fenetre2)).pack(side = LEFT)
            Button(fenetre2, text="Fermer", command=fenetre2.destroy).pack(side = RIGHT)
    elif value == 2:
            fenetre2.title("Exploration parametrique (T et A0)")
            valueD = StringVar() 
            valueD.set(0.1)
            valueA0 = StringVar() 
            valueA0.set(5)
            valueT = StringVar() 
            valueT.set(5)
            valuezone = StringVar() 
            valuezone.set("???")
            Label(frame, text = "Valeur du coefficient de diffusion").pack()
            EntryD = Entry(frame, textvariable=valueD, width=30).pack()
            Label(frame, text = "Intervalle de concentration en glucose à tester(entre 0 et 50)").pack()
            EntryA0 = Entry(frame, textvariable=valueA0, width=30).pack()
            Label(frame, text = "Intervalle de temps entre les repiquages à tester (entre 1 et 1500)").pack()
            EntryT = Entry(frame, textvariable=valueT, width=30).pack()
            Button(fenetre2, text="Valider", command=lambda: envoyer("./main all "+valueLargeur.get()+" "+valueHauteur.get()+" "+valueD.get()+" "+valueA0.get()+" "+valueT.get(), fenetre2)).pack(side = LEFT)
            Button(fenetre2, text="Fermer", command=fenetre2.destroy).pack(side = RIGHT)
    elif value == 3:
            fenetre2.title("Exploration parametrique (T, A0 et Dmax)")
            valueDmax = StringVar() 
            valueDmax.set(1)
            valueDstep = StringVar() 
            valueDstep.set(0.1)
            valueA0 = StringVar() 
            valueA0.set(5)
            valueT = StringVar() 
            valueT.set(5)
            valueNessai = StringVar() 
            valueNessai.set(10)
            Label(frame, text = "Valeur du coefficient de diffusion maximum").pack()
            EntryDmax = Entry(frame, textvariable=valueDmax, width=30).pack()
            Label(frame, text = "Intervalle des coefficients de diffusion à tester").pack()
            EntryDstep = Entry(frame, textvariable=valueDstep, width=30).pack()
            Label(frame, text = "Intervalle de concentration en glucose à tester").pack()
            EntryA0 = Entry(frame, textvariable=valueA0, width=30).pack()
            Label(frame, text = "Intervalle de temps entre les repiquages à tester").pack()
            EntryT = Entry(frame, textvariable=valueT, width=30).pack()
            Label(frame, text = "Nombres d'essais à réaliser").pack()
            EntryNessai = Entry(frame, textvariable=valueNessai, width=30).pack()
            Button(fenetre2, text="Valider", command=lambda: envoyer("./main explore3D "+valueLargeur.get()+" "+valueHauteur.get()+" "+valueDmax.get()+" "+valueDstep.get()+" "+valueA0.get()+" "+valueT.get()+" "+valueNessai.get(), fenetre2)).pack(side = LEFT)
            Button(fenetre2, text="Fermer", command=fenetre2.destroy).pack(side = RIGHT)
    return;

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C !'

def envoyer(params, fenetre):
    fenetre.destroy()
    fenetre2=Tk()
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
    	popup = showinfo("", "Les calculs sont prêts à être effectués. Cliquez sur OK pour continuer.")
        s.sendall(params)
 	if "run" in params:
		received = receive_file(s, "mean-life-A.txt", 12)
		if received: received = receive_file(s,"mean-life-B.txt", 12)
		if received: received = receive_file(s,"mean-A-in-A.txt", 12)
		if received: received = receive_file(s,"mean-A-in-B.txt", 12)
		if received: received = receive_file(s,"mean-B-in-A.txt", 12)
		if received: received = receive_file(s,"mean-B-in-B.txt", 12)
		if received: received = receive_file(s,"mean-C-in-A.txt", 12)
		if received: received = receive_file(s,"mean-C-in-B.txt", 12)
		if received: received = receive_file(s,"mean-A-out.txt", 12)
		if received: received = receive_file(s,"mean-B-out.txt", 12)
		if received: received = receive_file(s,"mean-C-out.txt", 12)
		if received:
			os.system("Rscript Analyse.R")
		afficher(1, fenetre2)
		os.system("rm *.txt")
		global enregistrer
		if (not enregistrer):
			os.system("rm th.png")
        if "all" in params:
		fichier = open("results.txt", "w")
		received = add_file(s, 12, fichier)
		i = 1
		while (received and i < 6):
		        received = add_file(s, 12, fichier)
			i += 1
		fichier.close()
		if (received):
			os.system("Rscript phases.R")
		afficher(2, fenetre2)
		os.system("rm *.txt")
		global enregistrer
		if (not enregistrer):
			os.system("rm th2.png")
    except socket.error, e:
        print "erreur dans l'appel a une methode de la classe socket : %s"%e
        sys.exit(1)
    finally:
        s.shutdown(1)
        s.close()
    print "fin"
    return;

def afficher(nb, fenetre):
    path = os.getcwd()
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
    global enregistrer
    enregistrer = 0
    Button(fenetre, text="Cliquez ici pour enregistrer l'image", command=enregistrer_image).pack(side = LEFT)
    Button(fenetre, text="Fermer", command=fenetre.destroy).pack(side = RIGHT)
    fenetre.mainloop()

def enregistrer_image():
	global enregistrer
	enregistrer = 1

def main():
    fenetre = Tk()
    f1 = Frame(fenetre).pack(padx = 1, pady = 1)
    fenetre.title('')
    label = Label(f1, text = "Merci de choisir la requête à envoyer").pack()
    valueRequest = IntVar()
    valueRequest.set(1)
    Radiobutton(f1, text="Realiser une simulation", variable=valueRequest, value=1).pack(anchor=W)
    Radiobutton(f1, text="Exploration parametrique (T et A0)", variable=valueRequest, value=2).pack(anchor=W)
    Radiobutton(f1, text="Exploration parametrique (T, A0 et Dmax)", variable=valueRequest, value=3).pack(anchor=W)
    Button(f1, text="Valider", command=lambda: ParamRequest(valueRequest.get(), fenetre)).pack(side = LEFT)
    Button(f1, text="Fermer", command=fenetre.destroy).pack(side = RIGHT)
    L, H = geoliste(fenetre.geometry())
    h = fenetre.winfo_screenheight()
    w = fenetre.winfo_screenwidth()
    L = 350
    H = 150
    fenetre.geometry("%dx%d+"%(L, H) + str(w/2-L/2) + "+"+ str(h/2-H/2))
    fenetre.mainloop()

main()
