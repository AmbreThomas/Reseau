
//=========================== Includes =================================

#include "Ecoli.h"

//================= Definition of static attributes ====================

double Ecoli::Wmin_ = 0.001;
double Ecoli::RAA_ = 0.1;
double Ecoli::RAB_ = 0.1;
double Ecoli::RBB_ = 0.1;
double Ecoli::RBC_ = 0.1;
double Ecoli::Pmut_ = 0.00;
double Ecoli::Pdeath_ = 1;
  
//=========================== Constructors =============================

Ecoli::Ecoli(){
  G_ = rand()%2;
  A_ = 0;
  B_ = 0;
  C_ = 0;
  vie_ = 1;
}

//=========================== Destructor ===============================

//=========================== Public Methods ===========================

double Ecoli::fitness(void) const{
  double w = B_* not(G_) + C_ * G_;
  if (w<Wmin_) w=0;
  return w;
}

void Ecoli::divide_to(Ecoli& dest){
  if (rand()/(double)RAND_MAX< Ecoli::Pmut_ ) { G_ = 1-G_; }
  A_ /= 2.;
  B_ /= 2.;
  C_ /= 2.;
  action_ = 1;
  dest.A_ = A_;
  dest.B_ = B_;
  dest.C_ = C_;
  dest.G_ = G_;
  dest.vie_ = 1;
  dest.action_ = 1;
}

void Ecoli::kill(void){
  vie_ = 0;
  A_ = 0;
  B_ = 0;
  C_ = 0;
  action_ = 1;
}
