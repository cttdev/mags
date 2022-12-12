#include "astar.h"

#include <iostream>
// #include <pybind11/eigen.h>
// #include <pybind11/numpy.h>
// #include <pybind11/pybind11.h>
// #include <pybind11/stl.h>

// namespace py = pybind11;

using namespace astar;
using namespace std;

int astar::add(int x, int y) {
    return x + y;
}

int main() {
    std::cout << "Hi" << add(1, 2) << '\n';
    return 0;
}
