
#ifndef Ecoli_H__
#define Ecoli_H__

#include <cstdio>
#include <cstdlib>
#include <iostream>

using namespace std;

class Ecoli {
 public :
  // =========================== Static attributes =====================
  
  static double Wmin_;
  static double RAA_;
  static double RAB_;
  static double RBB_;
  static double RBC_;
  static double Pmut_;
  static double Pdeath_;
  
  // =========================== Constructors ==========================
  
  Ecoli();
  
  //=========================== Destructor =============================
  
  // =========================== Getters ===============================
  
  inline bool alive(void) const;
  inline bool genome(void) const;
  inline double A(void) const;
  inline double B(void) const;
  inline double C(void) const;
  inline bool cold(void) const;

  //=========================== Setters ================================
  
  inline void setA(double A);
  inline void setB(double B);
  inline void setC(double C);
  inline void mature(void);
  inline void sleep(void);
  
  //=========================== Public Methods =========================
  
  double fitness(void) const;
  void divide_to(Ecoli& dest);
  void kill(void);
  
protected :
  
  //=========================== Attributes =============================
  
  int x_;
  int y_;
  int G_;
  double A_;
  double B_;
  double C_;
  bool vie_;
  bool action_;
  
};

//========================== Getters' definitions ======================

  inline bool Ecoli::alive(void) const { return vie_; }
  inline bool Ecoli::genome(void) const { return G_; }
  inline double Ecoli::A(void) const{ return A_; }
  inline double Ecoli::B(void) const{ return B_; }
  inline double Ecoli::C(void) const{ return C_; }
  inline bool Ecoli::cold(void) const{ return action_; }

//========================== Setters' definitions ======================

  inline void Ecoli::setA(double A) { A_ = A; }
  inline void Ecoli::setB(double B) { B_ = B; }
  inline void Ecoli::setC(double C) { C_ = C; }
  inline void Ecoli::sleep(void) { action_ = 0; }

#endif // Ecoli_H__
