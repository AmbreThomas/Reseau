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
    case (7): Tmin = 1; Tmax = 1500; break;
  }

  cout << "W: " << W << endl;
  cout << "H: " << H << endl;
  cout << "D: " << D << endl;
  cout << "Amin: " << Amin << endl;
  cout << "Amax: " << Amax << endl;
  cout << "Astep: " << resolA << endl;
  cout << "Tmin: " << Tmin << endl;
  cout << "Tmax: " << Tmax << endl;
  cout << "Tstep: " << resolT << endl;

  for (double Azero=Amin; Azero<Amax+1; Azero+= resolA){
    //~ int Tmin = 5.0*(Azero+150.0);
    //~ int Tmax = 5.0*(Azero+225.0);

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
  cout << "W: " << W << endl;
  cout << "H: " << H << endl;
  cout << "D: " << D << endl;
  cout << "A0: " << Azero << endl;
  cout << "T: " << T << endl;
  cout << "itermax: " << iterMax << endl;
  cout << "photo: " << photo << endl;

  while (Petri.isAlive() and iter<iterMax and not Petri.isFixed()){
    if (iter > 0 and iter%T==0){
      Petri.renew(Azero);
      cout << iter << ": repiquage !"  << endl;
    }

    Petri.diffuse();
    Petri.nagasaki();
    Petri.refill();
    Petri.eat();

    if (photo>0 and iter > 0 and iter%photo == 0){
      string num = to_string(iter);
      if (iter<10) num = "0"+num;
      if (iter<100) num = "0"+num;
      if (iter<1000) num = "0"+num;

      Petri.visualize_A_out("Aout-"+num+".ppm", Azero);
      //~ Petri.visualize_B_out("Bout-"+num+".ppm", Azero);
      //~ Petri.visualize_C_out("Cout-"+num+".ppm", Azero);
      //~ Petri.visualize_A_in("Ain-"+num+".ppm", Azero);
      //~ Petri.visualize_B_in("Bin-"+num+".ppm", Azero);
      //~ Petri.visualize_C_in("Cin-"+num+".ppm", Azero);
      //~ Petri.visualize_life("life-"+num+".ppm");
      Petri.visualize_genome("cells-"+num+".ppm");
      //~ Petri.visualize_fitness("fitness-"+num+".ppm", Azero);

    }

    Petri.study_data();
    iter++;
  }

  cout << "Azero: " << Azero << " ; T: " << T;
  if (not(Petri.isAlive())) cout << " >> Mort des deux souches.";
  if (Petri.isFixed()) cout << " >> Fixation de la population A";
  if (Petri.isAlive() and not Petri.isFixed()) cout << " >> Cohabitation !";
  cout << endl;

  if (photo>0){
    cout << "creating .gif..." << endl;
    success += system("convert -delay 20 -loop 0 Aout-*.ppm Aout.gif");
    //~ success += system("convert -delay 20 -loop 0 Bout-*. Bout.gif");
    //~ success += system("convert -delay 20 -loop 0 Cout-*.ppm Cout.gif");
    //~ success += system("convert -delay 20 -loop 0 Ain-*.ppm Ain.gif");
    //~ success += system("convert -delay 20 -loop 0 Bin-*.ppm Bin.gif");
    //~ success += system("convert -delay 20 -loop 0 Cin-*.ppm Cin.gif");
    //~ success += system("convert -delay 20 -loop 0 life-*.ppm life.gif");
    success += system("convert -delay 20 -loop 0 cells-*.ppm cells.gif");
    //~ success += system("convert -delay 20 -loop 0 fitness-*.ppm fitness.gif");
    success += system("rm *.ppm");
  }

  exit(success);
}

int main(int argc, char* argv[]){

  srand(time(NULL));
  int success = EXIT_SUCCESS;

  //======================= checking args ==============================

  string All("all");
  string Run("run");
  string Arg(argv[1]);

  if (Arg==All) {
    int W = 32;
    int H = 32;
    double D = 0.1;
    int Amin = 0;
    int Amax = 50;
    int resolT = 20;
    int resolA = 1;
    int zone =7;

    if (argc<7){
      cout << "./main all W H D resolT resolA zone" << endl;
      cout << "using default parameters." << endl;
    }
    else {
      W = atoi(argv[2]);
      H = atoi(argv[3]);
      D = atof(argv[4]);
      resolT = atoi(argv[5]);
      resolA = atoi(argv[6]);
      zone = atoi(argv[7]);
    }

    explore_params(W,H,D,Amin,Amax,resolT,resolA, zone);
  }

  if (Arg==Run) {
    int W = 32;
    int H = 32;
    double D = 0.1;
    double Azero = 20;
    unsigned int T = 500;
    size_t iterMax = 10000;
    size_t photo = 0;

    if (argc<8){
      cout << "./main run W H D A0 T iterMax photo" << endl;
      cout << "using default parameters:" << endl;
    }
    else {
      W = atoi(argv[2]);
      H = atoi(argv[3]);
      D = atof(argv[4]);
      Azero = atof(argv[5]);
      T = atoi(argv[6]);
      iterMax = atoi(argv[7]);
      photo = atoi(argv[8]);
    }

    run(W,H,D,Azero,T,iterMax,photo);
  }

  return EXIT_SUCCESS;
}
