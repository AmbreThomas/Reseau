all: main

main: main.o Box.o Ecoli.o
	g++ -g -O4 -o main main.o Ecoli.o Box.o --std=c++11
	mv main ../main

main.o: main.cpp
	g++ -g -O4 -c -o main.o main.cpp --std=c++11

Box.o: Box.cpp Box.h
	g++ -g -O4 -c -o Box.o Box.cpp --std=c++11

Ecoli.o: Ecoli.cpp Ecoli.h
	g++ -g -O4 -c -o Ecoli.o Ecoli.cpp --std=c++11

clean:
	rm *.o *.gif  Rplots.pdf mean*.txt
