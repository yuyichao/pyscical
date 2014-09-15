double compose_g(double J_sum, double J1, double J2, double g1, double g2);
double compose_gJ(double J, double L, double S);
double compose_gF(double F, double I, double J, double L, double S, double g_I);

long double genlaguerre(unsigned n, unsigned m, long double x);
long double harmonic_recoil(unsigned n1, unsigned n2, long double eta);
long double harmonic_scatter(unsigned n1, unsigned n2, long double eta,
                             long double theta0);
