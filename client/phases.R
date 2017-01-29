png("Diagramme_de_phase.png")

Azero = read.table("results.txt")$V1
T = read.table("results.txt")$V2
result = read.table("results.txt")$V3
plot(T,Azero,col=result+7, main="Diagramme de phases des colonies satellites", ylim=c(0,50),
     ylab="[Glucose] du milieu de culture neuf", xlab="Temps avant de repiquer la culture", pch=15, xlim=c(0,1500))
abline(h=0)
abline(h=50)
abline(v=0)
abline(v=1500)
legend(220,45, legend = c("Extinction","Exclusion","Cohabitation"), col=c(9,8,7), pch=15)


#===========================================================
