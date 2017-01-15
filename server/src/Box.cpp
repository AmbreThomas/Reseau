
//=========================== Includes =================================

#include "Box.h"

//=========================== Constructors =============================

Box::Box(void){
  W_ = 0;
  H_ = 0;
  D_ = 0.1;
  Ainit_ = 0;
  population = nullptr;
  CA_ = nullptr;
  CB_ = nullptr;
  CC_ = nullptr;
}

Box::Box(int W, int H, double D, double Ainit){
  W_ = W;
  H_ = H;
  D_ = D;
  Ainit_ = Ainit;
  population = new Ecoli*[W_];
  for(size_t i=0; i<W_; i++){
    population[i] = new Ecoli[H_];
    for(size_t j=0; j<H_; j++){
      population[i][j] = Ecoli();
    }
  }
  CA_ = new double*[W_];
  for(size_t i=0; i<W_; i++){
    CA_[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      CA_[i][j] = Ainit_;
    }
  }
  CB_ = new double*[W_];
  for(size_t i=0; i<W_; i++){
    CB_[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      CB_[i][j] = 0;
    }
  }
  CC_ = new double*[W_];
  for(size_t i=0; i<W_; i++){
    CC_[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      CC_[i][j] = 0;
    }
  }
}

//=========================== Destructor ===============================

Box::~Box(void){
  for(size_t i=0; i<W_; i++){
    delete[] population[i];
  }
  delete[] population;
  for(size_t i=0; i<W_; i++){
    delete[] CA_[i];
  }
  delete[] CA_;
  for(size_t i=0; i<W_; i++){
    delete[] CB_[i];
  }
  delete[] CB_;
  for(size_t i=0; i<W_; i++){
    delete[] CC_[i];
  }
  delete[] CC_;
}

//=========================== Public Methods ===========================

void Box::diffuse(void){
  double** newCA_ = new double*[W_];
  double** newCB_ = new double*[W_];
  double** newCC_ = new double*[W_];
  
  for(size_t x=0; x<W_; x++){
    newCA_[x] = new double[H_];
    newCB_[x] = new double[H_];
    newCC_[x] = new double[H_];
    for(size_t y=0; y<H_; y++){
      
      //This does not deal with diffusion but is practical here:
      population[x][y].sleep();
      
      newCA_[x][y] = CA_[x][y];
      newCB_[x][y] = CB_[x][y];
      newCC_[x][y] = CC_[x][y];
      
      for(int i=-1; i<2; i++){
        for(int j=-1; j<2; j++){
          int a = (W_+x+i)%W_;
          int b = (H_+y+j)%H_;
          newCA_[x][y] += D_ * CA_[a][b];
          newCB_[x][y] += D_ * CB_[a][b];
          newCC_[x][y] += D_ * CC_[a][b];
        }
      }
      newCA_[x][y] -= 9.0 * D_ * CA_[x][y];
      newCB_[x][y] -= 9.0 * D_ * CB_[x][y];
      newCC_[x][y] -= 9.0 * D_ * CC_[x][y];
    }
  }
  
  for(size_t i=0; i<W_; i++){
    delete[] CA_[i];
    delete[] CB_[i];
    delete[] CC_[i];
  }
  delete[] CA_;
  delete[] CB_;
  delete[] CC_;
  
  CA_ = newCA_;
  CB_ = newCB_;
  CC_ = newCC_;
}

void Box::nagasaki(void){
  for(size_t i=0; i<W_; i++){
    for(size_t j=0; j<H_; j++){
      if (rand()/(double)RAND_MAX< Ecoli::Pdeath_ and population[i][j].alive()) {
        CA_[i][j] += population[i][j].A();
        CB_[i][j] += population[i][j].B();
        CC_[i][j] += population[i][j].C();
        population[i][j].kill();
      }
    }
  }
}

void Box::pop(int x, int y){
  double w_max = Ecoli::Wmin_;
  
  int a;
  int b;
  int i;
  int j;
  
  // Looks for the best fitness in the neighborhood:
  for(i=-1; i<2; i++){
    for(j=-1; j<2; j++){
      a = (W_ + x + i)%W_;
      b = (H_ + y + j)%H_;
      if ( !population[a][b].cold() ){
        double fitw = population[a][b].fitness();
        if (fitw > w_max){ w_max = fitw; }
      }
    }
  }
  
  // Gets the list of candidates for division:
  vector<int> listX;
  vector<int> listY;
  for(int i=-1; i<2; i++){
    for(int j=-1; j<2; j++){
      int a = (W_ + x + i)%W_;
      int b = (H_ + y + j)%H_;
      if (population[a][b].fitness() == w_max and not population[a][b].cold() ){
        listX.push_back(a);
        listY.push_back(b);
      }
    }
  }
  
  if (listX.size() > 0) {
    int choice = rand()%(listX.size());
    int posX = listX[choice];
    int posY = listY[choice];
    
    population[posX][posY].divide_to( population[x][y] );
  }
}

