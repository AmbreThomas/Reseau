# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
import sys
import socket
import signal
import time
import select
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
            valueIP = StringVar()
            valueIP.set("82.67.36.108")
            valuePort = StringVar()
            valuePort.set(8000)
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
            Label(frame, text = "Adresse IP hôte :").pack()
            EntryIP = Entry(frame, textvariable=valueIP, width=30).pack()
            Label(frame, text = "Port :").pack()
