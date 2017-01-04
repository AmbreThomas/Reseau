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
    elif value == 2:
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
            Label(frame, text = "Zone ?").pack()
            Entryzone = Entry(frame, textvariable=valuezone, width=30).pack()
    elif value == 3:
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
    Button(fenetre2, text="Valider", command=fenetre2.destroy).pack(side = LEFT)
    Button(fenetre2, text="Fermer", command=fenetre2.destroy).pack(side = RIGHT)
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
    label = Label(f1, text = "Merci de choisir la requête à envoyer").pack()
    valueIP = StringVar() 
    valueIP.set("000")
    valueRequest = IntVar() 
    valueRequest.set(1)
    bouton1 = Radiobutton(fenetre, text="Requête 1", variable=valueRequest, value=1).pack()
    bouton2 = Radiobutton(fenetre, text="Requête 2", variable=valueRequest, value=2).pack()
    bouton3 = Radiobutton(fenetre, text="Requête 3", variable=valueRequest, value=3).pack()
    bouton_entree=Button(fenetre, text="Valider", command=lambda: ParamRequest(valueRequest.get(), fenetre)).pack(side = LEFT)
    bouton_fermer=Button(fenetre, text="Fermer", command=fenetre.destroy).pack(side = RIGHT)
    envoyer(valueIP, valueRequest)
    fenetre.mainloop()
else :
    envoyer(sys.argv[1], sys.argv[2])
