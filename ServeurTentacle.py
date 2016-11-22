# -*- coding: utf-8 -*-
#https://pymotw.com/2/threading/ 
# https://docs.python.org/2.3/lib/semaphore-examples.html pour pool
# see http://www.programcreek.com/python/example/21025/signal.CTRL_BREAK_EVENT for breaking
# cf helio : https://duckduckgo.com/?q=global+variable+thread+python&atb=v37-5__&ia=qa&iax=1
#des daemons pour les ordi calculant ? interet ?

import socket
import threading
import time
import signal
import sys
import time


#traiter l'arrêt
def signal_handler_stop(signal, frame):
    global WorkingServ
    global WorkingComp
    if (!WorkingServ) & WorkingComp :
        print('The subcontractors stop working (Ctrl+C)')
        WorkingComp = False #pour arrêt des thread. #essayer exemple minimal...
    if WorkingServ :
        print('We do not accept new clients anymore (Ctrl+C)')
        WorkingServ = False #pour arrêt de l'écoute

#gérer la relation client
def handlerCLI(clientsock,sema,poolCLI,poolSUB):
    #on est connecté avec client
    #on a la liste des socket des sous-traitants dispo au moment de l'appel dans poolSUB
    #si trop dans le pool envoyer un message NON et d'attendre ou de réessayer
    #sinon envoyer un message OUI

    ##ICI PREMIER CONTACT AVEC CLIENT
    if poolCLI.getsize() > self.nbcli :
        #refuser, dire qu'ils vont devoir attendre.

    else :
        #dire que la connection est acceptés

    with sema:
        #on peut pas join sur tout poolSUB parce qu'il aura peut etre changé -> faire une copie maintenant.
        poolCLI.makeActive(clientsock) 
        #envoyer message indiquant qu'on commence la relation.

        #réceptionner le fichier contenant les informations à savoir

        #confirmer réception et dire cb de machies travaillent sur le sujet

        
        #on veut pouvoir arrêter tous les thread proprement si ctr+c, puis arrive à a fin de thread, et le fermer ainsi proprement.
        while WorkingComp :
            #peut-être hériter de socket pour avoir un système ou on a un lock dessus ? 
            #idee : envoyer une demande aux sous-traitants pour une nouvelle connexion ? 
        
            #ici créer de nouveaux threads pour gérer les connexions mutliples avec les sous-traitants (degré 2)
        
        pool.makeInactive(clientsock)
        #fermer la socket du client pour libérer sema

#gérer la relation subcontractors
def handlerSUB(subsock,poolCLI,poolSUB) :
    print('nouveau client...')    


#sauvegarde de socket et suivi de leur activité.
class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.size = 0
        self.lock = threading.Lock() #pour ne pas avoir d'accès simultané à l'objet
    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            self.size+=1
    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            self.size-=1
    def __str__(self):
        with self.lock:
            return(str(self.active))
    def getsize(self):
        return(self.size))

class Serveur(object) :
    def __init__(self):
        ## paramètres
        self.port1 = sys.argv[1]
        self.port2 = sys.argv[2]
        self.nbcli = sys.argv[3]
        #self.TAILLE_BLOC=1024
        self.listeClients

        ## gestion de l'arrêt
        global WorkingServ
        WorkingServ = True
        global WorkingComp
        WorkingComp = True

        ## gestion des connections (multiples)
        AllThreadCLI = []
        AllThreadSUB = []
        poolCLI = ActivePool() #les déclarer global peut-etre et mettre global dans les handler ????????
        poolSUB = ActivePool() 
        sema = BoundedSemaphore(value=self.nbcli)

        sockCLI = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockCLI.bind(('',int(self.port1)))
        sockCLI.listen(10)
        print('Listening Clients on port %d' %self.port1)

        sockSUB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockSUB.biend('',int(self.port2))
        sockSUB.listen(10)
        print('Listening Subcontractors on port %d'%self.port2)

        waiting_list = [socketCLI, socketSUB]
        while WorkingServ :
            readable, writable, errored = select.select(waiting_list,[],[]) #wait for a potential connection
            for sock in readable : 
                if sock is sockCLI :
                    clientsock, addr = sock.accept() 
                    print('A Client is conneted : %s:%d' % addr)
                    t = threading.Thread(target=handlerCLI, args=(clientsock,sema,poolCLI,poolSUB))
                    AllThreadCLI.append(t)
                    t.start()
                    print('Client currently connected are :')
                    print(poolCLI)
                elif sock is sockSUB :
                    subsock,addr = sock.accept()
                    print('A subcontractor wants to work : %s:%d' %addr)
                    t = threading.Thread(target=handlerSUB, args = (subsock,poolSUB))
                    AllThreadSUB.append(t)
                    t.start()
                    print('Subcontractors currently connected are :')
                    print(poolSUB)
            #enlever les thread obsoletes, etc.

        print('Ctrl+c pressed : no more client accepted')

        #les thread tournent encore.
        #join sur tous les thread qui devraient s'arrêter (puis fermeture de thread ?? pas la peine car fin du script )
        #(différent de fermeture de socket qui se fait dans thread)
        for t in allThread :
            t.join()
        #soit terminés naturellement, soit avec Ctrl-Break
        print('All operations over')

## main
if __name__=="__main__":
    import sys
    if len(sys.argv)<4:
        print("usage : %s <port1> <port2> <nbclients>" % (sys.argv[0],))
        sys.exit(-1)
    signal.signal(signal.SIGINT, signal_handler) #1er CTRL+C gère arrêt écoute, 2e gère arrêt clients.
    Serveur()
    
