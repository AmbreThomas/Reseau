import matplotlib.pyplot as plt
from numpy import *
from sys import argv

#=================== Syntax of the command: ============================
# > python heatphases.py D Nessais resolT resolA

D = int(argv[1])
N = int(argv[2])
resolT = int(argv[3])
resolA = int(argv[4])
ncol = 1500/resolT
nrow = 51/resolA

print "D:",D
print "Nessais:", N
print "resolT:", resolT
print "resolA:", resolA

#=================== Parsing files =====================================
data = []
print "\nouverture de %d fichiers..."%N
for i in xrange(1,N+1):
  file_list = open("essai%d/results-D%f.txt"%(i,10**(-D)))
  data.append(file_list.readlines())
  file_list.close()

matrix = zeros((nrow+1, ncol+1))
print "> OK"

#=================== Creating the mean =================================

print "\nmixing the %d runs..."%N
for point in xrange(len(data[0])):
  l = []
  for essai in xrange(N):
    l.append( data[essai][point].split(' ') )
  matrix[ int(l[0][0])/resolA, int(l[0][1])/resolT] = sum([ int(l[k][2]) for k in xrange(N) ])/float(N)
print "> OK"

#=================== Creating the heatmap ==============================

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
plt.ylim(0,50)
plt.xlabel("Temps avant de repiquer la culture")
plt.ylabel("[Glucose] initiale")
print "saving %d.png..."%D
plt.savefig("%d.png"%D)
print "\n> Done."

