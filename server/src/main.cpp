#include <ctime>
#include "Ecoli.h"
#include "Box.h"

using namespace std;

void explore_params(int W, int H, double& D, int Amin, int Amax, int resolT, int resolA, int zone){

  int success = EXIT_SUCCESS;

  int Tmin;
  int Tmax;

  switch (zone){
    case (1): Tmin = 1; Tmax = 250; break;
    case (2): Tmin = 251; Tmax = 500; break;
    case (3): Tmin = 501; Tmax = 750; break;
    case (4): Tmin = 751; Tmax = 1000; break;
    case (5): Tmin = 1001; Tmax = 1250; break;
    case (6): Tmin = 1251; Tmax = 1500; break;
  }

  for (double Azero=Amin; Azero<Amax+1; Azero+= resolA){
    for (unsigned int T=Tmin; T<Tmax+1; T+= resolT){

      Box Petri = Box(W,H,D,Azero);
      size_t iter = 1;

      while (Petri.isAlive() and iter<10000){
        if (iter%T==0) Petri.renew(Azero);
        Petri.diffuse();
        Petri.nagasaki();
        Petri.refill();
        Petri.eat();
        iter++;
      }

      ofstream f;
      f.open("results.txt", ios::out | ios::app);
      f << Azero << " " << T << " ";
      f << not Petri.isAlive() << Petri.isFixed() << endl;
      f.close();

    }
  }
}

void run(int W, int H, double D, double Azero, int T, size_t iterMax, size_t photo){

  int success = EXIT_SUCCESS;
  Box Petri = Box(W,H,D,Azero);
  size_t iter = 1;

  while (Petri.isAlive() and iter<iterMax and not Petri.isFixed()){

    if (iter > 0 and iter%T==0) Petri.renew(Azero);
    Petri.diffuse();
    Petri.nagasaki();
    Petri.refill();
    Petri.eat();

    if (photo>0 and iter > 0 and iter%10 == 0){
      string num = to_string(iter);
      if (iter<10) num = "0"+num;
      if (iter<100) num = "0"+num;
      if (iter<1000) num = "0"+num;
      switch (photo){
        case (1): Petri.visualize_A_out("Aout-"+num+".ppm", Azero); break;
        case (2): Petri.visualize_B_out("Bout-"+num+".ppm", Azero); break;
        case (3): Petri.visualize_C_out("Cout-"+num+".ppm", Azero); break;
        case (4): Petri.visualize_A_in("Ain-"+num+".ppm", Azero); break;
        case (5): Petri.visualize_B_in("Bin-"+num+".ppm", Azero); break;
        case (6): Petri.visualize_C_in("Cin-"+num+".ppm", Azero); break;
        case (7): Petri.visualize_life("life-"+num+".ppm"); break;
        case (8): Petri.visualize_genome("cells-"+num+".ppm"); break;
        case (9): Petri.visualize_fitness("fitness-"+num+".ppm", Azero); break;
      }
    }

    Petri.study_data();
    iter++;
  }

  if (photo>0){ 
    string command;
    switch (photo){
      case (1): command = "convert -scale " + to_string(60000.0/(float) H)+"% -delay 20 -loop 0 Aout-*.ppm result.gif"; break;
      case (2): command = "convert -scale " + to_string(60000.0/(float) H)+"% -delay 20 -loop 0 Bout-*.ppm result.gif"; break;
      case (3): command = "convert -scale " + to_string(60000.0/(float) H)+"% -delay 20 -loop 0 Cout-*.ppm result.gif"; break;
      case (4): command = "convert -scale " + to_string(60000.0/(float) H)+"% -delay 20 -loop 0 Ain-*.ppm result.gif"; break;
      case (5): command = "convert -scale " + to_string(60000.0/(float) H)+"% -delay 20 -loop 0 Bin-*.ppm result.gif"; break;
      case (6): command = "convert -scale " + to_string(60000.0/(float) H)+"% -delay 20 -loop 0 Cin-*.ppm result.gif"; break;
      case (7): command = "convert -scale " + to_string(60000.0/(float) H)+"% -delay 20 -loop 0 life-*.ppm result.gif"; break;
      case (8): command = "convert -scale " + to_string(60000.0/(float) H)+"% -delay 20 -loop 0 cells-*.ppm result.gif"; break;
      case (9): command = "convert -scale " + to_string(60000.0/(float) H)+"% -delay 20 -loop 0 fitness-*.ppm result.gif"; break;
    }
    success += system( command.c_str() );
    if (success != EXIT_SUCCESS) exit(success);
    success += system("rm *.ppm");
  }

  exit(success);
}

int main(int argc, char* argv[]){

  srand(time(NULL));
  int success = EXIT_SUCCESS;

  string All("all");
  string Run("run");
  string Arg(argv[1]);

  if (Arg==All) {
    int Amin = 0;
    int Amax = 50;
    int W = atoi(argv[2]);
    int H = atoi(argv[3]);
    double D = atof(argv[4]);
    int resolT = atoi(argv[5]);
    int resolA = atoi(argv[6]);
    int zone = atoi(argv[7]);
    explore_params(W,H,D,Amin,Amax,resolT,resolA, zone);
  }

  if (Arg==Run) {
    int W = atoi(argv[2]);
    int H = atoi(argv[3]);
    double D = atof(argv[4]);
    double Azero = atof(argv[5]);
    unsigned int T = atoi(argv[6]);
    size_t iterMax = atoi(argv[7]);
    size_t photo = atoi(argv[8]);
    run(W,H,D,Azero,T,iterMax,photo);
  }

  return EXIT_SUCCESS;
}
