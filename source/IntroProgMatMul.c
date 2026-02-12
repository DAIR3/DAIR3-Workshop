#include <Eigen/Dense>
#include <iostream>

int main() {
    Eigen::Matrix2f A;
    A << 1, 2,
         3, 4;
    Eigen::Matrix2f B;
    B << 5, 6,
         7, 8;
    std::cout << "The product AB is:\n" << A * B;
}