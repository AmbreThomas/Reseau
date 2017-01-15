# -*- coding: utf-8 -*-
from Tkinter import *
from tkMessageBox import *
import sys
import socket
import string
import signal
import time
import select

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
            valueA0.set(0.1)
            valueT = StringVar() 
            valueT.set(100)
            valueiterMax = StringVar() 
            valueiterMax.set(1000)
            Label(frame, text = "Valeur du coefficient de diffusion").pack()
            EntryD = Entry(frame, textvariable=valueD, width=30).pack()
            Label(frame, text = "Valeur de la concentration initiale en glucose").pack()
            EntryA0 = Entry(frame, textvariable=valueA0, width=30).pack()
            Label(frame, text = "Intervalle de temps entre les repiquages").pack()
            EntryT = Entry(frame, textvariable=valueT, width=30).pack()
            Label(frame, text = "Durée de l'expérience").pack()
            EntryiterMax = Entry(frame, textvariable=valueiterMax, width=30).pack()
            Button(fenetre2, text="Valider", command=lambda: envoyer("./main run "+valueLargeur.get()+" "+valueHauteur.get()+" "+valueD.get()+" "+valueA0.get()+" "+valueT.get()+" "+valueiterMax.get(), fenetre2)).pack(side = LEFT)
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
            Label(frame, text = "Intervalle de concentration en glucose à tester").pack()
            EntryA0 = Entry(frame, textvariable=valueA0, width=30).pack()
            Label(frame, text = "Intervalle de temps entre les repiquages à tester").pack()
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
"""
def requestIP(params, fenetre2):
    fenetre2.destroy()
    fenetre3 = Tk()
    fenetre3.title('')
    frame = Frame(fenetre3, borderwidth=2, relief=GROOVE).pack(padx=1, pady=1)
    Label(frame, text = "Merci de rentrer votre adresse IP").pack()
    valueIP = StringVar() 
    valueIP.set("000")
    EntryIP = Entry(frame, textvariable=valueIP, width=30).pack()
    Button(fenetre3, text="Valider", command=lambda: envoyer(params, valueIP.get())).pack(side = LEFT)
    Button(fenetre3, text="Fermer", command=fenetre3.destroy).pack(side = RIGHT)
    return;
"""
def signal_handler(signal, frame):
    print 'You pressed Ctrl+C !'

def envoyer(params, fenetre):
    fenetre.destroy()    
    signal.signal(signal.SIGINT, signal_handler)
    print 'Press Ctrl+C pour arreter le client'
    params = params
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect(("134.214.159.33", 6666))
        print s.recv(255)
        s.sendall(params)
        print s.recv(255)
    except socket.error, e:
        print "erreur dans l'appel a une methode de la classe socket : %s"%e
        sys.exit(1)
    finally:
        s.shutdown(1)
        s.close()
    print "fin"
    return;

def main():
    fenetre = Tk()
    f1 = Frame(fenetre, bg='purple', borderwidth=2, relief=GROOVE)
    f1.pack(padx=1, pady=1)
    fenetre.title('')
    label = Label(f1, text = "Merci de choisir la requête à envoyer").pack()
    valueRequest = IntVar() 
    valueRequest.set(1)
    Radiobutton(fenetre, text="Realiser une simulation", variable=valueRequest, value=1).pack(anchor=W)
    Radiobutton(fenetre, text="Exploration parametrique (T et A0)", variable=valueRequest, value=2).pack(anchor=W)
    Radiobutton(fenetre, text="Exploration parametrique (T, A0 et Dmax)", variable=valueRequest, value=3).pack(anchor=W)
    Button(fenetre, text="Valider", command=lambda: ParamRequest(valueRequest.get(), fenetre)).pack(side = LEFT)
    Button(fenetre, text="Fermer", command=fenetre.destroy).pack(side = RIGHT)
    fenetre.mainloop()

main()