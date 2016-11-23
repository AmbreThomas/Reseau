# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
import sys
import string

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
            valueD = StringVar() 
            valueD.set(0.1)
            Label(frame, text = "Valeur du coefficient de diffusion").pack()
            EntryD = Entry(frame, textvariable=valueD, width=30).pack()
    elif value == 2:
            valueD = StringVar() 
            valueD.set(0.1)
            Label(frame, text = "Valeur du coefficient de diffusion").pack()
            EntryD = Entry(frame, textvariable=valueD, width=30).pack()
    else :
            valueDmax = StringVar() 
            valueDmax.set(1)
            Label(frame, text = "Valeur du coefficient de diffusion maximum").pack()
            EntryDmax = Entry(frame, textvariable=valueDmax, width=30).pack()
    Button(fenetre2, text="Valider", command=fenetre2.destroy).pack(anchor=SW)
    Button(fenetre2, text="Fermer", command=fenetre2.destroy).pack(anchor=SE)
    return;

def envoyer(a, b):
    #largeur, hauteur (W,H) (32 par défaut)
    #A0 : concentration initiale en glucose [0,50]
    #resolA : pas sur A
    #T : temps avant repiquage [1,1500]
    #resolT : pas sur T
    #Nessais : nombre d'essais pour faire une moyenne
    #D : coef de diffusion des substrats dans le milieu (0.1)
    #photo : imprimer image de la boite ou pas ?
    #1 : ./main run W H D A0 T iterMax photo
    #2 : ./main all W H D resolT resolA zone
    #3 : ./main explore3D W H resolT resolA Dmax Dstep Nessais
    return;

try : sys.argv[1] and sys.argv[2]
except:
    fenetre = Tk()
    f1 = Frame(fenetre, borderwidth=2, relief=GROOVE)
    f1.pack(padx=1, pady=1)
    label = Label(f1, text = "Merci de choisir la requête à envoyer")
    label.pack()
    valueIP = StringVar() 
    valueIP.set("000")
    entree = Entry(fenetre, textvariable=string, width=30)
    entree.pack()
    valueRequest = IntVar() 
    valueRequest.set(0)
    bouton1 = Radiobutton(fenetre, text="Requête 1", variable=valueRequest, value=1)
    bouton2 = Radiobutton(fenetre, text="Requête 2", variable=valueRequest, value=2)
    bouton3 = Radiobutton(fenetre, text="Requête 3", variable=valueRequest, value=3)
    bouton1.pack()
    bouton2.pack()
    bouton3.pack()
    bouton_entree=Button(fenetre, text="Valider", command=lambda: ParamRequest(valueRequest.get(), fenetre))
    bouton_entree.pack(anchor=SW)
    bouton_fermer=Button(fenetre, text="Fermer", command=fenetre.destroy)
    bouton_fermer.pack(anchor=SE)
    
    envoyer(valueIP, valueRequest)
    fenetre.mainloop()
else :
    envoyer(sys.argv[1], sys.argv[2])
    