void Box::refill(void){
  vector<int> Xgaps;
  vector<int> Ygaps;
  for(size_t i=0; i<W_; i++){
    for(size_t j=0; j<H_; j++){
      if (not population[i][j].alive() and not population[i][j].cold() ){
        Xgaps.push_back(i);
        Ygaps.push_back(j);
      }
    }
  }
  vector<int> order;
  for (size_t i=0; i<Xgaps.size(); i++){ order.push_back(i); }
  random_shuffle( order.begin(), order.end() );
  for (size_t i=0; i<order.size(); i++){
    this->pop(Xgaps[order[i]], Ygaps[order[i]]);
  }
}

void Box::eat(void){
  for (size_t i=0; i<W_; i++){
    for (size_t j=0; j<H_; j++){
      if (population[i][j].alive()){
        exchange(CA_[i][j],CB_[i][j],population[i][j]);
      }
    }
  }
}

void Box::exchange(double& CA, double& CB, Ecoli& cell ){
  double A = cell.A();
  double B = cell.B();
  double C = cell.C();
  
  if (cell.genome()){
    for (int t=0; t<10; t++){
      C += 0.1*B*Ecoli::RBC_;
      B += 0.1*(CB*Ecoli::RBB_ - B*Ecoli::RBC_);
      CB -= 0.1*CB*Ecoli::RBB_;
    }
    
    cell.setC(C);
    cell.setB(B);
  }
  else {
    for (int t=0; t<10; t++){
      B += 0.1*A*Ecoli::RAB_;
      A += 0.1*(CA*Ecoli::RAA_ - A*Ecoli::RAB_);
      CA -= 0.1*CA*Ecoli::RAA_;
    }
    
    cell.setA(A);
    cell.setB(B);
  }
  
}

void Box::renew(double Azero){
  for(unsigned int i=0; i<W_; i++){
    for(unsigned int j=0; j<H_; j++){
      CA_[i][j] = Azero;
      CB_[i][j] = 0;
      CC_[i][j] = 0;
    }
  }
}

void Box::visualize_life(string filename){
  double** life = new double*[W_];
  for(size_t i=0; i<W_; i++){
    life[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      life[i][j] = population[i][j].alive();
    }
  }
  
  save_image(life, "fitness", filename);
  
  for(size_t i=0; i<W_; i++){
    delete[] life[i];
  }
  delete[] life;
}

void Box::visualize_A_out(string filename, double max){
  double** map_A = new double*[W_];
  for(size_t i=0; i<W_; i++){
    map_A[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      map_A[i][j] = CA_[i][j]/ max;
    }
  }
  
  save_image(map_A, "A", filename);
  
  for(size_t i=0; i<W_; i++){
    delete[] map_A[i];
  }
  delete[] map_A;
}

void Box::visualize_B_out(string filename, double max){
  double** map_B = new double*[W_];
  for(size_t i=0; i<W_; i++){
    map_B[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      map_B[i][j] = CB_[i][j] / max;
    }
  }
    
  save_image(map_B, "B", filename);
  
  for(size_t i=0; i<W_; i++){
    delete[] map_B[i];
  }
  delete[] map_B;
}

void Box::visualize_C_out(string filename, double max){
  double** map_C = new double*[W_];
  for(size_t i=0; i<W_; i++){
    map_C[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      map_C[i][j] = CC_[i][j] / max;
    }
  }
    
  save_image(map_C, "C", filename);
  
  for(size_t i=0; i<W_; i++){
    delete[] map_C[i];
  }
  delete[] map_C;
}

void Box::visualize_A_in(string filename, double max){
  double** map_A = new double*[W_];
  for(size_t i=0; i<W_; i++){
    map_A[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      map_A[i][j] = population[i][j].A()/max;
    }
  }
    
  save_image(map_A, "A", filename);
  
  for(size_t i=0; i<W_; i++){
    delete[] map_A[i];
  }
  delete[] map_A;
}

void Box::visualize_B_in(string filename, double max){
  double** map_B = new double*[W_];
  for(size_t i=0; i<W_; i++){
    map_B[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      map_B[i][j] = population[i][j].B() / max;
    }
  }
    
  save_image(map_B, "B", filename);
  
  for(size_t i=0; i<W_; i++){
    delete[] map_B[i];
  }
  delete[] map_B;
}

void Box::visualize_C_in(string filename, double max){
  double** map_C = new double*[W_];
  for(size_t i=0; i<W_; i++){
    map_C[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      map_C[i][j] = population[i][j].C() / max;
    }
  }
    
  save_image(map_C, "C", filename);
  
  for(size_t i=0; i<W_; i++){
    delete[] map_C[i];
  }
  delete[] map_C;
}

void Box::visualize_fitness(string filename, double max){
  double** map_fitness = new double*[W_];
  for(size_t i=0; i<W_; i++){
    map_fitness[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      map_fitness[i][j] = population[i][j].fitness();
    }
  }
    
  save_image(map_fitness, "fitness", filename);
  
  for(size_t i=0; i<W_; i++){
    delete[] map_fitness[i];
  }
  delete[] map_fitness;
}

