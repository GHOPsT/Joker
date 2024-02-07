#include <iostream>
#include <thread>
#include <vector>

// Definición del tamaño de las matrices
const int N = 100;
const int M = 100;
const int K = 100;

// Definición de matrices
int A[N][M];
int B[M][K];
int C[N][K];

// Función para multiplicar una fila de la matriz A por una columna de la matriz B
void multiply(int row_A, int col_B) {
    int sum = 0;
    for (int i = 0; i < M; ++i) {
        sum += A[row_A][i] * B[i][col_B];
    }
    C[row_A][col_B] = sum;
}

int main() {
    // Inicialización de matrices A y B (para simplificar el ejemplo)
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < M; ++j) {
            A[i][j] = i + j;
            B[j][i] = i - j;
        }
    }

    // Creación de hilos para la multiplicación de matrices
    std::vector<std::thread> threads;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < K; ++j) {
            threads.push_back(std::thread(multiply, i, j));
        }
    }

    // Esperar a que todos los hilos terminen
    for (auto& t : threads) {
        t.join();
    }

    // Impresión de la matriz resultado C
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < K; ++j) {
            std::cout << C[i][j] << " ";
        }
        std::cout << std::endl;
    }

    return 0;
}