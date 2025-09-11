def rotate_face_clockwise(grid):
    """Rotate a 3x3 grid clockwise"""
    return [[grid[2-i][j] for i in range(3)] for j in range(3)]

def rotate_face_counter_clockwise(grid):
    """Rotate a 3x3 grid counter-clockwise"""
    return [[grid[i][2-j] for i in range(3)] for j in range(3)]

def rotate_face_grid(grid, clockwise=True):
    """Rotate a 3x3 grid (default: clockwise)"""
    if clockwise:
        return rotate_face_clockwise(grid)
    else:
        return rotate_face_counter_clockwise(grid)
