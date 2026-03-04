#include <bits/stdc++.h>
using namespace std;

// Compute denom = ((i+j-2)*(i+j-1)/2) + i
inline double denom(int i, int j) {
    double k = i + j - 1;
    return ( (k-1)*k*0.5 ) + i;
}

// Compute y = A * x
void matvec_A(const vector<double>& x, vector<double>& y, int N) {
    fill(y.begin(), y.end(), 0.0);
    for(int i = 1; i <= N; ++i) {
        double *yp = &y[i-1];
        for(int j = 1; j <= N; ++j) {
            *yp += x[j-1] / denom(i, j);
        }
    }
}

// Compute y = A^T * x
void matvec_AT(const vector<double>& x, vector<double>& y, int N) {
    fill(y.begin(), y.end(), 0.0);
    for(int i = 1; i <= N; ++i) {
        double xi = x[i-1];
        for(int j = 1; j <= N; ++j) {
            y[j-1] += xi / denom(i, j);
        }
    }
}

// L2 norm of a vector
double norm2(const vector<double>& v) {
    long double s = 0;
    for(double x : v) s += (long double)x * x;
    return sqrt((double)s);
}

int main(int argc, char** argv) {
    int N = 2000;            // default size
    int max_iters = 100;
    double tol = 1e-12;

    if (argc > 1) N = stoi(argv[1]);
    vector<double> v(N), u(N), vt(N);

    // initialize v to random unit vector
    mt19937_64 rng(42);
    normal_distribution<double> dist(0.0,1.0);
    for(double &x : v) x = dist(rng);
    double nv = norm2(v);
    for(double &x : v) x /= nv;

    double sigma = 0, sigma_prev = 0;
    for(int iter = 1; iter <= max_iters; ++iter) {
        // u = A * v
        matvec_A(v, u, N);
        sigma = norm2(u);

        // vt = A^T * u
        matvec_AT(u, vt, N);

        // normalize vt → v
        double nvt = norm2(vt);
        for(int i = 0; i < N; ++i) v[i] = vt[i] / nvt;

        // check convergence
        if (iter > 1 && fabs(sigma - sigma_prev) < tol) {
            cout << "# converged in " << iter
                 << " iters, σ ≈ " << setprecision(12) << sigma << "\n";
            break;
        }
        sigma_prev = sigma;
        if (iter == max_iters)
            cout << "# max iters reached, σ ≈ " << setprecision(12)
                 << sigma << "\n";
    }

    return 0;
}
