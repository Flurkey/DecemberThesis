from Cube.Solver.beginners import solver
from .solver import solve_3x3

def solve(cube):
    if cube.dim == (2, 2):
        return solver.__solve_2x2(cube)
    elif cube.dim == (3, 3):
        return solver.__solve_3x3(cube)