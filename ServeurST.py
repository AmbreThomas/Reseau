from socket import *
from sys import argv
import threading
from os import system

tentacle_ip = argv[1]

s = socket(AF_INET, SOCK_STREAM)
print "Disponible..."
s.connect( (tentacle_ip, 7777) )

threads = []

def proceed(s,received):
	print "New job from tentacle server."
	args = " ".split(received)
	
	#system("")
	result = "2"
	s.sendall(result)
	print "One job completed."


try:
	while 1: #tant que le sous-traitant n'est pas coupe avec Ctrl+C 
		received = s.recv(1024) 
		if received: #Accepte une demande de tentacle
			thread = threading.Thread(target=proceed, args=(s,received)) #lance un thread de calcul
			thread.start()
			threads.append(thread)
		
finally: #lorsque le sous-traitant est coupe avec Ctrl+C
	for t in threads:
		t.join()
	s.close()
	print "Server shut down."
s.close()
