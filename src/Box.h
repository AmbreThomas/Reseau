
#ifndef Box_H__
#define Box_H__

#include "Ecoli.h"
#include <cstring>
#include <vector>
#include <algorithm>
#include <fstream>

using namespace std;

class Box {
 public :
  // =========================== Constructors ==========================
  
  Box(void);
  Box(int W, int H, double D, double Ainit);
  
  //=========================== Destructor =============================
  
  ~Box(void);
  
  // =========================== Getters ===============================
  
  inline Ecoli bact(int x, int y);
  inline double CA(int x, int y) const;
  inline double CB(int x, int y) const;
  inline double CC(int x, int y) const;
  inline int W(void) const;
  inline int H(void) const;
  
  //=========================== Setters ================================

  //=========================== Operators ==============================

  //=========================== Public Methods =========================

  void renew(double Azero);
  void diffuse(void);
  void nagasaki(void);
  void refill(void);
  void eat(void);
  void exchange(double& CA, double& CB, Ecoli& cell );
  
  void visualize_life(string filename);
  void visualize_A_out(string filename, double max);
  void visualize_B_out(string filename, double max);
  void visualize_C_out(string filename, double max);
  void visualize_A_in(string filename, double max);
  void visualize_B_in(string filename, double max);
  void visualize_C_in(string filename, double max);
  void visualize_fitness(string filename, double max);
  void visualize_genome(string filename);
  
  void study_data(void);
  
  void save_image(double** map, string type, string filename) const;
  bool isAlive(void) const;
  bool isFixed(void) const;
  
 protected :
  //=========================== Protected Methods ======================
  
  void pop(int x, int y);
  
  //=========================== Attributes =============================

  size_t W_;
  size_t H_;
  double D_;
  double Ainit_;
  Ecoli** population;
  double** CA_;
  double** CB_;
  double** CC_;
  
};

//===========================Getters' definitions=======================

  inline Ecoli Box::bact(int x, int y){ return population[x][y]; }
  inline double Box::CA(int x, int y) const { return CA_[x][y]; }
  inline double Box::CB(int x, int y) const { return CB_[x][y]; }
  inline double Box::CC(int x, int y) const { return CC_[x][y]; }
  inline int Box::W(void) const{ return W_; }
  inline int Box::H(void) const{ return H_; }

#endif // Box_H__