void Box::visualize_genome(string filename){
  double** map_genome = new double*[W_];
  for(size_t i=0; i<W_; i++){
    map_genome[i] = new double[H_];
    for(size_t j=0; j<H_; j++){
      map_genome[i][j] = population[i][j].alive() *( 1 + population[i][j].genome() );
    }
  }
  
  save_image(map_genome, "genome", filename);
  
  for(size_t i=0; i<W_; i++){
    delete[] map_genome[i];
  }
  delete[] map_genome;
}

void Box::study_data(void){
  double A_out = 0;
  double B_out = 0;
  double C_out = 0;
  double A_in_A = 0;
  double B_in_A = 0;
  double C_in_A = 0;
  double A_in_B = 0;
  double B_in_B = 0;
  double C_in_B = 0;
  double A_alive = 0;
  double B_alive = 0;
  ofstream f;
  
  for(size_t i=0; i<W_; i++){
    for(size_t j=0; j<H_; j++){
      if (population[i][j].genome()){
        B_alive += population[i][j].alive();
        A_in_B += population[i][j].A();
        B_in_B += population[i][j].B();
        C_in_B += population[i][j].C();
      }
      else {
        A_alive += population[i][j].alive();
        A_in_A += population[i][j].A();
        B_in_A += population[i][j].B();
        C_in_A += population[i][j].C();
      }
      A_out += CA_[i][j];
      B_out += CB_[i][j];
      C_out += CC_[i][j];
    }
  }
  
  f.open("mean-life-A.txt", ios::out | ios::app);
  f << A_alive << endl;
  f.close();
  f.open("mean-life-B.txt", ios::out | ios::app);
  f << B_alive << endl;
  f.close();
  f.open("mean-A-out.txt", ios::out | ios::app);
  f << A_out /( H_ * W_) << endl;
  f.close();
  f.open("mean-B-out.txt", ios::out | ios::app);
  f << B_out /( H_ * W_) << endl;
  f.close();
  f.open("mean-C-out.txt", ios::out | ios::app);
  f << C_out /( H_ * W_) << endl;
  f.close();
  f.open("mean-A-in-A.txt", ios::out | ios::app);
  f << A_in_A / A_alive << endl;
  f.close();
  f.open("mean-B-in-A.txt", ios::out | ios::app);
  f << B_in_A / A_alive << endl;
  f.close();
  f.open("mean-C-in-A.txt", ios::out | ios::app);
  f << C_in_A / A_alive << endl;
  f.close();
  f.open("mean-A-in-B.txt", ios::out | ios::app);
  f << A_in_B / B_alive << endl;
  f.close();
  f.open("mean-B-in-B.txt", ios::out | ios::app);
  f << B_in_B / B_alive << endl;
  f.close();
  f.open("mean-C-in-B.txt", ios::out | ios::app);
  f << C_in_B / B_alive << endl;
  f.close();
  
}

void Box::save_image(double** map, string type, string filename) const {
  //data in map[i][j] is a coefficient between 0 and 1,(except for genome)
  unsigned int MaxVal_ = 255;
  unsigned char* data_ = new unsigned char[ W_*H_*3 ];
  double R;
  double V;
  double B;
  
  for (size_t i=0; i<W_; i++){
    for (size_t j=0; j<H_; j++){
      
      if (type=="genome") {
        if (1 == map[i][j]) { R = 255; V = 100; B = 0; }
        if (2 == map[i][j]) { R = 0; V = 100; B = 255; }
        if (not map[i][j]) { R = 0; V = 0; B = 0; }
        map[i][j] = 1;
      }
      
      if (type=="fitness") {
        R = 255;
        V = 255;
        B = 255;  
      }
      
      if (type=="A") {
        R = 255;
        V = 0;
        B = 0;        
      }
      
      if (type=="B") {
        R = 0;
        V = 255;
        B = 0;  
      }
      
      if (type=="C") {
        R = 0;
        V = 0;
        B = 255;  
      }
      
      data_[(W_*j+i)*3] = (unsigned char) R * map[i][j];
      data_[(W_*j+i)*3+1] = (unsigned char) V * map[i][j];
      data_[(W_*j+i)*3+2] = (unsigned char) B * map[i][j];
    }
  }
  
  fstream f( filename.c_str(), ios::out | ios::trunc | ios::binary);
  f << "P6\n" << W_ << " " << H_ << "\n" << MaxVal_ << "\n";
  f.write((char*)data_ , sizeof(char)*W_*H_*3);
  f.close();
  
  delete[] data_;
  data_ = nullptr;
}

bool Box::isAlive(void) const {
  int life = 0;
  for(size_t i=0; i<W_; i++){
    for(size_t j=0; j<H_; j++){
      life += population[i][j].alive();
    }
  }
  return (life != 0);
}

bool Box::isFixed(void) const {
  unsigned int A = 0;
  for(size_t i=0; i<W_; i++){
    for(size_t j=0; j<H_; j++){
      A += population[i][j].genome();
    }
  }
  return (A == 0 and this->isAlive() );
}






