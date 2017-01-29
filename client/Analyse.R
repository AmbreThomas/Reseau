png("Resultats_simulation.png")

meanAinA = read.table("mean-A-in-A.txt")$V1
meanBinA = read.table("mean-B-in-A.txt")$V1
meanCinA = read.table("mean-C-in-A.txt")$V1
meanAinB = read.table("mean-A-in-B.txt")$V1
meanBinB = read.table("mean-B-in-B.txt")$V1
meanCinB = read.table("mean-C-in-B.txt")$V1
meanAout = read.table("mean-A-out.txt")$V1
meanBout = read.table("mean-B-out.txt")$V1
meanCout = read.table("mean-C-out.txt")$V1
totalA = meanAinA+meanAinB+meanAout
totalB = meanBinA+meanBinB+meanBout
totalC = meanCinA+meanCinB+meanCout
inteA = meanAinA+meanBinA+meanCinA
inteB = meanAinB+meanBinB+meanCinB
exte = meanAout+meanBout+meanCout
A = read.table("mean-life-A.txt")$V1
B = read.table("mean-life-B.txt")$V1

x = 1:length(meanAinA)
par(mfrow=c(2,2))

plot(x, meanAinA, main="Concentrations bactériennes chez A",
     xlab = "temps", ylab = "Concentration moyenne",
     type='l',col=2, ylim=c(0,meanAout[1]+1))
lines(x, meanBinA, type='l', col=3)
lines(x, meanCinA, type='l', col=4)
abline(v=0)
abline(h=0)
abline(h=0.001, lty=2)
legend("topleft", legend=c("[Glc]","[Acétate]","[Ethanol]"), col=c(2,3,4), lty=1)



plot(x, meanAinB, main="Concentrations bactériennes chez B",
     xlab = "temps", ylab = "Concentration moyenne",
     type='l',col=2, ylim=c(0,meanAout[1]+1))
lines(x, meanBinB, type='l', col=3)
lines(x, meanCinB, type='l', col=4)
abline(v=0)
abline(h=0)
abline(h=0.001, lty=2)
legend("topleft", legend=c("[Glc]","[Acétate]","[Ethanol]"), col=c(2,3,4), lty=1)


plot(x, meanAout, main="Concentrations du milieu",
     xlab = "temps", ylab = "Concentration moyenne",
     type='l',col=2, ylim=c(0,meanAout[1]+1))
abline(h=meanAout[1], lty=2)
abline(v=0)
abline(h=0)
lines(x, meanBout, type='l', col=3)  
lines(x, meanCout, type='l', col=4)



plot(x, A, main="Population bactérienne",
     xlab = "temps", ylab = "Nombre d'individus",
     type='l', col=2, ylim=c(0,1024))
lines(x,B, type='l', col=4)
lines(x,A+B, type='l')
abline(h=0)
abline(v=0)
legend("bottomleft", legend=c("génome A","génome B","Total"),
       col=c(2,4,1), lty=1)
abline(h=1024, lty=2)
